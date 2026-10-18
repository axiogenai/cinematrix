# CineMatrix

CineMatrix turns a natural-language brief into an AI-directed shot plan, generates actual footage with a self-hosted video model through ComfyUI, and assembles the clips into an MP4.

**Important distinction:** Chromium/OpenCV are still available as optional motion-graphics renderers. They are not text-to-video models. CineMatrix defaults to the ComfyUI video-generation path and never silently substitutes a template when real generation fails.

## Architecture

1. **Creative director** — Groq's OpenAI-compatible chat API plans an original film and writes a detailed, standalone video_prompt for each shot. It does not select a fixed sequence of archetypes.
2. **Self-hosted video model** — ComfyUI runs an open video model locally or on a GPU machine you control. CineMatrix submits each shot prompt to an API-format workflow.
3. **Editor and sound design** — CineMatrix normalizes and assembles clips with FFmpeg, preserves clip audio, and can mix a locally synthesized background score underneath it.
4. **Explicit errors** — Missing credentials, unreachable ComfyUI, invalid workflows, and failed generations produce visible errors. No canned storyboard or fake video is returned as a fallback.

Presets remain available as editable examples, but are not used as the AI director's decision logic.

## Requirements

- Python 3.10+
- Node.js 18+ and Chromium only if you want to use the optional legacy Chromium renderer
- FFmpeg installed and available on PATH
- A GPU-capable machine for practical local video generation; model requirements vary
- A ComfyUI installation with a video-generation workflow exported in **API format**
- A Groq API key for AI shot planning (use its available free tier; the video generation itself runs on your own ComfyUI machine)

Open video models are free to download under their respective licenses, but local inference is not cost-free in compute, electricity, storage, or hardware. A CPU-only VM can host CineMatrix's web/API layer, but should not be expected to generate video at practical speed. Keep ComfyUI on a GPU machine and expose it only on a private network or through a secured tunnel.

## Quick start

~~~
git clone https://github.com/axiogenai/cinematrix.git
cd cinematrix
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
# macOS/Linux:
# source .venv/bin/activate
python -m pip install -r requirements.txt
~~~

Install Node dependencies for the optional motion-graphics renderer:

~~~
npm install puppeteer-core ffmpeg-static
~~~

Copy .env.example to .env and set the values below. Start CineMatrix:

~~~
python server.py
~~~

Open http://127.0.0.1:8090.

CineMatrix's API has no built-in user authentication. Keep it bound to localhost for personal use. If you deploy it for other people, put it behind an authenticated reverse proxy and configure trusted frontend origins; do not expose the unauthenticated app or ComfyUI directly to the public internet.

## Configure actual AI video generation

### 1. Run ComfyUI with an open video model

Install ComfyUI on a machine with a compatible GPU. Choose an open model and workflow that your hardware can run. Examples include Wan-family and LTX-Video workflows. Review each model's license and hardware requirements before downloading weights.

- Wan2.1's official repository describes its 1.3B text-to-video model as requiring about 8.19 GB VRAM and demonstrates 480p generation; this is a modest entry point, not a guarantee that every ComfyUI workflow fits every GPU.
- Larger models can require substantially more VRAM and disk space.
- CPU-only inference may be impractically slow for production video.

Start ComfyUI on the machine where the model is installed. For a same-machine setup, the default API address is http://127.0.0.1:8188. For a separate GPU workstation, set COMFYUI_BASE_URL to its private, reachable address. Do not expose an unauthenticated ComfyUI server directly to the public internet.

### 2. Export an API workflow

In ComfyUI, load a workflow that produces a video file, run it once to verify it works, then export it using **Save (API Format)**. Store that JSON as workflows/video_api.json inside the CineMatrix repository, or set COMFYUI_WORKFLOW_PATH to its absolute path.

