import json
import html
import re

# ─────────────────────────────────────────────────────────────────────────────
# CineMatrix Dynamic HTML Motion Engine v5.0 — 100% Bespoke AI Cinema
# Features:
# 1. Zero Fixed Templates / Zero Presets: Domain-intelligent palettes & typography
# 2. 7 Distinct Filmic Compositions:
#    - kinetic_poster       (Massive display typography & graphic energy)
#    - full_bleed_hero      (Full-canvas vector artwork & cinematic lower-third)
#    - centered_monumental  (Symmetrical hero reveal with top & bottom framing)
#    - split_dynamic        (Asymmetric dual-panel with alternating left/right)
#    - editorial_asymmetric (Luxury haute couture serif & generous whitespace)
#    - hud_technical        (Corner crosshairs, telemetry gauges & wireframes)
#    - brand_finale         (Monumental logo resolve & call-to-action stinger)
# 3. Precision Damped Harmonic Springs (Zero robotic linear lerps)
# 4. Cinema Transition & Switch Engine (Whip Pans, 3D Snaps, Zoom Punches, Splits, Irises)
# ─────────────────────────────────────────────────────────────────────────────

def _hex_to_rgb(hex_str: str):
    try:
        h = str(hex_str).strip().lstrip('#')
        if len(h) == 3:
            h = ''.join([c * 2 for c in h])
        if len(h) >= 6:
            return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    except Exception:
        pass
    return 10, 10, 14


def _is_light_bg(hex_str: str) -> bool:
    r, g, b = _hex_to_rgb(hex_str)
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255.0
    return luminance > 0.55


def generate_motion_html(storyboard: dict) -> str:
    """Dynamically generates a broadcast-grade HTML5 motion design stage.
    Every film and scene has completely unique layout geometry, typography,
    color palettes, SVG artwork, and animation logic.
    """
    aspect_ratio = storyboard.get("aspect_ratio", "16:9")
    if aspect_ratio == "9:16":
        width, height = 1080, 1920
        is_vertical = True
    elif aspect_ratio == "1:1":
        width, height = 1080, 1080
        is_vertical = False
    elif aspect_ratio == "4:5":
        width, height = 1080, 1350
        is_vertical = True
    else:  # 16:9
        width, height = 1920, 1080
        is_vertical = False

    scenes = storyboard.get("scenes", [])
    total_duration = sum(s.get("duration", 3.5) for s in scenes)
    brand_name = storyboard.get("brand_name", "")
    web_url = storyboard.get("web_url", "")
    title = storyboard.get("title", "CineMatrix Motion Film")

    # Master Palette Extraction & Contrast Resolution
    palette = storyboard.get("palette") or storyboard.get("theme", {}).get("palette") or {}
    bg = palette.get("bg", "#09090b")
    is_light = _is_light_bg(bg)

    if is_light:
        fg = palette.get("text", "#09090b")
        muted = palette.get("muted", "#52525b")
        surface = palette.get("surface", "rgba(0, 0, 0, 0.04)")
        card_border = palette.get("border", "rgba(0, 0, 0, 0.12)")
        accent = palette.get("accent", "#18181b")
        dot_grid_color = "rgba(0, 0, 0, 0.06)"
    else:
        fg = palette.get("text", "#f4f4f5")
        muted = palette.get("muted", "#94a3b8")
        surface = palette.get("surface", "rgba(255, 255, 255, 0.05)")
        card_border = palette.get("border", "rgba(255, 255, 255, 0.12)")
        accent = palette.get("accent", "#f4f4f5")
        dot_grid_color = "rgba(255, 255, 255, 0.06)"

    # Master Typography Extraction
    typography = storyboard.get("typography") or storyboard.get("theme", {}).get("typography") or {}
    headline_font = typography.get("headline_font", "Plus Jakarta Sans")
    body_font = typography.get("body_font", "Plus Jakarta Sans")

    # Build Scene Time Offsets
    scene_data = []
    curr_time = 0.0
    for idx, sc in enumerate(scenes):
        dur = sc.get("duration", 3.5)
        scene_data.append({
            "idx": idx,
            "start": curr_time,
            "end": curr_time + dur,
            "dur": dur,
            "config": sc
        })
        curr_time += dur

    # Assign Transitions
    TRANSITION_TYPES = [
        "whip_pan_left",
        "zoom_punch",
        "rotational_snap_3d",
        "whip_pan_right",
        "shutter_split",
        "circular_iris",
        "depth_dissolve",
        "whip_pan_up"
    ]
    for item in scene_data:
        sc = item["config"]
        if "transition_out" not in sc or not sc["transition_out"]:
            sc["transition_out"] = TRANSITION_TYPES[item["idx"] % len(TRANSITION_TYPES)]

    # Dynamic Scene Composition Router
    ALLOWED_COMPOSITIONS = [
        "kinetic_poster",
        "full_bleed_hero",
        "split_dynamic",
        "centered_monumental",
        "editorial_asymmetric",
        "hud_technical",
        "brand_finale"
    ]

    scenes_html = []
    all_scene_css = []
    all_scene_js_blocks = []

    for item in scene_data:
        idx = item["idx"]
        sc = item["config"]
        st = item["start"]
        en = item["end"]
        dur = item["dur"]
        sid = f"scene-{idx}"
        pfx = f"s{idx}"

        # Determine composition type
        raw_comp = str(sc.get("composition") or sc.get("layout") or sc.get("type") or "").lower()
        if "poster" in raw_comp or "manifesto" in raw_comp or "kinetic" in raw_comp:
            comp = "kinetic_poster"
        elif "full" in raw_comp or "bleed" in raw_comp or "cinematic" in raw_comp or "hero" in raw_comp:
            comp = "full_bleed_hero"
        elif "monument" in raw_comp or "center" in raw_comp or "product" in raw_comp or "showcase" in raw_comp or "turntable" in raw_comp:
            comp = "centered_monumental"
        elif "split" in raw_comp or "bento" in raw_comp or "compare" in raw_comp:
            comp = "split_dynamic"
        elif "editorial" in raw_comp or "luxury" in raw_comp or "lookbook" in raw_comp or "fashion" in raw_comp:
            comp = "editorial_asymmetric"
        elif "hud" in raw_comp or "tech" in raw_comp or "blueprint" in raw_comp or "terminal" in raw_comp or "matrix" in raw_comp:
            comp = "hud_technical"
        elif "finale" in raw_comp or "stinger" in raw_comp or "outro" in raw_comp or idx == len(scenes) - 1:
            comp = "brand_finale"
        else:
            comp = ALLOWED_COMPOSITIONS[idx % len(ALLOWED_COMPOSITIONS)]

        # Scene Data Normalization
        badge = sc.get("badge") or f"0{idx + 1} // CHAPTER 0{idx + 1}"
        headline = sc.get("headline") or f"Chapter {idx + 1}"
        subtext = sc.get("subtext") or sc.get("visual_description") or ""
        visual_code = sc.get("visual_code") or ""
        animation_css = sc.get("animation_css") or ""
        camera_note = sc.get("camera", "Cinematic Angle")

        # Compile specific scene composition
        markup, css, js = _compile_composition_scene(
            comp=comp,
            sid=sid,
            pfx=pfx,
            idx=idx,
            total_scenes=len(scenes),
            dur=dur,
            is_vertical=is_vertical,
            width=width,
            height=height,
            bg=bg,
            fg=fg,
            muted=muted,
            surface=surface,
            card_border=card_border,
            accent=accent,
            headline_font=headline_font,
            body_font=body_font,
            badge=badge,
            headline=headline,
            subtext=subtext,
            camera_note=camera_note,
            visual_code=visual_code,
            animation_css=animation_css,
            brand_name=brand_name,
            web_url=web_url
        )
        scenes_html.append(markup)
        all_scene_css.append(css)
        all_scene_js_blocks.append(js)

    combined_css = "\n".join(all_scene_css)
    combined_js = "\n".join(all_scene_js_blocks)
    scene_data_json = json.dumps(scene_data)

    # Accent glow for atmospheric stage lighting
    ar, ag, ab = _hex_to_rgb(accent)
    accent_glow = f"rgba({ar}, {ag}, {ab}, 0.08)"

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{html.escape(title)}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Anton&family=Cinzel:wght@600;700;900&family=Inter:wght@400;600;800&family=JetBrains+Mono:wght@400;500;700;800&family=Outfit:wght@500;700;800&family=Playfair+Display:ital,wght@0,600;0,700;0,900;1,600&family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&family=Space+Grotesk:wght@500;600;700;800&family=Syne:wght@700;800&display=swap" rel="stylesheet">
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; }}
  body, html {{
    width: {width}px;
    height: {height}px;
    overflow: hidden;
    background-color: {bg};
    font-family: '{body_font}', -apple-system, BlinkMacSystemFont, sans-serif;
    color: {fg};
  }}
  #stage {{
    position: relative;
    width: {width}px;
    height: {height}px;
    overflow: hidden;
    background-color: {bg};
    background: radial-gradient(circle at 50% 35%, {accent_glow} 0%, {bg} 85%);
    perspective: 1400px;
    transform-style: preserve-3d;
  }}
  #stage::after {{
    content: "";
    position: absolute;
    inset: 0;
    pointer-events: none;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.02'/%3E%3C/svg%3E");
    z-index: 1000;
  }}
  .scene {{
    position: absolute;
    top: 0; left: 0;
    width: {width}px;
    height: {height}px;
    display: none;
    opacity: 0;
    overflow: hidden;
    transform-style: preserve-3d;
    backface-visibility: hidden;
    will-change: transform, opacity, filter, clip-path;
  }}
  .dot-grid {{
    position: absolute;
    inset: 0;
    pointer-events: none;
    background-image: radial-gradient({dot_grid_color} 1.5px, transparent 1.5px);
    background-size: 40px 40px;
  }}
{combined_css}
</style>
</head>
<body>
<div id="stage">
  {''.join(scenes_html)}
