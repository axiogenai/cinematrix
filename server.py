import os
import glob
import time
import uuid
import json
import re
from typing import Dict, Any
from threading import Thread


def _load_local_env_file():
    """Load a project .env without overriding explicitly exported process variables."""
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    if not os.path.isfile(env_path):
        return
    try:
        with open(env_path, "r", encoding="utf-8-sig") as env_file:
            for raw_line in env_file:
                line = raw_line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip()
                if value.startswith(("'", '"')) and len(value) >= 2 and value[-1] == value[0]:
                    value = value[1:-1]
                if key and key.replace("_", "").isalnum():
                    os.environ.setdefault(key, value)
    except OSError:
        # A missing/unreadable .env is handled by explicit configuration errors later.
        return


_load_local_env_file()

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from core.render_bridge import DynamicChromiumVideoEngine
from core.video_engine import VideoEngine as OpenCVVideoEngine
from core.comfyui_video_engine import ComfyUIVideoEngine, VideoGenerationError
from ai.groq_director import GroqCreativeDirector, CreativeDirectorError

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
STATIC_DIR = os.path.join(BASE_DIR, "static")
PRESETS_DIR = os.path.join(BASE_DIR, "presets")
os.makedirs(OUTPUT_DIR, exist_ok=True)

app = FastAPI(title="CineMatrix Media Studio API", version="3.1.0")
allowed_origins = [
    origin.strip()
    for origin in os.getenv("CINEMATRIX_ALLOWED_ORIGINS", "http://127.0.0.1:8090,http://localhost:8090").split(",")
    if origin.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

groq_director = GroqCreativeDirector()
chromium_engine = DynamicChromiumVideoEngine()
opencv_engine = OpenCVVideoEngine()
comfyui_engine = ComfyUIVideoEngine()
RENDER_JOBS: Dict[str, Dict[str, Any]] = {}


class GenerateStoryboardRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=12000)
    aspect_ratio: str = "16:9"
    target_duration: float = Field(default=15.0, ge=4, le=180)
    mood: str = "cinematic"


class RenderRequest(BaseModel):
    storyboard: Dict[str, Any]
    # comfyui is actual generative video; chromium/opencv are explicitly motion-graphics modes.
    engine: str = "comfyui"


@app.get("/api/status")
def get_status():
    video_status = comfyui_engine.status()
    return {
        "status": "online",
        "version": app.version,
        "storyboard_model": groq_director.model,
        "storyboard_ai_configured": bool(groq_director.api_key),
        "video_generation": video_status,
        "motion_graphics_available": True,
        "output_count": len(glob.glob(os.path.join(OUTPUT_DIR, "*.mp4"))),
    }


@app.get("/api/presets")
def list_presets():
    # Presets are removed: AI generates 100% bespoke visual code and storyboards from scratch
    return {"presets": []}


@app.post("/api/storyboard/generate")
def generate_storyboard(req: GenerateStoryboardRequest):
    if req.aspect_ratio not in {"16:9", "9:16", "1:1"}:
        raise HTTPException(status_code=422, detail="aspect_ratio must be 16:9, 9:16, or 1:1.")
    try:
        storyboard = groq_director.generate_storyboard(
            prompt=req.prompt,
            aspect_ratio=req.aspect_ratio,
            target_duration=req.target_duration,
            mood=req.mood,
        )
    except CreativeDirectorError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    storyboard["id"] = "film_" + uuid.uuid4().hex[:12]
    return {"success": True, "storyboard": storyboard}


def run_render_worker(job_id: str, storyboard: dict, engine_name: str):
    def update_progress(data: dict):
        if job_id in RENDER_JOBS:
            RENDER_JOBS[job_id].update(data)

    try:
        RENDER_JOBS[job_id].update({"status": "processing", "percent": 1})
        if engine_name == "comfyui":
            result = comfyui_engine.render_storyboard(storyboard, OUTPUT_DIR, progress_callback=update_progress)
        elif engine_name == "opencv":
            result = opencv_engine.render_storyboard(storyboard, OUTPUT_DIR, progress_callback=update_progress)
        elif engine_name == "chromium":
            result = chromium_engine.render_storyboard(storyboard, OUTPUT_DIR, progress_callback=update_progress)
        else:
            raise ValueError("Unknown rendering engine " + repr(engine_name) + ". Choose comfyui, chromium, or opencv.")

        RENDER_JOBS[job_id].update({
            "status": "completed",
            "percent": 100,
            "result": result,
            "video_url": "/output/" + os.path.basename(result["output_mp4"]),
            "thumb_url": "/output/" + os.path.basename(result["thumbnail"]) if result.get("thumbnail") else None,
        })
    except Exception as exc:
        RENDER_JOBS[job_id].update({
            "status": "failed",
            "error": str(exc),
            "percent": 0,
            "message": "Generation failed. No substitute video was rendered.",
        })


