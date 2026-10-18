# CineMatrix 🎬
### Broadcast-Grade AI Motion Design & Video Synthesis Engine

> **CineMatrix** converts natural language creative concepts into broadcast-quality motion graphics films, commercials, product launches, and viral reels with cinema-grade transitions, dynamic archetypes, and harmonic spring physics.

---

## 🌟 Architecture Overview

```
User Prompt / Creative Brief
            │
            ▼
┌────────────────────────────────────────┐
│  Groq LPU Creative Director (120B)    │  ── Storyboard JSON composition
└────────────────────────────────────────┘     with mood, typography & pacing
            │
            ▼
┌────────────────────────────────────────┐
│  HTML5 / SVG Motion Engine (v4.0)     │  ── 14 Bespoke Production Archetypes
│  - Damped Harmonic Spring Physics      │     + 8 Cinema Transitions Engine
│  - Live Typewriter, Charts & Gauges   │
└────────────────────────────────────────┘
            │
            ▼
┌────────────────────────────────────────┐
│  Chromium Headless GPU Pipe (Puppeteer)│  ── window.renderAt(t) deterministic
│  + FFmpeg High-Throughput Pipe        │     60fps / 30fps lossless capture
└────────────────────────────────────────┘
            │
            ▼
┌────────────────────────────────────────┐
│  Procedural Audio Synthesizer Engine  │  ── Stereo detuned ambient pads,
│  (NumPy / Scipy Acoustic Modeling)     │     risers, sub-impacts & chimes
└────────────────────────────────────────┘
            │
            ▼
    Master MP4 Broadcast Video
```

---

## 🚀 Key Highlights & Capabilities

### 1. 14 Unique Production Archetypes (Zero Hardcoded Repetition)
Never outputs the same cloned video formula. Every concept is matched to its authentic aesthetic genre:
- **`kinetic_manifesto`**: Bold display typography with line-by-line masked reveals and syncopated rhythm (Apple Keynote / Nike style).
- **`product_showcase`**: 3D central product turntable pedestal with concentric rotating SVG telemetry rings and floating glassmorphism spec callouts.
- **`terminal_code_stream`**: Realistic developer terminal with syntax-highlighted code typewriter, live blinking cursor, compilation pass status, and telemetry.
- **`financial_telemetry`**: Real-time SVG Area chart dynamically drawing Bézier curves, animated numerical price ticker, and market indicators.
- **`split_comparison`**: Dual-pane duel (The Legacy Way vs The Next-Gen Standard) with animated laser divider beam.
- **`bento_grid_v2`**: Asymmetric modern bento with live interactive UI components (animated circular SVG progress dial, spring toggle switch, stacked avatar badges).
- **`metric_impact_matrix`**: 3 massive statistical proof cards with high-impact numbers and labels.
- **`brand_stinger_outro`**: High-end geometric logo resolve with converging lines, typography drop, and animated domain underline.
- **`editorial_lookbook`**: Elegant Playfair serif italic typography with 1px architectural corner registration marks (Luxury / Fashion / Fragrance).
- **`coin_parade`**: 3D cylindrical carousel of metallic badges with staggered spring entrance.
- **`blueprint_reveal`**: CAD / Figma style technical corner arc and dimension bounding box.
- **`dashboard_device`**: Responsive device frame with clean dashboard rows for mobile applications.
- **`cinematic_hero`**: Anamorphic letterboxed format with bold centered headline and progress tracking.
- **`kinetic_parallax`**: Multi-speed floating badge cloud with organic drifting physics.

### 2. Cinema Transition & Switch Engine
Seamless handover between scenes using mathematical motion blur and spatial transformations:
- **Whip Pan (Left / Right / Up)**: Extreme camera translation with dynamic directional motion blur (`blur(20px, 0)`).
- **Zoom Punch**: Camera dives into scene focal point (`scale(3x)`) while incoming scene punches in with spring settle.
- **3D Rotational Snap**: Perspective cube turn on Y-axis (Scene A: `0deg -> -90deg`, Scene B: `90deg -> 0deg`) with 1400px perspective.
- **Shutter Split**: Dual-blade horizontal matte parting from the center line.
- **Circular Iris**: Dynamic circular vector mask expanding outward from center (`clip-path: circle(r% at 50% 50%)`).
- **Depth Dissolve**: Cinematic rack focus with shallow depth-of-field blur.