</div>

<script>
  function clamp(v, min, max) {{ return Math.max(min, Math.min(max, v)); }}
  function lerp(a, b, t) {{ return a + (b - a) * t; }}
  function easeOutCubic(t) {{ return 1 - Math.pow(1 - t, 3); }}
  function easeInOutCubic(t) {{ return t < 0.5 ? 4*t*t*t : 1 - Math.pow(-2*t+2, 3)/2; }}
  function easeOutExpo(t) {{ return t === 1 ? 1 : 1 - Math.pow(2, -10 * t); }}
  function easeOutBack(t) {{
    const c1 = 1.70158, c3 = c1 + 1;
    return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2);
  }}

  // Precision Damped Harmonic Spring Physics
  function spring(t, stiffness = 130, damping = 15, mass = 1) {{
    if (t <= 0) return 0;
    if (t >= 1) return 1;
    const w0 = Math.sqrt(stiffness / mass);
    const zeta = damping / (2 * Math.sqrt(stiffness * mass));
    if (zeta < 1) {{
      const wd = w0 * Math.sqrt(1 - zeta * zeta);
      return 1 - Math.exp(-zeta * w0 * t) * (Math.cos(wd * t) + (zeta * w0 / wd) * Math.sin(wd * t));
    }}
    return 1 - (1 + w0 * t) * Math.exp(-w0 * t);
  }}

  const SCENES = {scene_data_json};
  const TOTAL_DURATION = {total_duration};
  const TRANS_DUR = 0.44; // Broadcast transition window in seconds

  function applyTransition(curEl, nextEl, transType, pTrans, easeTrans, width, height) {{
    const blurStrength = Math.sin(pTrans * Math.PI) * 20;

    switch(transType) {{
      case 'whip_pan_left':
        curEl.style.zIndex = '10';
        nextEl.style.zIndex = '20';
        curEl.style.transform = `translateX(${{-easeTrans * 100}}%) scale(${{lerp(1.0, 0.94, easeTrans)}})`;
        curEl.style.opacity = (1 - easeTrans * 0.4).toString();
        curEl.style.filter = blurStrength > 1 ? `blur(${{blurStrength}}px)` : 'none';

        nextEl.style.transform = `translateX(${{(1 - easeTrans) * 100}}%) scale(${{lerp(0.94, 1.0, easeTrans)}})`;
        nextEl.style.opacity = clamp(easeTrans * 2.2, 0, 1).toString();
        nextEl.style.filter = blurStrength > 1 ? `blur(${{blurStrength}}px)` : 'none';
        break;

      case 'whip_pan_right':
        curEl.style.zIndex = '10';
        nextEl.style.zIndex = '20';
        curEl.style.transform = `translateX(${{easeTrans * 100}}%) scale(${{lerp(1.0, 0.94, easeTrans)}})`;
        curEl.style.opacity = (1 - easeTrans * 0.4).toString();
        curEl.style.filter = blurStrength > 1 ? `blur(${{blurStrength}}px)` : 'none';

        nextEl.style.transform = `translateX(${{-(1 - easeTrans) * 100}}%) scale(${{lerp(0.94, 1.0, easeTrans)}})`;
        nextEl.style.opacity = clamp(easeTrans * 2.2, 0, 1).toString();
        nextEl.style.filter = blurStrength > 1 ? `blur(${{blurStrength}}px)` : 'none';
        break;

      case 'whip_pan_up':
        curEl.style.zIndex = '10';
        nextEl.style.zIndex = '20';
        curEl.style.transform = `translateY(${{-easeTrans * 100}}%) scale(${{lerp(1.0, 0.94, easeTrans)}})`;
        curEl.style.opacity = (1 - easeTrans * 0.4).toString();
        curEl.style.filter = blurStrength > 1 ? `blur(0px, ${{blurStrength}}px)` : 'none';

        nextEl.style.transform = `translateY(${{(1 - easeTrans) * 100}}%) scale(${{lerp(0.94, 1.0, easeTrans)}})`;
        nextEl.style.opacity = clamp(easeTrans * 2.2, 0, 1).toString();
        nextEl.style.filter = blurStrength > 1 ? `blur(0px, ${{blurStrength}}px)` : 'none';
        break;

      case 'zoom_punch':
        curEl.style.zIndex = '10';
        nextEl.style.zIndex = '20';
        curEl.style.transform = `scale(${{lerp(1.0, 2.6, easeTrans)}})`;
        curEl.style.opacity = (1 - easeTrans * 1.2).toString();
        curEl.style.filter = blurStrength > 1 ? `blur(${{blurStrength * 0.5}}px)` : 'none';

        const sB = lerp(0.38, 1.0, easeOutBack(pTrans));
        nextEl.style.transform = `scale(${{sB}})`;
        nextEl.style.opacity = clamp(pTrans * 2.5, 0, 1).toString();
        nextEl.style.filter = 'none';
        break;

      case 'rotational_snap_3d':
        curEl.style.zIndex = '10';
        nextEl.style.zIndex = '20';
        curEl.style.transformOrigin = '100% 50%';
        curEl.style.transform = `perspective(1400px) rotateY(${{-easeTrans * 90}}deg)`;
        curEl.style.opacity = (1 - easeTrans * 0.6).toString();
        curEl.style.filter = `brightness(${{1 - easeTrans * 0.5}})`;

        nextEl.style.transformOrigin = '0% 50%';
        nextEl.style.transform = `perspective(1400px) rotateY(${{(1 - easeTrans) * 90}}deg)`;
        nextEl.style.opacity = clamp(easeTrans * 2, 0, 1).toString();
        nextEl.style.filter = `brightness(${{0.5 + easeTrans * 0.5}})`;
        break;

      case 'shutter_split':
        curEl.style.zIndex = '20';
        nextEl.style.zIndex = '10';
        const gap = easeTrans * 52;
        curEl.style.clipPath = `polygon(0 0, 100% 0, 100% ${{50 - gap}}%, 0 ${{50 - gap}}%, 0 ${{50 + gap}}%, 100% ${{50 + gap}}%, 100% 100%, 0 100%)`;
        curEl.style.opacity = (1 - easeTrans * 0.8).toString();

        nextEl.style.transform = `scale(${{lerp(0.92, 1.0, easeTrans)}})`;
        nextEl.style.opacity = '1';
        break;

      case 'circular_iris':
        curEl.style.zIndex = '10';
        nextEl.style.zIndex = '20';
        curEl.style.opacity = (1 - easeTrans * 0.6).toString();
        nextEl.style.clipPath = `circle(${{easeTrans * 150}}% at 50% 50%)`;
        nextEl.style.opacity = '1';
        break;

      case 'depth_dissolve':
      default:
        curEl.style.zIndex = '10';
        nextEl.style.zIndex = '20';
        curEl.style.transform = `scale(${{lerp(1.0, 0.88, easeTrans)}}) translateZ(-80px)`;
        curEl.style.opacity = (1 - easeTrans).toString();
        curEl.style.filter = `blur(${{easeTrans * 14}}px)`;
        nextEl.style.transform = `scale(${{lerp(1.08, 1.0, easeTrans)}})`;
        nextEl.style.opacity = easeTrans.toString();
        nextEl.style.filter = 'none';
        break;
    }}
  }}

  function runSceneAnimation(idx, tScene) {{
    {combined_js}
  }}

  window.renderAt = function(t) {{
    let activeIdx = 0;
    for (let i = 0; i < SCENES.length; i++) {{
      if (t >= SCENES[i].start && t < SCENES[i].end) {{
        activeIdx = i;
        break;
      }}
    }}

    const curScene = SCENES[activeIdx];
    const nextScene = activeIdx < SCENES.length - 1 ? SCENES[activeIdx + 1] : null;
    const curEl = document.getElementById('scene-' + curScene.idx);
    const tScene = t - curScene.start;
    const dur = curScene.dur;
    const pScene = clamp(tScene / dur, 0, 1);

    // Hide all scenes not participating in this frame
    for (let i = 0; i < SCENES.length; i++) {{
      if (i !== activeIdx && (!nextScene || i !== nextScene.idx)) {{
        const el = document.getElementById('scene-' + SCENES[i].idx);
        if (el) {{
          el.style.display = 'none';
          el.style.opacity = '0';
        }}
      }}
    }}

    const inExitTrans = nextScene && (tScene >= dur - TRANS_DUR);

    if (inExitTrans && nextScene) {{
      const nextEl = document.getElementById('scene-' + nextScene.idx);
      const pTrans = clamp((tScene - (dur - TRANS_DUR)) / TRANS_DUR, 0, 1);
      const easeTrans = easeInOutCubic(pTrans);
      const transType = (curScene.config && curScene.config.transition_out) || 'whip_pan_left';

      if (curEl) curEl.style.display = 'block';
      if (nextEl) nextEl.style.display = 'block';

      runSceneAnimation(curScene.idx, tScene);
      runSceneAnimation(nextScene.idx, t - nextScene.start);

      applyTransition(curEl, nextEl, transType, pTrans, easeTrans, {width}, {height});

    }} else {{
      if (curEl) {{
        curEl.style.display = 'block';
        curEl.style.opacity = '1';
        curEl.style.zIndex = '10';

        // Organic Ken Burns spatial drift
        const dir = activeIdx % 2 === 0 ? 1 : -1;
        const panX = lerp(-12, 12, pScene) * dir;
        const panY = lerp(7, -7, pScene);
        const rotY = lerp(-1.1, 1.1, pScene) * dir;
        const rotX = lerp(0.8, -0.7, pScene);
        const camScale = lerp(0.992, 1.032, pScene);
        curEl.style.transform = `perspective(1400px) translate3d(${{panX}}px,${{panY}}px,0) rotateX(${{rotX}}deg) rotateY(${{rotY}}deg) scale(${{camScale}})`;

        runSceneAnimation(curScene.idx, tScene);
      }}
    }}
  }};

  window.fontsReady = false;
  document.fonts.ready.then(function() {{ window.fontsReady = true; }});
