"""Real video generation through a user-owned ComfyUI instance.

The adapter deliberately supports API-format workflows instead of pretending that one
node graph fits every model. Optional node mappings let users pass shot duration,
dimensions, and frame rate to workflows that expose those inputs.
"""
import json
import os
import re
import shutil
import time
import uuid
import urllib.parse
import urllib.request
import urllib.error
import subprocess
from pathlib import Path

VIDEO_EXTENSIONS = {".mp4", ".webm", ".mov", ".mkv", ".gif"}


class VideoGenerationError(RuntimeError):
    pass


class ComfyUIVideoEngine:
    def __init__(self):
        self.base_url = os.getenv("COMFYUI_BASE_URL", "http://127.0.0.1:8188").rstrip("/")
        configured_workflow = os.getenv("COMFYUI_WORKFLOW_PATH", "")
        if configured_workflow and not os.path.isabs(configured_workflow):
            configured_workflow = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), configured_workflow)
        self.workflow_path = configured_workflow
        self.prompt_node_id = os.getenv("COMFYUI_PROMPT_NODE_ID", "")
        self.prompt_input = os.getenv("COMFYUI_PROMPT_INPUT", "text")
        self.negative_node_id = os.getenv("COMFYUI_NEGATIVE_NODE_ID", "")
        self.negative_input = os.getenv("COMFYUI_NEGATIVE_INPUT", "text")
        self.width_node_id = os.getenv("COMFYUI_WIDTH_NODE_ID", "")
        self.width_input = os.getenv("COMFYUI_WIDTH_INPUT", "width")
        self.height_node_id = os.getenv("COMFYUI_HEIGHT_NODE_ID", "")
        self.height_input = os.getenv("COMFYUI_HEIGHT_INPUT", "height")
        self.frames_node_id = os.getenv("COMFYUI_FRAMES_NODE_ID", "")
        self.frames_input = os.getenv("COMFYUI_FRAMES_INPUT", "length")
        self.fps_node_id = os.getenv("COMFYUI_FPS_NODE_ID", "")
        self.fps_input = os.getenv("COMFYUI_FPS_INPUT", "frame_rate")
        self.ffmpeg = os.getenv("FFMPEG_PATH") or shutil.which("ffmpeg") or "ffmpeg"
        self.ffprobe = os.getenv("FFPROBE_PATH") or shutil.which("ffprobe") or "ffprobe"
        try:
            self.timeout = max(30, int(os.getenv("COMFYUI_TIMEOUT_SECONDS", "1800")))
        except ValueError:
            self.timeout = 1800

    def status(self):
        workflow_exists = bool(self.workflow_path and os.path.isfile(self.workflow_path))
        configured = bool(self.base_url and self.prompt_node_id and workflow_exists)
        reachable = False
        detail = "ComfyUI workflow is not configured."
        try:
            with urllib.request.urlopen(self.base_url + "/system_stats", timeout=3) as response:
                reachable = response.status == 200
                detail = "ComfyUI reachable."
        except Exception as exc:
            detail = "Cannot reach ComfyUI at " + self.base_url + ": " + str(exc)
        return {
            "configured": configured,
            "reachable": reachable,
            "base_url": self.base_url,
            "workflow_configured": workflow_exists,
            "detail": detail,
        }

    def _request_json(self, url, payload=None, timeout=30):
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        headers = {"Content-Type": "application/json"} if data is not None else {}
        request = urllib.request.Request(url, data=data, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise VideoGenerationError("ComfyUI returned HTTP " + str(exc.code) + ": " + body[:1200]) from exc
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise VideoGenerationError("ComfyUI request failed (" + url + "): " + str(exc)) from exc

    def _load_workflow(self):
        if not self.workflow_path or not os.path.isfile(self.workflow_path):
            raise VideoGenerationError(
                "Real video generation is not configured. Set COMFYUI_WORKFLOW_PATH to a ComfyUI "
                "API-format workflow JSON and configure COMFYUI_PROMPT_NODE_ID."
            )
        if not self.prompt_node_id:
            raise VideoGenerationError("Set COMFYUI_PROMPT_NODE_ID to the positive prompt node ID in your API workflow.")
        try:
            with open(self.workflow_path, "r", encoding="utf-8") as handle:
                workflow = json.load(handle)
        except (OSError, ValueError) as exc:
            raise VideoGenerationError("Cannot read ComfyUI workflow JSON: " + str(exc)) from exc
        if not isinstance(workflow, dict) or not workflow:
            raise VideoGenerationError("ComfyUI workflow must be a non-empty API-format node dictionary.")
        return workflow

    @staticmethod
    def _set_node_input(workflow, node_id, input_name, value, label):
        if not node_id:
            return
        node_id = str(node_id)
        if node_id not in workflow:
            raise VideoGenerationError(label + " node " + repr(node_id) + " does not exist in the configured workflow.")
        inputs = workflow[node_id].get("inputs", {})
        if input_name not in inputs:
            raise VideoGenerationError(label + " input " + repr(input_name) + " was not found on node " + repr(node_id) + ".")
        inputs[input_name] = value

    @staticmethod
    def _video_files(outputs):
        """Extract supported video files from standard and common custom-node output keys."""
        files = []
        for node_output in outputs.values():
            if not isinstance(node_output, dict):
                continue
            for key, value in node_output.items():
                if key not in {"videos", "gifs", "files", "images"} or not isinstance(value, list):
                    continue
                for item in value:
                    if isinstance(item, dict) and item.get("filename"):
                        if Path(item["filename"]).suffix.lower() in VIDEO_EXTENSIONS:
                            files.append(item)
        return files

    def _generate_clip(self, workflow_template, prompt, negative_prompt, output_dir, index, scene, storyboard):
        workflow = json.loads(json.dumps(workflow_template))
        self._set_node_input(workflow, self.prompt_node_id, self.prompt_input, prompt, "Positive prompt")
        if self.negative_node_id:
            self._set_node_input(workflow, self.negative_node_id, self.negative_input, negative_prompt, "Negative prompt")

        ratio = storyboard.get("aspect_ratio", "16:9")
        dimensions = {"9:16": (720, 1280), "1:1": (1024, 1024), "16:9": (1280, 720)}
        width, height = dimensions.get(ratio, dimensions["16:9"])
        fps = int(storyboard.get("fps", 24) or 24)
        duration = max(1.0, float(scene.get("duration", 4)))
        # Only update optional controls explicitly mapped by the user; node meanings vary by model.
        self._set_node_input(workflow, self.width_node_id, self.width_input, width, "Width")
        self._set_node_input(workflow, self.height_node_id, self.height_input, height, "Height")
        self._set_node_input(workflow, self.frames_node_id, self.frames_input, max(1, int(round(duration * fps))), "Frame count")
        self._set_node_input(workflow, self.fps_node_id, self.fps_input, fps, "Frame rate")

        # Vary integer seed inputs between shots without touching linked values or non-seed controls.
        for node in workflow.values():
            node_inputs = node.get("inputs", {}) if isinstance(node, dict) else {}
            if isinstance(node_inputs, dict) and isinstance(node_inputs.get("seed"), int):
                node_inputs["seed"] = (node_inputs["seed"] + uuid.uuid4().int % 2_000_000_000) % 2_000_000_000

        queued = self._request_json(self.base_url + "/prompt", {"prompt": workflow, "client_id": "cinematrix-" + uuid.uuid4().hex})
        prompt_id = queued.get("prompt_id")
        if not prompt_id:
            node_errors = queued.get("node_errors")
            raise VideoGenerationError("ComfyUI did not queue the workflow: " + json.dumps(node_errors or queued)[:1200])

        deadline = time.monotonic() + self.timeout
        history = None
        while time.monotonic() < deadline:
            history_payload = self._request_json(
                self.base_url + "/history/" + urllib.parse.quote(prompt_id, safe=""), timeout=15
            )
            history = history_payload.get(prompt_id)
            if history:
                status = history.get("status") or {}
                if status.get("status_str") in {"error", "failed"}:
                    raise VideoGenerationError("ComfyUI workflow failed: " + json.dumps(status)[:1600])
                if history.get("outputs"):
                    break
            time.sleep(2)
        if not history or not history.get("outputs"):
            raise VideoGenerationError("Timed out waiting for ComfyUI generation " + str(prompt_id) + ".")

        files = self._video_files(history["outputs"])
        if not files:
            raise VideoGenerationError(
                "The workflow finished but returned no supported video file. Add a video-output node "
                "(such as Video Combine) and ensure its output is included in the API workflow."
            )
        item = files[-1]
        query = urllib.parse.urlencode({
            "filename": item["filename"],
            "subfolder": item.get("subfolder", ""),
            "type": item.get("type", "output"),
        })
        url = self.base_url + "/view?" + query
        extension = Path(item["filename"]).suffix.lower()
        destination = os.path.join(output_dir, "shot_" + str(index).zfill(3) + extension)
        try:
            with urllib.request.urlopen(url, timeout=180) as response, open(destination, "wb") as output:
                shutil.copyfileobj(response, output)
        except Exception as exc:
            raise VideoGenerationError("Could not download generated clip " + str(index) + ": " + str(exc)) from exc
        if not os.path.isfile(destination) or os.path.getsize(destination) < 1024:
            raise VideoGenerationError("ComfyUI returned an empty or invalid clip for shot " + str(index) + ".")
        return destination

    def _has_audio(self, path):
        try:
            result = subprocess.run(
                [self.ffprobe, "-v", "error", "-select_streams", "a:0", "-show_entries", "stream=codec_type",
                 "-of", "default=noprint_wrappers=1:nokey=1", path],
                capture_output=True, text=True, timeout=30,
            )
            return result.returncode == 0 and "audio" in result.stdout.lower()
        except (OSError, subprocess.SubprocessError):
            return False

    def _normalize_clip(self, source, destination, width, height, fps, duration):
        # Trim long model outputs and freeze the last frame only if a model produced a shorter shot.
        # The duration-aware workflow mapping remains the preferred way to generate the right motion length.
        video_filter = "scale=" + str(width) + ":" + str(height) + ":force_original_aspect_ratio=increase,crop=" + str(width) + ":" + str(height) + ",fps=" + str(fps) + ",tpad=stop_mode=clone:stop_duration=" + str(duration) + ",setsar=1,format=yuv420p"
        command = [self.ffmpeg, "-y", "-i", source]
        if self._has_audio(source):
            command += ["-map", "0:v:0", "-map", "0:a:0", "-vf", video_filter,
                        "-af", "aresample=async=1:first_pts=0,apad", "-c:a", "aac", "-ar", "48000", "-ac", "2", "-shortest"]
        else:
            command += ["-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=48000",
                        "-map", "0:v:0", "-map", "1:a:0", "-vf", video_filter,
                        "-c:a", "aac", "-ar", "48000", "-ac", "2", "-shortest"]
        command += ["-t", str(duration), "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-movflags", "+faststart", destination]
        try:
            completed = subprocess.run(command, capture_output=True, text=True, timeout=600)
        except (OSError, subprocess.SubprocessError) as exc:
            raise VideoGenerationError("FFmpeg could not normalize a generated clip: " + str(exc)) from exc
        if completed.returncode != 0 or not os.path.isfile(destination) or os.path.getsize(destination) < 1024:
            raise VideoGenerationError("FFmpeg clip normalization failed: " + (completed.stderr[-1600:] if completed else "no output"))

    def render_storyboard(self, storyboard, output_dir, progress_callback=None):
        started_at = time.time()
        os.makedirs(output_dir, exist_ok=True)
        workflow = self._load_workflow()
        scenes = storyboard.get("scenes") or []
        if not scenes:
            raise VideoGenerationError("Storyboard has no shots to generate.")
        raw_id = str(storyboard.get("id") or "cinematrix_" + uuid.uuid4().hex[:12])
        video_id = re.sub(r"[^A-Za-z0-9_-]", "_", raw_id)[:100] or "cinematrix_" + uuid.uuid4().hex[:12]
        work_dir = os.path.join(output_dir, video_id + "_clips")
        os.makedirs(work_dir, exist_ok=True)
        raw_clips = []
        for index, scene in enumerate(scenes, start=1):
            shot_prompt = (scene.get("video_prompt") or scene.get("shot_prompt") or
                           scene.get("visual_description") or scene.get("headline") or "").strip()
            if not shot_prompt:
                raise VideoGenerationError("Shot " + str(index) + " has no video_prompt. Regenerate the storyboard with the AI director.")
            if progress_callback:
                progress_callback({"status": "generating_video", "percent": int((index - 1) / len(scenes) * 70),
                                   "message": "Generating real footage: shot " + str(index) + "/" + str(len(scenes))})
            style = storyboard.get("visual_style", "cinematic, coherent natural motion")
            prompt = shot_prompt + ". Visual direction: " + str(style) + ". Camera: " + str(scene.get("camera", "motivated cinematic camera movement")) + ". "
            prompt += "Lighting: " + str(scene.get("lighting", "motivated cinematic lighting")) + ". Target shot duration: " + str(scene.get("duration", 4)) + " seconds."
            negative = scene.get("negative_prompt") or storyboard.get(
                "negative_prompt", "text overlays, subtitles, watermark, logo artifacts, flicker, distorted anatomy, low quality"
            )
            raw_clips.append(self._generate_clip(workflow, prompt, negative, work_dir, index, scene, storyboard))

        ratio = storyboard.get("aspect_ratio", "16:9")
        dimensions = {"9:16": (720, 1280), "1:1": (1024, 1024), "16:9": (1280, 720)}
        width, height = dimensions.get(ratio, dimensions["16:9"])
        fps = int(storyboard.get("fps", 24) or 24)
        normalized = []
        for index, clip in enumerate(raw_clips, start=1):
            normalized_path = os.path.join(work_dir, "normalized_" + str(index).zfill(3) + ".mp4")
            if progress_callback:
                progress_callback({"status": "normalizing", "percent": 70 + int((index - 1) / len(raw_clips) * 12),
                                   "message": "Normalizing clip format: " + str(index) + "/" + str(len(raw_clips))})
            shot_duration = max(1.0, float(scenes[index - 1].get("duration", 4)))
            self._normalize_clip(clip, normalized_path, width, height, fps, shot_duration)
            normalized.append(normalized_path)

        concat_file = os.path.join(work_dir, "concat.txt")
        with open(concat_file, "w", encoding="utf-8") as handle:
            for clip in normalized:
                safe_path = os.path.abspath(clip).replace("\\", "/").replace("'", "'\\''")
                handle.write("file '" + safe_path + "'\n")
        output_mp4 = os.path.join(output_dir, video_id + ".mp4")
        command = [self.ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", concat_file,
                   "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                   "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", "-movflags", "+faststart", output_mp4]
        if progress_callback:
            progress_callback({"status": "assembling", "percent": 85, "message": "Assembling generated footage with FFmpeg..."})
        try:
            completed = subprocess.run(command, capture_output=True, text=True, timeout=900)
        except (OSError, subprocess.SubprocessError) as exc:
            raise VideoGenerationError("FFmpeg could not assemble generated clips: " + str(exc)) from exc
        if completed.returncode != 0 or not os.path.isfile(output_mp4) or os.path.getsize(output_mp4) < 1024:
            raise VideoGenerationError("FFmpeg clip assembly failed: " + (completed.stderr[-1800:] if completed else "no output"))

        audio_status = "Original clip audio preserved; no synthetic soundtrack requested."
        if os.getenv("CINEMATRIX_SYNTHESIZE_SOUNDTRACK", "true").strip().lower() not in {"0", "false", "no", "off"}:
            if progress_callback:
                progress_callback({"status": "sound_design", "percent": 94, "message": "Creating and mixing a locally synthesized background score..."})
            try:
                from .audio_synth import synthesize_soundtrack
                soundtrack = os.path.join(work_dir, "soundtrack.wav")
                synthesize_soundtrack(sum(max(1.0, float(scene.get("duration", 4))) for scene in scenes),
                                      mood=storyboard.get("mood", "cinematic_tech"), output_wav=soundtrack)
                mixed_path = os.path.join(output_dir, video_id + "_mixed.mp4")
                mix_command = [self.ffmpeg, "-y", "-i", output_mp4, "-i", soundtrack,
                    "-filter_complex", "[0:a]volume=0.82[original];[1:a]volume=0.18[music];[original][music]amix=inputs=2:duration=first:dropout_transition=1,alimiter=limit=0.95[aout]",
                    "-map", "0:v:0", "-map", "[aout]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", "-movflags", "+faststart", mixed_path]
                mixed = subprocess.run(mix_command, capture_output=True, text=True, timeout=180)
                if mixed.returncode == 0 and os.path.isfile(mixed_path) and os.path.getsize(mixed_path) > 1024:
                    os.replace(mixed_path, output_mp4)
                    audio_status = "Locally synthesized background score mixed under generated clip audio."
                else:
                    audio_status = "Video rendered; soundtrack mix skipped: " + (mixed.stderr[-500:] if mixed else "FFmpeg returned no result.")
            except Exception as exc:
                audio_status = "Video rendered; soundtrack mix skipped: " + str(exc)

        thumbnail = os.path.join(output_dir, video_id + "_thumb.jpg")
        try:
            thumb_result = subprocess.run(
                [self.ffmpeg, "-y", "-ss", "0.5", "-i", output_mp4, "-frames:v", "1", "-q:v", "2", thumbnail],
                capture_output=True, text=True, timeout=60,
            )
            if thumb_result.returncode != 0 or not os.path.isfile(thumbnail):
                thumbnail = None
        except (OSError, subprocess.SubprocessError):
            thumbnail = None
        if progress_callback:
            progress_callback({"status": "completed", "percent": 100, "message": "Generated video assembled."})
        return {
            "id": video_id,
            "title": storyboard.get("title", "CineMatrix AI Film"),
            "aspect_ratio": ratio,
            "duration": round(sum(max(1.0, float(scene.get("duration", 4))) for scene in scenes), 2),
            "output_mp4": output_mp4,
            "thumbnail": thumbnail,
            "clips": raw_clips,
            "engine": "comfyui",
            "file_size_bytes": os.path.getsize(output_mp4),
            "render_time_seconds": round(time.time() - started_at, 2),
            "audio_status": audio_status,
        }
