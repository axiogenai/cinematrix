"""AI creative director for CineMatrix.

This module plans original films rather than selecting fixed archetype sequences. It has no
programmatic storyboard fallback: if the configured LLM fails, callers receive a clear error.
"""
import json
import os
import urllib.error
import urllib.request


class CreativeDirectorError(RuntimeError):
    pass


class GroqCreativeDirector:
    def __init__(self, api_key=None, model=None):
        if api_key is not None:
            configured_key = api_key
        else:
            configured_key = os.getenv("GROQ_API_KEY")
            if not configured_key:
                env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
                if os.path.isfile(env_file):
                    try:
                        with open(env_file, "r", encoding="utf-8-sig") as ef:
                            for line in ef:
                                if line.strip().startswith("GROQ_API_KEY="):
                                    configured_key = line.strip().split("=", 1)[1].strip()
                                    break
                    except OSError:
                        pass
        configured_key = (configured_key or "").strip()
        self.api_key = configured_key if configured_key and configured_key.lower() not in {
            "your_groq_api_key_here", "your_api_key_here", "replace_me", "changeme"
        } else None
        self.model = model or os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
        self.api_url = os.getenv("GROQ_API_URL", "https://api.groq.com/openai/v1/chat/completions")

    def generate_storyboard(self, prompt, aspect_ratio="16:9", target_duration=15.0, mood="cinematic"):
        prompt = (prompt or "").strip()
        if not prompt:
            raise CreativeDirectorError("A creative prompt is required.")
        if not self.api_key:
            raise CreativeDirectorError(
                "AI storyboarding is unavailable: GROQ_API_KEY is not configured. "
                "No canned storyboard was substituted."
            )
        try:
            duration = float(target_duration)
        except (TypeError, ValueError):
            raise CreativeDirectorError("target_duration must be a number.")
        if duration < 4 or duration > 180:
            raise CreativeDirectorError("Choose a duration between 4 and 180 seconds.")

        system_prompt = """You are CineMatrix AI's autonomous film director, cinematographer, and generative visual coder.
You invent a completely bespoke, broadcast-grade commercial or promotional film from the user's brief.

CRITICAL DIRECTIVES:
1. ZERO TEMPLATES & ZERO FIXED THEMES: Never generate generic identical slides. Every film must possess its own unique visual soul, domain-intelligent color palette, typography pairing, and shot architectures.
   - Bakery / Artisanal Food: Warm wood-fired espresso (#120905), rustic hearth amber (#D97706 / #F59E0B), flour linen (#FBF9F5), warm serif or organic display typography.
   - Luxury / Haute Horlogerie: Deepest caviar obsidian (#070605), champagne gold (#E5C378), titanium (#E2E8F0), serif Playfair/Cinzel typography.
   - High-Tech / Cyber / SaaS: Deep carbon slate (#080D1A), technical titanium (#F1F5F9), cyan/sky (#38BDF8), JetBrains Mono or Space Grotesk.
   - Automotive / Athletics / Energy: Carbon black (#0B0C10), racing crimson (#E11D48) or high-velocity white (#FFFFFF), Anton or Syne display type.
   - Medical / Biotech / Clean: Clinical pure white (#F8FAFC) or crisp slate (#0F172A), sterile sage (#10B981) or calming azure, Plus Jakarta Sans.

2. DYNAMIC COMPOSITIONS (VARY ACROSS EVERY SCENE):
   Each scene MUST use a DIFFERENT cinematic composition from these 7 architectures. NEVER use the same composition for every scene:
   - "kinetic_poster": Massive 90px-130px display typography dominating the frame with dynamic SVG vector cut-throughs.
   - "full_bleed_hero": Edge-to-edge full canvas SVG vector artwork with a cinematic lower-third / corner title card.
   - "centered_monumental": Symmetrical, majestic central hero subject with top & bottom typographic framing.
   - "split_dynamic": Asymmetric dual-panel split screen (contrasting text panel + visual stage).
   - "editorial_asymmetric": Refined off-center editorial spread with generous negative space, serif titles, and delicate framing.
   - "hud_technical": Technical blueprint/HUD with corner crosshair reticles, coordinate markers, and telemetry gauges.
   - "brand_finale": Grand cinematic brand resolve, emblem/logo, and final call-to-action stinger.

3. BESPOKE SVG VECTOR ARTWORK (visual_code):
   For EVERY shot, write genuine, detailed, beautiful SVG code (viewBox='0 0 1200 800' or appropriate) illustrating the actual subject matter of the scene (e.g. rising sourdough loaf with score lines, aerodynamic chassis airflow curves, ticking tourbillon balance wheel, neural network cluster).

4. CUSTOM CSS KEYFRAME ANIMATIONS (animation_css):
   Provide CSS @keyframes and class rules animating the SVG paths and scene elements (transform, stroke-dashoffset, opacity, scale, rotate, drift).

Return only valid JSON with this exact schema:
{
  "title": "Specific Film Title",
  "logline": "One sentence creative thesis",
  "genre": "Inferred genre",
  "mood": "cinematic_tech, minimalist_apple, high_energy_saas, cyber_pulse, or luxury_ambient",
  "aspect_ratio": "16:9, 9:16, 1:1, or 4:5",
  "typography": {
    "headline_font": "Space Grotesk | Playfair Display | Anton | JetBrains Mono | Plus Jakarta Sans | Cinzel | Syne | Outfit",
    "body_font": "Plus Jakarta Sans | Inter | JetBrains Mono | Space Grotesk"
  },
  "palette": {
    "bg": "#120905",
    "surface": "#1E110A",
    "accent": "#F59E0B",
    "text": "#FFFDF7",
    "muted": "#B5A79E",
    "border": "rgba(245, 158, 11, 0.2)"
  },
  "scenes": [
    {
      "duration": 3.0,
      "composition": "kinetic_poster",
      "badge": "01 // CHAPTER OR METRIC",
      "headline": "Impactful Headline",
      "subtext": "Compelling narrative or technical explanation line",
      "camera": "Specific camera movement, angle and focal length",
      "lighting": "Specific light atmosphere and direction",
      "transition_out": "whip_pan_left, zoom_punch, rotational_snap_3d, shutter_split, circular_iris, or depth_dissolve",
      "visual_code": "<svg viewBox='0 0 1200 800' xmlns='http://www.w3.org/2000/svg'>... detailed bespoke SVG vectors ...</svg>",
      "animation_css": "@keyframes pulseGlow { 0% { opacity: 0.6; } 100% { opacity: 1; } } .anim-glow { animation: pulseGlow 2s ease-in-out infinite alternate; }",
      "video_prompt": "Standalone generative video prompt describing visible subjects, action, and motion"
    }
  ]
}
"""

        user_message = {
            "brief": prompt,
            "aspect_ratio": aspect_ratio,
            "target_duration_seconds": duration,
            "mood_hint": mood,
            "deliverable": "production-ready shot plan with distinct visual compositions and bespoke SVG visual code"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_message, ensure_ascii=False)}
            ],
            "temperature": 0.85,
            "response_format": {"type": "json_object"}
        }
        request = urllib.request.Request(
            self.api_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": "Bearer " + self.api_key,
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) CineMatrix/3.1"
            }
        )
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                response_json = json.loads(response.read().decode("utf-8"))
            raw = response_json["choices"][0]["message"]["content"]
            storyboard = json.loads(raw)
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise CreativeDirectorError(f"Creative director API returned HTTP {exc.code}: {body[:1000]}") from exc
        except (urllib.error.URLError, TimeoutError) as exc:
            raise CreativeDirectorError(f"Creative director API could not be reached: {exc}") from exc
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            raise CreativeDirectorError(f"Creative director returned an invalid storyboard: {exc}") from exc

        scenes = storyboard.get("scenes")
        if not isinstance(scenes, list) or not scenes:
            raise CreativeDirectorError("AI returned no shots. Please retry with a more specific brief.")
        if len(scenes) > 12:
            raise CreativeDirectorError("AI returned too many shots (maximum 12). Please retry.")

        # Normalize film-level palette & typography
        palette = storyboard.get("palette") or storyboard.get("theme", {}).get("palette") or {}
        bg = palette.get("bg", "#09090b")
        storyboard["palette"] = {
            "bg": bg,
            "surface": palette.get("surface", "#141419"),
            "accent": palette.get("accent", "#f4f4f5"),
            "text": palette.get("text", "#f4f4f5"),
            "muted": palette.get("muted", "#94a3b8"),
            "border": palette.get("border", "rgba(255,255,255,0.12)")
        }

        typography = storyboard.get("typography") or storyboard.get("theme", {}).get("typography") or {}
        storyboard["typography"] = {
            "headline_font": typography.get("headline_font", "Plus Jakarta Sans"),
            "body_font": typography.get("body_font", "Plus Jakarta Sans")
        }

        ALLOWED_COMPOSITIONS = [
            "kinetic_poster",
            "full_bleed_hero",
            "split_dynamic",
            "centered_monumental",
            "editorial_asymmetric",
            "hud_technical",
            "brand_finale"
        ]

        for index, scene in enumerate(scenes, start=1):
            if not isinstance(scene, dict):
                raise CreativeDirectorError(f"AI shot {index} is not a valid dictionary.")

            # Ensure video_prompt is never empty
            if not str(scene.get("video_prompt", "")).strip():
                scene["video_prompt"] = scene.get("visual_description") or scene.get("headline") or "Cinematic shot with dramatic motion and lighting"

            try:
                scene_duration = float(scene.get("duration", duration / len(scenes)))
            except (TypeError, ValueError):
                scene_duration = duration / len(scenes)
            scene["duration"] = max(1.0, scene_duration)

            comp = scene.get("composition") or scene.get("layout") or scene.get("type")
            if comp not in ALLOWED_COMPOSITIONS:
                comp = ALLOWED_COMPOSITIONS[(index - 1) % len(ALLOWED_COMPOSITIONS)]
            scene["composition"] = comp
            scene["layout"] = comp
            scene["type"] = comp

            scene.setdefault("headline", f"Shot {index}")
            scene.setdefault("visual_description", scene["video_prompt"])
            scene.setdefault("camera", "cinematic camera movement appropriate to the action")
            scene.setdefault("lighting", "motivated naturalistic lighting")
            scene.setdefault("negative_prompt", storyboard.get("negative_prompt", ""))

        raw_total = sum(scene["duration"] for scene in scenes)
        for scene in scenes:
            scene["duration"] = round(scene["duration"] * duration / raw_total, 2)
        scenes[-1]["duration"] = round(duration - sum(s["duration"] for s in scenes[:-1]), 2)

        storyboard["aspect_ratio"] = aspect_ratio
        storyboard["fps"] = 24
        storyboard["mood"] = mood
        storyboard["target_duration"] = duration
        storyboard["source_prompt"] = prompt
        return storyboard
