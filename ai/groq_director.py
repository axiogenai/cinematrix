import os
import json
import re
import urllib.request
import urllib.error

class GroqCreativeDirector:
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
            if os.path.exists(env_file):
                try:
                    with open(env_file, "r", encoding="utf-8") as ef:
                        for line in ef:
                            if line.strip().startswith("GROQ_API_KEY="):
                                self.api_key = line.strip().split("=", 1)[1].strip()
                                break
                except Exception:
                    pass

        self.model = model or os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"

    def generate_storyboard(self, prompt: str, aspect_ratio: str = "16:9", target_duration: float = 15.0, mood: str = "cinematic_tech") -> dict:
        """Uses Groq LPU AI to compose a broadcast-grade storyboard JSON.
        Produces bespoke, genre-authentic storyboards with rich per-scene data.
        """

        system_prompt = f"""You are a World-Class Creative Director & Motion Design Lead for tier-1 brand films, commercials, and product launches.
Your job: convert a user's concept into a bespoke production-ready Storyboard JSON for our high-precision video synthesis engine.

AVAILABLE PRODUCTION ARCHETYPES (Choose dynamically based on concept — NEVER follow a fixed sequence!):
1. "kinetic_manifesto": Bold typographic hook with synchronized masked line reveals. Perfect for opening statements or key manifestos.
2. "product_showcase": 3D floating turntable pedestal with concentric rotating SVG telemetry rings and floating spec callouts. Ideal for physical products, hardware, watches, sneakers, tech gadgets.
3. "terminal_code_stream": Authentic developer terminal window with live syntax-highlighted typing, compilation status, and telemetry. Ideal for devtools, CLI, cloud infra, algorithms.
4. "financial_telemetry": Real-time live SVG area chart drawing with Bézier curves, animated numerical price ticker, and market indicators. Ideal for crypto, trading, fintech, investments.
5. "split_comparison": Dual-pane duel (The Legacy Way vs The Next-Gen Standard) with animated dividing laser beam. Ideal for problem vs solution, before vs after.
6. "bento_grid_v2": Asymmetric modern bento with live interactive UI components (animated circular SVG progress dial, spring toggle switch, stacked avatar badges).
7. "metric_impact_matrix": 3 massive statistical proof cards with high-impact numbers and labels.
8. "brand_stinger_outro": High-end geometric logo resolve with converging lines, typography drop, and animated domain underline.
9. "editorial_lookbook": Elegant Playfair serif italic typography with 1px architectural corner registration marks. Ideal for luxury, fashion, fragrance.
10. "coin_parade": 3D cylindrical carousel of metallic badges with staggered spring entrance.
11. "blueprint_reveal": CAD / Figma style technical corner arc and dimension bounding box.
12. "cinematic_hero": Anamorphic letterboxed format with bold centered headline and progress tracking.

AVAILABLE CINEMA TRANSITIONS (Specify "transition_out" for every scene):
- "whip_pan_left": High-velocity horizontal camera whip to left with directional motion blur.
- "whip_pan_right": High-velocity horizontal camera whip to right with directional motion blur.
- "whip_pan_up": Aggressive vertical camera push upward with vertical motion blur.
- "zoom_punch": Camera dives deep into focal point (scale 3x) while next scene punches in with spring settle.
- "rotational_snap_3d": 3D perspective cube turn (Scene A rotates Y: 0 -> -90deg, Scene B enters Y: 90 -> 0deg).
- "shutter_split": Dual-blade horizontal matte parting from the center line.
- "circular_iris": Dynamic circular vector mask expanding outward from center.
- "depth_dissolve": Cinematic rack focus with shallow depth-of-field blur.

MANDATORY DIRECTIVES:
1. ZERO AI SLOP: No clichés, no generic placeholder copy. Every word must be authentic to the brand and product.
2. Total Duration: Create 4 to 6 scenes summing to exactly {target_duration} seconds.
3. DYNAMIC STRUCTURE:
   - For Hardware / Physical Products: "kinetic_manifesto" -> "product_showcase" -> "bento_grid_v2" -> "brand_stinger_outro"
   - For Developer / SaaS: "kinetic_manifesto" -> "terminal_code_stream" -> "bento_grid_v2" -> "brand_stinger_outro"
   - For Finance / Trading: "kinetic_manifesto" -> "financial_telemetry" -> "metric_impact_matrix" -> "brand_stinger_outro"
   - For Luxury / Fashion: "editorial_lookbook" -> "product_showcase" -> "cinematic_hero" -> "brand_stinger_outro"
   - For Disruptors / Startups: "kinetic_manifesto" -> "split_comparison" -> "bento_grid_v2" -> "brand_stinger_outro"
4. Rich scene data:
   - "pills": array of 4 short impact words
   - "metrics": array of 3 objects with "label", "value", "delta" keys
   - "features": array of 3 specific feature phrases
   - "subtext": 1-2 concise, high-impact brand sentences
5. bg_theme choices: "dark_grid", "carbon_grid", "cream_grid", "luxury_gold", "crimson_news", "terminal_matrix"

OUTPUT: Return ONLY raw JSON (NO markdown, NO commentary):
{{
  "title": "Short Video Title",
  "brand_name": "Brand Name",
  "web_url": "brand.io",
  "aspect_ratio": "{aspect_ratio}",
  "mood": "{mood}",
  "genre": "tech_saas",
  "fps": 30,
  "scenes": [
    {{
      "layout": "kinetic_manifesto",
      "transition_out": "whip_pan_left",
      "duration": 3.5,
      "bg_theme": "dark_grid",
      "badge": "01 // GENESIS",
      "headline": "Powerfully Concise Headline",
      "subtext": "One specific compelling sentence about the product or breakthrough.",
      "pills": ["Speed", "Precision", "Global", "Scale"],
      "metrics": [{{"label": "Throughput", "value": "100k", "delta": "+140%"}}, {{"label": "Latency", "value": "0.8ms", "delta": "P99"}}],
      "features": ["Sub-millisecond execution", "Self-healing core", "Autonomous distribution"]
    }}
  ]
}}"""

        if not self.api_key:
            return self._fallback_storyboard(prompt, aspect_ratio, target_duration, mood)

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Create a bespoke {aspect_ratio} storyboard for: '{prompt}'. Duration: {target_duration}s. Mood: {mood}. Make every scene visually distinct, brand-specific, and broadcast-grade with cinema transitions."}
            ],
            "temperature": 0.4
        }

        try:
            req = urllib.request.Request(
                self.api_url,
                data=json.dumps(payload).encode('utf-8'),
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0"
                }
            )
            with urllib.request.urlopen(req, timeout=22) as response:
                res_body = response.read().decode('utf-8')
                res_json = json.loads(res_body)
                raw_content = res_json['choices'][0]['message']['content'].strip()
                if "```json" in raw_content:
                    raw_content = raw_content.split("```json")[1].split("```")[0].strip()
                elif "```" in raw_content:
                    raw_content = raw_content.split("```")[1].split("```")[0].strip()

                storyboard = json.loads(raw_content)
                storyboard["aspect_ratio"] = aspect_ratio
                storyboard["fps"] = 30
                storyboard["mood"] = mood
                return storyboard
        except Exception as e:
            print(f"[GroqDirector] API error: {e}. Using intelligent programmatic fallback.")
            return self._fallback_storyboard(prompt, aspect_ratio, target_duration, mood)

    def _fallback_storyboard(self, prompt: str, aspect_ratio: str, duration: float, mood: str) -> dict:
        """Intelligent, genre-authentic programmatic fallback generator when offline."""
        title = prompt.strip().split('.')[0][:40].title() if prompt else "CineMatrix Visual Studio"
        prompt_lower = prompt.lower()
        dur_scene = round(duration / 4.0, 1)

        # 1. PHYSICAL PRODUCTS / HARDWARE / LUXURY GOODS
        if any(w in prompt_lower for w in ["watch", "shoe", "sneaker", "perfume", "product", "bottle", "sale", "hardware", "device", "camera", "headphone"]):
            brand = title.split()[0] if title else "AERION"
            return {
                "title": title,
                "brand_name": brand,
                "web_url": brand.lower() + ".studio",
                "aspect_ratio": aspect_ratio,
                "mood": "minimalist_luxury",
                "genre": "product_launch",
                "fps": 30,
                "scenes": [
                    {
                        "layout": "kinetic_manifesto",
                        "transition_out": "whip_pan_left",
                        "duration": dur_scene,
                        "bg_theme": "dark_grid",
                        "badge": "01 // THE REVELATION",
                        "headline": title or "Sculpted for Pure Precision",
                        "subtext": "Engineered with aerospace grade 5 titanium and millimeter-level geometric tolerance.",
                        "pills": ["Aerospace", "Grade 5 Ti", "Precision", "Limited"],
                        "metrics": [{"label": "Tolerance", "value": "0.02mm", "delta": "Micron"}, {"label": "Mass", "value": "142g", "delta": "Featherlight"}, {"label": "Edition", "value": "500 Units", "delta": "Numbered"}],
                        "features": ["Hand-finished titanium bezel", "Sapphire crystal dome", "100m water resistance"]
                    },
                    {
                        "layout": "product_showcase",
                        "transition_out": "zoom_punch",
                        "duration": dur_scene,
                        "bg_theme": "dark_grid",
                        "badge": "02 // ARCHITECTURE",
                        "headline": "Obsessive Craftsmanship",
                        "subtext": "Every contour deliberate. Every component tested across 68 stress vectors.",
                        "pills": ["Titanium", "Sapphire", "Ceramic", "Precision"],
                        "metrics": [{"label": "Stress Tests", "value": "68", "delta": "Passed"}, {"label": "Rigidity", "value": "99.4%", "delta": "Verified"}],
                        "features": ["Aerospace Grade 5 Titanium", "Quantum Sensor Array", "Zero-Latency Core"]
                    },
                    {
                        "layout": "bento_grid_v2",
                        "transition_out": "rotational_snap_3d",
                        "duration": dur_scene,
                        "bg_theme": "carbon_grid",
                        "badge": "03 // PERFORMANCE",
                        "headline": "Engineered for Velocity",
                        "subtext": "Uncompromising performance architecture designed to outlast the century.",
                        "pills": ["Autonomous", "Sub-10ms", "Global Edge", "Zero Defect"],
                        "metrics": [{"label": "Efficiency", "value": "99.8%", "delta": "SLA"}, {"label": "Cold Start", "value": "0.8ms", "delta": "Instant"}],
                        "features": ["Instantaneous responsiveness", "Self-calibrating telemetry", "Enduring battery reserve"]
                    },
                    {
                        "layout": "brand_stinger_outro",
                        "transition_out": "depth_dissolve",
                        "duration": dur_scene,
                        "bg_theme": "dark_grid",
                        "badge": "04 // OWN THE MOMENT",
                        "headline": f"Experience {brand}",
                        "subtext": "Available worldwide in limited numbered quantities. Complimentary white-glove delivery.",
                        "pills": ["Order Now", "Global Ship", "Lifetime", "Concierge"],
                        "metrics": [{"label": "Delivery", "value": "Global", "delta": "Complimentary"}, {"label": "Warranty", "value": "Lifetime", "delta": "Guaranteed"}],
                        "features": []
                    }
                ]
            }

        # 2. DEVELOPER TOOLS / CLI / INFRASTRUCTURE / SAAS
        elif any(w in prompt_lower for w in ["code", "developer", "terminal", "cli", "api", "infra", "cloud", "saas", "engine", "software", "ai agent"]):
            brand = title.split()[0] if title else "HYPERION"
            return {
                "title": title,
                "brand_name": brand,
                "web_url": brand.lower() + ".dev",
                "aspect_ratio": aspect_ratio,
                "mood": "tech_developer",
                "genre": "developer",
                "fps": 30,
                "scenes": [
                    {
                        "layout": "kinetic_manifesto",
                        "transition_out": "whip_pan_left",
                        "duration": dur_scene,
                        "bg_theme": "dark_grid",
                        "badge": "01 // SYSTEM RELEASE",
                        "headline": title or "The Next-Gen Runtime Engine",
                        "subtext": "Built for developers who refuse to compromise on latency, stability, and scale.",
                        "pills": ["Zero-Config", "Sub-10ms", "Global", "Wasm"],
                        "metrics": [{"label": "P99 Latency", "value": "0.8ms", "delta": "Fastest"}, {"label": "Uptime", "value": "99.99%", "delta": "SLA Backed"}],
                        "features": ["Instant edge compilation", "Self-healing micro-runtimes", "Distributed global state"]
                    },
                    {
                        "layout": "terminal_code_stream",
                        "transition_out": "shutter_split",
                        "duration": dur_scene,
                        "bg_theme": "dark_grid",
                        "badge": "02 // LIVE COMPILATION",
                        "headline": "Native Speed. Zero Cold Starts.",
                        "subtext": "Execute workloads closer to the metal with automated multi-region replication.",
                        "pills": ["Compile", "Execute", "Verify", "Scale"],
                        "metrics": [{"label": "Cold Start", "value": "0.82ms", "delta": "P99"}, {"label": "Nodes", "value": "320+", "delta": "Global"}],
                        "features": ["Autonomous thread management", "Direct SIMD acceleration", "Zero-copy IPC"]
                    },
                    {
                        "layout": "bento_grid_v2",
                        "transition_out": "zoom_punch",
                        "duration": dur_scene,
                        "bg_theme": "carbon_grid",
                        "badge": "03 // OBSERVABILITY",
                        "headline": "Real-Time Telemetry at Scale",
                        "subtext": "Deep runtime metrics and traces streamed directly into your observability stack.",
                        "pills": ["Autonomous", "Sub-10ms", "Global Edge", "Zero Defect"],
                        "metrics": [{"label": "Throughput", "value": "120k req/s", "delta": "+400%"}, {"label": "Defects", "value": "0", "delta": "Verified"}],
                        "features": ["Distributed tracing", "Live heap analysis", "Automated anomaly mitigation"]
                    },
                    {
                        "layout": "brand_stinger_outro",
                        "transition_out": "depth_dissolve",
                        "duration": dur_scene,
                        "bg_theme": "dark_grid",
                        "badge": "04 // GET STARTED",
                        "headline": f"Build on {brand}",
                        "subtext": "Join thousands of high-velocity engineering teams shipping with confidence.",
                        "pills": ["Get Started", "Read Docs", "GitHub", "Enterprise"],
                        "metrics": [{"label": "Setup", "value": "< 60s", "delta": "CLI Native"}, {"label": "License", "value": "Apache 2.0", "delta": "Open Core"}],
                        "features": []
                    }
                ]
            }

        # 3. FINANCE / TRADING / CRYPTO / DEFI
        elif any(w in prompt_lower for w in ["crypto", "bitcoin", "stock", "finance", "trading", "market", "invest", "defi", "blockchain", "token"]):
            brand = "APEX"
            return {
                "title": title,
                "brand_name": brand,
                "web_url": "apex.capital",
                "aspect_ratio": aspect_ratio,
                "mood": "high_energy_finance",
                "genre": "finance",
                "fps": 30,
                "scenes": [
                    {
                        "layout": "kinetic_manifesto",
                        "transition_out": "whip_pan_left",
                        "duration": dur_scene,
                        "bg_theme": "dark_grid",
                        "badge": "01 // PROTOCOL GENESIS",
                        "headline": title or "Institutional Liquidity Unleashed",
                        "subtext": "Sub-millisecond trade execution infrastructure engineered for sovereign capital.",
                        "pills": ["Liquidity", "Execution", "Zero-Slippage", "Alpha"],
                        "metrics": [{"label": "Fill Rate", "value": "99.98%", "delta": "Guaranteed"}, {"label": "Latency", "value": "0.4ms", "delta": "Direct"}],
                        "features": ["Sub-millisecond smart routing", "Direct liquidity pool access", "Institutional-grade custody"]
                    },
                    {
                        "layout": "financial_telemetry",
                        "transition_out": "rotational_snap_3d",
                        "duration": dur_scene,
                        "bg_theme": "dark_grid",
                        "badge": "02 // LIVE ORDER BOOK",
                        "headline": "All-Time High. Every Second.",
                        "subtext": "Continuous algorithmic matching with zero front-running and complete cryptographic verification.",
                        "pills": ["BTC", "ETH", "Volume", "Open Interest"],
                        "metrics": [{"label": "24h Volume", "value": "$14.8B", "delta": "+42.4%"}, {"label": "TVL", "value": "$64.2B", "delta": "ATH"}, {"label": "Latency", "value": "0.4ms", "delta": "P99"}],
                        "features": ["Cross-exchange arbitrage engine", "Dark pool execution", "Zero MEV exposure"]
                    },
                    {
                        "layout": "metric_impact_matrix",
                        "transition_out": "zoom_punch",
                        "duration": dur_scene,
                        "bg_theme": "carbon_grid",
                        "badge": "03 // CAPITAL ASSURANCE",
                        "headline": "Proven at Extreme Scale",
                        "subtext": "Over $400 billion in cumulative volume executed without a single second of downtime.",
                        "pills": ["Audited", "SOC 2", "Secure", "Global"],
                        "metrics": [{"label": "Cumulative Vol", "value": "$420B+", "delta": "Audited"}, {"label": "SLA Uptime", "value": "100%", "delta": "Historical"}, {"label": "Active Markets", "value": "180+", "delta": "Global"}],
                        "features": ["Multi-sig cold storage", "Real-time proof of reserves", "Continuous formal verification"]
                    },
                    {
                        "layout": "brand_stinger_outro",
                        "transition_out": "depth_dissolve",
                        "duration": dur_scene,
                        "bg_theme": "dark_grid",
                        "badge": "04 // ACCESS THE PROTOCOL",
                        "headline": "Trade Without Compromise",
                        "subtext": "Connect institutional API endpoints or launch the terminal. Zero barriers to entry.",
                        "pills": ["Launch Terminal", "API Keys", "Docs", "Whitepaper"],
                        "metrics": [{"label": "Account Setup", "value": "Instant", "delta": "No Wait"}, {"label": "Support", "value": "24/7", "delta": "Dedicated"}],
                        "features": []
                    }
                ]
            }

        # 4. LUXURY / HIGH FASHION / EDITORIAL
        elif any(w in prompt_lower for w in ["fashion", "luxury", "atelier", "editorial", "couture", "fragrance", "jewelry", "elegance"]):
            brand = "VELOURS"
            return {
                "title": title,
                "brand_name": brand,
                "web_url": "maisonvelours.com",
                "aspect_ratio": aspect_ratio,
                "mood": "minimalist_luxury",
                "genre": "luxury",
                "fps": 30,
                "scenes": [
                    {
                        "layout": "editorial_lookbook",
                        "transition_out": "depth_dissolve",
                        "duration": dur_scene,
                        "bg_theme": "dark_grid",
                        "badge": "01 // THE ESSENCE",
                        "headline": title or "Sculpting Light Into Form",
                        "subtext": "Crafted in limited numbered editions. Where architectural discipline meets pure haute couture.",
                        "pills": ["Handcrafted", "Heritage", "Rare", "Pure"],
                        "metrics": [{"label": "Edition", "value": "100 Only", "delta": "Numbered"}, {"label": "Craftsmanship", "value": "240 Hours", "delta": "Bespoke"}],
                        "features": ["Museum-grade natural materials", "Hand-sewn French seams", "Individually signed cert"]
                    },
                    {
                        "layout": "product_showcase",
                        "transition_out": "circular_iris",
                        "duration": dur_scene,
                        "bg_theme": "dark_grid",
                        "badge": "02 // THE SILHOUETTE",
                        "headline": "Deliberate in Every Seam",
                        "subtext": "Proportions engineered to command attention through understated mastery.",
                        "pills": ["Bespoke", "Titanium", "Silk", "Rare"],
                        "metrics": [{"label": "Precision", "value": "Grade A", "delta": "Certified"}, {"label": "Heritage", "value": "Since 1924", "delta": "Paris"}],
                        "features": ["Handcrafted titanium core", "Natural mulberry silk lining", "Bespoke monogramming"]
                    },
                    {
                        "layout": "cinematic_hero",
                        "transition_out": "whip_pan_right",
                        "duration": dur_scene,
                        "bg_theme": "dark_grid",
                        "badge": "03 // MANIFESTO",
                        "headline": "True Luxury Never Shouts",
                        "subtext": "Designed for those whose standard needs no explanation.",
                        "pills": ["Exclusive", "Timeless", "Signature", "Paris"],
                        "metrics": [{"label": "Concierge", "value": "Personal", "delta": "Worldwide"}],
                        "features": []
                    },
                    {
                        "layout": "brand_stinger_outro",
                        "transition_out": "depth_dissolve",
                        "duration": dur_scene,
                        "bg_theme": "dark_grid",
                        "badge": "04 // THE ATELIER",
                        "headline": f"Maison {brand}",
                        "subtext": "Inquire with your private client advisor for private salon viewings.",
                        "pills": ["Request Access", "Private Salon", "Lookbook", "Concierge"],
                        "metrics": [{"label": "Global Salon", "value": "Paris // Tokyo", "delta": "Private"}],
                        "features": []
                    }
                ]
            }

        # 5. GENERAL DISRUPTOR / STARTUP / AGENCY / LAUNCH
        else:
            skip_words = {"launch", "introducing", "create", "build", "presenting", "meet", "announcing", "the", "a", "an", "new", "get"}
            words = [w for w in title.split() if w.lower() not in skip_words]
            brand = words[0] if words else "VORTEX"
            return {
                "title": title,
                "brand_name": brand,
                "web_url": brand.lower() + ".io",
                "aspect_ratio": aspect_ratio,
                "mood": mood,
                "genre": "tech_saas",
                "fps": 30,
                "scenes": [
                    {
                        "layout": "kinetic_manifesto",
                        "transition_out": "whip_pan_left",
                        "duration": dur_scene,
                        "bg_theme": "dark_grid",
                        "badge": "01 // THE LEAP",
                        "headline": prompt[:50] if prompt else "Engineering The Impossible",
                        "subtext": "Designed for the velocity of tomorrow's market leaders. Zero friction. Pure speed.",
                        "pills": ["Autonomous", "Sub-10ms", "Global", "Scale"],
                        "metrics": [{"label": "Speed", "value": "10x Faster", "delta": "Verified"}, {"label": "Uptime", "value": "99.99%", "delta": "Enterprise"}],
                        "features": ["Autonomous execution runtime", "Instantaneous state sync", "Zero-downtime scaling"]
                    },
                    {
                        "layout": "split_comparison",
                        "transition_out": "zoom_punch",
                        "duration": dur_scene,
                        "bg_theme": "dark_grid",
                        "badge": "02 // THE SHIFT",
                        "headline": "Legacy Friction vs Autonomous Velocity",
                        "subtext": "Why leading technology teams are leaving traditional fractured stacks behind.",
                        "pills": ["Legacy", "Modern", "Shift", "Win"],
                        "metrics": [{"label": "Overhead", "value": "-94%", "delta": "Reduced"}, {"label": "Deploy Speed", "value": "< 12s", "delta": "Instant"}],
                        "features": ["Autonomous workflow dispatch", "Unified command interface", "End-to-end verification"]
                    },
                    {
                        "layout": "bento_grid_v2",
                        "transition_out": "rotational_snap_3d",
                        "duration": dur_scene,
                        "bg_theme": "carbon_grid",
                        "badge": "03 // ECOSYSTEM",
                        "headline": "Engineered for Complete Command",
                        "subtext": "An integrated creative intelligence platform built from the ground up for relentless precision.",
                        "pills": ["Autonomous", "Sub-10ms", "Global Edge", "Zero Defect"],
                        "metrics": [{"label": "Integrations", "value": "320+", "delta": "Growing"}, {"label": "Accuracy", "value": "99.9%", "delta": "Certified"}],
                        "features": ["Real-time multi-agent orchestration", "Deterministic rendering pipeline", "Global edge caching"]
                    },
                    {
                        "layout": "brand_stinger_outro",
                        "transition_out": "depth_dissolve",
                        "duration": dur_scene,
                        "bg_theme": "dark_grid",
                        "badge": "04 // JOIN THE NEXT WAVE",
                        "headline": f"Ship With {brand}",
                        "subtext": "Start building today with zero infrastructure overhead. The future waits for no one.",
                        "pills": ["Get Started", "Read Docs", "Pricing", "Enterprise"],
                        "metrics": [{"label": "Onboarding", "value": "< 2 min", "delta": "Instant"}, {"label": "Free Tier", "value": "Available", "delta": "No CC"}],
                        "features": []
                    }
                ]
            }
