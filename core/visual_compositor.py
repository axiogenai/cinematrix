import math
import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Helper Easing Functions
def ease_out_cubic(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return 1.0 - math.pow(1.0 - t, 3)

def ease_in_out_cubic(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return 4 * t * t * t if t < 0.5 else 1 - math.pow(-2 * t + 2, 3) / 2

def ease_out_expo(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return 1.0 if t == 1.0 else 1.0 - math.pow(2, -10 * t)

def clamp(val, min_val, max_val):
    return max(min_val, min(max_val, val))

class VisualCompositor:
    def __init__(self, width: int = 1920, height: int = 1080):
        self.width = width
        self.height = height
        self.is_vertical = height > width
        self.scale_factor = width / 1920.0 if not self.is_vertical else width / 1080.0

        # Load System Fonts with fallbacks
        self.font_sans_light = self._load_font(['C:/Windows/Fonts/segoeuil.ttf', 'C:/Windows/Fonts/arial.ttf'], int(48 * self.scale_factor))
        self.font_sans_regular = self._load_font(['C:/Windows/Fonts/segoeui.ttf', 'C:/Windows/Fonts/arial.ttf'], int(32 * self.scale_factor))
        self.font_sans_bold = self._load_font(['C:/Windows/Fonts/seguisb.ttf', 'C:/Windows/Fonts/arialbd.ttf'], int(38 * self.scale_factor))
        self.font_mono = self._load_font(['C:/Windows/Fonts/consola.ttf', 'C:/Windows/Fonts/cour.ttf'], int(24 * self.scale_factor))
        self.font_badge = self._load_font(['C:/Windows/Fonts/seguisb.ttf', 'C:/Windows/Fonts/arialbd.ttf'], int(18 * self.scale_factor))
        self.font_title_large = self._load_font(['C:/Windows/Fonts/segoeuil.ttf', 'C:/Windows/Fonts/arial.ttf'], int(72 * self.scale_factor))
        self.font_title_hero = self._load_font(['C:/Windows/Fonts/segoeuib.ttf', 'C:/Windows/Fonts/arialbd.ttf'], int(84 * self.scale_factor))

    def _load_font(self, font_paths: list[str], size: int) -> ImageFont.FreeTypeFont:
        for p in font_paths:
            if os.path.exists(p):
                try:
                    return ImageFont.truetype(p, size)
                except Exception:
                    pass
        return ImageFont.load_default()

    def create_canvas(self, bg_style: str = "obsidian_grid", progress: float = 0.0) -> Image.Image:
        """Create high-density matte canvas with subtle technical pattern."""
        img = Image.new("RGBA", (self.width, self.height), (9, 9, 11, 255)) # #09090b
        draw = ImageDraw.Draw(img)

        if bg_style == "obsidian_grid":
            # Subtle architectural dots
            grid_spacing = int(60 * self.scale_factor)
            dot_color = (255, 255, 255, 14)
            for x in range(0, self.width, grid_spacing):
                for y in range(0, self.height, grid_spacing):
                    draw.ellipse([x - 1, y - 1, x + 1, y + 1], fill=dot_color)

            # Very faint vignette
            np_arr = np.array(img, dtype=np.uint8)
            cx, cy = self.width // 2, self.height // 2
            y_coords, x_coords = np.ogrid[:self.height, :self.width]
            dist_sq = ((x_coords - cx) ** 2 + (y_coords - cy) ** 2) / float(cx ** 2 + cy ** 2)
            vignette = np.clip(1.0 - 0.25 * dist_sq, 0.65, 1.0)
            for c in range(3):
                np_arr[:, :, c] = (np_arr[:, :, c] * vignette).astype(np.uint8)
            return Image.fromarray(np_arr, "RGBA")

        elif bg_style == "deep_carbon":
            # Radial subtle glow center
            return img

        return img

    def draw_telemetry_badge(self, draw: ImageDraw.ImageDraw, x: int, y: int, text: str, opacity: float = 1.0):
        """Draws crisp frosted HUD telemetry pill."""
        if opacity <= 0.01:
            return
        alpha = int(opacity * 255)
        text_bbox = draw.textbbox((0, 0), text, font=self.font_badge)
        tw = text_bbox[2] - text_bbox[0]
        th = text_bbox[3] - text_bbox[1]

        pad_x = int(14 * self.scale_factor)
        pad_y = int(6 * self.scale_factor)
        rect = [x, y, x + tw + pad_x * 2, y + th + pad_y * 2]

        # Pill background
        draw.rounded_rectangle(rect, radius=int(6 * self.scale_factor), fill=(24, 24, 27, int(alpha * 0.9)), outline=(255, 255, 255, int(alpha * 0.15)), width=1)
        # Indicator dot (subtle desaturated sage)
        dot_r = int(3 * self.scale_factor)
        draw.ellipse([x + pad_x - int(4 * self.scale_factor) - dot_r, y + (th + pad_y * 2) // 2 - dot_r, x + pad_x - int(4 * self.scale_factor) + dot_r, y + (th + pad_y * 2) // 2 + dot_r], fill=(163, 190, 140, alpha))
        # Text
        draw.text((x + pad_x + int(8 * self.scale_factor), y + pad_y), text, font=self.font_badge, fill=(228, 228, 231, alpha))

    def draw_kinetic_headline(self, img: Image.Image, text: str, subtext: str = "", progress: float = 0.0, y_anchor: float = 0.45):
        """Renders cinematic kinetic typography with smooth cubic gliding."""
        draw = ImageDraw.Draw(img)

        # Smooth reveal curve
        ease_p = ease_out_cubic(clamp(progress / 0.7, 0.0, 1.0))
        alpha = int(clamp(progress / 0.5, 0.0, 1.0) * 255)

        # Slide up offset
        slide_offset = int((1.0 - ease_p) * 40 * self.scale_factor)

        # Split text into lines if needed
        words = text.split(' ')
        lines = []
        cur_line = []
        max_w = self.width * (0.85 if self.is_vertical else 0.75)

        for w in words:
            test_line = ' '.join(cur_line + [w])
            bbox = draw.textbbox((0, 0), test_line, font=self.font_title_hero if not self.is_vertical else self.font_title_large)
            if bbox[2] - bbox[0] > max_w and cur_line:
                lines.append(' '.join(cur_line))
                cur_line = [w]
            else:
                cur_line.append(w)
        if cur_line:
            lines.append(' '.join(cur_line))

        font_used = self.font_title_hero if not self.is_vertical else self.font_title_large
        line_h = int(95 * self.scale_factor) if not self.is_vertical else int(80 * self.scale_factor)
        total_text_h = len(lines) * line_h

        base_y = int(self.height * y_anchor) - (total_text_h // 2) + slide_offset

        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font_used)
            tw = bbox[2] - bbox[0]
            tx = (self.width - tw) // 2
            ty = base_y + (i * line_h)
            # Crisp white titanium typography
            draw.text((tx, ty), line, font=font_used, fill=(244, 244, 245, alpha))

        # Render subtext if present
        if subtext and progress > 0.35:
            sub_p = ease_out_cubic(clamp((progress - 0.35) / 0.5, 0.0, 1.0))
            sub_alpha = int(sub_p * 255)
            sub_offset = int((1.0 - sub_p) * 25 * self.scale_factor)

            sub_bbox = draw.textbbox((0, 0), subtext, font=self.font_sans_regular)
            stw = sub_bbox[2] - sub_bbox[0]
            stx = (self.width - stw) // 2
            sty = base_y + total_text_h + int(30 * self.scale_factor) + sub_offset

            draw.text((stx, sty), subtext, font=self.font_sans_regular, fill=(161, 161, 170, sub_alpha))

    def draw_code_editor_window(self, img: Image.Image, code_lines: list[str], filename: str = "orchestrator.ts", progress: float = 0.0):
        """Renders an authentic dark IDE / Monaco window with line typing and cursor."""
        draw = ImageDraw.Draw(img)

        # Positioning
        if self.is_vertical:
            win_w = int(self.width * 0.90)
            win_h = int(self.height * 0.50)
            win_x = (self.width - win_w) // 2
            win_y = int(self.height * 0.32)
        else:
            win_w = int(self.width * 0.65)
            win_h = int(self.height * 0.55)
            win_x = (self.width - win_w) // 2
            win_y = int(self.height * 0.28)

        ease_p = ease_out_cubic(clamp(progress / 0.4, 0.0, 1.0))
        alpha = int(clamp(progress / 0.3, 0.0, 1.0) * 255)
        offset_y = int((1.0 - ease_p) * 35 * self.scale_factor)

        actual_y = win_y + offset_y

        # Window Frame
        draw.rounded_rectangle(
            [win_x, actual_y, win_x + win_w, actual_y + win_h],
            radius=int(12 * self.scale_factor),
            fill=(15, 15, 18, int(alpha * 0.95)),
            outline=(255, 255, 255, int(alpha * 0.12)),
            width=1
        )

        # Title bar
        title_bar_h = int(38 * self.scale_factor)
        draw.rounded_rectangle(
            [win_x, actual_y, win_x + win_w, actual_y + title_bar_h],
            radius=int(12 * self.scale_factor),
            fill=(24, 24, 27, int(alpha * 0.98))
        )
        # Straighten bottom of title bar
        draw.rectangle([win_x, actual_y + title_bar_h - 10, win_x + win_w, actual_y + title_bar_h], fill=(24, 24, 27, int(alpha * 0.98)))
        draw.line([win_x, actual_y + title_bar_h, win_x + win_w, actual_y + title_bar_h], fill=(255, 255, 255, int(alpha * 0.08)), width=1)

        # Window control dots
        dot_radius = int(5 * self.scale_factor)
        dot_pad = int(14 * self.scale_factor)
        dot_y = actual_y + (title_bar_h // 2)
        draw.ellipse([win_x + dot_pad - dot_radius, dot_y - dot_radius, win_x + dot_pad + dot_radius, dot_y + dot_radius], fill=(239, 68, 68, int(alpha * 0.7)))
        draw.ellipse([win_x + dot_pad * 2 - dot_radius, dot_y - dot_radius, win_x + dot_pad * 2 + dot_radius, dot_y + dot_radius], fill=(245, 158, 11, int(alpha * 0.7)))
        draw.ellipse([win_x + dot_pad * 3 - dot_radius, dot_y - dot_radius, win_x + dot_pad * 3 + dot_radius, dot_y + dot_radius], fill=(34, 197, 94, int(alpha * 0.7)))

        # Filename tab
        draw.text((win_x + dot_pad * 4 + int(10 * self.scale_factor), actual_y + int(10 * self.scale_factor)), filename, font=self.font_badge, fill=(161, 161, 170, alpha))

        # Code Lines typing
        line_spacing = int(28 * self.scale_factor)
        start_code_y = actual_y + title_bar_h + int(20 * self.scale_factor)

        # Typing progress
        type_progress = clamp((progress - 0.2) / 0.7, 0.0, 1.0)
        total_chars = sum(len(line) for line in code_lines)
        chars_to_show = int(type_progress * total_chars)

        char_acc = 0
        cur_line_idx = 0
        cur_col_idx = 0

        for idx, line in enumerate(code_lines):
            line_y = start_code_y + (idx * line_spacing)
            if line_y > actual_y + win_h - line_spacing:
                break

            # Line numbers
            draw.text((win_x + int(20 * self.scale_factor), line_y), f"{idx+1:2d}", font=self.font_mono, fill=(82, 82, 91, int(alpha * 0.6)))

            # Sliced line content
            line_len = len(line)
            if char_acc + line_len <= chars_to_show:
                visible_text = line
                char_acc += line_len
            elif char_acc < chars_to_show:
                rem = chars_to_show - char_acc
                visible_text = line[:rem]
                char_acc = chars_to_show
                cur_line_idx = idx
                cur_col_idx = rem
            else:
                visible_text = ""

            # Syntax coloring (light technical tokens)
            draw.text((win_x + int(60 * self.scale_factor), line_y), visible_text, font=self.font_mono, fill=(228, 228, 231, alpha))

        # Blinking typing cursor
        if int(progress * 15) % 2 == 0 and chars_to_show < total_chars:
            cursor_line_y = start_code_y + (cur_line_idx * line_spacing)
            # Estimate cursor x
            cx_offset = int(60 * self.scale_factor) + int(cur_col_idx * 14 * self.scale_factor)
            draw.rectangle([win_x + cx_offset, cursor_line_y, win_x + cx_offset + int(2 * self.scale_factor), cursor_line_y + int(20 * self.scale_factor)], fill=(244, 244, 245, alpha))

    def draw_metric_telemetry_card(self, img: Image.Image, metrics: list[dict], progress: float = 0.0):
        """Renders sleek insight telemetry cards (Bklit / Spectrum UI style) with animated values."""
        draw = ImageDraw.Draw(img)

        num_cards = len(metrics)
        if num_cards == 0:
            return

        if self.is_vertical:
            card_w = int(self.width * 0.88)
            card_h = int(95 * self.scale_factor)
            spacing = int(16 * self.scale_factor)
            total_h = num_cards * card_h + (num_cards - 1) * spacing
            start_y = int(self.height * 0.42) - (total_h // 2)

            for i, m in enumerate(metrics):
                card_x = (self.width - card_w) // 2
                card_y = start_y + i * (card_h + spacing)
                self._draw_single_metric_card(draw, card_x, card_y, card_w, card_h, m, progress, i)
        else:
            spacing = int(24 * self.scale_factor)
            card_w = int((self.width * 0.75 - (num_cards - 1) * spacing) / num_cards)
            card_h = int(120 * self.scale_factor)
            start_x = (self.width - (num_cards * card_w + (num_cards - 1) * spacing)) // 2
            card_y = int(self.height * 0.48)

            for i, m in enumerate(metrics):
                card_x = start_x + i * (card_w + spacing)
                self._draw_single_metric_card(draw, card_x, card_y, card_w, card_h, m, progress, i)

    def _draw_single_metric_card(self, draw: ImageDraw.ImageDraw, x: int, y: int, w: int, h: int, m: dict, progress: float, index: int):
        stagger = index * 0.15
        p = ease_out_cubic(clamp((progress - stagger) / 0.45, 0.0, 1.0))
        alpha = int(p * 255)
        offset_y = int((1.0 - p) * 20 * self.scale_factor)

        actual_y = y + offset_y

        # Card container (Matte obsidian + 1px crisp border)
        draw.rounded_rectangle(
            [x, actual_y, x + w, actual_y + h],
            radius=int(10 * self.scale_factor),
            fill=(18, 18, 22, int(alpha * 0.95)),
            outline=(255, 255, 255, int(alpha * 0.12)),
            width=1
        )

        pad_x = int(20 * self.scale_factor)
        pad_y = int(16 * self.scale_factor)

        # Label
        label = m.get("label", "Metric").upper()
        draw.text((x + pad_x, actual_y + pad_y), label, font=self.font_badge, fill=(161, 161, 170, alpha))

        # Animated Value
        target_val = m.get("value", "100%")
        # Numeric progression if numeric
        val_display = target_val
        draw.text((x + pad_x, actual_y + pad_y + int(24 * self.scale_factor)), val_display, font=self.font_sans_bold, fill=(244, 244, 245, alpha))

        # Note / delta
        delta = m.get("delta", "")
        if delta:
            draw.text((x + pad_x, actual_y + h - int(24 * self.scale_factor)), delta, font=self.font_mono, fill=(163, 190, 140, alpha))

    def draw_brand_reveal(self, img: Image.Image, brand_title: str, tagline: str = "", web_url: str = "", progress: float = 0.0):
        """Renders minimalist, high-prestige brand finale with clean geometric emblem."""
        draw = ImageDraw.Draw(img)

        ease_p = ease_out_cubic(clamp(progress / 0.6, 0.0, 1.0))
        alpha = int(clamp(progress / 0.4, 0.0, 1.0) * 255)
        scale = 0.92 + 0.08 * ease_p

        cy = int(self.height * 0.42)
        cx = self.width // 2

        # Draw Minimalist Titanium Emblem (Vector Polygon)
        emblem_size = int(90 * self.scale_factor * scale)
        pts = [
            (cx, cy - emblem_size // 2),
            (cx + emblem_size // 2, cy + emblem_size // 2),
            (cx - emblem_size // 2, cy + emblem_size // 2)
        ]
        # Outer triangle outline
        draw.polygon(pts, outline=(244, 244, 245, alpha), width=int(2 * self.scale_factor))
        # Inner technical node
        draw.ellipse([cx - int(6 * self.scale_factor), cy + int(10 * self.scale_factor) - int(6 * self.scale_factor), cx + int(6 * self.scale_factor), cy + int(10 * self.scale_factor) + int(6 * self.scale_factor)], fill=(244, 244, 245, alpha))

        # Brand Title
        ty = cy + (emblem_size // 2) + int(40 * self.scale_factor)
        title_bbox = draw.textbbox((0, 0), brand_title, font=self.font_sans_bold)
        tw = title_bbox[2] - title_bbox[0]
        draw.text((cx - tw // 2, ty), brand_title, font=self.font_sans_bold, fill=(244, 244, 245, alpha))

        # Tagline
        if tagline and progress > 0.3:
            tag_p = ease_out_cubic(clamp((progress - 0.3) / 0.5, 0.0, 1.0))
            tag_alpha = int(tag_p * 255)
            tag_y = ty + int(48 * self.scale_factor)
            tag_bbox = draw.textbbox((0, 0), tagline, font=self.font_sans_regular)
            tgw = tag_bbox[2] - tag_bbox[0]
            draw.text((cx - tgw // 2, tag_y), tagline, font=self.font_sans_regular, fill=(161, 161, 170, tag_alpha))

        # Web URL
        if web_url and progress > 0.5:
            web_p = ease_out_cubic(clamp((progress - 0.5) / 0.4, 0.0, 1.0))
            web_alpha = int(web_p * 255)
            web_y = ty + int(90 * self.scale_factor)
            web_bbox = draw.textbbox((0, 0), web_url, font=self.font_mono)
            wbw = web_bbox[2] - web_bbox[0]
            draw.text((cx - wbw // 2, web_y), web_url, font=self.font_mono, fill=(113, 113, 122, web_alpha))
