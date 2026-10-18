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
You invent an original visual treatment and bespoke visual code from the user's brief.
STRICT RULE: Do NOT use fixed templates, canned archetypes, or presets. Every single visual element, vector illustration, layout structure, typography treatment, and animation must be invented specifically for the user's prompt.

Return only valid JSON with this schema:
{
  "title": "specific original film title",
  "logline": "one sentence describing the film's creative thesis",
  "visual_style": "cohesive visual treatment and color language",
  "genre": "inferred genre (e.g. Artisanal Culinary, High-Tech Launch, Luxury Fashion, Documentary, Automotive, Sports)",
  "mood": "emotional and soundtrack direction (cinematic_tech, minimalist_apple, high_energy_saas, cyber_pulse, or luxury_ambient)",
  "aspect_ratio": "16:9, 9:16, 1:1, or 4:5",
  "negative_prompt": "visual defects to avoid",
  "palette": {
    "bg": "#09090b",
    "surface": "#141419",
    "accent": "#f4f4f5",
    "text": "#f4f4f5"
  },
  "scenes": [
    {
      "duration": 3.5,
      "badge": "01 // CHAPTER OR TECHNICAL METRIC",
      "headline": "Powerful Scene Headline",
      "subtext": "Supporting explanation or narrative line",
      "camera": "specific framing, lens feel, camera movement and speed",
      "lighting": "specific light source, direction, contrast and atmosphere",
      "transition_out": "whip_pan_left, zoom_punch, rotational_snap_3d, shutter_split, circular_iris, or depth_dissolve",
      "visual_code": "<svg viewBox='0 0 600 400' xmlns='http://www.w3.org/2000/svg'>... bespoke SVG vector art, diagram, illustration, or visual subject created specifically for this scene ...</svg>",
      "animation_css": "CSS keyframes and classes for elements inside this scene",
      "video_prompt": "a complete standalone generative-video prompt describing visible subjects, action, environment, composition, motion and temporal development"
    }
  ]
}

Directing & Creative Coding rules:
- Invent a genuine creative interpretation; do not merely rephrase the prompt.
- Create 2-8 purposeful shots fitting the requested duration.
- For EVERY shot, generate bespoke 'visual_code' containing valid SVG graphics, vector illustrations, geometry, or visual symbols depicting the subject matter (e.g. for a bakery: oven, bread, flour; for space: rocket, orbit; for a car: chassis, aerodynamics; for finance: charts, order books).
- Do not repeat the same visual code across scenes; each scene must show a distinct visual progression.
- In 'animation_css', provide custom CSS keyframes that animate the SVG paths (transform, scale, rotate, opacity, stroke-dashoffset).
- Return durations whose sum is close to the requested total. Include no markdown or prose outside the JSON.
"""

        user_message = {
            "brief": prompt,
            "aspect_ratio": aspect_ratio,
            "target_duration_seconds": duration,
            "mood_hint": mood,
            "deliverable": "production-ready shot plan for a real generative video model"
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

        for index, scene in enumerate(scenes, start=1):
            if not isinstance(scene, dict):
                raise CreativeDirectorError(f"AI shot {index} is not a valid dictionary.")
            
            # Ensure video_prompt is never empty (fallback to visual_description or headline)
            if not str(scene.get("video_prompt", "")).strip():
                scene["video_prompt"] = scene.get("visual_description") or scene.get("headline") or "Cinematic shot with dramatic motion and lighting"

            try:
                scene_duration = float(scene.get("duration", duration / len(scenes)))
            except (TypeError, ValueError):
                scene_duration = duration / len(scenes)
            scene["duration"] = max(1.0, scene_duration)
            
            if scene.get("visual_code"):
                scene["type"] = "bespoke_ai"
                scene["layout"] = "bespoke_ai"
            else:
                scene.setdefault("type", "bespoke_ai")
                scene.setdefault("layout", "bespoke_ai")

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
