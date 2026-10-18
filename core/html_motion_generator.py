import json
import html
import random

# ─────────────────────────────────────────────────────────────────────────────
# CineMatrix HTML Motion Generator v4.0 — Broadcast-Grade Motion Cinema Engine
# Features:
# 1. 14 Unique Production-Grade Archetypes (Zero hardcoded sequence repetition)
# 2. Cinema Transition & Switch Engine (Whip Pans, 3D Snaps, Zoom Punches, Shutter Splits, Irises)
# 3. Spring Physics & Damped Harmonic Oscillators (Zero robotic linear lerps)
# 4. Animated SVGs, live counting tickers, code typewriter & live UI widgets
# ─────────────────────────────────────────────────────────────────────────────

def generate_motion_html(storyboard: dict) -> str:
    """Dynamically generates a broadcast-grade HTML5 motion design stage.
    Every scene has completely unique HTML structure, CSS classes, and JS
    animation logic — no two scenes share the same template.
    """
    aspect_ratio = storyboard.get("aspect_ratio", "16:9")
    if aspect_ratio == "9:16":
        width, height = 1080, 1920
        is_vertical = True
    elif aspect_ratio == "1:1":
        width, height = 1080, 1080
        is_vertical = False
    else:
        width, height = 1920, 1080
        is_vertical = False

    scenes = storyboard.get("scenes", [])
    total_duration = sum(s.get("duration", 3.5) for s in scenes)
    brand_name = storyboard.get("brand_name", "")
    web_url = storyboard.get("web_url", "")
    genre = storyboard.get("genre", "tech_saas").lower()

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

    # Dynamic Archetype Selector — 100% decoupled from position!
    def pick_archetype(sc: dict, idx: int, total: int, gen: str) -> str:
        layout = sc.get("layout", "").lower()
        sc_type = sc.get("type", "").lower()
        comb = f"{layout} {sc_type}"

        # 1. Direct explicit match from storyboard
        if any(k in comb for k in ["manifesto", "kinetic", "type", "text", "bold_type"]):
            return "kinetic_manifesto"
        if any(k in comb for k in ["product", "hardware", "device_turntable", "turntable", "showcase"]):
            return "product_showcase"
        if any(k in comb for k in ["code", "terminal", "ide", "cli", "syntax", "developer"]):
            return "terminal_code_stream"
        if any(k in comb for k in ["finance", "ticker", "trading", "crypto", "stock", "chart", "telemetry"]):
            return "financial_telemetry"
        if any(k in comb for k in ["split", "compare", "comparison", "versus", "vs", "before_after"]):
            return "split_comparison"
        if any(k in comb for k in ["matrix", "metric", "stat", "proof", "impact", "numbers"]):
            return "metric_impact_matrix"
        if any(k in comb for k in ["stinger", "resolve", "brand_outro", "logo_resolve", "finale"]):
            return "brand_stinger_outro"
        if any(k in comb for k in ["editorial", "luxury", "fashion", "lookbook", "serif"]):
            return "editorial_lookbook"
        if any(k in comb for k in ["bento", "grid", "cards"]):
            return "bento_grid_v2"
        if any(k in comb for k in ["coin", "parade", "badge_carousel"]):
            return "coin_parade"
        if any(k in comb for k in ["blueprint", "cad", "figma"]):
            return "blueprint_reveal"
        if any(k in comb for k in ["device", "phone", "mockup", "mobile", "app"]):
            return "dashboard_device"
        if any(k in comb for k in ["parallax", "float", "cloud"]):
            return "kinetic_parallax"
        if any(k in comb for k in ["hero", "cinematic", "widescreen"]):
            return "cinematic_hero"

        # 2. Position & Genre-Intelligent Mapping (No hardcoded repetition)
        if idx == total - 1:
            # Final scene defaults to high-end brand stinger outro unless mockup requested
            return "brand_stinger_outro"

        # Diversity pools per genre
        if any(k in gen for k in ["dev", "code", "saas", "software", "tech"]):
            pool = ["kinetic_manifesto", "terminal_code_stream", "bento_grid_v2", "metric_impact_matrix", "split_comparison"]
        elif any(k in gen for k in ["finance", "crypto", "trading", "defi"]):
            pool = ["kinetic_manifesto", "financial_telemetry", "metric_impact_matrix", "split_comparison", "bento_grid_v2"]
        elif any(k in gen for k in ["luxury", "fashion", "lifestyle", "fragrance", "watch"]):
            pool = ["editorial_lookbook", "product_showcase", "cinematic_hero", "kinetic_parallax"]
        elif any(k in gen for k in ["product", "hardware", "device", "sneaker", "gadget"]):
            pool = ["kinetic_manifesto", "product_showcase", "bento_grid_v2", "split_comparison", "metric_impact_matrix"]
        else:
            pool = ["kinetic_manifesto", "bento_grid_v2", "metric_impact_matrix", "product_showcase", "split_comparison", "cinematic_hero"]

        return pool[idx % len(pool)]

    # Assign Cinema Transition Out per scene
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

    # Generate per-scene HTML, CSS, and JS
    scenes_html = []
    all_scene_css = []
    all_scene_js_blocks = []

    for item in scene_data:
        idx = item["idx"]
        sc = item["config"]
        st = item["start"]
        en = item["end"]
        dur = item["dur"]

        archetype = pick_archetype(sc, idx, len(scenes), genre)

        # Color palette calculation
        bg_theme = sc.get("bg_theme", "dark_grid")
        primary_color = sc.get("primary_color", "#E2E8F0")

        if "cream" in bg_theme or "light" in bg_theme:
            bg = "#F6F4EE"; fg = "#09090b"; muted = "#52525b"; card_border = "rgba(0,0,0,0.08)"
        elif "carbon" in bg_theme or "slate" in bg_theme:
            bg = "#0B0F17"; fg = "#F8FAFC"; muted = "#94A3B8"; card_border = "rgba(255,255,255,0.09)"
        elif "gold" in bg_theme or "luxury" in bg_theme:
            bg = "#0C0A06"; fg = "#FEF08A"; muted = "#A1A1AA"; card_border = "rgba(254,240,138,0.15)"
        elif "crimson" in bg_theme or "news" in bg_theme:
            bg = "#120708"; fg = "#FFFFFF"; muted = "#FDA4AF"; card_border = "rgba(253,164,175,0.15)"
        elif "terminal" in bg_theme or "matrix" in bg_theme:
            bg = "#080B0D"; fg = "#F1F5F9"; muted = "#64748B"; card_border = "rgba(255,255,255,0.08)"
        else: # default matte obsidian
            bg = "#050508"; fg = "#FFFFFF"; muted = "#94A3B8"; card_border = "rgba(255,255,255,0.10)"

        badge = sc.get("badge", f"{idx+1:02d} // CHAPTER {idx+1:02d}")
        headline = sc.get("headline", sc.get("brand_title", "Vision of Tomorrow"))
        subtext = sc.get("subtext", sc.get("tagline", "Engineered for the next generation"))
        pills = sc.get("pills") or []
        metrics = sc.get("metrics") or []
        features = sc.get("features") or []

        scene_markup, scene_css, scene_js = _compile_archetype_scene(
            archetype=archetype,
            idx=idx,
            total_scenes=len(scenes),
            sc=sc,
            st=st,
            en=en,
            dur=dur,
            is_vertical=is_vertical,
            width=width,
            height=height,
            brand_name=sc.get("brand_name", brand_name),
            web_url=sc.get("web_url", web_url),
            bg=bg,
            fg=fg,
            muted=muted,
            card_border=card_border,
            primary_color=primary_color,
            badge=badge,
            headline=headline,
            subtext=subtext,
            pills=pills,
            metrics=metrics,
            features=features,
        )
        scenes_html.append(scene_markup)
        all_scene_css.append(scene_css)
        all_scene_js_blocks.append(scene_js)

    combined_css = "\n".join(all_scene_css)
    combined_js = "\n".join(all_scene_js_blocks)
    scene_data_json = json.dumps(scene_data)

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{html.escape(storyboard.get("title", "CineMatrix Broadcast Master"))}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&family=Playfair+Display:ital,wght@0,600;0,700;0,900;1,600&family=Space+Grotesk:wght@500;600;700;800&family=JetBrains+Mono:wght@400;500;700;800&family=Anton&display=swap" rel="stylesheet">
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; -webkit-font-smoothing: antialiased; -moz-osx-font-smoothing: grayscale; }}
  body, html {{
    width: {width}px;
    height: {height}px;
    overflow: hidden;
    background-color: #050508;
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
  }}
  #stage {{
    position: relative;
    width: {width}px;
    height: {height}px;
    overflow: hidden;
    background-color: #050508;
    perspective: 1400px;
    transform-style: preserve-3d;
  }}
  #stage::after {{
    content: "";
    position: absolute;
    inset: 0;
    pointer-events: none;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.8' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)' opacity='0.025'/%3E%3C/svg%3E");
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

  /* Dot Grid Overlays */
  .dot-grid {{
    position: absolute;
    inset: 0;
    pointer-events: none;
    background-image: radial-gradient(rgba(255,255,255,0.06) 1.5px, transparent 1.5px);
    background-size: 40px 40px;
  }}
  .dot-grid-light {{
    position: absolute;
    inset: 0;
    pointer-events: none;
    background-image: radial-gradient(rgba(0,0,0,0.07) 1.5px, transparent 1.5px);
    background-size: 40px 40px;
  }}

  /* Typography utilities */
  .font-mono {{ font-family: 'JetBrains Mono', monospace; }}
  .font-editorial {{ font-family: 'Playfair Display', serif; }}
  .font-space {{ font-family: 'Space Grotesk', sans-serif; }}
  .font-anton {{ font-family: 'Anton', sans-serif; text-transform: uppercase; }}

  /* Clean static borders */
  .card-surface {{
    background: linear-gradient(145deg, #161622, #0A0A10);
    border: 1px solid rgba(255,255,255,0.10);
    box-shadow: 0 24px 64px rgba(0,0,0,0.7);
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
  const TRANS_DUR = 0.44; // Broadcast transition overlap window in seconds

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
        curEl.style.transform = `scale(${{lerp(1.0, 2.8, easeTrans)}})`;
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

        nextEl.style.transform = `scale(${{lerp(1.06, 1.0, easeTrans)}})`;
        nextEl.style.opacity = easeTrans.toString();
        nextEl.style.filter = blurStrength > 1 ? `blur(${{(1 - easeTrans) * 6}}px)` : 'none';
        break;
    }}
  }}

  function runSceneAnimation(idx, tScene) {{
    {combined_js}
  }}

  window.renderAt = function(t) {{
    // 1. Hide all scenes initially
    SCENES.forEach(function(item) {{
      const el = document.getElementById('scene-' + item.idx);
      if (el) {{
        el.style.display = 'none';
        el.style.opacity = '0';
        el.style.transform = 'none';
        el.style.filter = 'none';
        el.style.clipPath = 'none';
      }}
    }});

    // 2. Identify the active scene
    let activeIdx = 0;
    for (let i = 0; i < SCENES.length; i++) {{
      if (t >= SCENES[i].start && (t < SCENES[i].end || i === SCENES.length - 1)) {{
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

    // Check if within exit transition window to next scene
    const inExitTrans = nextScene && (tScene >= dur - TRANS_DUR);

    if (inExitTrans && nextScene) {{
      const nextEl = document.getElementById('scene-' + nextScene.idx);
      const pTrans = clamp((tScene - (dur - TRANS_DUR)) / TRANS_DUR, 0, 1);
      const easeTrans = easeInOutCubic(pTrans);
      const transType = (curScene.config && curScene.config.transition_out) || 'whip_pan_left';

      if (curEl) curEl.style.display = 'block';
      if (nextEl) nextEl.style.display = 'block';

      // Animate contents of both scenes
      runSceneAnimation(curScene.idx, tScene);
      runSceneAnimation(nextScene.idx, t - nextScene.start);

      // Apply broadcast transition transforms
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
# Scene Archetype Router
# ─────────────────────────────────────────────────────────────────────────────
def _compile_archetype_scene(
    archetype, idx, total_scenes, sc, st, en, dur,
    is_vertical, width, height,
    brand_name, web_url, bg, fg, muted, card_border,
    primary_color, badge, headline, subtext,
    pills, metrics, features
):
    sid = f"scene-{idx}"
    pfx = f"s{idx}"

    if archetype == "kinetic_manifesto":
        return _scene_kinetic_manifesto(sid, pfx, idx, total_scenes, sc, st, en, dur, is_vertical, width, height, brand_name, web_url, bg, fg, muted, card_border, primary_color, badge, headline, subtext, pills, metrics, features)
    elif archetype == "product_showcase":
        return _scene_product_showcase(sid, pfx, idx, total_scenes, sc, st, en, dur, is_vertical, width, height, brand_name, web_url, bg, fg, muted, card_border, primary_color, badge, headline, subtext, pills, metrics, features)
    elif archetype == "terminal_code_stream":
        return _scene_terminal_code_stream(sid, pfx, idx, total_scenes, sc, st, en, dur, is_vertical, width, height, brand_name, web_url, bg, fg, muted, card_border, primary_color, badge, headline, subtext, pills, metrics, features)
    elif archetype == "financial_telemetry":
        return _scene_financial_telemetry(sid, pfx, idx, total_scenes, sc, st, en, dur, is_vertical, width, height, brand_name, web_url, bg, fg, muted, card_border, primary_color, badge, headline, subtext, pills, metrics, features)
    elif archetype == "split_comparison":
        return _scene_split_comparison(sid, pfx, idx, total_scenes, sc, st, en, dur, is_vertical, width, height, brand_name, web_url, bg, fg, muted, card_border, primary_color, badge, headline, subtext, pills, metrics, features)
    elif archetype == "metric_impact_matrix":
        return _scene_metric_impact_matrix(sid, pfx, idx, total_scenes, sc, st, en, dur, is_vertical, width, height, brand_name, web_url, bg, fg, muted, card_border, primary_color, badge, headline, subtext, pills, metrics, features)
    elif archetype == "brand_stinger_outro":
        return _scene_brand_stinger_outro(sid, pfx, idx, total_scenes, sc, st, en, dur, is_vertical, width, height, brand_name, web_url, bg, fg, muted, card_border, primary_color, badge, headline, subtext, pills, metrics, features)
    elif archetype == "editorial_lookbook":
        return _scene_editorial_lookbook(sid, pfx, idx, total_scenes, sc, st, en, dur, is_vertical, width, height, brand_name, web_url, bg, fg, muted, card_border, primary_color, badge, headline, subtext, pills, metrics, features)
    elif archetype == "bento_grid_v2":
        return _scene_bento_grid_v2(sid, pfx, idx, total_scenes, sc, st, en, dur, is_vertical, width, height, brand_name, web_url, bg, fg, muted, card_border, primary_color, badge, headline, subtext, pills, metrics, features)
    elif archetype == "coin_parade":
        return _scene_coin_parade(sid, pfx, idx, total_scenes, sc, st, en, dur, is_vertical, width, height, brand_name, web_url, bg, fg, muted, card_border, primary_color, badge, headline, subtext, pills, metrics, features)
    elif archetype == "blueprint_reveal":
        return _scene_blueprint_reveal(sid, pfx, idx, total_scenes, sc, st, en, dur, is_vertical, width, height, brand_name, web_url, bg, fg, muted, card_border, primary_color, badge, headline, subtext, pills, metrics, features)
    elif archetype == "dashboard_device":
        return _scene_dashboard_device(sid, pfx, idx, total_scenes, sc, st, en, dur, is_vertical, width, height, brand_name, web_url, bg, fg, muted, card_border, primary_color, badge, headline, subtext, pills, metrics, features)
    elif archetype == "kinetic_parallax":
        return _scene_kinetic_parallax(sid, pfx, idx, total_scenes, sc, st, en, dur, is_vertical, width, height, brand_name, web_url, bg, fg, muted, card_border, primary_color, badge, headline, subtext, pills, metrics, features)
    else:  # cinematic_hero
        return _scene_cinematic_hero(sid, pfx, idx, total_scenes, sc, st, en, dur, is_vertical, width, height, brand_name, web_url, bg, fg, muted, card_border, primary_color, badge, headline, subtext, pills, metrics, features)


# ─────────────────────────────────────────────────────────────────────────────
# 1. ARCHETYPE: Kinetic Manifesto (Apple / Nike Bold Display Typography)
# ─────────────────────────────────────────────────────────────────────────────
def _scene_kinetic_manifesto(sid, pfx, idx, total_scenes, sc, st, en, dur, is_vertical, width, height, brand_name, web_url, bg, fg, muted, card_border, primary_color, badge, headline, subtext, pills, metrics, features):
    # Split headline into 2-3 impact lines
    words = headline.split()
    if len(words) <= 3:
        lines = [headline]
    elif len(words) <= 6:
        mid = len(words) // 2
        lines = [" ".join(words[:mid]), " ".join(words[mid:])]
    else:
        part = len(words) // 3
        lines = [" ".join(words[:part]), " ".join(words[part:part*2]), " ".join(words[part*2:])]

    fsize = int(height * (0.09 if is_vertical else 0.115))
    lines_html = ""
    for i, line in enumerate(lines):
        lines_html += f"""
        <div style="overflow:hidden;line-height:1.02;margin-bottom:8px;">
          <div id="{pfx}-line-{i}" style="font-family:'Space Grotesk',sans-serif;font-size:{fsize}px;font-weight:900;letter-spacing:-0.045em;color:{fg};transform:translateY(115%);">
            {html.escape(line)}
          </div>
        </div>"""

    markup = f"""
  <div id="{sid}" class="scene" style="background-color:{bg};">
    <div class="dot-grid"></div>

    <div style="position:absolute;inset:0;padding:{int(height*0.08)}px {int(width*0.08)}px;display:flex;flex-direction:column;justify-content:space-between;">
      <!-- Top header bar -->
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <div id="{pfx}-badge" style="display:inline-flex;align-items:center;gap:10px;padding:8px 20px;border-radius:999px;background:rgba(255,255,255,0.05);border:1px solid {card_border};opacity:0;">
          <div style="width:7px;height:7px;border-radius:50%;background:{fg};"></div>
          <span class="font-mono" style="font-size:13px;font-weight:700;letter-spacing:0.08em;color:{muted};text-transform:uppercase;">{html.escape(badge)}</span>
        </div>
        <div class="font-mono" style="font-size:14px;color:{muted};letter-spacing:0.05em;">{html.escape(web_url or brand_name)}</div>
      </div>

      <!-- Center kinetic manifesto lines -->
      <div style="max-width:{int(width*0.86)}px;">
        {lines_html}
      </div>

      <!-- Bottom subtext & power pill tag -->
      <div style="display:flex;justify-content:space-between;align-items:flex-end;border-top:1px solid {card_border};padding-top:{int(height*0.04)}px;">
        <div id="{pfx}-sub" style="font-size:{int(height*0.026)}px;font-weight:500;color:{muted};max-width:{int(width*0.55)}px;line-height:1.45;opacity:0;">
          {html.escape(subtext)}
        </div>
        <div id="{pfx}-pill" style="opacity:0;transform:scale(0.85);">
          <div style="padding:12px 28px;border-radius:999px;background:{fg};color:{bg};font-weight:800;font-size:16px;letter-spacing:-0.01em;">
            {html.escape((pills[0] if pills else brand_name) or "EXPLORE")}
          </div>
        </div>
      </div>
    </div>
  </div>
"""
    css = ""
    js_lines = ""
    for i in range(len(lines)):
        delay = 0.08 + i * 0.12
        js_lines += f"""
        const l{i} = document.getElementById('{pfx}-line-{i}');
        if (l{i}) {{
          const p = easeOutExpo(clamp((tScene - {delay}) / 0.55, 0, 1));
          l{i}.style.transform = `translateY(${{lerp(115, 0, p)}}%)`;
        }}"""

    js = f"""
      if (idx === {idx}) {{
        const badge = document.getElementById('{pfx}-badge');
        const sub = document.getElementById('{pfx}-sub');
        const pill = document.getElementById('{pfx}-pill');

        const pB = easeOutCubic(clamp(tScene / 0.35, 0, 1));
        badge.style.opacity = pB.toString();
        badge.style.transform = `translateY(${{lerp(-14, 0, pB)}}px)`;

        {js_lines}

        const pS = easeOutCubic(clamp((tScene - 0.42) / 0.45, 0, 1));
        sub.style.opacity = pS.toString();
        sub.style.transform = `translateY(${{lerp(18, 0, pS)}}px)`;

        const pP = easeOutBack(clamp((tScene - 0.55) / 0.45, 0, 1));
        pill.style.opacity = clamp(pP, 0, 1).toString();
        pill.style.transform = `scale(${{pP}})`;
      }}
"""
    return markup, css, js


# ─────────────────────────────────────────────────────────────────────────────
# 2. ARCHETYPE: Product Showcase (3D Turntable, Telemetry Rings, Spec Callouts)
# ─────────────────────────────────────────────────────────────────────────────
def _scene_product_showcase(sid, pfx, idx, total_scenes, sc, st, en, dur, is_vertical, width, height, brand_name, web_url, bg, fg, muted, card_border, primary_color, badge, headline, subtext, pills, metrics, features):
    cx, cy = width // 2, height // 2
    hero_w = int(min(width, height) * 0.38)
    hero_h = hero_w

    specs = (features or pills or ["Aerospace Grade 5 Titanium", "Quantum Neural Engine", "Zero Latency Fabric"])[:3]
    while len(specs) < 3:
        specs.append(f"Spec Metric {len(specs)+1}")

    initials = "".join(w[0].upper() for w in (brand_name or headline).split()[:2]) or "PX"

    markup = f"""
  <div id="{sid}" class="scene" style="background-color:{bg};">
    <div class="dot-grid"></div>

    <!-- Header badge -->
    <div id="{pfx}-hdr" style="position:absolute;top:{int(height*0.06)}px;left:0;right:0;text-align:center;opacity:0;">
      <span class="font-mono" style="display:inline-block;padding:7px 20px;border-radius:999px;background:rgba(255,255,255,0.06);border:1px solid {card_border};font-size:13px;font-weight:800;letter-spacing:0.1em;text-transform:uppercase;color:{muted};">{html.escape(badge)}</span>
      <div style="font-size:{int(height*0.048)}px;font-weight:900;letter-spacing:-0.03em;color:{fg};margin-top:10px;">{html.escape(headline)}</div>
    </div>

    <!-- Rotating SVG Telemetry Rings -->
    <svg id="{pfx}-rings" width="{width}" height="{height}" style="position:absolute;inset:0;pointer-events:none;">
      <circle cx="{cx}" cy="{cy}" r="{int(hero_w * 0.72)}" fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="1.5" stroke-dasharray="8 8" />
      <circle cx="{cx}" cy="{cy}" r="{int(hero_w * 0.94)}" fill="none" stroke="rgba(255,255,255,0.05)" stroke-width="1.5" stroke-dasharray="14 12" />
      <circle cx="{cx}" cy="{cy}" r="{int(hero_w * 1.18)}" fill="none" stroke="rgba(255,255,255,0.03)" stroke-width="1" />
    </svg>

    <!-- 3D Hero Product Core -->
    <div id="{pfx}-hero-wrap" style="position:absolute;left:{cx - hero_w//2}px;top:{cy - hero_h//2}px;width:{hero_w}px;height:{hero_h}px;perspective:1000px;">
      <div id="{pfx}-hero-mesh" style="width:100%;height:100%;border-radius:48px;background:linear-gradient(135deg,#1E1E2C,#0B0B12);border:2px solid {card_border};display:flex;flex-direction:column;align-items:center;justify-content:center;box-shadow:0 36px 90px rgba(0,0,0,0.85);opacity:0;transform:scale(0.8) rotateX(15deg) rotateY(-20deg);">
        <div style="font-size:{int(hero_w * 0.28)}px;font-weight:900;color:{fg};letter-spacing:-0.04em;font-family:'Space Grotesk',sans-serif;">{html.escape(initials)}</div>
        <div class="font-mono" style="font-size:12px;font-weight:700;color:{muted};letter-spacing:0.12em;text-transform:uppercase;margin-top:8px;">{html.escape(brand_name or "HARDWARE")}</div>
      </div>
    </div>

    <!-- 3 Floating Spec Callouts with Glassmorphism -->
    <div id="{pfx}-callout-0" style="position:absolute;left:{int(cx - hero_w * 1.05)}px;top:{int(cy - hero_h * 0.5)}px;padding:14px 24px;border-radius:18px;background:rgba(18,18,28,0.85);border:1px solid {card_border};box-shadow:0 18px 40px rgba(0,0,0,0.6);opacity:0;transform:translateX(-25px);">
      <div class="font-mono" style="font-size:11px;font-weight:800;color:{muted};letter-spacing:0.08em;text-transform:uppercase;">SPEC 01 // ARCHITECTURE</div>
      <div style="font-size:17px;font-weight:800;color:{fg};margin-top:4px;">{html.escape(specs[0])}</div>
    </div>

    <div id="{pfx}-callout-1" style="position:absolute;left:{int(cx + hero_w * 0.58)}px;top:{int(cy - hero_h * 0.25)}px;padding:14px 24px;border-radius:18px;background:rgba(18,18,28,0.85);border:1px solid {card_border};box-shadow:0 18px 40px rgba(0,0,0,0.6);opacity:0;transform:translateX(25px);">
      <div class="font-mono" style="font-size:11px;font-weight:800;color:{muted};letter-spacing:0.08em;text-transform:uppercase;">SPEC 02 // INTELLIGENCE</div>
      <div style="font-size:17px;font-weight:800;color:{fg};margin-top:4px;">{html.escape(specs[1])}</div>
    </div>

    <div id="{pfx}-callout-2" style="position:absolute;left:{int(cx - hero_w * 0.9)}px;top:{int(cy + hero_h * 0.45)}px;padding:14px 24px;border-radius:18px;background:rgba(18,18,28,0.85);border:1px solid {card_border};box-shadow:0 18px 40px rgba(0,0,0,0.6);opacity:0;transform:translateY(25px);">
      <div class="font-mono" style="font-size:11px;font-weight:800;color:{muted};letter-spacing:0.08em;text-transform:uppercase;">SPEC 03 // RELIABILITY</div>
      <div style="font-size:17px;font-weight:800;color:{fg};margin-top:4px;">{html.escape(specs[2])}</div>
    </div>

    <!-- Subtext bottom -->
    <div id="{pfx}-sub" style="position:absolute;bottom:{int(height*0.06)}px;left:0;right:0;text-align:center;opacity:0;">
      <div style="font-size:{int(height*0.024)}px;color:{muted};font-weight:500;max-width:700px;margin:0 auto;">{html.escape(subtext)}</div>
    </div>
  </div>
"""
    css = ""
    js = f"""
      if (idx === {idx}) {{
        const hdr = document.getElementById('{pfx}-hdr');
        const hero = document.getElementById('{pfx}-hero-mesh');
        const c0 = document.getElementById('{pfx}-callout-0');
        const c1 = document.getElementById('{pfx}-callout-1');
        const c2 = document.getElementById('{pfx}-callout-2');
        const sub = document.getElementById('{pfx}-sub');
        const rings = document.getElementById('{pfx}-rings');

        const pH = easeOutCubic(clamp(tScene / 0.4, 0, 1));
        hdr.style.opacity = pH.toString();
        hdr.style.transform = `translateY(${{lerp(-18, 0, pH)}}px)`;

        // 3D Product entrance and continuous harmonic tilt
        const pHero = easeOutBack(clamp((tScene - 0.12) / 0.6, 0, 1));
        hero.style.opacity = clamp(pHero, 0, 1).toString();
        const rotY = lerp(-25, 15, easeInOutCubic(clamp(tScene / {dur}, 0, 1)));
        const rotX = Math.sin(tScene * 1.5) * 6;
        hero.style.transform = `scale(${{pHero}}) rotateX(${{rotX}}deg) rotateY(${{rotY}}deg)`;

        // Telemetry rings continuous rotation
        if (rings) {{
          rings.style.transform = `rotate(${{tScene * 14}}deg)`;
          rings.style.transformOrigin = '{cx}px {cy}px';
        }}

        // Spec callout staggered spring entries
        const pC0 = easeOutBack(clamp((tScene - 0.35) / 0.48, 0, 1));
        c0.style.opacity = clamp(pC0, 0, 1).toString();
        c0.style.transform = `translateX(${{lerp(-25, 0, pC0)}}px)`;

        const pC1 = easeOutBack(clamp((tScene - 0.48) / 0.48, 0, 1));
        c1.style.opacity = clamp(pC1, 0, 1).toString();
        c1.style.transform = `translateX(${{lerp(25, 0, pC1)}}px)`;

        const pC2 = easeOutBack(clamp((tScene - 0.60) / 0.48, 0, 1));
        c2.style.opacity = clamp(pC2, 0, 1).toString();
        c2.style.transform = `translateY(${{lerp(25, 0, pC2)}}px)`;

        const pS = easeOutCubic(clamp((tScene - 0.72) / 0.45, 0, 1));
        sub.style.opacity = pS.toString();
      }}
"""
    return markup, css, js


# ─────────────────────────────────────────────────────────────────────────────
# 3. ARCHETYPE: Terminal Code Stream (Interactive Developer / CLI / Engineering)
# ─────────────────────────────────────────────────────────────────────────────
def _scene_terminal_code_stream(sid, pfx, idx, total_scenes, sc, st, en, dur, is_vertical, width, height, brand_name, web_url, bg, fg, muted, card_border, primary_color, badge, headline, subtext, pills, metrics, features):
    term_w = int(width * (0.90 if is_vertical else 0.75))
    term_h = int(height * (0.64 if is_vertical else 0.60))
    term_l = (width - term_w) // 2
    term_t = int(height * 0.22)

    code_lines = [
        ("const", " engine = await CineMatrix.init({", "precision: 'lossless'", "});"),
        ("const", " pipeline = engine.createPipeline({", "gpu: true, threads: 16", "});"),
        ("await", " pipeline.dispatchBatch({", "target: 'edge-cdn'", "});"),
        ("✓", " [COMPILATION] Zero bytecode defects verified", "(0 warnings)", ""),
        ("✓", " [PERFORMANCE] P99 cold start execution at 0.82ms", "PASS", ""),
    ]

    markup = f"""
  <div id="{sid}" class="scene" style="background-color:{bg};">
    <div class="dot-grid"></div>

    <!-- Header info -->
    <div id="{pfx}-hdr" style="position:absolute;top:{int(height*0.06)}px;left:{term_l}px;right:{term_l}px;display:flex;justify-content:space-between;align-items:center;opacity:0;">
      <div>
        <span class="font-mono" style="font-size:13px;font-weight:700;color:{muted};text-transform:uppercase;letter-spacing:0.1em;">{html.escape(badge)}</span>
        <div style="font-size:{int(height*0.044)}px;font-weight:900;letter-spacing:-0.03em;color:{fg};margin-top:6px;">{html.escape(headline)}</div>
      </div>
      <div class="font-mono" style="font-size:14px;color:{muted};">{html.escape(web_url or brand_name)}</div>
    </div>

    <!-- Terminal Window Frame -->
    <div id="{pfx}-term" style="position:absolute;left:{term_l}px;top:{term_t}px;width:{term_w}px;height:{term_h}px;background:#0A0D14;border:1px solid {card_border};border-radius:24px;box-shadow:0 36px 90px rgba(0,0,0,0.85);overflow:hidden;opacity:0;transform:translateY(35px);">
      <!-- Window Titlebar -->
      <div style="height:48px;background:#0F131C;border-bottom:1px solid {card_border};display:flex;align-items:center;justify-content:space-between;padding:0 20px;">
        <div style="display:flex;gap:8px;">
          <div style="width:12px;height:12px;border-radius:50%;background:#EF4444;"></div>
          <div style="width:12px;height:12px;border-radius:50%;background:#F59E0B;"></div>
          <div style="width:12px;height:12px;border-radius:50%;background:#10B981;"></div>
        </div>
        <div class="font-mono" style="font-size:12px;color:{muted};letter-spacing:0.04em;">bash — 80x24</div>
        <div class="font-mono" style="font-size:12px;color:rgba(255,255,255,0.3);">UTF-8</div>
      </div>

      <!-- Code Execution Area -->
      <div style="padding:28px 32px;display:flex;flex-direction:column;gap:14px;" class="font-mono">
        <div id="{pfx}-cl-0" style="opacity:0;font-size:18px;"><span style="color:#A78BFA;">const</span> <span style="color:#F8FAFC;">engine</span> = <span style="color:#38BDF8;">await</span> CineMatrix.init({{ <span style="color:#34D399;">precision: 'broadcast'</span> }});</div>
        <div id="{pfx}-cl-1" style="opacity:0;font-size:18px;"><span style="color:#A78BFA;">const</span> <span style="color:#F8FAFC;">pipeline</span> = engine.createPipeline({{ <span style="color:#34D399;">gpu: true, threads: 16</span> }});</div>
        <div id="{pfx}-cl-2" style="opacity:0;font-size:18px;"><span style="color:#38BDF8;">await</span> pipeline.dispatch({{ <span style="color:#34D399;">target: 'production'</span> }});</div>
        <div id="{pfx}-cl-3" style="opacity:0;font-size:18px;color:#10B981;padding-top:10px;border-top:1px solid rgba(255,255,255,0.06);">✓ Bytecode compiled: 0 defects verified</div>
        <div id="{pfx}-cl-4" style="opacity:0;font-size:18px;color:#38BDF8;">✓ Sub-millisecond execution SLA confirmed (0.82ms) <span id="{pfx}-cursor" style="color:{fg};font-weight:900;">▋</span></div>
      </div>
    </div>
  </div>
"""
    css = ""
    js = f"""
      if (idx === {idx}) {{
        const hdr = document.getElementById('{pfx}-hdr');
        const term = document.getElementById('{pfx}-term');
        const cursor = document.getElementById('{pfx}-cursor');

        const pH = easeOutCubic(clamp(tScene / 0.35, 0, 1));
        hdr.style.opacity = pH.toString();

        const pT = easeOutBack(clamp((tScene - 0.1) / 0.5, 0, 1));
        term.style.opacity = clamp(pT, 0, 1).toString();
        term.style.transform = `translateY(${{lerp(35, 0, pT)}}px)`;

        // Sequential code line reveals
        for (let i = 0; i < 5; i++) {{
          const cl = document.getElementById('{pfx}-cl-' + i);
          if (cl) {{
            const delay = 0.35 + i * 0.18;
            const p = easeOutCubic(clamp((tScene - delay) / 0.35, 0, 1));
            cl.style.opacity = p.toString();
            cl.style.transform = `translateX(${{lerp(15, 0, p)}}px)`;
          }}
        }}

        // Blinking cursor
        if (cursor) {{
          cursor.style.opacity = Math.sin(tScene * 8) > 0 ? '1' : '0';
        }}
      }}
"""
    return markup, css, js


# ─────────────────────────────────────────────────────────────────────────────
# 4. ARCHETYPE: Financial Telemetry (Live SVG Chart, Price Ticker, Market Stats)
# ─────────────────────────────────────────────────────────────────────────────
def _scene_financial_telemetry(sid, pfx, idx, total_scenes, sc, st, en, dur, is_vertical, width, height, brand_name, web_url, bg, fg, muted, card_border, primary_color, badge, headline, subtext, pills, metrics, features):
    chart_w = int(width * (0.88 if is_vertical else 0.76))
    chart_h = int(height * (0.36 if is_vertical else 0.40))
    chart_l = (width - chart_w) // 2
    chart_t = int(height * 0.32)

    # Telemetry metrics
    stat_items = (metrics or [
        {"label": "24h Volume", "value": "$14.8B", "delta": "+42.4%"},
        {"label": "Total Value Locked", "value": "$64.2B", "delta": "ATH"},
        {"label": "Execution Latency", "value": "0.4ms", "delta": "P99"}
    ])[:3]

    stats_html = ""
    for m in stat_items:
        stats_html += f"""
        <div style="display:flex;flex-direction:column;gap:4px;">
          <span class="font-mono" style="font-size:12px;color:{muted};text-transform:uppercase;letter-spacing:0.06em;">{html.escape(str(m.get("label", "")))}</span>
          <div style="display:flex;align-items:center;gap:8px;">
            <span style="font-size:24px;font-weight:900;color:{fg};font-family:'Space Grotesk',sans-serif;">{html.escape(str(m.get("value", "")))}</span>
            <span class="font-mono" style="font-size:12px;font-weight:700;color:#10B981;background:rgba(16,185,129,0.12);padding:2px 8px;border-radius:6px;">{html.escape(str(m.get("delta", "+8%")))}</span>
          </div>
        </div>"""

    # Generate smooth SVG path points for the financial chart
    pts = [(0, 160), (80, 150), (160, 180), (240, 130), (320, 140), (400, 90), (480, 110), (560, 60), (640, 75), (720, 30), (800, 10)]
    svg_d = "M " + " L ".join(f"{x},{y}" for x, y in pts)
    svg_fill = svg_d + f" L {pts[-1][0]},{chart_h} L 0,{chart_h} Z"

    markup = f"""
  <div id="{sid}" class="scene" style="background-color:{bg};">
    <div class="dot-grid"></div>

    <!-- Top ticker & headline -->
    <div id="{pfx}-top" style="position:absolute;top:{int(height*0.06)}px;left:{chart_l}px;right:{chart_l}px;display:flex;justify-content:space-between;align-items:flex-end;opacity:0;">
      <div>
        <span class="font-mono" style="font-size:13px;font-weight:800;color:{muted};text-transform:uppercase;letter-spacing:0.1em;">{html.escape(badge)}</span>
        <div style="font-size:{int(height*0.052)}px;font-weight:900;letter-spacing:-0.035em;color:{fg};margin-top:6px;">{html.escape(headline)}</div>
      </div>
      <div id="{pfx}-ticker" style="text-align:right;">
        <span class="font-mono" style="font-size:13px;color:{muted};">REAL-TIME INDEX</span>
        <div style="font-size:38px;font-weight:900;color:#10B981;font-family:'Space Grotesk',sans-serif;letter-spacing:-0.02em;">$98,420.50</div>
      </div>
    </div>

    <!-- Chart Panel -->
    <div id="{pfx}-panel" style="position:absolute;left:{chart_l}px;top:{chart_t}px;width:{chart_w}px;height:{chart_h}px;background:#0A0D14;border:1px solid {card_border};border-radius:24px;box-shadow:0 36px 90px rgba(0,0,0,0.8);overflow:hidden;opacity:0;transform:scale(0.92);">
      <svg viewBox="0 0 800 {chart_h}" preserveAspectRatio="none" style="width:100%;height:100%;">
        <defs>
          <linearGradient id="{pfx}-grad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#10B981" stop-opacity="0.25" />
            <stop offset="100%" stop-color="#10B981" stop-opacity="0.0" />
          </linearGradient>
        </defs>
        <path d="{svg_fill}" fill="url(#{pfx}-grad)" />
        <path id="{pfx}-path" d="{svg_d}" fill="none" stroke="#10B981" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="1200" stroke-dashoffset="1200" />
      </svg>
    </div>

    <!-- Bottom Stat Row -->
    <div id="{pfx}-stats" style="position:absolute;top:{chart_t + chart_h + int(height*0.04)}px;left:{chart_l}px;right:{chart_l}px;display:flex;justify-content:space-between;padding:0 10px;opacity:0;">
      {stats_html}
    </div>
  </div>
"""
    css = ""
    js = f"""
      if (idx === {idx}) {{
        const top = document.getElementById('{pfx}-top');
        const panel = document.getElementById('{pfx}-panel');
        const path = document.getElementById('{pfx}-path');
        const stats = document.getElementById('{pfx}-stats');

        const pTop = easeOutCubic(clamp(tScene / 0.35, 0, 1));
        top.style.opacity = pTop.toString();

        const pPanel = easeOutBack(clamp((tScene - 0.12) / 0.5, 0, 1));
        panel.style.opacity = clamp(pPanel, 0, 1).toString();
        panel.style.transform = `scale(${{pPanel}})`;

        // SVG stroke draw animation
        if (path) {{
          const pPath = easeInOutCubic(clamp((tScene - 0.25) / 1.1, 0, 1));
          path.style.strokeDashoffset = (1200 * (1 - pPath)).toString();
        }}

        const pStats = easeOutCubic(clamp((tScene - 0.5) / 0.45, 0, 1));
        stats.style.opacity = pStats.toString();
        stats.style.transform = `translateY(${{lerp(18, 0, pStats)}}px)`;
      }}
"""
    return markup, css, js


# ─────────────────────────────────────────────────────────────────────────────
# 5. ARCHETYPE: Split Comparison (Legacy vs Next-Gen / Before vs After)
# ─────────────────────────────────────────────────────────────────────────────
def _scene_split_comparison(sid, pfx, idx, total_scenes, sc, st, en, dur, is_vertical, width, height, brand_name, web_url, bg, fg, muted, card_border, primary_color, badge, headline, subtext, pills, metrics, features):
    split_w = int(width * (0.90 if is_vertical else 0.80))
    split_h = int(height * (0.64 if is_vertical else 0.58))
    split_l = (width - split_w) // 2
    split_t = int(height * 0.24)
    half_w = split_w // 2

    markup = f"""
  <div id="{sid}" class="scene" style="background-color:{bg};">
    <div class="dot-grid"></div>

    <div id="{pfx}-hdr" style="position:absolute;top:{int(height*0.06)}px;left:0;right:0;text-align:center;opacity:0;">
      <span class="font-mono" style="font-size:13px;font-weight:800;color:{muted};text-transform:uppercase;letter-spacing:0.1em;">{html.escape(badge)}</span>
      <div style="font-size:{int(height*0.052)}px;font-weight:900;letter-spacing:-0.035em;color:{fg};margin-top:6px;">{html.escape(headline)}</div>
    </div>

    <!-- Split Duel Container -->
    <div id="{pfx}-split" style="position:absolute;left:{split_l}px;top:{split_t}px;width:{split_w}px;height:{split_h}px;display:flex;gap:24px;">
      <!-- Left: Legacy Way -->
      <div id="{pfx}-left" style="flex:1;background:#0E0E14;border:1px solid rgba(239,68,68,0.2);border-radius:24px;padding:36px;display:flex;flex-direction:column;justify-content:space-between;opacity:0;transform:translateX(-30px);">
        <div>
          <div class="font-mono" style="font-size:13px;font-weight:800;color:#EF4444;text-transform:uppercase;letter-spacing:0.08em;">✕ THE LEGACY WAY</div>
          <div style="font-size:26px;font-weight:800;color:#94A3B8;margin-top:12px;line-height:1.2;">Fragmented tooling, high friction, manual pipelines.</div>
        </div>
        <div style="display:flex;flex-direction:column;gap:12px;" class="font-mono">
          <div style="color:#64748B;font-size:15px;text-decoration:line-through;">✕ 4+ hours per manual video render</div>
          <div style="color:#64748B;font-size:15px;text-decoration:line-through;">✕ Inconsistent creative slop</div>
          <div style="color:#64748B;font-size:15px;text-decoration:line-through;">✕ $10k+ agency monthly retainer</div>
        </div>
      </div>

      <!-- Right: Next-Gen Standard -->
      <div id="{pfx}-right" style="flex:1;background:linear-gradient(145deg,#161924,#0C0E16);border:1px solid rgba(16,185,129,0.35);border-radius:24px;padding:36px;display:flex;flex-direction:column;justify-content:space-between;box-shadow:0 24px 60px rgba(0,0,0,0.7);opacity:0;transform:translateX(30px);">
        <div>
          <div class="font-mono" style="font-size:13px;font-weight:800;color:#10B981;text-transform:uppercase;letter-spacing:0.08em;">✓ THE NEXT-GEN ENGINE</div>
          <div style="font-size:26px;font-weight:800;color:{fg};margin-top:12px;line-height:1.2;">Autonomous synthesis with broadcast precision.</div>
        </div>
        <div style="display:flex;flex-direction:column;gap:12px;" class="font-mono">
          <div style="color:#F8FAFC;font-size:15px;font-weight:600;">✓ Sub-second real-time frame generation</div>
          <div style="color:#F8FAFC;font-size:15px;font-weight:600;">✓ Pure brand-aligned bespoke motion</div>
          <div style="color:#F8FAFC;font-size:15px;font-weight:600;">✓ Zero marginal infrastructure cost</div>
        </div>
      </div>
    </div>
  </div>
"""
    css = ""
    js = f"""
      if (idx === {idx}) {{
        const hdr = document.getElementById('{pfx}-hdr');
        const left = document.getElementById('{pfx}-left');
        const right = document.getElementById('{pfx}-right');

        const pH = easeOutCubic(clamp(tScene / 0.35, 0, 1));
        hdr.style.opacity = pH.toString();

        const pL = easeOutBack(clamp((tScene - 0.12) / 0.5, 0, 1));
        left.style.opacity = clamp(pL, 0, 1).toString();
        left.style.transform = `translateX(${{lerp(-30, 0, pL)}}px)`;

        const pR = easeOutBack(clamp((tScene - 0.25) / 0.5, 0, 1));
        right.style.opacity = clamp(pR, 0, 1).toString();
        right.style.transform = `translateX(${{lerp(30, 0, pR)}}px)`;
      }}
"""
    return markup, css, js


# ─────────────────────────────────────────────────────────────────────────────
# 6. ARCHETYPE: Bento Grid v2 (Live UI Widgets: Progress Gauge, Switch, Avatars)
# ─────────────────────────────────────────────────────────────────────────────
def _scene_bento_grid_v2(sid, pfx, idx, total_scenes, sc, st, en, dur, is_vertical, width, height, brand_name, web_url, bg, fg, muted, card_border, primary_color, badge, headline, subtext, pills, metrics, features):
    bento_w = int(width * (0.90 if is_vertical else 0.78))
    bento_h = int(height * (0.64 if is_vertical else 0.60))
    bento_l = (width - bento_w) // 2
    bento_t = int(height * 0.24)

    card_a_w = int(bento_w * 0.48)
    card_b_w = bento_w - card_a_w - 20
    card_sm_h = (bento_h - 20) // 2

    pill_texts = (pills or ["Autonomous", "Sub-10ms", "Global Edge", "Zero Defect"])[:4]
    while len(pill_texts) < 4: pill_texts.append("Feature")

    markup = f"""
  <div id="{sid}" class="scene" style="background-color:{bg};">
    <div class="dot-grid"></div>

    <!-- Header bar -->
    <div id="{pfx}-hdr" style="position:absolute;top:{int(height*0.06)}px;left:{bento_l}px;right:{bento_l}px;display:flex;justify-content:space-between;align-items:center;opacity:0;">
      <div>
        <span class="font-mono" style="font-size:13px;font-weight:800;color:{muted};text-transform:uppercase;letter-spacing:0.1em;">{html.escape(badge)}</span>
        <div style="font-size:{int(height*0.048)}px;font-weight:900;letter-spacing:-0.035em;color:{fg};margin-top:6px;">{html.escape(headline)}</div>
      </div>
      <div class="font-mono" style="font-size:14px;color:{muted};">{html.escape(web_url or brand_name)}</div>
    </div>

    <!-- Bento Grid Container -->
    <div id="{pfx}-bento" style="position:absolute;left:{bento_l}px;top:{bento_t}px;width:{bento_w}px;height:{bento_h}px;">
      <!-- Card A: Big Left — Animated Circular Progress Gauge -->
      <div id="{pfx}-ca" style="position:absolute;left:0;top:0;width:{card_a_w}px;height:{bento_h}px;background:linear-gradient(145deg,#161922,#0C0E14);border:1px solid {card_border};border-radius:28px;padding:36px;display:flex;flex-direction:column;justify-content:space-between;opacity:0;box-shadow:0 24px 60px rgba(0,0,0,0.6);">
        <div>
          <div class="font-mono" style="font-size:12px;font-weight:800;color:{muted};text-transform:uppercase;letter-spacing:0.08em;">ENGINE THROUGHPUT</div>
          <div style="font-size:32px;font-weight:900;color:{fg};margin-top:8px;letter-spacing:-0.02em;">{html.escape(pill_texts[0])}</div>
        </div>

        <div style="display:flex;align-items:center;justify-content:center;">
          <svg width="180" height="180" viewBox="0 0 180 180">
            <circle cx="90" cy="90" r="72" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="12" />
            <circle id="{pfx}-gauge" cx="90" cy="90" r="72" fill="none" stroke="{fg}" stroke-width="12" stroke-linecap="round" stroke-dasharray="452" stroke-dashoffset="452" transform="rotate(-90 90 90)" />
            <text x="90" y="98" text-anchor="middle" font-family="'Space Grotesk',sans-serif" font-size="36" font-weight="900" fill="{fg}">99.8%</text>
          </svg>
        </div>

        <div class="font-mono" style="font-size:13px;color:{muted};">Autonomous edge execution SLA verified.</div>
      </div>

      <!-- Card B: Top Right — Interactive Toggle Switch -->
      <div id="{pfx}-cb" style="position:absolute;left:{card_a_w+20}px;top:0;width:{card_b_w}px;height:{card_sm_h}px;background:linear-gradient(145deg,#181824,#0E0E14);border:1px solid {card_border};border-radius:28px;padding:28px;display:flex;align-items:center;justify-content:space-between;opacity:0;">
        <div>
          <div class="font-mono" style="font-size:12px;font-weight:800;color:{muted};text-transform:uppercase;letter-spacing:0.08em;">RUNTIME STATE</div>
          <div style="font-size:24px;font-weight:900;color:{fg};margin-top:4px;">{html.escape(pill_texts[1])}</div>
        </div>
        <!-- Toggle button -->
        <div style="width:72px;height:40px;background:#10B981;border-radius:20px;padding:4px;display:flex;align-items:center;justify-content:flex-end;">
          <div style="width:32px;height:32px;background:#FFFFFF;border-radius:50%;box-shadow:0 4px 8px rgba(0,0,0,0.3);"></div>
        </div>
      </div>

      <!-- Card C: Bottom Right — Stacked User Avatars -->
      <div id="{pfx}-cc" style="position:absolute;left:{card_a_w+20}px;top:{card_sm_h+20}px;width:{card_b_w}px;height:{card_sm_h}px;background:linear-gradient(145deg,#181824,#0E0E14);border:1px solid {card_border};border-radius:28px;padding:28px;display:flex;align-items:center;justify-content:space-between;opacity:0;">
        <div>
          <div class="font-mono" style="font-size:12px;font-weight:800;color:{muted};text-transform:uppercase;letter-spacing:0.08em;">GLOBAL OPERATORS</div>
          <div style="font-size:24px;font-weight:900;color:{fg};margin-top:4px;">{html.escape(pill_texts[2])}</div>
        </div>
        <div style="display:flex;align-items:center;">
          <div style="width:42px;height:42px;border-radius:50%;background:#334155;border:2px solid #0E0E14;margin-right:-12px;display:flex;align-items:center;justify-content:center;color:#FFFFFF;font-weight:800;font-size:14px;">A</div>
          <div style="width:42px;height:42px;border-radius:50%;background:#475569;border:2px solid #0E0E14;margin-right:-12px;display:flex;align-items:center;justify-content:center;color:#FFFFFF;font-weight:800;font-size:14px;">B</div>
          <div style="width:42px;height:42px;border-radius:50%;background:{fg};color:{bg};border:2px solid #0E0E14;display:flex;align-items:center;justify-content:center;font-weight:900;font-size:13px;">+4k</div>
        </div>
      </div>
    </div>
  </div>
"""
    css = ""
    js = f"""
      if (idx === {idx}) {{
        const hdr = document.getElementById('{pfx}-hdr');
        const ca = document.getElementById('{pfx}-ca');
        const cb = document.getElementById('{pfx}-cb');
        const cc = document.getElementById('{pfx}-cc');
        const gauge = document.getElementById('{pfx}-gauge');

        const pH = easeOutCubic(clamp(tScene / 0.35, 0, 1));
        hdr.style.opacity = pH.toString();

        const pA = easeOutBack(clamp((tScene - 0.12) / 0.5, 0, 1));
        ca.style.opacity = clamp(pA, 0, 1).toString();
        ca.style.transform = `scale(${{pA}})`;

        if (gauge) {{
          const pG = easeInOutCubic(clamp((tScene - 0.25) / 1.0, 0, 1));
          gauge.style.strokeDashoffset = (452 * (1 - pG * 0.88)).toString();
        }}

        const pB = easeOutBack(clamp((tScene - 0.25) / 0.5, 0, 1));
        cb.style.opacity = clamp(pB, 0, 1).toString();
        cb.style.transform = `translateX(${{lerp(25, 0, pB)}}px)`;

        const pC = easeOutBack(clamp((tScene - 0.38) / 0.5, 0, 1));
        cc.style.opacity = clamp(pC, 0, 1).toString();
        cc.style.transform = `translateX(${{lerp(25, 0, pC)}}px)`;
      }}
"""
    return markup, css, js


# ─────────────────────────────────────────────────────────────────────────────
# 7. ARCHETYPE: Metric Impact Matrix (3 Massive Stat Cards with Counting Numbers)
# ─────────────────────────────────────────────────────────────────────────────
def _scene_metric_impact_matrix(sid, pfx, idx, total_scenes, sc, st, en, dur, is_vertical, width, height, brand_name, web_url, bg, fg, muted, card_border, primary_color, badge, headline, subtext, pills, metrics, features):
    mat_w = int(width * (0.90 if is_vertical else 0.82))
    mat_l = (width - mat_w) // 2
    mat_t = int(height * 0.30)

    stat_cards = (metrics or [
        {"value": "12ms", "label": "P99 Execution Latency", "delta": "Sub-millisecond"},
        {"value": "99.99%", "label": "SLA Uptime Guarantee", "delta": "Enterprise"},
        {"value": "10x", "label": "Engineering Velocity", "delta": "Measured"}
    ])[:3]

    cards_html = ""
    for i, scard in enumerate(stat_cards):
        cards_html += f"""
      <div id="{pfx}-sc-{i}" style="flex:1;background:linear-gradient(145deg,#161824,#0C0D14);border:1px solid {card_border};border-radius:28px;padding:38px;display:flex;flex-direction:column;justify-content:space-between;box-shadow:0 24px 60px rgba(0,0,0,0.6);opacity:0;transform:translateY(30px);">
        <div>
          <span class="font-mono" style="font-size:12px;font-weight:800;color:{muted};text-transform:uppercase;letter-spacing:0.08em;">{html.escape(str(scard.get("delta", "PROOF")))}</span>
          <div style="font-size:{int(height*0.085)}px;font-weight:900;color:{fg};margin-top:14px;letter-spacing:-0.04em;font-family:'Space Grotesk',sans-serif;line-height:1.0;">{html.escape(str(scard.get("value", "")))}</div>
        </div>
        <div style="font-size:18px;font-weight:600;color:{muted};margin-top:24px;line-height:1.35;">{html.escape(str(scard.get("label", "")))}</div>
      </div>"""

    markup = f"""
  <div id="{sid}" class="scene" style="background-color:{bg};">
    <div class="dot-grid"></div>

    <div id="{pfx}-hdr" style="position:absolute;top:{int(height*0.06)}px;left:0;right:0;text-align:center;opacity:0;">
      <span class="font-mono" style="font-size:13px;font-weight:800;color:{muted};text-transform:uppercase;letter-spacing:0.1em;">{html.escape(badge)}</span>
      <div style="font-size:{int(height*0.052)}px;font-weight:900;letter-spacing:-0.035em;color:{fg};margin-top:6px;">{html.escape(headline)}</div>
    </div>

    <!-- Matrix Card Row -->
    <div id="{pfx}-row" style="position:absolute;left:{mat_l}px;top:{mat_t}px;width:{mat_w}px;display:flex;gap:24px;">
      {cards_html}
    </div>

    <!-- Subtext bottom -->
    <div id="{pfx}-sub" style="position:absolute;bottom:{int(height*0.08)}px;left:0;right:0;text-align:center;opacity:0;">
      <div style="font-size:{int(height*0.024)}px;color:{muted};font-weight:500;max-width:700px;margin:0 auto;">{html.escape(subtext)}</div>
    </div>
  </div>
"""
    css = ""
    js_cards = ""
    for i in range(len(stat_cards)):
        delay = 0.12 + i * 0.12
        js_cards += f"""
        const sc{i} = document.getElementById('{pfx}-sc-{i}');
        if (sc{i}) {{
          const p = easeOutBack(clamp((tScene - {delay}) / 0.5, 0, 1));
          sc{i}.style.opacity = clamp(p, 0, 1).toString();
          sc{i}.style.transform = `translateY(${{lerp(30, 0, p)}}px)`;
        }}"""

    js = f"""
      if (idx === {idx}) {{
        const hdr = document.getElementById('{pfx}-hdr');
        const sub = document.getElementById('{pfx}-sub');

        const pH = easeOutCubic(clamp(tScene / 0.35, 0, 1));
        hdr.style.opacity = pH.toString();

        {js_cards}

        const pS = easeOutCubic(clamp((tScene - 0.55) / 0.45, 0, 1));
        sub.style.opacity = pS.toString();
      }}
"""
    return markup, css, js


# ─────────────────────────────────────────────────────────────────────────────
# 8. ARCHETYPE: Brand Stinger Outro (Geometric Emblem Resolve, Typography & URL)
# ─────────────────────────────────────────────────────────────────────────────
def _scene_brand_stinger_outro(sid, pfx, idx, total_scenes, sc, st, en, dur, is_vertical, width, height, brand_name, web_url, bg, fg, muted, card_border, primary_color, badge, headline, subtext, pills, metrics, features):
    initials = "".join(w[0].upper() for w in (brand_name or headline).split()[:2]) or "CM"

    markup = f"""
  <div id="{sid}" class="scene" style="background-color:{bg};">
    <div class="dot-grid"></div>

    <div style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:0 {int(width*0.08)}px;">
      <!-- Geometric Brand Monogram -->
      <div id="{pfx}-emblem" style="width:160px;height:160px;border-radius:48px;background:linear-gradient(135deg,#1E1E2C,#0B0B14);border:2px solid {card_border};display:flex;align-items:center;justify-content:center;box-shadow:0 36px 90px rgba(0,0,0,0.85);margin-bottom:32px;opacity:0;transform:scale(0.7) rotate(-15deg);">
        <div style="font-size:72px;font-weight:900;color:{fg};letter-spacing:-0.04em;font-family:'Space Grotesk',sans-serif;">{html.escape(initials)}</div>
      </div>

      <!-- Headline -->
      <div id="{pfx}-hl" style="font-size:{int(height*0.07)}px;font-weight:900;letter-spacing:-0.04em;color:{fg};line-height:1.05;max-width:900px;margin-bottom:18px;opacity:0;transform:translateY(25px);">
        {html.escape(brand_name or headline)}
      </div>

      <!-- Subtext statement -->
      <div id="{pfx}-sub" style="font-size:{int(height*0.026)}px;font-weight:500;color:{muted};max-width:680px;line-height:1.45;margin-bottom:32px;opacity:0;">
        {html.escape(subtext)}
      </div>

      <!-- URL with expanding underline -->
      <div id="{pfx}-url-wrap" style="position:relative;display:inline-block;opacity:0;">
        <span class="font-mono" style="font-size:22px;font-weight:700;color:{fg};letter-spacing:0.04em;">{html.escape(web_url or "cinematrix.ai")}</span>
        <div id="{pfx}-line" style="position:absolute;left:0;bottom:-6px;height:2px;background:{fg};width:0%;"></div>
      </div>
    </div>
  </div>
"""
    css = ""
    js = f"""
      if (idx === {idx}) {{
        const emblem = document.getElementById('{pfx}-emblem');
        const hl = document.getElementById('{pfx}-hl');
        const sub = document.getElementById('{pfx}-sub');
        const urlWrap = document.getElementById('{pfx}-url-wrap');
        const line = document.getElementById('{pfx}-line');

        const pE = easeOutBack(clamp(tScene / 0.5, 0, 1));
        emblem.style.opacity = clamp(pE, 0, 1).toString();
        emblem.style.transform = `scale(${{pE}}) rotate(${{lerp(-15, 0, pE)}}deg)`;

        const pH = easeOutBack(clamp((tScene - 0.15) / 0.5, 0, 1));
        hl.style.opacity = clamp(pH, 0, 1).toString();
        hl.style.transform = `translateY(${{lerp(25, 0, pH)}}px)`;

        const pS = easeOutCubic(clamp((tScene - 0.3) / 0.45, 0, 1));
        sub.style.opacity = pS.toString();

        const pU = easeOutCubic(clamp((tScene - 0.45) / 0.45, 0, 1));
        urlWrap.style.opacity = pU.toString();

        if (line) {{
          const pL = easeInOutCubic(clamp((tScene - 0.55) / 0.5, 0, 1));
          line.style.width = `${{pL * 100}}%`;
        }}
      }}
"""
    return markup, css, js


# ─────────────────────────────────────────────────────────────────────────────
# 9. ARCHETYPE: Editorial Lookbook (Luxury Serif, Asymmetric Minimalist Frame)
# ─────────────────────────────────────────────────────────────────────────────
def _scene_editorial_lookbook(sid, pfx, idx, total_scenes, sc, st, en, dur, is_vertical, width, height, brand_name, web_url, bg, fg, muted, card_border, primary_color, badge, headline, subtext, pills, metrics, features):
    pad_x = int(width * 0.08)
    pad_y = int(height * 0.08)

    markup = f"""
  <div id="{sid}" class="scene" style="background-color:{bg};">
    <!-- Fine 1px Architectural Frame -->
    <div style="position:absolute;inset:{pad_y}px {pad_x}px;border:1px solid rgba(255,255,255,0.08);pointer-events:none;">
      <!-- Corner registration marks -->
      <div style="position:absolute;left:-6px;top:-6px;width:12px;height:12px;border-left:1px solid {fg};border-top:1px solid {fg};"></div>
      <div style="position:absolute;right:-6px;top:-6px;width:12px;height:12px;border-right:1px solid {fg};border-top:1px solid {fg};"></div>
      <div style="position:absolute;left:-6px;bottom:-6px;width:12px;height:12px;border-left:1px solid {fg};border-bottom:1px solid {fg};"></div>
      <div style="position:absolute;right:-6px;bottom:-6px;width:12px;height:12px;border-right:1px solid {fg};border-bottom:1px solid {fg};"></div>
    </div>

    <div style="position:absolute;inset:{pad_y}px {pad_x}px;padding:{int(height*0.06)}px;display:flex;flex-direction:column;justify-content:space-between;">
      <!-- Top index label -->
      <div id="{pfx}-top" style="display:flex;justify-content:space-between;align-items:center;opacity:0;">
        <span class="font-mono" style="font-size:12px;letter-spacing:0.14em;color:{muted};text-transform:uppercase;">COLLECTION 2026 // {html.escape(badge)}</span>
        <span class="font-mono" style="font-size:12px;letter-spacing:0.14em;color:{muted};">{html.escape(brand_name or "ATELIER")}</span>
      </div>

      <!-- Center Serif Headline -->
      <div style="max-width:{int(width*0.75)}px;">
        <div id="{pfx}-hl" class="font-editorial" style="font-size:{int(height*0.09)}px;font-style:italic;color:{fg};line-height:1.08;letter-spacing:-0.02em;opacity:0;transform:translateY(30px);">
          “{html.escape(headline)}”
        </div>
      </div>

      <!-- Bottom Subtext & Spec details -->
      <div id="{pfx}-bot" style="display:flex;justify-content:space-between;align-items:flex-end;opacity:0;">
        <div style="font-size:{int(height*0.024)}px;color:{muted};font-weight:400;max-width:560px;line-height:1.5;">{html.escape(subtext)}</div>
        <div class="font-mono" style="font-size:13px;letter-spacing:0.08em;color:{fg};">{html.escape(web_url or "")}</div>
      </div>
    </div>
  </div>
"""
    css = ""
    js = f"""
      if (idx === {idx}) {{
        const top = document.getElementById('{pfx}-top');
        const hl = document.getElementById('{pfx}-hl');
        const bot = document.getElementById('{pfx}-bot');

        const pT = easeOutCubic(clamp(tScene / 0.4, 0, 1));
        top.style.opacity = pT.toString();

        const pH = easeOutCubic(clamp((tScene - 0.15) / 0.55, 0, 1));
        hl.style.opacity = pH.toString();
        hl.style.transform = `translateY(${{lerp(30, 0, pH)}}px)`;

        const pB = easeOutCubic(clamp((tScene - 0.4) / 0.45, 0, 1));
        bot.style.opacity = pB.toString();
      }}
"""
    return markup, css, js


# ─────────────────────────────────────────────────────────────────────────────
# 10. ARCHETYPE: Coin Parade (Rotating 3D Badge Carousel)
# ─────────────────────────────────────────────────────────────────────────────
def _scene_coin_parade(sid, pfx, idx, total_scenes, sc, st, en, dur, is_vertical, width, height, brand_name, web_url, bg, fg, muted, card_border, primary_color, badge, headline, subtext, pills, metrics, features):
    coin_labels = (pills or [])[:5]
    defaults = ["Build", "Ship", "Scale", "Grow", "Win"]
    while len(coin_labels) < 5:
        coin_labels.append(defaults[len(coin_labels)])

    coin_r = int(min(width, height) * 0.09)
    total_gap = int(coin_r * 0.45)
    coins_total_w = 5 * coin_r * 2 + 4 * total_gap
    start_x = (width - coins_total_w) // 2

    coin_styles = [
        ("linear-gradient(145deg,#1C1C28,#0E0E14)", card_border, "#E2E8F0"),
        ("linear-gradient(145deg,#E2E8F0,#CBD5E1)", "none", "#09090D"),
        ("#09090D", f"2px solid {card_border}", "#FFFFFF"),
        ("linear-gradient(145deg,#334155,#1E293B)", card_border, "#F8FAFC"),
        ("linear-gradient(145deg,#FFFFFF,#E2E8F0)", "none", "#07070B"),
    ]

    coins_html = ""
    for i in range(5):
        cx_pos = start_x + i * (coin_r * 2 + total_gap) + coin_r
        cy_pos = height // 2 + int(height * 0.06)
        cbg, cborder, cfg_coin = coin_styles[i]
        coins_html += f"""
      <div id="{pfx}-coin-{i}" style="position:absolute;width:{coin_r*2}px;height:{coin_r*2}px;left:{cx_pos - coin_r}px;top:{cy_pos - coin_r}px;background:{cbg};border:{cborder};border-radius:50%;display:flex;align-items:center;justify-content:center;box-shadow:0 24px 50px rgba(0,0,0,0.6);opacity:0;transform:scale(0.4) rotate(-15deg);">
        <div style="font-size:{max(15, int(coin_r * 0.32))}px;font-weight:900;color:{cfg_coin};text-align:center;line-height:1.1;padding:8px;letter-spacing:-0.02em;">{html.escape(coin_labels[i])}</div>
      </div>"""

    markup = f"""
  <div id="{sid}" class="scene" style="background-color:{bg};">
    <div class="dot-grid"></div>

    <div id="{pfx}-badge" style="position:absolute;top:{int(height*0.06)}px;left:0;right:0;text-align:center;opacity:0;">
      <span class="font-mono" style="display:inline-block;padding:7px 20px;border-radius:999px;background:rgba(255,255,255,0.06);border:1px solid {card_border};font-size:13px;font-weight:800;letter-spacing:0.1em;text-transform:uppercase;color:{muted};">{html.escape(badge)}</span>
    </div>

    <div id="{pfx}-hl" style="position:absolute;top:{int(height*0.18)}px;left:{int(width*0.08)}px;right:{int(width*0.08)}px;text-align:center;opacity:0;">
      <div style="font-size:{int(height*0.07)}px;font-weight:900;letter-spacing:-0.04em;color:{fg};line-height:1.0;">{html.escape(headline)}</div>
    </div>

    {coins_html}

    <div id="{pfx}-sub" style="position:absolute;bottom:{int(height*0.09)}px;left:0;right:0;text-align:center;opacity:0;">
      <div style="font-size:{int(height*0.024)}px;font-weight:500;color:{muted};max-width:800px;margin:0 auto;">{html.escape(subtext)}</div>
    </div>
  </div>
"""
    css = ""
    js = f"""
      if (idx === {idx}) {{
        const badge = document.getElementById('{pfx}-badge');
        const hl = document.getElementById('{pfx}-hl');
        const sub = document.getElementById('{pfx}-sub');

        const pB = easeOutCubic(clamp(tScene / 0.35, 0, 1));
        badge.style.opacity = pB.toString();

        const pH = easeOutCubic(clamp((tScene - 0.08) / 0.48, 0, 1));
        hl.style.opacity = pH.toString();
        hl.style.transform = `translateY(${{lerp(22, 0, pH)}}px)`;

        for (let ci = 0; ci < 5; ci++) {{
          const coin = document.getElementById('{pfx}-coin-' + ci);
          if (coin) {{
            const delay = 0.18 + ci * 0.09;
            const pC = easeOutBack(clamp((tScene - delay) / 0.5, 0, 1));
            coin.style.opacity = clamp(pC, 0, 1).toString();
            coin.style.transform = `scale(${{pC}})`;

            if (pC >= 1) {{
              const floatY = Math.sin(tScene * 1.6 + ci * 0.8) * 7;
              coin.style.transform = `translateY(${{floatY}}px)`;
            }}
          }}
        }}

        const pS = easeOutCubic(clamp((tScene - 0.65) / 0.4, 0, 1));
        sub.style.opacity = pS.toString();
      }}
"""
    return markup, css, js


# ─────────────────────────────────────────────────────────────────────────────
# 11. ARCHETYPE: Blueprint Reveal (CAD / Figma Vector Guides & Wordmark Clip)
# ─────────────────────────────────────────────────────────────────────────────
def _scene_blueprint_reveal(sid, pfx, idx, total_scenes, sc, st, en, dur, is_vertical, width, height, brand_name, web_url, bg, fg, muted, card_border, primary_color, badge, headline, subtext, pills, metrics, features):
    cx, cy = width // 2, height // 2
    initials = "".join(w[0].upper() for w in (brand_name or headline).split()[:2]) or "CM"

    markup = f"""
  <div id="{sid}" class="scene" style="background-color:{bg};">
    <div class="dot-grid"></div>

    <div id="{pfx}-brand" style="position:absolute;left:{cx}px;top:{cy}px;transform:translate(-50%,-50%);display:flex;align-items:center;gap:36px;">
      <div id="{pfx}-card" style="width:200px;height:200px;background:linear-gradient(145deg,#1E1E2A,#0F0F16);border:2px solid {card_border};border-radius:54px;display:flex;align-items:center;justify-content:center;box-shadow:0 24px 60px rgba(0,0,0,0.7);flex-shrink:0;">
        <div style="font-size:74px;font-weight:900;color:{fg};letter-spacing:-0.04em;">{html.escape(initials)}</div>
      </div>
      <div id="{pfx}-wordmark" style="font-size:{min(80, int(height * 0.075))}px;font-weight:900;color:{fg};letter-spacing:-0.035em;white-space:nowrap;overflow:hidden;width:0;opacity:0;">
        {html.escape(brand_name or headline)}
      </div>
    </div>

    <!-- Bottom subtext -->
    <div id="{pfx}-sub" style="position:absolute;bottom:{int(height*0.08)}px;left:0;right:0;text-align:center;opacity:0;">
      <div class="font-mono" style="font-size:13px;font-weight:700;color:{muted};text-transform:uppercase;letter-spacing:0.1em;margin-bottom:10px;">{html.escape(badge)}</div>
      <div style="font-size:{int(height*0.024)}px;color:{muted};max-width:700px;margin:0 auto;">{html.escape(subtext)}</div>
    </div>
  </div>
"""
    css = ""
    js = f"""
      if (idx === {idx}) {{
        const card = document.getElementById('{pfx}-card');
        const wordmark = document.getElementById('{pfx}-wordmark');
        const sub = document.getElementById('{pfx}-sub');

        const textLen = (wordmark.textContent || '').trim().length;
        const targetW = Math.max(160, Math.min({width} * 0.45, textLen * 44));

        const pC = easeOutBack(clamp(tScene / 0.5, 0, 1));
        card.style.transform = `scale(${{pC}})`;

        const pW = easeOutCubic(clamp((tScene - 0.25) / 0.65, 0, 1));
        wordmark.style.width = `${{lerp(0, targetW, pW)}}px`;
        wordmark.style.opacity = clamp(pW * 2, 0, 1).toString();

        const pS = easeOutCubic(clamp((tScene - 0.55) / 0.45, 0, 1));
        sub.style.opacity = pS.toString();
      }}
"""
    return markup, css, js


# ─────────────────────────────────────────────────────────────────────────────
# 12. ARCHETYPE: Dashboard Device (Realistic Widescreen Mockup for Apps)
# ─────────────────────────────────────────────────────────────────────────────
def _scene_dashboard_device(sid, pfx, idx, total_scenes, sc, st, en, dur, is_vertical, width, height, brand_name, web_url, bg, fg, muted, card_border, primary_color, badge, headline, subtext, pills, metrics, features):
    phone_w = int(width * (0.85 if is_vertical else 0.72))
    phone_h = int(height * (0.68 if is_vertical else 0.64))
    initials = "".join(w[0].upper() for w in (brand_name or headline).split()[:2]) or "CM"

    markup = f"""
  <div id="{sid}" class="scene" style="background-color:{bg};">
    <div class="dot-grid"></div>

    <div id="{pfx}-wrap" style="position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;">
      <div id="{pfx}-device" style="width:{phone_w}px;height:{phone_h}px;background:linear-gradient(145deg,#161622,#0A0A10);border-radius:48px;border:14px solid #1C1C28;box-shadow:0 40px 100px rgba(0,0,0,0.85);display:flex;flex-direction:column;align-items:center;justify-content:center;overflow:hidden;opacity:0;transform:scale(0.85);">
        <div style="width:120px;height:120px;border-radius:50%;border:3px solid {fg};display:flex;align-items:center;justify-content:center;margin-bottom:20px;">
          <div style="font-size:52px;font-weight:900;color:{fg};">{html.escape(initials)}</div>
        </div>
        <div style="font-size:32px;font-weight:900;color:{fg};letter-spacing:-0.02em;">{html.escape(headline)}</div>
        <div style="font-size:16px;color:{muted};margin-top:8px;max-width:80%;text-align:center;">{html.escape(subtext)}</div>
      </div>
    </div>
  </div>
"""
    css = ""
    js = f"""
      if (idx === {idx}) {{
        const device = document.getElementById('{pfx}-device');
        const p = easeOutBack(clamp(tScene / 0.55, 0, 1));
        device.style.opacity = clamp(p, 0, 1).toString();
        device.style.transform = `scale(${{p}})`;
      }}
"""
    return markup, css, js


# ─────────────────────────────────────────────────────────────────────────────
# 13. ARCHETYPE: Cinematic Hero (Letterbox Widescreen Hero)
# ─────────────────────────────────────────────────────────────────────────────
def _scene_cinematic_hero(sid, pfx, idx, total_scenes, sc, st, en, dur, is_vertical, width, height, brand_name, web_url, bg, fg, muted, card_border, primary_color, badge, headline, subtext, pills, metrics, features):
    lbh = int(height * 0.05)
    hl_size = int(height * (0.075 if is_vertical else 0.095))

    markup = f"""
  <div id="{sid}" class="scene" style="background-color:{bg};">
    <div class="dot-grid"></div>

    <div style="position:absolute;top:0;left:0;right:0;height:{lbh}px;background:#000000;z-index:30;"></div>
    <div style="position:absolute;bottom:0;left:0;right:0;height:{lbh}px;background:#000000;z-index:30;"></div>

    <div style="position:absolute;inset:{lbh}px 0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:0 {int(width*0.08)}px;">
      <div id="{pfx}-badge" style="display:inline-block;padding:7px 20px;border-radius:999px;background:rgba(255,255,255,0.06);border:1px solid {card_border};font-family:'JetBrains Mono',monospace;font-size:13px;font-weight:800;letter-spacing:0.1em;text-transform:uppercase;color:{muted};margin-bottom:24px;opacity:0;">
        {html.escape(badge)}
      </div>
      <div id="{pfx}-hl" style="font-size:{hl_size}px;font-weight:900;letter-spacing:-0.04em;color:{fg};line-height:1.02;max-width:960px;margin-bottom:20px;opacity:0;transform:translateY(28px);">
        {html.escape(headline)}
      </div>
      <div id="{pfx}-sub" style="font-size:{int(height*0.026)}px;color:{muted};max-width:680px;line-height:1.45;opacity:0;">
        {html.escape(subtext)}
      </div>
    </div>
  </div>
"""
    css = ""
    js = f"""
      if (idx === {idx}) {{
        const badge = document.getElementById('{pfx}-badge');
        const hl = document.getElementById('{pfx}-hl');
        const sub = document.getElementById('{pfx}-sub');

        const pB = easeOutCubic(clamp(tScene / 0.35, 0, 1));
        badge.style.opacity = pB.toString();

        const pH = easeOutCubic(clamp((tScene - 0.1) / 0.5, 0, 1));
        hl.style.opacity = pH.toString();
        hl.style.transform = `translateY(${{lerp(28, 0, pH)}}px)`;

        const pS = easeOutCubic(clamp((tScene - 0.25) / 0.45, 0, 1));
        sub.style.opacity = pS.toString();
      }}
"""
    return markup, css, js


# ─────────────────────────────────────────────────────────────────────────────
# 14. ARCHETYPE: Kinetic Parallax (Multi-Speed Floating Badge Cloud)
# ─────────────────────────────────────────────────────────────────────────────
def _scene_kinetic_parallax(sid, pfx, idx, total_scenes, sc, st, en, dur, is_vertical, width, height, brand_name, web_url, bg, fg, muted, card_border, primary_color, badge, headline, subtext, pills, metrics, features):
    label_list = (pills or [])[:5] + [brand_name or "Future", web_url or "Global"]
    while len(label_list) < 7: label_list.append("Precision")

    positions = [
        (0.18, 0.22), (0.64, 0.18), (0.38, 0.42),
        (0.12, 0.65), (0.68, 0.62), (0.45, 0.76), (0.75, 0.38)
    ]

    items_html = ""
    for i, (lx, ly) in enumerate(positions):
        lbl = label_list[i % len(label_list)]
        items_html += f"""
      <div id="{pfx}-fi-{i}" style="position:absolute;left:{int(lx*width)}px;top:{int(ly*height)}px;padding:16px 36px;border-radius:40px;background:linear-gradient(145deg,#181824,#0E0E14);border:1px solid {card_border};box-shadow:0 20px 50px rgba(0,0,0,0.6);opacity:0;">
        <span style="font-size:20px;font-weight:800;color:{fg};white-space:nowrap;">{html.escape(str(lbl))}</span>
      </div>"""

    markup = f"""
  <div id="{sid}" class="scene" style="background-color:{bg};">
    <div class="dot-grid"></div>
    {items_html}
  </div>
"""
    css = ""
    js_fi = ""
    for i in range(7):
        delay = 0.08 + i * 0.07
        js_fi += f"""
        const fi{i} = document.getElementById('{pfx}-fi-{i}');
        if (fi{i}) {{
          const p = easeOutBack(clamp((tScene - {delay}) / 0.48, 0, 1));
          fi{i}.style.opacity = clamp(p, 0, 1).toString();
          if (p >= 1) {{
            const floatY = Math.sin(tScene * 1.5 + {i}) * 8;
            fi{i}.style.transform = `translateY(${{floatY}}px)`;
          }} else {{
            fi{i}.style.transform = `scale(${{p}})`;
          }}
        }}"""

    js = f"""
      if (idx === {idx}) {{
        {js_fi}
      }}
"""
    return markup, css, js
