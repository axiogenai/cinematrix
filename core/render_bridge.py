import os
import sys
import json
import time
import subprocess
import cv2
import numpy as np

from .audio_synth import synthesize_soundtrack
from .html_motion_generator import generate_motion_html

class DynamicChromiumVideoEngine:
    def __init__(self, ffmpeg_path: str = None, node_exe: str = "node"):
        self.node_exe = node_exe
        self.ffmpeg_path = ffmpeg_path or r"C:\Users\aditya\node_modules\ffmpeg-static\ffmpeg.exe"
        self.renderer_js = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chromium_renderer.js")

    def render_storyboard(self, storyboard: dict, output_dir: str, progress_callback=None) -> dict:
        """Dynamically compiles HTML5 + SVG motion stage and renders broadcast-grade MP4 via Headless Chromium."""
        os.makedirs(output_dir, exist_ok=True)

        video_id = storyboard.get("id", f"reel_{int(time.time())}")
        output_mp4 = os.path.join(output_dir, f"{video_id}.mp4")
        temp_wav = os.path.join(output_dir, f"{video_id}_audio.wav")
        stage_html = os.path.join(output_dir, f"{video_id}_stage.html")
        thumb_jpg = os.path.join(output_dir, f"{video_id}_thumb.jpg")

        scenes = storyboard.get("scenes", [])
        total_duration = sum(s.get("duration", 3.5) for s in scenes)
        fps = storyboard.get("fps", 30)

        aspect_ratio = storyboard.get("aspect_ratio", "16:9")
        if aspect_ratio == "9:16":
            width, height = 1080, 1920
        elif aspect_ratio == "1:1":
            width, height = 1080, 1080
        else: # 16:9
            width, height = 1920, 1080

        # Step 1: Synthesize Audio
        if progress_callback:
            progress_callback({
                "status": "synthesizing_audio",
                "percent": 5,
                "message": "Synthesizing multi-track ambient soundtrack (44.1kHz Master)..."
            })

        mood = storyboard.get("mood", "cinematic_tech")
        synthesize_soundtrack(total_duration, mood=mood, output_wav=temp_wav)

        # Step 2: Dynamically compile the HTML5 + SVG + GSAP stage
        if progress_callback:
            progress_callback({
                "status": "compiling_stage",
                "percent": 10,
                "message": f"Compiling dynamic SVG vector stage & typography ({len(scenes)} scenes)..."
            })

        html_content = generate_motion_html(storyboard)
        with open(stage_html, "w", encoding="utf-8") as f:
            f.write(html_content)

        # Step 3: Launch Headless Chromium Stream Pipeline
        cmd = [
            self.node_exe,
            self.renderer_js,
            "--html", stage_html,
            "--audio", temp_wav,
            "--output", output_mp4,
            "--fps", str(fps),
            "--duration", str(total_duration),
            "--width", str(width),
            "--height", str(height),
            "--ffmpeg", self.ffmpeg_path
        ]

        start_time = time.time()
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, universal_newlines=True)

        last_status = {}
        for line in process.stdout:
            line_str = line.strip()
            if not line_str:
                continue
            try:
                data = json.loads(line_str)
                last_status = data
                if progress_callback and data.get("status") == "rendering":
                    progress_callback(data)
            except Exception:
                pass

        process.wait()
        if process.returncode != 0:
            err_msg = last_status.get("error") or last_status.get("message") or f"Chromium render subprocess failed with exit code {process.returncode}"
            raise RuntimeError(err_msg)
        if not os.path.exists(output_mp4) or os.path.getsize(output_mp4) == 0:
            raise RuntimeError(f"Output video was not created or is 0 bytes: {output_mp4}")

        # Step 4: Extract Snapshot Thumbnail
        if os.path.exists(output_mp4):
            cap = cv2.VideoCapture(output_mp4)
            cap.set(cv2.CAP_PROP_POS_MSEC, int(total_duration * 0.35 * 1000))
            ret, frame = cap.read()
            if ret:
                cv2.imwrite(thumb_jpg, frame)
            cap.release()

        file_size = os.path.getsize(output_mp4) if os.path.exists(output_mp4) else 0

        if progress_callback:
            progress_callback({
                "status": "completed",
                "percent": 100,
                "output_mp4": output_mp4,
                "file_size": file_size,
                "message": f"Master motion film delivered successfully ({round(file_size / 1024 / 1024, 2)} MB)"
            })

        return {
            "id": video_id,
            "title": storyboard.get("title", "CineMatrix Motion Film"),
            "aspect_ratio": aspect_ratio,
            "duration": total_duration,
            "output_mp4": output_mp4,
            "thumbnail": thumb_jpg,
            "file_size_bytes": file_size,
            "render_time_seconds": round(time.time() - start_time, 2)
        }