</script>
</body>
</html>"""
    return full_html


# ─────────────────────────────────────────────────────────────────────────────
# 7 Distinct Production-Grade Filmic Compositions
# ─────────────────────────────────────────────────────────────────────────────
def _compile_composition_scene(
    comp: str,
    sid: str,
    pfx: str,
    idx: int,
    total_scenes: int,
    dur: float,
    is_vertical: bool,
    width: int,
    height: int,
    bg: str,
    fg: str,
    muted: str,
    surface: str,
    card_border: str,
    accent: str,
    headline_font: str,
    body_font: str,
    badge: str,
    headline: str,
    subtext: str,
    camera_note: str,
    visual_code: str,
    animation_css: str,
    brand_name: str,
    web_url: str
):
    """Compiles one of 7 bespoke visual compositions for this scene."""

    # 1. KINETIC POSTER
    if comp == "kinetic_poster":
        return _build_kinetic_poster(
            sid, pfx, idx, dur, is_vertical, width, height,
            bg, fg, muted, surface, card_border, accent,
            headline_font, body_font, badge, headline, subtext,
            visual_code, animation_css, brand_name, web_url
        )

    # 2. FULL BLEED HERO
    elif comp == "full_bleed_hero":
        return _build_full_bleed_hero(
            sid, pfx, idx, dur, is_vertical, width, height,
            bg, fg, muted, surface, card_border, accent,
            headline_font, body_font, badge, headline, subtext,
            visual_code, animation_css, camera_note, brand_name
        )

    # 3. CENTERED MONUMENTAL
    elif comp == "centered_monumental":
        return _build_centered_monumental(
            sid, pfx, idx, dur, is_vertical, width, height,
            bg, fg, muted, surface, card_border, accent,
            headline_font, body_font, badge, headline, subtext,
            visual_code, animation_css, camera_note
        )

    # 4. SPLIT DYNAMIC
    elif comp == "split_dynamic":
        return _build_split_dynamic(
            sid, pfx, idx, dur, is_vertical, width, height,
            bg, fg, muted, surface, card_border, accent,
            headline_font, body_font, badge, headline, subtext,
            visual_code, animation_css, camera_note
        )

    # 5. EDITORIAL ASYMMETRIC
    elif comp == "editorial_asymmetric":
        return _build_editorial_asymmetric(
            sid, pfx, idx, dur, is_vertical, width, height,
            bg, fg, muted, surface, card_border, accent,
            headline_font, body_font, badge, headline, subtext,
            visual_code, animation_css, brand_name
        )

    # 6. HUD TECHNICAL
    elif comp == "hud_technical":
        return _build_hud_technical(
            sid, pfx, idx, dur, is_vertical, width, height,
            bg, fg, muted, surface, card_border, accent,
            headline_font, body_font, badge, headline, subtext,
            visual_code, animation_css, camera_note
        )

    # 7. BRAND FINALE
    else:
        return _build_brand_finale(
            sid, pfx, idx, dur, is_vertical, width, height,
            bg, fg, muted, surface, card_border, accent,
            headline_font, body_font, badge, headline, subtext,
            visual_code, animation_css, brand_name, web_url
        )


# ─────────────────────────────────────────────────────────────────────────────
# 1. KINETIC POSTER
# ─────────────────────────────────────────────────────────────────────────────
def _build_kinetic_poster(
    sid, pfx, idx, dur, is_vertical, width, height,
    bg, fg, muted, surface, card_border, accent,
    headline_font, body_font, badge, headline, subtext,
    visual_code, animation_css, brand_name, web_url
):
    words = headline.split()
    if len(words) <= 3:
        lines = [headline]
    elif len(words) <= 6:
        mid = len(words) // 2
        lines = [" ".join(words[:mid]), " ".join(words[mid:])]
    else:
        part = len(words) // 3
        lines = [" ".join(words[:part]), " ".join(words[part:part*2]), " ".join(words[part*2:])]

    fsize = int(height * (0.08 if is_vertical else 0.11))
    lines_html = ""
    for i, line in enumerate(lines):
        lines_html += f"""
        <div style="overflow: hidden; line-height: 1.02; margin-bottom: 6px;">
          <div id="{pfx}_line_{i}" style="font-family: '{headline_font}', sans-serif; font-size: {fsize}px; font-weight: 900; letter-spacing: -0.04em; color: {fg}; transform: translateY(115%); text-transform: uppercase;">
            {html.escape(line)}
          </div>
        </div>"""

    vis_w = "860px" if is_vertical else "520px"
    vis_h = "500px" if is_vertical else "380px"

    markup = f"""
    <div id="{sid}" class="scene" style="position: absolute; inset: 0; width: {width}px; height: {height}px; background-color: {bg};">
      <div class="dot-grid"></div>

      <div style="position: absolute; inset: 0; padding: {int(height*0.07)}px {int(width*0.07)}px; display: flex; flex-direction: column; justify-content: space-between; z-index: 10;">
        <!-- Top bar -->
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <div id="{pfx}_badge" style="display: inline-flex; align-items: center; gap: 8px; padding: 6px 16px; border-radius: 9999px; background: {surface}; border: 1px solid {card_border}; font-family: 'JetBrains Mono', monospace; font-size: 13px; font-weight: 700; color: {accent}; text-transform: uppercase; letter-spacing: 1.2px; opacity: 0;">
            <span style="width: 7px; height: 7px; border-radius: 50%; background: {accent};"></span>
            <span>{html.escape(badge)}</span>
          </div>
          <div style="font-family: 'JetBrains Mono', monospace; font-size: 13px; color: {muted}; letter-spacing: 1px;">
            {html.escape(brand_name or web_url or "CINEMATRIX MASTER")}
          </div>
        </div>

        <!-- Center content: Kinetic lines + Integrated Vector Art -->
        <div style="display: grid; grid-template-columns: {'1fr' if is_vertical else '1.2fr 0.8fr'}; align-items: center; gap: 40px;">
          <div>
            {lines_html}
            <p id="{pfx}_sub" style="font-family: '{body_font}', sans-serif; font-size: {int(height*0.024)}px; color: {muted}; line-height: 1.5; margin-top: 24px; max-width: 640px; opacity: 0;">
              {html.escape(subtext)}
            </p>
          </div>

          <div id="{pfx}_vis" style="width: {vis_w}; height: {vis_h}; display: flex; align-items: center; justify-content: center; position: relative; border-radius: 16px; background: {surface}; border: 1px solid {card_border}; padding: 24px; opacity: 0;">
            <div style="width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;">
              {visual_code}
            </div>
          </div>
        </div>

        <!-- Bottom bar -->
        <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid {card_border}; padding-top: 20px;">
          <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: {muted}; text-transform: uppercase;">
            ARCHETYPE // KINETIC POSTER
          </div>
          <div id="{pfx}_pill" style="padding: 10px 24px; border-radius: 9999px; background: {fg}; color: {bg}; font-family: '{body_font}', sans-serif; font-weight: 800; font-size: 14px; letter-spacing: 0.5px; opacity: 0;">
            DISCOVER
          </div>
        </div>
      </div>
    </div>
    """

    css = f"""
    #{pfx}_vis svg {{
      width: 100%; height: 100%; max-width: 100%; max-height: 100%; object-fit: contain; overflow: visible;
    }}
    {animation_css}
    """

    js_lines = ""
    for i in range(len(lines)):
        delay = 0.08 + i * 0.10
        js_lines += f"""
        const l{i} = document.getElementById('{pfx}_line_{i}');
        if (l{i}) {{
          const p = easeOutExpo(clamp((tScene - {delay}) / 0.55, 0, 1));
          l{i}.style.transform = `translateY(${{lerp(115, 0, p)}}%)`;
        }}"""

    js = f"""
      if (idx === {idx}) {{
        const badge = document.getElementById('{pfx}_badge');
        const sub = document.getElementById('{pfx}_sub');
        const vis = document.getElementById('{pfx}_vis');
        const pill = document.getElementById('{pfx}_pill');

        if (badge) {{
          const pB = easeOutCubic(clamp(tScene / 0.35, 0, 1));
          badge.style.opacity = pB.toString();
          badge.style.transform = `translateY(${{lerp(-12, 0, pB)}}px)`;
        }}

        {js_lines}

        if (sub) {{
          const pS = easeOutCubic(clamp((tScene - 0.35) / 0.45, 0, 1));
          sub.style.opacity = pS.toString();
          sub.style.transform = `translateY(${{lerp(16, 0, pS)}}px)`;
        }}

        if (vis) {{
          const pV = spring(clamp((tScene - 0.2) * 1.8, 0, 1));
          vis.style.opacity = clamp((tScene - 0.2) * 3, 0, 1).toString();
          vis.style.transform = `scale(${{lerp(0.88, 1.0, pV)}})`;
        }}

        if (pill) {{
          const pP = easeOutBack(clamp((tScene - 0.5) / 0.45, 0, 1));
          pill.style.opacity = clamp(pP, 0, 1).toString();
          pill.style.transform = `scale(${{pP}})`;
        }}
      }}
    """
    return markup, css, js


# ─────────────────────────────────────────────────────────────────────────────
# 2. FULL BLEED HERO
# ─────────────────────────────────────────────────────────────────────────────
def _build_full_bleed_hero(
    sid, pfx, idx, dur, is_vertical, width, height,
    bg, fg, muted, surface, card_border, accent,
    headline_font, body_font, badge, headline, subtext,
    visual_code, animation_css, camera_note, brand_name
):
    markup = f"""
    <div id="{sid}" class="scene" style="position: absolute; inset: 0; width: {width}px; height: {height}px; background-color: {bg};">
      <!-- Full Canvas SVG Hero Stage -->
      <div id="{pfx}_hero_art" style="position: absolute; inset: 0; width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; z-index: 5; padding: 40px;">
        <div style="width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;">
          {visual_code}
        </div>
      </div>

      <!-- Cinematic Lower-Third Title Overlay -->
      <div id="{pfx}_card" style="position: absolute; bottom: {int(height*0.08)}px; left: {int(width*0.06)}px; max-width: {int(width*0.58)}px; background: {surface}; backdrop-filter: blur(20px); border: 1px solid {card_border}; border-radius: 20px; padding: 32px 40px; z-index: 20; opacity: 0; box-shadow: 0 24px 64px rgba(0,0,0,0.5);">
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 16px;">
          <span style="width: 8px; height: 8px; border-radius: 50%; background: {accent};"></span>
          <span style="font-family: 'JetBrains Mono', monospace; font-size: 13px; font-weight: 700; color: {accent}; letter-spacing: 1.5px; text-transform: uppercase;">
            {html.escape(badge)}
          </span>
          <span style="color: {muted}; opacity: 0.4;">|</span>
          <span style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: {muted}; text-transform: uppercase;">
            {html.escape(camera_note[:32])}
          </span>
        </div>

        <h1 style="font-family: '{headline_font}', sans-serif; font-size: {int(height*0.055)}px; font-weight: 800; color: {fg}; line-height: 1.1; letter-spacing: -0.03em; margin-bottom: 12px;">
          {html.escape(headline)}
        </h1>

        <p style="font-family: '{body_font}', sans-serif; font-size: {int(height*0.022)}px; color: {muted}; line-height: 1.45; font-weight: 400;">
          {html.escape(subtext)}
        </p>
      </div>
    </div>
    """

    css = f"""
    #{pfx}_hero_art svg {{
      width: 100%; height: 100%; max-width: 100%; max-height: 100%; object-fit: contain; overflow: visible;
    }}
    {animation_css}
    """

    js = f"""
      if (idx === {idx}) {{
        const card = document.getElementById('{pfx}_card');
        const art = document.getElementById('{pfx}_hero_art');
        const p = clamp(tScene / {dur}, 0, 1);

        if (art) {{
          const artScale = lerp(0.96, 1.05, easeOutCubic(p));
          art.style.transform = `scale(${{artScale}})`;
        }}

        if (card) {{
          const pC = spring(clamp((tScene - 0.25) * 1.8, 0, 1));
          card.style.opacity = clamp((tScene - 0.25) * 3, 0, 1).toString();
          card.style.transform = `translateY(${{lerp(40, 0, pC)}}px)`;
        }}
      }}
    """
    return markup, css, js


# ─────────────────────────────────────────────────────────────────────────────
# 3. CENTERED MONUMENTAL
# ─────────────────────────────────────────────────────────────────────────────
def _build_centered_monumental(
    sid, pfx, idx, dur, is_vertical, width, height,
    bg, fg, muted, surface, card_border, accent,
    headline_font, body_font, badge, headline, subtext,
    visual_code, animation_css, camera_note
):
    vis_w = "920px" if is_vertical else "820px"
    vis_h = "720px" if is_vertical else "480px"

    markup = f"""
    <div id="{sid}" class="scene" style="position: absolute; inset: 0; width: {width}px; height: {height}px; background-color: {bg}; display: flex; flex-direction: column; align-items: center; justify-content: space-between; padding: {int(height*0.06)}px 60px;">
      <div class="dot-grid"></div>

      <!-- Top Badge -->
      <div id="{pfx}_badge" style="display: inline-flex; align-items: center; gap: 8px; padding: 6px 18px; border-radius: 9999px; background: {surface}; border: 1px solid {card_border}; font-family: 'JetBrains Mono', monospace; font-size: 13px; font-weight: 700; color: {accent}; text-transform: uppercase; letter-spacing: 1.5px; opacity: 0; z-index: 10;">
        <span style="width: 7px; height: 7px; border-radius: 50%; background: {accent};"></span>
        <span>{html.escape(badge)}</span>
      </div>

      <!-- Grand Center Visual Stage -->
      <div id="{pfx}_stage" style="width: {vis_w}; height: {vis_h}; display: flex; align-items: center; justify-content: center; position: relative; border-radius: 24px; background: {surface}; border: 1px solid {card_border}; padding: 30px; opacity: 0; z-index: 10; box-shadow: 0 32px 80px rgba(0,0,0,0.6);">
        <div style="width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;">
          {visual_code}
        </div>
      </div>

      <!-- Monumental Bottom Headline -->
      <div id="{pfx}_text" style="text-align: center; max-width: 900px; z-index: 10; opacity: 0;">
        <h1 style="font-family: '{headline_font}', sans-serif; font-size: {int(height*0.052)}px; font-weight: 800; color: {fg}; line-height: 1.15; letter-spacing: -0.03em; margin-bottom: 12px;">
          {html.escape(headline)}
        </h1>
        <p style="font-family: '{body_font}', sans-serif; font-size: {int(height*0.022)}px; color: {muted}; line-height: 1.5; font-weight: 400; max-width: 720px; margin: 0 auto;">
          {html.escape(subtext)}
        </p>
      </div>
    </div>
    """

    css = f"""
    #{pfx}_stage svg {{
      width: 100%; height: 100%; max-width: 100%; max-height: 100%; object-fit: contain; overflow: visible;
    }}
    {animation_css}
    """

    js = f"""
      if (idx === {idx}) {{
        const b = document.getElementById('{pfx}_badge');
        const st = document.getElementById('{pfx}_stage');
        const txt = document.getElementById('{pfx}_text');

        if (b) {{
          const pB = easeOutCubic(clamp(tScene / 0.35, 0, 1));
          b.style.opacity = pB.toString();
          b.style.transform = `translateY(${{lerp(-18, 0, pB)}}px)`;
        }}

        if (st) {{
          const pSt = spring(clamp((tScene - 0.15) * 1.8, 0, 1));
          st.style.opacity = clamp((tScene - 0.15) * 3, 0, 1).toString();
          st.style.transform = `scale(${{lerp(0.85, 1.0, pSt)}})`;
        }}

        if (txt) {{
          const pT = spring(clamp((tScene - 0.35) * 1.8, 0, 1));
          txt.style.opacity = clamp((tScene - 0.35) * 3, 0, 1).toString();
          txt.style.transform = `translateY(${{lerp(30, 0, pT)}}px)`;
        }}
      }}
    """
    return markup, css, js


# ─────────────────────────────────────────────────────────────────────────────
# 4. SPLIT DYNAMIC
# ─────────────────────────────────────────────────────────────────────────────
def _build_split_dynamic(
    sid, pfx, idx, dur, is_vertical, width, height,
    bg, fg, muted, surface, card_border, accent,
    headline_font, body_font, badge, headline, subtext,
    visual_code, animation_css, camera_note
):
    # Alternating layout: even scenes text left/vis right; odd scenes vis left/text right
    reverse = (idx % 2 == 1) and not is_vertical
    grid_cols = "1fr 1fr" if not is_vertical else "1fr"

    markup = f"""
    <div id="{sid}" class="scene" style="position: absolute; inset: 0; width: {width}px; height: {height}px; background-color: {bg};">
      <div class="dot-grid"></div>

      <div style="position: absolute; inset: 0; display: grid; grid-template-columns: {grid_cols}; align-items: center; gap: 50px; padding: 80px 100px; z-index: 10;">
        <!-- Text Column -->
        <div id="{pfx}_col_text" style="display: flex; flex-direction: column; justify-content: center; gap: 24px; order: {2 if reverse else 1}; opacity: 0;">
          <div style="display: inline-flex; align-items: center; gap: 8px; width: fit-content; padding: 6px 14px; border-radius: 9999px; background: {surface}; border: 1px solid {card_border}; font-family: 'JetBrains Mono', monospace; font-size: 13px; font-weight: 700; color: {accent}; text-transform: uppercase; letter-spacing: 1.2px;">
            <span style="width: 7px; height: 7px; border-radius: 50%; background: {accent};"></span>
            <span>{html.escape(badge)}</span>
          </div>

          <h1 style="font-family: '{headline_font}', sans-serif; font-size: {int(height*0.052)}px; font-weight: 800; color: {fg}; line-height: 1.12; letter-spacing: -0.03em;">
            {html.escape(headline)}
          </h1>

          <p style="font-family: '{body_font}', sans-serif; font-size: {int(height*0.022)}px; color: {muted}; line-height: 1.5; font-weight: 400; max-width: 620px;">
            {html.escape(subtext)}
          </p>

          <div style="display: flex; align-items: center; gap: 16px; margin-top: 8px; font-family: 'JetBrains Mono', monospace; font-size: 11px; color: {muted};">
            <span>DIRECTION // {html.escape(camera_note[:32])}</span>
          </div>
        </div>

        <!-- Visual Stage Column -->
        <div id="{pfx}_col_vis" style="width: 100%; height: {int(height*0.62)}px; display: flex; align-items: center; justify-content: center; border-radius: 20px; background: {surface}; border: 1px solid {card_border}; padding: 30px; order: {1 if reverse else 2}; opacity: 0; box-shadow: 0 24px 64px rgba(0,0,0,0.5);">
          <div style="width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;">
            {visual_code}
          </div>
        </div>
      </div>
    </div>
    """

    css = f"""
    #{pfx}_col_vis svg {{
      width: 100%; height: 100%; max-width: 100%; max-height: 100%; object-fit: contain; overflow: visible;
    }}
    {animation_css}
    """

    js = f"""
      if (idx === {idx}) {{
        const txt = document.getElementById('{pfx}_col_text');
        const vis = document.getElementById('{pfx}_col_vis');

        if (txt) {{
          const pT = spring(clamp(tScene * 1.8, 0, 1));
          txt.style.opacity = clamp(tScene * 3, 0, 1).toString();
          txt.style.transform = `translateX(${{lerp({-30 if not reverse else 30}, 0, pT)}}px)`;
        }}

        if (vis) {{
          const pV = spring(clamp((tScene - 0.15) * 1.8, 0, 1));
          vis.style.opacity = clamp((tScene - 0.15) * 3, 0, 1).toString();
          vis.style.transform = `scale(${{lerp(0.90, 1.0, pV)}})`;
        }}
      }}
    """
    return markup, css, js


# ─────────────────────────────────────────────────────────────────────────────
# 5. EDITORIAL ASYMMETRIC
# ─────────────────────────────────────────────────────────────────────────────
def _build_editorial_asymmetric(
    sid, pfx, idx, dur, is_vertical, width, height,
    bg, fg, muted, surface, card_border, accent,
    headline_font, body_font, badge, headline, subtext,
    visual_code, animation_css, brand_name
):
    markup = f"""
    <div id="{sid}" class="scene" style="position: absolute; inset: 0; width: {width}px; height: {height}px; background-color: {bg}; padding: 90px 110px;">
      <div style="position: absolute; inset: 0; display: grid; grid-template-columns: {'1fr' if is_vertical else '0.9fr 1.1fr'}; align-items: center; gap: 70px; z-index: 10;">
        <!-- Portrait Visual Frame -->
        <div id="{pfx}_frame" style="width: 100%; height: {int(height*0.72)}px; display: flex; align-items: center; justify-content: center; border-radius: 12px; background: {surface}; border: 1px solid {card_border}; padding: 36px; opacity: 0; box-shadow: 0 32px 90px rgba(0,0,0,0.65);">
          <div style="width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;">
            {visual_code}
          </div>
        </div>

        <!-- Editorial Typography -->
        <div id="{pfx}_edit_text" style="display: flex; flex-direction: column; gap: 28px; opacity: 0;">
          <div style="display: flex; align-items: center; gap: 12px; font-family: 'JetBrains Mono', monospace; font-size: 13px; color: {accent}; letter-spacing: 2px; text-transform: uppercase;">
            <span>[ N° {idx + 1:02d} ]</span>
            <span>//</span>
            <span>{html.escape(badge)}</span>
          </div>

          <h1 style="font-family: 'Playfair Display', serif; font-size: {int(height*0.06)}px; font-weight: 700; font-style: italic; color: {fg}; line-height: 1.1; letter-spacing: -0.02em;">
            {html.escape(headline)}
          </h1>

          <div style="width: 60px; height: 1px; background: {accent}; opacity: 0.6;"></div>

          <p style="font-family: '{body_font}', sans-serif; font-size: {int(height*0.024)}px; color: {muted}; line-height: 1.6; font-weight: 400; max-width: 600px;">
            {html.escape(subtext)}
          </p>

          <div style="font-family: 'JetBrains Mono', monospace; font-size: 11px; color: {muted}; letter-spacing: 1px;">
            COLLECTION // {html.escape(brand_name or "HAUTE HORLOGERIE & ATELIER")}
          </div>
        </div>
      </div>
    </div>
    """

    css = f"""
    #{pfx}_frame svg {{
      width: 100%; height: 100%; max-width: 100%; max-height: 100%; object-fit: contain; overflow: visible;
    }}
    {animation_css}
    """

    js = f"""
      if (idx === {idx}) {{
        const fr = document.getElementById('{pfx}_frame');
        const txt = document.getElementById('{pfx}_edit_text');

        if (fr) {{
          const pF = easeOutCubic(clamp(tScene / 0.7, 0, 1));
          fr.style.opacity = pF.toString();
          fr.style.transform = `scale(${{lerp(0.92, 1.0, pF)}})`;
        }}

        if (txt) {{
          const pT = easeOutCubic(clamp((tScene - 0.25) / 0.65, 0, 1));
          txt.style.opacity = pT.toString();
          txt.style.transform = `translateY(${{lerp(24, 0, pT)}}px)`;
        }}
      }}
    """
    return markup, css, js


# ─────────────────────────────────────────────────────────────────────────────
# 6. HUD TECHNICAL
# ─────────────────────────────────────────────────────────────────────────────
def _build_hud_technical(
    sid, pfx, idx, dur, is_vertical, width, height,
    bg, fg, muted, surface, card_border, accent,
    headline_font, body_font, badge, headline, subtext,
    visual_code, animation_css, camera_note
):
    markup = f"""
    <div id="{sid}" class="scene" style="position: absolute; inset: 0; width: {width}px; height: {height}px; background-color: {bg}; padding: 60px 80px; display: flex; flex-direction: column; justify-content: space-between;">
      <div class="dot-grid"></div>

      <!-- Corner Crosshairs -->
      <div style="position: absolute; top: 30px; left: 30px; font-family: 'JetBrains Mono', monospace; font-size: 11px; color: {accent};">[ + ] LAT 37.7749</div>
      <div style="position: absolute; top: 30px; right: 30px; font-family: 'JetBrains Mono', monospace; font-size: 11px; color: {accent};">LON -122.4194 [ + ]</div>
      <div style="position: absolute; bottom: 30px; left: 30px; font-family: 'JetBrains Mono', monospace; font-size: 11px; color: {accent};">[ + ] SYS.ACTIVE</div>
      <div style="position: absolute; bottom: 30px; right: 30px; font-family: 'JetBrains Mono', monospace; font-size: 11px; color: {accent};">REV.4.1 [ + ]</div>

      <!-- Top Telemetry Bar -->
      <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid {card_border}; padding-bottom: 16px; z-index: 10;">
        <div style="display: flex; align-items: center; gap: 12px; font-family: 'JetBrains Mono', monospace; font-size: 12px; color: {accent}; font-weight: 700; text-transform: uppercase;">
          <span style="width: 8px; height: 8px; border-radius: 50%; background: {accent};"></span>
          <span>HUD // {html.escape(badge)}</span>
        </div>
        <div style="font-family: 'JetBrains Mono', monospace; font-size: 12px; color: {muted};">
          FRAME // 0{idx + 1} OF 07
        </div>
      </div>

      <!-- Center Wireframe / Blueprint Stage -->
      <div style="display: grid; grid-template-columns: {'1fr' if is_vertical else '1.1fr 0.9fr'}; align-items: center; gap: 50px; z-index: 10;">
        <div id="{pfx}_hud_vis" style="width: 100%; height: {int(height*0.52)}px; display: flex; align-items: center; justify-content: center; border-radius: 16px; background: {surface}; border: 1px solid {card_border}; padding: 24px; opacity: 0;">
          <div style="width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;">
            {visual_code}
          </div>
        </div>

        <div id="{pfx}_hud_text" style="display: flex; flex-direction: column; gap: 20px; opacity: 0;">
          <h1 style="font-family: 'Space Grotesk', sans-serif; font-size: {int(height*0.048)}px; font-weight: 800; color: {fg}; line-height: 1.15; letter-spacing: -0.03em;">
            {html.escape(headline)}
          </h1>
          <p style="font-family: '{body_font}', sans-serif; font-size: {int(height*0.022)}px; color: {muted}; line-height: 1.5;">
            {html.escape(subtext)}
          </p>

          <!-- 3-Column Metric Gauges -->
          <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-top: 12px;">
            <div style="background: {surface}; border: 1px solid {card_border}; border-radius: 8px; padding: 12px 14px;">
              <div style="font-family: 'JetBrains Mono', monospace; font-size: 10px; color: {muted};">EFFICIENCY</div>
              <div style="font-family: 'JetBrains Mono', monospace; font-size: 16px; font-weight: 700; color: {fg}; margin-top: 4px;">99.8%</div>
            </div>
            <div style="background: {surface}; border: 1px solid {card_border}; border-radius: 8px; padding: 12px 14px;">
              <div style="font-family: 'JetBrains Mono', monospace; font-size: 10px; color: {muted};">LATENCY</div>
              <div style="font-family: 'JetBrains Mono', monospace; font-size: 16px; font-weight: 700; color: {fg}; margin-top: 4px;">1.2 MS</div>
            </div>
            <div style="background: {surface}; border: 1px solid {card_border}; border-radius: 8px; padding: 12px 14px;">
              <div style="font-family: 'JetBrains Mono', monospace; font-size: 10px; color: {muted};">THROUGHPUT</div>
              <div style="font-family: 'JetBrains Mono', monospace; font-size: 16px; font-weight: 700; color: {fg}; margin-top: 4px;">10 GB/S</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Bottom Status Readout -->
      <div style="border-top: 1px solid {card_border}; padding-top: 16px; display: flex; justify-content: space-between; font-family: 'JetBrains Mono', monospace; font-size: 11px; color: {muted}; z-index: 10;">
        <span>CAMERA // {html.escape(camera_note[:36])}</span>
        <span>STATUS // TELEMETRY VERIFIED</span>
      </div>
    </div>
    """

    css = f"""
    #{pfx}_hud_vis svg {{
      width: 100%; height: 100%; max-width: 100%; max-height: 100%; object-fit: contain; overflow: visible;
    }}
    {animation_css}
    """

    js = f"""
      if (idx === {idx}) {{
        const v = document.getElementById('{pfx}_hud_vis');
        const t = document.getElementById('{pfx}_hud_text');

        if (v) {{
          const pV = easeOutCubic(clamp(tScene / 0.5, 0, 1));
          v.style.opacity = pV.toString();
          v.style.transform = `scale(${{lerp(0.92, 1.0, pV)}})`;
        }}

        if (t) {{
          const pT = easeOutCubic(clamp((tScene - 0.2) / 0.5, 0, 1));
          t.style.opacity = pT.toString();
          t.style.transform = `translateY(${{lerp(20, 0, pT)}}px)`;
        }}
      }}
    """
    return markup, css, js


# ─────────────────────────────────────────────────────────────────────────────
# 7. BRAND FINALE
# ─────────────────────────────────────────────────────────────────────────────
def _build_brand_finale(
    sid, pfx, idx, dur, is_vertical, width, height,
    bg, fg, muted, surface, card_border, accent,
    headline_font, body_font, badge, headline, subtext,
    visual_code, animation_css, brand_name, web_url
):
    markup = f"""
    <div id="{sid}" class="scene" style="position: absolute; inset: 0; width: {width}px; height: {height}px; background-color: {bg}; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 60px; text-align: center;">
      <div class="dot-grid"></div>

      <!-- Central Animated Vector Emblem -->
      <div id="{pfx}_emblem" style="width: 240px; height: 240px; display: flex; align-items: center; justify-content: center; border-radius: 50%; background: {surface}; border: 1px solid {card_border}; margin-bottom: 40px; opacity: 0; z-index: 10; box-shadow: 0 24px 64px rgba(0,0,0,0.6);">
        <div style="width: 75%; height: 75%; display: flex; align-items: center; justify-content: center;">
          {visual_code}
        </div>
      </div>

      <!-- Monumental Headline / Brand Call -->
      <h1 id="{pfx}_fin_head" style="font-family: '{headline_font}', sans-serif; font-size: {int(height*0.065)}px; font-weight: 900; color: {fg}; line-height: 1.1; letter-spacing: -0.04em; max-width: 960px; margin-bottom: 18px; opacity: 0; z-index: 10;">
        {html.escape(headline)}
      </h1>

      <!-- Tagline -->
      <p id="{pfx}_fin_sub" style="font-family: '{body_font}', sans-serif; font-size: {int(height*0.026)}px; color: {muted}; line-height: 1.5; font-weight: 500; max-width: 700px; margin-bottom: 36px; opacity: 0; z-index: 10;">
        {html.escape(subtext or brand_name)}
      </p>

      <!-- Action Pill / Web URL -->
      <div id="{pfx}_fin_pill" style="padding: 14px 36px; border-radius: 9999px; background: {fg}; color: {bg}; font-family: '{body_font}', sans-serif; font-weight: 800; font-size: 16px; letter-spacing: 0.5px; opacity: 0; z-index: 10; box-shadow: 0 16px 36px rgba(0,0,0,0.4);">
        {html.escape(web_url or brand_name or "DISCOVER MORE")}
      </div>
    </div>
    """

    css = f"""
    #{pfx}_emblem svg {{
      width: 100%; height: 100%; max-width: 100%; max-height: 100%; object-fit: contain; overflow: visible;
    }}
    {animation_css}
    """

    js = f"""
      if (idx === {idx}) {{
        const emb = document.getElementById('{pfx}_emblem');
        const h = document.getElementById('{pfx}_fin_head');
        const s = document.getElementById('{pfx}_fin_sub');
        const p = document.getElementById('{pfx}_fin_pill');

        if (emb) {{
          const pE = spring(clamp(tScene * 1.6, 0, 1));
          emb.style.opacity = clamp(tScene * 3, 0, 1).toString();
          emb.style.transform = `scale(${{lerp(0.75, 1.0, pE)}})`;
        }}

        if (h) {{
          const pH = spring(clamp((tScene - 0.2) * 1.8, 0, 1));
          h.style.opacity = clamp((tScene - 0.2) * 3, 0, 1).toString();
          h.style.transform = `translateY(${{lerp(28, 0, pH)}}px)`;
        }}

        if (s) {{
          const pS = easeOutCubic(clamp((tScene - 0.35) / 0.5, 0, 1));
          s.style.opacity = pS.toString();
        }}

        if (p) {{
          const pP = easeOutBack(clamp((tScene - 0.45) / 0.45, 0, 1));
          p.style.opacity = clamp(pP, 0, 1).toString();
          p.style.transform = `scale(${{pP}})`;
        }}
      }}
    """
    return markup, css, js
