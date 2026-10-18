import os
import sys
import time
import math
import subprocess
import cv2
import numpy as np
from PIL import Image, ImageDraw

from .audio_synth import synthesize_soundtrack
from .visual_compositor import VisualCompositor, clamp, ease_out_cubic

class VideoEngine:
    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        self.ffmpeg_path = ffmpeg_path
        if not os.path.exists(self.ffmpeg_path):
            # Check default static paths or PATH
            common_paths = [
                r"C:\Users\aditya\node_modules\ffmpeg-static\ffmpeg.exe",
                "ffmpeg.exe",
                "ffmpeg"
            ]
            for p in common_paths:
                if os.path.exists(p):
                    self.ffmpeg_path = p
                    break

    def render_storyboard(self, storyboard: dict, output_dir: str, progress_callback=None) -> dict:
        """Renders an entire storyboard into a broadcast-grade MP4 video."""
        os.makedirs(output_dir, exist_ok=True)

        aspect_ratio = storyboard.get("aspect_ratio", "16:9")
        if aspect_ratio == "9:16":
            width, height = 1080, 1920
        elif aspect_ratio == "1:1":
            width, height = 1080, 1080
        else: # 16:9
            width, height = 1920, 1080

        fps = storyboard.get("fps", 30)
        scenes = storyboard.get("scenes", [])
        total_duration = sum(s.get("duration", 4.0) for s in scenes)
        total_frames = int(total_duration * fps)

        video_id = storyboard.get("id", f"video_{int(time.time())}")
        output_mp4 = os.path.join(output_dir, f"{video_id}.mp4")
        temp_wav = os.path.join(output_dir, f"{video_id}_temp.wav")
        thumb_jpg = os.path.join(output_dir, f"{video_id}_thumb.jpg")

        # Step 1: Synthesize Master Audio
        if progress_callback:
            progress_callback({
                "status": "synthesizing_audio",
                "percent": 5,
                "message": "Synthesizing multi-track ambient soundtrack & sound effects..."
            })

        mood = storyboard.get("mood", "cinematic_tech")
        synthesize_soundtrack(total_duration, mood=mood, output_wav=temp_wav)

        # Step 2: Initialize Visual Compositor
        compositor = VisualCompositor(width, height)

        # Step 3: Spawn FFmpeg Stream Process
        cmd = [
            self.ffmpeg_path,
            "-y",
            "-f", "rawvideo",
            "-vcodec", "rawvideo",
            "-s", f"{width}x{height}",
            "-pix_fmt", "bgr24",
            "-r", str(fps),
            "-i", "-", # Pipe raw frames from stdin
            "-i", temp_wav, # Master audio
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", "fast",
            "-crf", "18",
            "-c:a", "aac",
            "-b:a", "256k",
            "-movflags", "+faststart",
            "-shortest",
            output_mp4
        ]

        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        start_time = time.time()
        rendered_frames = 0

        # Calculate scene time boundaries
        scene_bounds = []
        cur_t = 0.0
        for s in scenes:
            dur = s.get("duration", 4.0)
            scene_bounds.append((cur_t, cur_t + dur, s))
            cur_t += dur

        # Saved thumbnail frame (around 30% through the video)
        thumb_frame_target = int(total_frames * 0.35)

        for frame_idx in range(total_frames):
            current_time = frame_idx / fps

            # Find active scene
            active_scene = scenes[-1]
            local_progress = 1.0
            for start_t, end_t, sc in scene_bounds:
                if start_t <= current_time < end_t:
                    active_scene = sc
                    dur = end_t - start_t
                    local_progress = (current_time - start_t) / dur
                    break

            # Render Scene Frame
            scene_type = active_scene.get("type", "kinetic_title")
            img = compositor.create_canvas(bg_style=active_scene.get("bg_style", "obsidian_grid"), progress=local_progress)

            # Badge
            badge = active_scene.get("badge", "")
            if badge:
                badge_x = int(50 * compositor.scale_factor) if compositor.is_vertical else int(80 * compositor.scale_factor)
                badge_y = int(60 * compositor.scale_factor) if compositor.is_vertical else int(60 * compositor.scale_factor)
                compositor.draw_telemetry_badge(ImageDraw.Draw(img), badge_x, badge_y, badge, opacity=min(1.0, local_progress / 0.2))

            if scene_type == "kinetic_title":
                compositor.draw_kinetic_headline(
                    img,
                    text=active_scene.get("headline", ""),
                    subtext=active_scene.get("subtext", ""),
                    progress=local_progress,
                    y_anchor=active_scene.get("y_anchor", 0.45)
                )

            elif scene_type == "code_showcase":
                pkg_name = "".join(c for c in storyboard.get("brand_name", "app") if c.isalnum()).lower() or "runtime"
                code_lines = active_scene.get("code_lines", [
                    f"import {{ Service }} from '@{pkg_name}/core';",
                    "const app = new Service({ production: true });",
                    "await app.orchestrateStream();"
                ])
                compositor.draw_code_editor_window(
                    img,
                    code_lines=code_lines,
                    filename=active_scene.get("filename", "orchestrator.ts"),
                    progress=local_progress
                )
                if active_scene.get("headline"):
                    compositor.draw_kinetic_headline(img, active_scene["headline"], active_scene.get("subtext", ""), local_progress, y_anchor=0.18 if not compositor.is_vertical else 0.22)

            elif scene_type == "metrics_telemetry":
                metrics = active_scene.get("metrics", [
                    {"label": "Inference Latency", "value": "12ms", "delta": "+94% faster"},
                    {"label": "Precision Score", "value": "99.8%", "delta": "+14.2% YoY"},
                    {"label": "Scale Throughput", "value": "100k/s", "delta": "Verified"}
                ])
                compositor.draw_metric_telemetry_card(img, metrics=metrics, progress=local_progress)
                if active_scene.get("headline"):
                    compositor.draw_kinetic_headline(img, active_scene["headline"], active_scene.get("subtext", ""), local_progress, y_anchor=0.25 if not compositor.is_vertical else 0.24)

            elif scene_type in ["brand_stinger", "brand_radar"]:
                b_title = active_scene.get("brand_title") or storyboard.get("brand_name") or storyboard.get("title", "CINEMATRIX")
                b_tag = active_scene.get("tagline") or active_scene.get("subtext", "Engineered for Velocity")
                b_url = active_scene.get("web_url") or storyboard.get("web_url", "")
                compositor.draw_brand_reveal(
                    img,
                    brand_title=b_title,
                    tagline=b_tag,
                    web_url=b_url,
                    progress=local_progress
                )

            # Handle global fade-out at the very end
            if frame_idx >= total_frames - int(fps * 0.6):
                fade_progress = (frame_idx - (total_frames - int(fps * 0.6))) / (fps * 0.6)
                fade_alpha = 1.0 - ease_out_cubic(fade_progress)
                # Darken image
                np_frame = np.array(img, dtype=np.uint8)
                for c in range(3):
                    np_frame[:, :, c] = (np_frame[:, :, c] * fade_alpha).astype(np.uint8)
                img = Image.fromarray(np_frame, "RGBA")

            # Convert to BGR array for FFmpeg
            bgr_frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGBA2BGR)
            process.stdin.write(bgr_frame.tobytes())

            rendered_frames += 1

            # Save snapshot thumbnail
            if frame_idx == thumb_frame_target:
                cv2.imwrite(thumb_jpg, bgr_frame)

            # Progress tracking
            if progress_callback and (frame_idx % 15 == 0 or frame_idx == total_frames - 1):
                elapsed = time.time() - start_time
                current_fps = rendered_frames / max(0.001, elapsed)
                pct = int(10 + (rendered_frames / total_frames) * 85)
                eta = (total_frames - rendered_frames) / max(0.001, current_fps)

                progress_callback({
                    "status": "rendering",
                    "percent": pct,
                    "frame": rendered_frames,
                    "total_frames": total_frames,
                    "fps": round(current_fps, 1),
                    "eta_seconds": round(eta, 1),
                    "message": f"Rendering Scene: {active_scene.get('headline', scene_type)} ({rendered_frames}/{total_frames} frames @ {round(current_fps, 1)} fps)"
                })

        # Close stdin and wait for FFmpeg to finish encoding
        process.stdin.close()
        process.wait()

        # Clean up temporary WAV
        if os.path.exists(temp_wav):
            try:
                os.remove(temp_wav)
            except Exception:
                pass

        if not os.path.exists(thumb_jpg):
            # Fallback thumbnail
            dummy = np.zeros((height, width, 3), dtype=np.uint8)
            cv2.imwrite(thumb_jpg, dummy)

        file_size = os.path.getsize(output_mp4) if os.path.exists(output_mp4) else 0

        if progress_callback:
            progress_callback({
                "status": "completed",
                "percent": 100,
                "message": "Master video encoded successfully!",
                "output_mp4": output_mp4,
                "file_size": file_size
            })

        return {
            "id": video_id,
            "title": storyboard.get("title", "Untitled Film"),
            "aspect_ratio": aspect_ratio,
            "duration": total_duration,
            "total_frames": total_frames,
            "output_mp4": output_mp4,
            "thumbnail": thumb_jpg,
            "file_size_bytes": file_size,
            "render_time_seconds": round(time.time() - start_time, 2)
        }
