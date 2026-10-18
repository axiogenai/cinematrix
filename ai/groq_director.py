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
        configured_key = api_key if api_key is not None else os.getenv("GROQ_API_KEY")
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

        system_prompt = """You are CineMatrix's independent film director, cinematographer, and editor.
Invent an original visual treatment from the user's brief. Do not choose from a menu of templates.
Do not force a fixed opening, middle, or ending. The genre, story, product, emotional arc, and
duration must determine the structure. For abstract, documentary, narrative, product, travel,
fashion, science-fiction, or other prompts, choose the visual language that actually fits.

Return only valid JSON with this schema:
{
  "title": "specific film title",
  "logline": "one sentence describing the film's idea",
  "visual_style": "cohesive visual treatment",
  "genre": "inferred genre",
  "mood": "emotional direction",
  "negative_prompt": "visual defects to avoid",
  "scenes": [
    {
      "duration": 4.0,
      "video_prompt": "a complete standalone generative-video prompt describing visible subjects, action, environment, composition, motion and temporal development",
      "camera": "specific framing, lens feel, camera movement and movement speed",
      "lighting": "specific light source, direction, contrast and atmosphere",
      "visual_description": "what the audience sees",
      "headline": "short optional edit label, not text to generate inside footage",
      "subtext": "optional edit note",
      "transition_out": "editorial transition idea"
    }
  ]
}

Directing rules:
- Make a genuine creative interpretation; do not merely rephrase the prompt.
- Create as many shots as the idea needs for the requested duration, usually 2-10. Do not force a standard shot count or sequence.
- Each shot must depict a distinct purposeful visual event, not a renamed version of another shot.
- Every video_prompt must be self-contained, detailed, physically plausible, and usable directly by a text-to-video model without needing previous context.
- Maintain continuity for recurring characters, wardrobe, objects, location, time of day and color language when the story requires it. Explicitly describe continuity in each relevant shot.
- Choose shot size, lens character, camera movement, lighting, depth, atmosphere and pacing for the scene's intent.
- Avoid generic tech grids, floating UI, random charts, fake metrics, generic slogans, fabricated product specifications and arbitrary logos unless the user specifically asks for them.
- Do not ask the video model to render titles, subtitles, credits, or legible logos. Those belong in post-production.
- Do not invent factual claims or product details that the user did not provide.
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
            if not isinstance(scene, dict) or not str(scene.get("video_prompt", "")).strip():
                raise CreativeDirectorError(f"AI shot {index} is missing video_prompt. Please regenerate.")
            try:
                scene_duration = float(scene.get("duration", duration / len(scenes)))
            except (TypeError, ValueError):
                scene_duration = duration / len(scenes)
            scene["duration"] = max(1.0, scene_duration)
            scene["type"] = "generative_video"
            scene["layout"] = "generative_video"
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
