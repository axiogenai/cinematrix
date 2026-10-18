import os
import sys
import glob
import time
import uuid
import json
import asyncio
from typing import Dict, Any, Optional
from threading import Thread

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core.render_bridge import DynamicChromiumVideoEngine
from core.video_engine import VideoEngine as OpenCVVideoEngine
from ai.groq_director import GroqCreativeDirector

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
STATIC_DIR = os.path.join(BASE_DIR, "static")
PRESETS_DIR = os.path.join(BASE_DIR, "presets")

os.makedirs(OUTPUT_DIR, exist_ok=True)
STATIC_DIR = os.path.join(BASE_DIR, "static")
PRESETS_DIR = os.path.join(BASE_DIR, "presets")

app = FastAPI(title="CineMatrix Media Studio API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Services
groq_director = GroqCreativeDirector()
chromium_engine = DynamicChromiumVideoEngine()
opencv_engine = OpenCVVideoEngine()

# In-memory job progress tracking
RENDER_JOBS: Dict[str, Dict[str, Any]] = {}

class GenerateStoryboardRequest(BaseModel):
    prompt: str
    aspect_ratio: str = "16:9"
    target_duration: float = 15.0
    mood: str = "cinematic_tech"

class RenderRequest(BaseModel):
    storyboard: Dict[str, Any]
    engine: str = "chromium"  # "chromium" (HTML5/SVG motion) or "opencv" (100% pure Python)

@app.get("/api/status")
def get_status():
    return {
        "status": "online",
        "engine": "CineMatrix Pro Video Engine v2.0 (Dual Engine: Chromium SVG + Pure Python OpenCV)",
        "groq_model": groq_director.model,
        "groq_active": bool(groq_director.api_key),
        "ffmpeg_path": chromium_engine.ffmpeg_path,
        "output_count": len(glob.glob(os.path.join(OUTPUT_DIR, "*.mp4")))
    }

@app.get("/api/presets")
def list_presets():
    presets = []
    for f in glob.glob(os.path.join(PRESETS_DIR, "*.json")):
        try:
            with open(f, "r", encoding="utf-8") as pf:
                data = json.load(pf)
                presets.append({
                    "id": data.get("id", os.path.basename(f).replace(".json", "")),
                    "title": data.get("title", "Untitled Preset"),
                    "aspect_ratio": data.get("aspect_ratio", "16:9"),
                    "duration": sum(s.get("duration", 3.0) for s in data.get("scenes", [])),
                    "storyboard": data
                })
        except Exception:
            pass
    return {"presets": presets}

@app.post("/api/storyboard/generate")
def generate_storyboard(req: GenerateStoryboardRequest):
    if not req.prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")

    storyboard = groq_director.generate_storyboard(
        prompt=req.prompt,
        aspect_ratio=req.aspect_ratio,
        target_duration=req.target_duration,
        mood=req.mood
    )
    storyboard["id"] = f"reel_{int(time.time())}"
    return {"success": True, "storyboard": storyboard}

def run_render_worker(job_id: str, storyboard: dict, engine_name: str = "chromium"):
    def update_progress(data: dict):
        RENDER_JOBS[job_id].update(data)

    try:
        RENDER_JOBS[job_id]["status"] = "processing"
        if engine_name == "opencv":
            result = opencv_engine.render_storyboard(storyboard, OUTPUT_DIR, progress_callback=update_progress)
        else:
            result = chromium_engine.render_storyboard(storyboard, OUTPUT_DIR, progress_callback=update_progress)
            
        RENDER_JOBS[job_id].update({
            "status": "completed",
            "percent": 100,
            "result": result,
            "video_url": f"/output/{os.path.basename(result['output_mp4'])}",
            "thumb_url": f"/output/{os.path.basename(result['thumbnail'])}"
        })
    except Exception as e:
        RENDER_JOBS[job_id].update({
            "status": "failed",
            "error": str(e),
            "percent": 0
        })

@app.post("/api/render")
def trigger_render(req: RenderRequest):
    sb = req.storyboard
    if not sb.get("scenes"):
        raise HTTPException(status_code=400, detail="Storyboard must contain at least one scene")

    job_id = f"job_{uuid.uuid4().hex[:8]}"
    sb["id"] = sb.get("id") or f"video_{int(time.time())}"

    RENDER_JOBS[job_id] = {
        "job_id": job_id,
        "video_id": sb["id"],
        "engine": req.engine,
        "status": "queued",
        "percent": 0,
        "message": f"Render job queued in pipeline (Engine: {req.engine})...",
        "created_at": time.time()
    }

    thread = Thread(target=run_render_worker, args=(job_id, sb, req.engine), daemon=True)
    thread.start()

    return {"job_id": job_id, "video_id": sb["id"], "status": "queued"}

@app.get("/api/render/progress/{job_id}")
@app.get("/api/jobs/{job_id}")
def get_render_progress(job_id: str):
    if job_id not in RENDER_JOBS:
        raise HTTPException(status_code=404, detail="Job not found")
    return RENDER_JOBS[job_id]

@app.get("/api/videos")
def list_videos():
    videos = []
    mp4_files = sorted(glob.glob(os.path.join(OUTPUT_DIR, "*.mp4")), key=os.path.getmtime, reverse=True)

    for mp4 in mp4_files:
        basename = os.path.basename(mp4)
        vid_id = basename.replace(".mp4", "")
        thumb_file = os.path.join(OUTPUT_DIR, f"{vid_id}_thumb.jpg")
        size_bytes = os.path.getsize(mp4)

        videos.append({
            "id": vid_id,
            "filename": basename,
            "video_url": f"/output/{basename}",
            "thumb_url": f"/output/{os.path.basename(thumb_file)}" if os.path.exists(thumb_file) else None,
            "size_bytes": size_bytes,
            "size_formatted": f"{round(size_bytes / (1024 * 1024), 2)} MB",
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(mp4)))
        })
    return {"videos": videos}

# Static file routes
@app.get("/output/{filename}")
def serve_output_file(filename: str):
    file_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    media_type = "video/mp4" if filename.endswith(".mp4") else "image/jpeg" if filename.endswith(".jpg") else "audio/wav"
    return FileResponse(file_path, media_type=media_type)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def serve_index():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "CineMatrix Media Studio API is running. Build static UI in /static."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8090, reload=False)