The workflow must:
- accept a positive text prompt through a node input (commonly a CLIP Text Encode node's text input);
- generate video with your selected model;
- use a video output node that writes an MP4, WebM, MOV, MKV, or GIF file.

Configure the node IDs and input names in .env:

~~~
COMFYUI_BASE_URL=http://127.0.0.1:8188
COMFYUI_WORKFLOW_PATH=./workflows/video_api.json
COMFYUI_PROMPT_NODE_ID=6
COMFYUI_PROMPT_INPUT=text
COMFYUI_NEGATIVE_NODE_ID=
COMFYUI_NEGATIVE_INPUT=text
COMFYUI_TIMEOUT_SECONDS=1800
# Optional: map dimensions/frame count/FPS to nodes that exist in your workflow.
COMFYUI_WIDTH_NODE_ID=
COMFYUI_WIDTH_INPUT=width
COMFYUI_HEIGHT_NODE_ID=
COMFYUI_HEIGHT_INPUT=height
COMFYUI_FRAMES_NODE_ID=
COMFYUI_FRAMES_INPUT=length
COMFYUI_FPS_NODE_ID=
COMFYUI_FPS_INPUT=frame_rate
FFMPEG_PATH=ffmpeg
FFPROBE_PATH=ffprobe
~~~

The example prompt node ID 6 is only a placeholder. **Use the ID and input name from your own API workflow.** If your workflow has a negative prompt node, set its ID too. Keep the same workflow's model, dimensions, frame count, and sampling settings configured in ComfyUI.

### 3. Generate

1. Enter a prompt and choose the aspect ratio and duration.
2. Click **Generate Storyboard with Groq AI**. Review/edit each generated shot's video_prompt.
3. Keep **Real AI Video Generation** selected in the rendering engine.
4. Start rendering. CineMatrix sends each shot to ComfyUI separately, downloads the actual generated video, and assembles the clips.
5. If a dependency or workflow is misconfigured, read the reported error and fix it. CineMatrix will not pretend a template render is generative footage.

## Environment variables

| Variable | Purpose |
|---|---|
| GROQ_API_KEY | API key for creative shot planning |
| GROQ_MODEL | Chat model name |
| COMFYUI_BASE_URL | ComfyUI API base URL |
| COMFYUI_WORKFLOW_PATH | Path to ComfyUI API-format workflow JSON |
| COMFYUI_PROMPT_NODE_ID | Positive prompt node ID |
| COMFYUI_PROMPT_INPUT | Positive prompt input key |
| COMFYUI_NEGATIVE_NODE_ID | Optional negative prompt node ID |
| COMFYUI_NEGATIVE_INPUT | Negative prompt input key |
| COMFYUI_TIMEOUT_SECONDS | Maximum wait per generated shot |
| CINEMATRIX_SYNTHESIZE_SOUNDTRACK | Mix a locally synthesized score (true/false) |
| FFMPEG_PATH | FFmpeg executable path |
| HOST, PORT | CineMatrix web/API bind address and port |

## API

- GET /api/status — storyboard and ComfyUI configuration/readiness
- POST /api/storyboard/generate — create an original AI-directed shot plan
- POST /api/render — queue rendering with engine: "comfyui" (real video), "chromium" (motion graphics), or "opencv" (procedural pixel graphics)
- GET /api/render/progress/{job_id} — render progress and errors
- GET /api/videos — list rendered MP4 files

Example storyboard request:

~~~json
{
  "prompt": "A quiet science-fiction short about a botanist discovering a living forest beneath Europa's ice. Slow, tactile, emotionally restrained.",
  "aspect_ratio": "16:9",
  "target_duration": 15,
  "mood": "restrained science fiction"
}
~~~

## Troubleshooting

- **AI planning says key is missing:** set GROQ_API_KEY in the environment or .env.
- **Real video generation is not configured:** set the ComfyUI URL, workflow path, and prompt node ID.
- **ComfyUI cannot be reached:** start it and verify network access from the CineMatrix server.
- **Workflow completed but no video was returned:** ensure the API workflow includes a video-output node and writes a supported video file.
- **Shot duration or dimensions do not change:** map the optional frame-count/width/height/FPS node IDs to matching numeric inputs in your specific workflow. Model workflows differ; CineMatrix only changes those inputs when explicitly mapped.
- **Clips have different sizes, frame rates, or audio tracks:** CineMatrix normalizes every clip to a common aspect ratio, frame rate, H.264 video, and AAC audio before joining them.
- **Disable the synthesized background score:** set CINEMATRIX_SYNTHESIZE_SOUNDTRACK=false. Generated clip audio remains preserved.
- **Out of memory:** reduce resolution, frame count, batch size, or use a smaller/quantized model supported by your workflow.
- **FFmpeg not found:** install FFmpeg or set FFMPEG_PATH to its absolute executable path.

## License

CineMatrix source code is licensed under Apache-2.0. Individual model weights, workflow nodes, and dependencies retain their own licenses.