### 3. Precision Spring Physics & Damped Harmonic Oscillators
All reveals, cards, badges, and dials use physical simulation formulas instead of flat linear lerps:
```javascript
function spring(t, stiffness = 130, damping = 15, mass = 1) {
  const w0 = Math.sqrt(stiffness / mass);
  const zeta = damping / (2 * Math.sqrt(stiffness * mass));
  if (zeta < 1) {
    const wd = w0 * Math.sqrt(1 - zeta * zeta);
    return 1 - Math.exp(-zeta * w0 * t) * (Math.cos(wd * t) + (zeta * w0 / wd) * Math.sin(wd * t));
  }
  return 1 - (1 + w0 * t) * Math.exp(-w0 * t);
}
```

### 4. Procedural Stereo Audio Synthesizer
Generates custom stereo sound design synchronized to scene cuts:
- **Detuned Lush Ambient Pads**: Stereo detuned harmonic sine oscillators with smooth attack/decay envelopes.
- **Sub-Bass Braam Impacts**: Low-frequency resonant drops for scene entries and dramatic beats.
- **Acoustic Riser Sweeps**: White-noise frequency sweeps building into scene transitions.
- **Crystalline Bell Chimes**: Pure modal frequency chimes for brand name reveals.

---

## 🛠️ Quickstart

### Prerequisites
- Python 3.10+
- Node.js 18+
- Chromium / Google Chrome
- FFmpeg

### Installation
```bash
git clone https://github.com/axiogenai/cinematrix.git
cd cinematrix

# Python dependencies
pip install fastapi uvicorn pydantic numpy scipy

# Node dependencies
npm install puppeteer-core ffmpeg-static
```

### Configuration
Copy `.env.example` to `.env`:
```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-120b
HOST=127.0.0.1
PORT=8090
```

### Start the Media Studio Server
```bash
python server.py
```
Open `http://localhost:8090` in your browser to access the interactive web studio dashboard.

---

## 📡 API Reference

### Generate Storyboard
```http
POST /api/storyboard/generate
Content-Type: application/json

{
  "prompt": "Developer CLI tool for instant serverless deployments",
  "aspect_ratio": "16:9",
  "target_duration": 15.0,
  "mood": "tech_developer"
}
```

### Render Video
```http
POST /api/render/start
Content-Type: application/json

{
  "storyboard": { ... },
  "engine": "chromium"
}
```

### Check Render Progress
```http
GET /api/render/progress/{job_id}
```

---

## 📂 Project Structure
```
cinematrix/
├── ai/
│   └── groq_director.py          # Groq LPU Storyboard Director & Fallback Engine
├── core/
│   ├── html_motion_generator.py  # v4.0 HTML5/SVG/CSS/JS Motion Engine
│   ├── render_bridge.py          # Chromium Puppeteer & FFmpeg Bridge
│   ├── audio_synth.py            # Procedural Stereo Sound Synthesizer
│   ├── video_engine.py           # Fallback OpenCV Pure-Python Compositor
│   └── chromium_renderer.js      # Headless GPU Rendering Script
├── presets/
│   ├── apple_minimalist_film.json
│   ├── nike_product_launch.json
│   ├── crypto_finance_protocol.json
│   ├── viral_saas_reel.json
│   └── axiogen_services_showreel.json
├── static/
│   ├── index.html                # Web Studio Dashboard UI
│   ├── app.js                    # Studio Frontend Controller
│   └── style.css                 # Dark Studio Styling
├── output/                       # Generated Video Renders
├── server.py                     # FastAPI Async Video Synthesis Backend
├── .env.example
├── .gitignore
└── README.md
```

---

## 📜 License
Apache-2.0 License. Built with pride by Team Axiogen.