@app.post("/api/render")
def trigger_render(req: RenderRequest):
    storyboard = req.storyboard
    if not isinstance(storyboard.get("scenes"), list) or not storyboard["scenes"]:
        raise HTTPException(status_code=400, detail="Storyboard must contain at least one shot.")
    if len(storyboard["scenes"]) > 12:
        raise HTTPException(status_code=400, detail="A render may contain at most 12 shots.")
    if req.engine not in {"comfyui", "chromium", "opencv"}:
        raise HTTPException(status_code=400, detail="Engine must be comfyui, chromium, or opencv.")
    if req.engine == "comfyui":
        status = comfyui_engine.status()
        if not status["configured"] or not status["workflow_configured"]:
            raise HTTPException(
                status_code=503,
                detail="Real video generation is not configured. Set COMFYUI_BASE_URL, "
                       "COMFYUI_WORKFLOW_PATH, and COMFYUI_PROMPT_NODE_ID. See README.md. "
                       "CineMatrix will not silently render a template instead."
            )
        if not status["reachable"]:
            raise HTTPException(status_code=503, detail=status["detail"])

    job_id = "job_" + uuid.uuid4().hex[:12]
    raw_video_id = str(storyboard.get("id") or "film_" + uuid.uuid4().hex[:12])
    storyboard["id"] = re.sub(r"[^A-Za-z0-9_-]", "_", raw_video_id)[:100] or "film_" + uuid.uuid4().hex[:12]
    RENDER_JOBS[job_id] = {
        "job_id": job_id,
        "video_id": storyboard["id"],
        "engine": req.engine,
        "status": "queued",
        "percent": 0,
        "message": "Generation job queued.",
        "created_at": time.time(),
    }
    Thread(target=run_render_worker, args=(job_id, storyboard, req.engine), daemon=True).start()
    return {"job_id": job_id, "video_id": storyboard["id"], "status": "queued"}


@app.get("/api/render/progress/{job_id}")
@app.get("/api/jobs/{job_id}")
def get_render_progress(job_id: str):
    if job_id not in RENDER_JOBS:
        raise HTTPException(status_code=404, detail="Job not found.")
    return RENDER_JOBS[job_id]


@app.get("/api/videos")
def list_videos():
    videos = []
    for video_path in sorted(glob.glob(os.path.join(OUTPUT_DIR, "*.mp4")), key=os.path.getmtime, reverse=True):
        basename = os.path.basename(video_path)
        video_id = basename[:-4]
        thumb = os.path.join(OUTPUT_DIR, video_id + "_thumb.jpg")
        size = os.path.getsize(video_path)
        videos.append({
            "id": video_id,
            "filename": basename,
            "video_url": "/output/" + basename,
            "thumb_url": "/output/" + os.path.basename(thumb) if os.path.exists(thumb) else None,
            "size_bytes": size,
            "size_formatted": str(round(size / (1024 * 1024), 2)) + " MB",
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(video_path))),
        })
    return {"videos": videos}


@app.delete("/api/videos/{filename}")
def delete_video(filename: str):
    if os.path.basename(filename) != filename or filename in {".", ".."}:
        raise HTTPException(status_code=400, detail="Invalid filename.")
    if not filename.endswith(".mp4"):
        raise HTTPException(status_code=400, detail="Only .mp4 files can be deleted.")
    
    file_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="Video not found.")
    
    # Remove video and associated assets (thumb, stage, audio)
    base_id = filename[:-4]
    deleted_files = []
    for pattern in [filename, f"{base_id}_thumb.jpg", f"{base_id}_stage.html", f"{base_id}_audio.wav"]:
        target = os.path.join(OUTPUT_DIR, pattern)
        if os.path.isfile(target):
            try:
                os.remove(target)
                deleted_files.append(pattern)
            except OSError:
                pass
                
    return {"success": True, "deleted": deleted_files}


@app.get("/output/{filename}")
def serve_output_file(filename: str):
    if os.path.basename(filename) != filename or filename in {".", ".."}:
        raise HTTPException(status_code=400, detail="Invalid filename.")
    file_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found.")
    ext = os.path.splitext(filename)[1].lower()
    media_types = {
        ".mp4": "video/mp4", ".webm": "video/webm", ".mov": "video/quicktime",
        ".mkv": "video/x-matroska", ".gif": "image/gif", ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg", ".png": "image/png", ".wav": "audio/wav",
    }
    return FileResponse(file_path, media_type=media_types.get(ext, "application/octet-stream"))


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def serve_index():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "CineMatrix Media Studio API is running."}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", "8090")), reload=False)
