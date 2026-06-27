import os
import sys
from pathlib import Path
from PIL import Image, ImageOps

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from manim import *
import numpy as np
from _common import *

ASSET_DIR = Path(__file__).resolve().parents[2] / "assets"
TMP_IMG_DIR = Path("/tmp/video_manim_s06_imgs")
TMP_IMG_DIR.mkdir(parents=True, exist_ok=True)



class S06_Jet(ThreeDScene):
    SCENE_KEY = "scene_06"

    def construct(self):
        T = load_scene_timing(self.SCENE_KEY)
        self.add_sound(T["audio_path"])
        add_subtitles(self, T)
        self.camera.background_color = BG_NAVY
        self.set_camera_orientation(phi=0 * DEGREES, theta=-90 * DEGREES, zoom=1.0)

        elapsed = 0.0

        def beat_to(t_target, *anims, **kw):
            nonlocal elapsed
            rt = max(0.2, t_target - elapsed)
            if anims:
                self.play(*anims, run_time=rt, **kw)
            else:
                self.wait(rt)
            elapsed = t_target

        def square_cache(path):
            stat = path.stat()
            cache_name = f"{path.stem}_{stat.st_size}_{int(stat.st_mtime)}.png"
            cache = TMP_IMG_DIR / cache_name
            if not cache.exists():
                with Image.open(path) as im:
                    im = im.convert("RGB")
                    side = max(im.size)
                    im = ImageOps.fit(im, (side, side), method=Image.Resampling.LANCZOS, centering=(0.5, 0.45))
                    im.save(cache)
            return cache

        def load_face(name, fallback_style="neutral", color=ACCENT_CYAN, height=2.2):
            for ext in (".png", ".jpg", ".jpeg"):
                p = ASSET_DIR / f"{name}{ext}"
                if p.exists():
                    img = ImageMobject(str(square_cache(p) if p.name.startswith("s2_") or p.name in ("face.png", "face_hd.png") else p))
                    img.scale_to_fit_height(height)
                    return img
            raise FileNotFoundError(f"Asset {name} not found in {ASSET_DIR}")

        def eye_crop_cache(path):
            stat = path.stat()
            cache_name = f"{path.stem}_eye_{stat.st_size}_{int(stat.st_mtime)}.png"
            cache = TMP_IMG_DIR / cache_name
            if not cache.exists():
                sq_path = square_cache(path)
                with Image.open(sq_path) as im:
                    w, h = im.size
                    cx = int(w * 0.37)
                    cy = int(h * 0.41)
                    r = int(w * 0.08)
                    cropped = im.crop((cx - r, cy - r, cx + r, cy + r))
                    cropped.save(cache)
            return cache

        def label(text, pos, color=TEXT_PRIMARY, scale=0.36, bold=False):
            return en_label(text, color=color, scale=scale, bold=bold).move_to(pos)

        def wavelet(angle=0.0, freq=3.0, color=ACCENT_CYAN, length=0.62):
            direction = np.array([np.cos(angle), np.sin(angle), 0])
            perp = np.array([-np.sin(angle), np.cos(angle), 0])
            curve = ParametricFunction(
                lambda t, d=direction, p=perp, f=freq: t * d + 0.075 * np.sin(14 * f * t) * np.exp(-2.4 * t) * p,
                t_range=[0.0, length],
                color=color,
                stroke_width=1.7,
            )
            dot = Dot(ORIGIN, radius=0.025, color=color)
            return VGroup(curve, dot)

        def wavelet_bank():
            bank = VGroup()
            for r in range(5):
                for c in range(8):
                    color = interpolate_color(ManimColor(ACCENT_CYAN), ManimColor(ACCENT_LAVENDER), c / 7)
                    w = wavelet(angle=c * PI / 8, freq=1.8 + r * 0.45, color=color, length=0.48).scale(0.8)
                    w.move_to([c * 0.72 - 2.52, 1.28 - r * 0.58, 0])
                    bank.add(w)
            box = SurroundingRectangle(bank, color=ACCENT_BLUE, buff=0.22, stroke_width=1.5)
            return VGroup(bank, box)

        def make_face_card(img):
            frame = RoundedRectangle(
                width=2.1,
                height=2.3,
                corner_radius=0.10,
                color=ACCENT_BLUE,
                stroke_width=1.6,
                fill_color=BG_NAVY_SOFT,
                fill_opacity=0.6,
            )
            content = img.copy().set_height(2.18)
            content.move_to(frame.get_center())
            return Group(frame, content)

        def complex_cards():
            cards = VGroup()
            for i in range(8):
                x = (i % 4) * 1.05 - 1.58
                y = 0.55 - (i // 4) * 0.92
                box = RoundedRectangle(
                    width=0.88,
                    height=0.58,
                    corner_radius=0.08,
                    color=ACCENT_LAVENDER,
                    stroke_width=1.4,
                    fill_color=ACCENT_LAVENDER,
                    fill_opacity=0.055,
                ).move_to([x, y, 0])
                m = MathTex(
                    rf"z_{{{i}}}",
                    tex_template=EN_TEX_TEMPLATE,
                    color=ACCENT_LAVENDER,
                ).scale(0.48).move_to(box)
                cards.add(VGroup(box, m))
            more = label(r"... x40", [2.05, 0.05, 0], color=ACCENT_LAVENDER, scale=0.44, bold=True)
            return VGroup(cards, more)

        def jet_stack():
            stack = VGroup()
            colors = [ACCENT_BLUE, ACCENT_TEAL, ACCENT_CYAN, ACCENT_LAVENDER, ACCENT_MINT]
            for k, color in enumerate(colors):
                disk = VGroup()
                for s in range(8):
                    disk.add(
                        AnnularSector(
                            inner_radius=0.22,
                            outer_radius=0.82,
                            start_angle=s * TAU / 8,
                            angle=TAU / 8,
                            color=interpolate_color(ManimColor(color), ManimColor(ACCENT_LAVENDER), s / 10),
                            fill_opacity=0.46,
                            stroke_color=BG_NAVY,
                            stroke_width=0.7,
                        )
                    )
                disk.scale([1.22, 0.34, 1]).shift(UP * k * 0.26 + RIGHT * k * 0.11)
                stack.add(disk)
            return stack

        def barcode():
            bars = VGroup()
            widths = [0.08, 0.16, 0.10, 0.24, 0.09, 0.18, 0.12, 0.28, 0.08, 0.20, 0.12, 0.18]
            x = -1.55
            for i, w in enumerate(widths):
                h = 1.0 + 0.55 * ((i * 7) % 5) / 4
                rect = Rectangle(width=w, height=h, stroke_width=0, fill_color=ACCENT_CYAN if i % 3 else ACCENT_LAVENDER, fill_opacity=0.72)
                rect.move_to([x + w / 2, 0, 0])
                bars.add(rect)
                x += w + 0.08
            frame = SurroundingRectangle(bars, color=ACCENT_BLUE, buff=0.22, stroke_width=1.5)
            return VGroup(frame, bars)

        title = label(r"Jet = 40 complex responses at one point", UP * 3.25, color=TEXT_PRIMARY, scale=0.50, bold=True)

        # B0-B1: Gabor wavelets bank setup
        bank = wavelet_bank().scale(1.08).move_to(DOWN * 0.15)
        bank_lbl = label(r"whole bank of Gabor wavelets", UP * 2.6, color=ACCENT_CYAN, scale=0.36, bold=True)
        beat_to(seg_end(T, 0), FadeIn(title, scale=0.85), FadeIn(bank_lbl), LaggedStart(*[FadeIn(w, scale=0.7) for w in bank[0]], lag_ratio=0.015), Create(bank[1]))

        mult = label(r"5 frequencies x 8 orientations = 40", DOWN * 2.75, color=ACCENT_LAVENDER, scale=0.46, bold=True)
        row_braces = VGroup()
        for r in range(5):
            y_r = (1.28 - r * 0.58) * 1.08 + (-0.15)
            row_braces.add(
                Line(
                    LEFT * 2.8 + UP * y_r,
                    RIGHT * 2.8 + UP * y_r,
                    color=ACCENT_BLUE,
                    stroke_width=0.8
                ).set_opacity(0.18)
            )
        beat_to(seg_end(T, 1), FadeIn(mult, shift=UP * 0.08), LaggedStart(*[Create(line) for line in row_braces], lag_ratio=0.05))

        # B2: Real face image setup and eye corner focus zoom.
        face_img = load_face("face_hd", fallback_style="neutral", color=ACCENT_CYAN, height=2.2)
        face_card = make_face_card(face_img).move_to(LEFT * 3.4 - UP * 0.1)
        focus_pos = face_card[0].get_center() + np.array([-0.28, 0.20, 0])
        focus_dot = Dot(focus_pos, radius=0.045, color=ACCENT_MINT)
        focus_ring = Circle(radius=0.15, color=ACCENT_MINT, stroke_width=2.2).move_to(focus_pos)

        # Magnifier setup using pre-cropped eye corner image
        mag_center = np.array([-1.4, 0.1, 0])
        magnifier_box = RoundedRectangle(
            width=1.2,
            height=1.2,
            corner_radius=0.08,
            color=ACCENT_MINT,
            stroke_width=1.8,
            fill_color=BG_NAVY_SOFT,
            fill_opacity=1.0,
        ).move_to(mag_center)
        mag_face = ImageMobject(str(eye_crop_cache(ASSET_DIR / "face_hd.png")))
        mag_face.set_height(1.14)
        mag_face.move_to(mag_center)
        mag_group = Group(mag_face, magnifier_box)

        connector = Line(focus_pos, [mag_center[0] - 0.6, mag_center[1], 0], color=ACCENT_MINT, stroke_width=1.6).set_opacity(0.6)
        eye_lbl = label("one eye corner", LEFT * 3.4 + DOWN * 1.86, color=ACCENT_MINT, scale=0.32, bold=True)

        face_group = Group(face_card, focus_dot, focus_ring, mag_group, connector, eye_lbl)

        small_bank = bank[0].copy().scale(0.36).arrange_in_grid(rows=5, cols=8, buff=0.07).move_to(RIGHT * 2.65 + DOWN * 0.05)
        converge = VGroup()
        for idx in [0, 8, 16, 24, 32]:
            arrow = thin_arrow(small_bank[idx].get_center(), focus_pos, color=ACCENT_CYAN, stroke_width=1.5, buff=0.15)
            converge.add(arrow)

        beat_to(
            seg_end(T, 2),
            FadeOut(bank),
            FadeOut(bank_lbl),
            FadeOut(row_braces),
            mult.animate.scale(0.72).move_to(UP * 2.45),
            FadeIn(face_group, shift=RIGHT * 0.08),
            FadeIn(small_bank, shift=LEFT * 0.08),
            LaggedStart(*[GrowArrow(a) for a in converge], lag_ratio=0.035),
        )

        # B3: complex numbers.
        cards = complex_cards().scale(1.12).move_to(RIGHT * 1.7 + DOWN * 0.02)
        z_formula = MathTex(r"z_j=a_j e^{i\phi_j}", tex_template=EN_TEX_TEMPLATE, color=MATH_YELLOW).scale(0.74).move_to(RIGHT * 1.7 + UP * 1.45)
        beat_to(
            seg_end(T, 3),
            FadeOut(small_bank),
            FadeOut(converge),
            FadeIn(cards, shift=LEFT * 0.08),
            Write(z_formula),
        )

        # B4: bundle into a Jet.
        stack = jet_stack().scale(1.35).move_to(ORIGIN + UP * 0.05)
        jet_lbl = label(r"JET", DOWN * 1.7, color=ACCENT_LAVENDER, scale=0.72, bold=True)
        jet_box = SurroundingRectangle(stack, color=ACCENT_LAVENDER, buff=0.28, stroke_width=2.0)
        beat_to(
            seg_end(T, 4),
            FadeOut(face_group),
            FadeOut(cards),
            FadeOut(z_formula),
            mult.animate.set_opacity(0.25),
            LaggedStart(*[FadeIn(d, shift=UP * 0.10) for d in stack], lag_ratio=0.10),
            Create(jet_box),
            FadeIn(jet_lbl, shift=UP * 0.05),
        )

        # B5: barcode metaphor.
        code = barcode().scale(1.45).move_to(ORIGIN)
        code_lbl = label(r"unique barcode of that eye corner", DOWN * 1.85, color=ACCENT_CYAN, scale=0.40, bold=True)
        beat_to(
            seg_end(T, 5),
            FadeOut(stack),
            FadeOut(jet_box),
            jet_lbl.animate.move_to(UP * 1.95).scale(0.62),
            FadeIn(code[0]),
            LaggedStart(*[GrowFromEdge(b, DOWN) for b in code[1]], lag_ratio=0.035),
            FadeIn(code_lbl),
        )

        # B6: complex elements split into two useful parts.
        element = MathTex(r"z_j=a_j e^{i\phi_j}", tex_template=EN_TEX_TEMPLATE, color=MATH_YELLOW).scale(1.05).move_to(UP * 1.0)
        amp_card = RoundedRectangle(width=3.2, height=2.4, corner_radius=0.14, color=ACCENT_MINT, stroke_width=1.8, fill_color=ACCENT_MINT, fill_opacity=0.06).move_to(LEFT * 2.4 - UP * 0.9)
        phase_card = RoundedRectangle(width=3.2, height=2.4, corner_radius=0.14, color=ACCENT_LAVENDER, stroke_width=1.8, fill_color=ACCENT_LAVENDER, fill_opacity=0.06).move_to(RIGHT * 2.4 - UP * 0.9)
        
        amp_lbl = label(r"Amplitude", amp_card.get_top() + DOWN * 0.35, color=ACCENT_MINT, scale=0.38, bold=True)
        phase_lbl = label(r"Phase", phase_card.get_top() + DOWN * 0.35, color=ACCENT_LAVENDER, scale=0.38, bold=True)
        two_weapons = label(r"two weapons", UP * 1.8, color=TEXT_PRIMARY, scale=0.42, bold=True)
        
        split_arrows = VGroup(
            thin_arrow(element.get_bottom() + LEFT * 0.15, amp_card.get_top(), color=ACCENT_MINT, stroke_width=2.2, buff=0.10),
            thin_arrow(element.get_bottom() + RIGHT * 0.15, phase_card.get_top(), color=ACCENT_LAVENDER, stroke_width=2.2, buff=0.10),
        )
        beat_to(
            seg_end(T, 6),
            FadeOut(code),
            FadeOut(code_lbl),
            FadeOut(jet_lbl),
            FadeOut(mult),
            FadeIn(two_weapons, shift=DOWN * 0.05),
            Write(element),
            GrowArrow(split_arrows[0]),
            GrowArrow(split_arrows[1]),
            FadeIn(amp_card),
            FadeIn(phase_card),
            FadeIn(amp_lbl),
            FadeIn(phase_lbl),
        )

        # B7: amplitude tells shape.
        shape_icon = VGroup(
            Arc(radius=0.42, start_angle=10 * DEGREES, angle=160 * DEGREES, color=ACCENT_MINT, stroke_width=3),
            Arc(radius=0.42, start_angle=190 * DEGREES, angle=160 * DEGREES, color=ACCENT_MINT, stroke_width=3),
            Dot(ORIGIN, radius=0.04, color=ACCENT_MINT),
        ).move_to(amp_card.get_center() - UP * 0.1)
        amp_note = label(r"what shape?", amp_card.get_bottom() + UP * 0.35, color=ACCENT_MINT, scale=0.30, bold=True)
        
        beat_to(
            seg_end(T, 7),
            amp_card.animate.set_fill(ACCENT_MINT, opacity=0.13).set_stroke(ACCENT_MINT, width=2.6),
            phase_card.animate.set_opacity(0.35),
            phase_lbl.animate.set_opacity(0.35),
            Create(shape_icon),
            FadeIn(amp_note),
        )

        # B8: phase tells coordinate.
        crosshair = VGroup(
            Circle(radius=0.28, color=ACCENT_LAVENDER, stroke_width=2.0),
            Line(LEFT * 0.45, RIGHT * 0.45, color=ACCENT_LAVENDER, stroke_width=2.0),
            Line(DOWN * 0.45, UP * 0.45, color=ACCENT_LAVENDER, stroke_width=2.0),
            Dot(ORIGIN, radius=0.045, color=ACCENT_LAVENDER),
        ).move_to(phase_card.get_center() - UP * 0.1)
        coord_note = label(r"which coordinate?", phase_card.get_bottom() + UP * 0.35, color=ACCENT_LAVENDER, scale=0.30, bold=True)
        conclusion = label(r"Amplitude -> shape   |   Phase -> coordinate", DOWN * 2.65, color=MATH_YELLOW, scale=0.34, bold=True)
        
        beat_to(
            seg_end(T, 8),
            phase_card.animate.set_opacity(1.0).set_fill(ACCENT_LAVENDER, opacity=0.13).set_stroke(ACCENT_LAVENDER, width=2.6),
            phase_lbl.animate.set_opacity(1.0),
            amp_card.animate.set_opacity(0.82),
            Create(crosshair),
            FadeIn(coord_note),
            FadeIn(conclusion, shift=UP * 0.05),
        )

        tail = max(0.0, T["duration"] - elapsed - 0.18)
        if tail > 0.05:
            self.wait(tail)
