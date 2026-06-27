import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from manim import *
import numpy as np
from PIL import Image, ImageOps

from _common import *


ASSET_DIR = Path(__file__).resolve().parents[2] / "assets"
TMP_FACE_DIR = Path("/tmp/video_manim_s02_faces")
TMP_FACE_DIR.mkdir(parents=True, exist_ok=True)


class S02_WhyHard(MovingCameraScene):
    SCENE_KEY = "scene_02"

    def construct(self):
        T = load_scene_timing(self.SCENE_KEY)
        self.add_sound(T["audio_path"])
        add_subtitles(self, T)
        self.camera.background_color = BG_NAVY

        elapsed = 0.0

        def beat_to(t_target, *anims, **kw):
            nonlocal elapsed
            rt = max(0.2, t_target - elapsed)
            if anims:
                self.play(*anims, run_time=rt, **kw)
            else:
                self.wait(rt)
            elapsed = t_target

        def stylized_face_2d(style="neutral", color=ACCENT_CYAN):
            hair = Ellipse(width=2.0, height=2.55, color=color, stroke_width=2, fill_opacity=0.05)
            face = Ellipse(width=1.72, height=2.18, color=color, stroke_width=2.2, fill_opacity=0.03)
            left_eye = Dot(LEFT * 0.28 + UP * 0.18, radius=0.04, color=color)
            right_eye = Dot(RIGHT * 0.28 + UP * 0.18, radius=0.04, color=color)
            nose = Line(UP * 0.12, DOWN * 0.12, color=color, stroke_width=2)
            if style == "smile":
                mouth = Arc(radius=0.24, start_angle=200 * DEGREES, angle=140 * DEGREES, color=color, stroke_width=2.8).shift(DOWN * 0.4)
            elif style == "frown":
                mouth = Arc(radius=0.24, start_angle=20 * DEGREES, angle=140 * DEGREES, color=color, stroke_width=2.8).shift(DOWN * 0.62)
            elif style == "under-lit":
                mouth = Arc(radius=0.2, start_angle=205 * DEGREES, angle=130 * DEGREES, color=color, stroke_width=2.6).shift(DOWN * 0.34)
                hair.set_fill(color, opacity=0.12)
                face.set_fill(color, opacity=0.01)
            elif style == "pose":
                hair = Ellipse(width=2.2, height=2.45, color=color, stroke_width=2, fill_opacity=0.05).shift(RIGHT * 0.1)
                face = Ellipse(width=1.7, height=2.12, color=color, stroke_width=2.2, fill_opacity=0.03).shift(RIGHT * 0.06)
                left_eye = Dot(LEFT * 0.23 + UP * 0.18, radius=0.04, color=color)
                right_eye = Dot(RIGHT * 0.18 + UP * 0.2, radius=0.04, color=color)
                mouth = Arc(radius=0.22, start_angle=205 * DEGREES, angle=120 * DEGREES, color=color, stroke_width=2.5).shift(DOWN * 0.34 + RIGHT * 0.04)
            else:
                mouth = Arc(radius=0.21, start_angle=205 * DEGREES, angle=130 * DEGREES, color=color, stroke_width=2.6).shift(DOWN * 0.48)
            neck = Rectangle(width=0.42, height=0.36, color=color, stroke_width=1.4, fill_opacity=0.04).shift(DOWN * 1.06)
            shoulders = Arc(radius=0.95, start_angle=200 * DEGREES, angle=140 * DEGREES, color=color, stroke_width=2).shift(DOWN * 1.25)
            return VGroup(hair, face, left_eye, right_eye, nose, mouth, neck, shoulders)

        def square_face_path(name):
            for ext in (".jpg", ".jpeg", ".png"):
                src = ASSET_DIR / f"{name}{ext}"
                if not src.exists():
                    continue
                stat = src.stat()
                cache_name = f"{src.stem}_{stat.st_size}_{int(stat.st_mtime)}.png"
                cache = TMP_FACE_DIR / cache_name
                if not cache.exists():
                    with Image.open(src) as im:
                        im = im.convert("RGB")
                        side = max(im.size)
                        im = ImageOps.fit(
                            im,
                            (side, side),
                            method=Image.Resampling.LANCZOS,
                            centering=(0.5, 0.42),
                        )
                        im.save(cache)
                return cache
            return None

        def load_face(name, fallback_style="neutral", color=ACCENT_CYAN, height=2.7):
            p = square_face_path(name)
            if p is not None:
                img = ImageMobject(str(p))
                img.set_height(height)
                return img
            mob = stylized_face_2d(style=fallback_style, color=color)
            mob.set_height(height)
            return mob

        def face_card(name, fallback_style="neutral", color=ACCENT_CYAN, height=2.75, frame_color=None):
            frame_color = frame_color or color
            img = load_face(name, fallback_style=fallback_style, color=color, height=height)
            size = max(img.width, img.height)
            plate = RoundedRectangle(
                width=size + 0.20,
                height=size + 0.20,
                corner_radius=0.12,
                color=frame_color,
                stroke_width=1.8,
                fill_color=BG_NAVY_SOFT,
                fill_opacity=0.72,
            ).move_to(img)
            border = RoundedRectangle(
                width=size + 0.20,
                height=size + 0.20,
                corner_radius=0.12,
                color=frame_color,
                stroke_width=1.8,
                fill_opacity=0.0,
            ).move_to(img)
            return Group(plate, img, border)

        def panel_box(width=6.05, height=4.12, color=ACCENT_BLUE):
            return RoundedRectangle(
                width=width,
                height=height,
                corner_radius=0.14,
                color=color,
                stroke_width=1.6,
                fill_color=BG_NAVY_SOFT,
                fill_opacity=0.62,
            )

        def pixel_grid(mob, rows=9, cols=9, color=ACCENT_BLUE, stroke_width=0.55, opacity=0.24):
            grid = VGroup()
            w = mob.width
            h = mob.height
            dx = w / cols
            dy = h / rows
            side = min(dx, dy) * 0.92
            origin = mob.get_center() + LEFT * (w / 2) + DOWN * (h / 2)
            for r in range(rows):
                for c in range(cols):
                    sq = Square(side_length=side, stroke_width=stroke_width, stroke_color=GRID_LINE)
                    sq.set_fill(color, opacity=opacity)
                    sq.move_to(origin + RIGHT * (dx * (c + 0.5)) + UP * (dy * (r + 0.5)))
                    grid.add(sq)
            return grid

        title = en_label("What troubles AI most?", color=TEXT_PRIMARY, scale=0.56, bold=True).move_to(UP * 2.85)
        title_box = SurroundingRectangle(title, color=ACCENT_BLUE, buff=0.18, stroke_width=1.2)
        neutral = face_card("s2_same_neutral", fallback_style="neutral", color=ACCENT_CYAN, height=2.9, frame_color=ACCENT_BLUE).move_to(ORIGIN + DOWN * 0.15)
        beat_to(0.42, FadeIn(title, scale=0.84), Create(title_box), FadeIn(neutral, shift=DOWN * 0.08))
        self.play(Indicate(title, color=ACCENT_CYAN), run_time=0.35)
        elapsed = max(elapsed, 0.77)
        beat_to(seg_end(T, 0), title.animate.scale(1.0), neutral.animate.scale(1.0))

        face_a = face_card("s2_personA", fallback_style="smile", color=ACCENT_CYAN, height=2.55, frame_color=ACCENT_CYAN).move_to(LEFT * 3.15 + DOWN * 0.15)
        face_b = face_card("s2_personB", fallback_style="pose", color=ACCENT_LAVENDER, height=2.55, frame_color=ACCENT_LAVENDER).move_to(RIGHT * 3.15 + DOWN * 0.15)
        diff_lbl = en_label("Different people", color=TEXT_MUTED, scale=0.42, bold=True).move_to(DOWN * 2.8)
        not_lbl = VGroup(MathTex(r"\times", color=ACCENT_CORAL).scale(0.7), en_label("not the hard part", color=ACCENT_CORAL, scale=0.34, bold=True)).arrange(RIGHT, buff=0.22)
        not_lbl.move_to(DOWN * 2.3)
        beat_to(
            T["segments"][1]["start"],
            FadeOut(neutral, shift=DOWN * 0.08),
            FadeOut(title_box),
            FadeIn(face_a, shift=LEFT * 0.2),
            FadeIn(face_b, shift=RIGHT * 0.2),
            FadeIn(diff_lbl, shift=UP * 0.08),
        )
        beat_to(
            2.72,
            FadeIn(not_lbl, shift=UP * 0.06),
            face_a.animate.set_opacity(0.76),
            face_b.animate.set_opacity(0.76),
        )
        beat_to(
            seg_end(T, 1),
            face_a.animate.set_opacity(0.22),
            face_b.animate.set_opacity(0.22),
            diff_lbl.animate.set_opacity(0.42),
            not_lbl.animate.set_opacity(0.56),
        )

        same_lbl = en_label("Same person", color=ACCENT_MINT, scale=0.54, bold=True).move_to(UP * 2.7)
        same_names = [
            ("s2_same_neutral", "neutral"),
            ("s2_same_smile", "smile"),
            ("s2_same_frown", "frown"),
            ("s2_same_lowlight", "under-lit"),
            ("s2_same_pose", "pose"),
        ]
        same_positions = [LEFT * 4.45, LEFT * 2.2, ORIGIN, RIGHT * 2.2, RIGHT * 4.45]
        same_cards = [
            face_card(name, fallback_style=style, color=ACCENT_MINT if i == 0 else ACCENT_CYAN, height=1.82, frame_color=ACCENT_MINT if i == 0 else ACCENT_BLUE).move_to(same_positions[i] + DOWN * 0.05)
            for i, (name, style) in enumerate(same_names)
        ]
        same_rings = VGroup(*[
            SurroundingRectangle(card, color=ACCENT_MINT if i == 0 else ACCENT_BLUE, buff=0.06, stroke_width=1.1)
            for i, card in enumerate(same_cards)
        ])
        same_note = en_label("looks like two completely different people", color=TEXT_MUTED, scale=0.31).move_to(DOWN * 2.68)
        beat_to(
            T["segments"][2]["start"],
            FadeOut(title, shift=UP * 0.08),
            FadeOut(face_a, shift=LEFT * 0.15),
            FadeOut(face_b, shift=RIGHT * 0.15),
            FadeOut(diff_lbl),
            FadeOut(not_lbl),
            FadeIn(same_lbl, scale=0.82),
            FadeIn(same_cards[0], shift=DOWN * 0.08),
            FadeIn(same_rings[0], shift=DOWN * 0.03),
            FadeIn(same_note, shift=UP * 0.05),
        )
        for idx in range(1, len(same_cards)):
            beat_to(
                4.54 + 0.78 * idx,
                FadeIn(same_cards[idx], shift=UP * 0.06),
                Create(same_rings[idx]),
                same_cards[idx - 1].animate.set_opacity(0.62),
                same_rings[idx - 1].animate.set_opacity(0.28),
            )
        beat_to(
            seg_end(T, 2),
            same_cards[-1].animate.set_opacity(0.96),
            same_rings[-1].animate.set_opacity(0.9),
            same_note.animate.set_opacity(0.6),
        )

        current = face_card("s2_same_smile", fallback_style="smile", color=ACCENT_CYAN, height=2.48, frame_color=ACCENT_CYAN).move_to(ORIGIN + UP * 0.05)
        current_tag = en_label("smile", color=ACCENT_CYAN, scale=0.33, bold=True).next_to(current, UP, buff=0.08)
        beat_to(
            T["segments"][3]["start"],
            FadeOut(same_lbl),
            FadeOut(same_note),
            FadeOut(Group(*same_cards), shift=DOWN * 0.08),
            FadeOut(same_rings),
            FadeIn(current, shift=UP * 0.06),
            FadeIn(current_tag, scale=0.88),
        )

        frown = face_card("s2_same_frown", fallback_style="frown", color=ACCENT_LAVENDER, height=2.48, frame_color=ACCENT_LAVENDER).move_to(ORIGIN + UP * 0.05)
        frown_tag = en_label("frown", color=ACCENT_LAVENDER, scale=0.33, bold=True).next_to(frown, UP, buff=0.08)
        under = face_card("s2_same_lowlight", fallback_style="under-lit", color=ACCENT_CORAL, height=2.48, frame_color=ACCENT_CORAL).move_to(ORIGIN + UP * 0.05)
        under_tag = en_label("under-lit", color=ACCENT_CORAL, scale=0.33, bold=True).next_to(under, UP, buff=0.08)
        pose = face_card("s2_same_pose", fallback_style="pose", color=ACCENT_MINT, height=2.48, frame_color=ACCENT_MINT).move_to(ORIGIN + UP * 0.05)
        pose_tag = en_label("pose", color=ACCENT_MINT, scale=0.33, bold=True).next_to(pose, UP, buff=0.08)

        beat_to(
            10.0,
            FadeOut(current, shift=LEFT * 0.18),
            FadeIn(frown, shift=RIGHT * 0.16),
            FadeOut(current_tag),
            FadeIn(frown_tag, scale=0.88),
        )
        beat_to(
            11.0,
            FadeOut(frown, shift=LEFT * 0.18),
            FadeIn(under, shift=RIGHT * 0.16),
            FadeOut(frown_tag),
            FadeIn(under_tag, scale=0.88),
        )
        beat_to(
            seg_end(T, 3),
            FadeOut(under, shift=LEFT * 0.18),
            FadeIn(pose, shift=RIGHT * 0.16),
            FadeOut(under_tag),
            FadeIn(pose_tag, scale=0.88),
        )

        pixel_left = face_card("s2_same_smile", fallback_style="smile", color=ACCENT_CYAN, height=2.25, frame_color=ACCENT_CYAN).move_to(LEFT * 2.8 + DOWN * 0.05)
        pixel_right = face_card("s2_same_lowlight", fallback_style="under-lit", color=ACCENT_LAVENDER, height=2.25, frame_color=ACCENT_LAVENDER).move_to(RIGHT * 2.8 + DOWN * 0.05)
        pixel_lbl = en_label("Pixel matrix changes entirely", color=ACCENT_CORAL, scale=0.43, bold=True).move_to(UP * 2.68)
        grid_left = pixel_grid(pixel_left[1], rows=9, cols=9, color=ACCENT_BLUE, opacity=0.18)
        grid_right = pixel_grid(pixel_right[1], rows=9, cols=9, color=ACCENT_BLUE, opacity=0.18)
        wash_left = Rectangle(width=pixel_left[1].width + 0.04, height=pixel_left[1].height + 0.04, color=ACCENT_CORAL, stroke_width=0, fill_color=ACCENT_CORAL, fill_opacity=0.0).move_to(pixel_left[1])
        wash_right = Rectangle(width=pixel_right[1].width + 0.04, height=pixel_right[1].height + 0.04, color=ACCENT_CORAL, stroke_width=0, fill_color=ACCENT_CORAL, fill_opacity=0.0).move_to(pixel_right[1])
        wash_left.set_fill(ACCENT_CORAL, opacity=0.16)
        wash_right.set_fill(ACCENT_CORAL, opacity=0.16)
        beat_to(
            T["segments"][4]["start"],
            FadeOut(pose, shift=LEFT * 0.15),
            FadeOut(pose_tag),
            FadeIn(pixel_left, shift=LEFT * 0.12),
            FadeIn(pixel_right, shift=RIGHT * 0.12),
            FadeIn(pixel_lbl, scale=0.82),
            FadeIn(grid_left),
            FadeIn(grid_right),
        )
        beat_to(
            13.36,
            AnimationGroup(
                *[
                    sq.animate.set_fill(ACCENT_CORAL, opacity=0.48).set_stroke(ACCENT_CORAL, opacity=0.82)
                    for sq in list(grid_left) + list(grid_right)
                ],
                lag_ratio=0.008,
            ),
            FadeIn(wash_left),
            FadeIn(wash_right),
        )
        beat_to(
            seg_end(T, 4),
            pixel_lbl.animate.set_color(ACCENT_LAVENDER),
            pixel_left.animate.set_opacity(0.68),
            pixel_right.animate.set_opacity(0.68),
        )

        variance_lbl = en_label("Intra-class variance", color=ACCENT_LAVENDER, scale=0.62, bold=True).move_to(ORIGIN + UP * 0.12)
        variance_box = SurroundingRectangle(variance_lbl, color=ACCENT_LAVENDER, buff=0.22, stroke_width=2.2)
        beat_to(
            T["segments"][5]["start"],
            FadeOut(pixel_left, shift=LEFT * 0.12),
            FadeOut(pixel_right, shift=RIGHT * 0.12),
            FadeOut(grid_left),
            FadeOut(grid_right),
            FadeOut(wash_left),
            FadeOut(wash_right),
            FadeOut(pixel_lbl),
            FadeIn(variance_lbl, scale=0.84),
            Create(variance_box),
        )
        beat_to(
            seg_end(T, 5),
            variance_lbl.animate.scale(1.0),
        )

        paradox_lbl = en_label("Paradox", color=TEXT_PRIMARY, scale=0.56, bold=True).move_to(UP * 2.72)
        sweep = Line(UP * 3.05, DOWN * 3.05, color=ACCENT_CYAN, stroke_width=10, stroke_opacity=0.26).shift(LEFT * 6.8)
        left_panel = panel_box(color=ACCENT_MINT).move_to(LEFT * 3.32 + DOWN * 0.12)
        right_panel = panel_box(color=ACCENT_CYAN).move_to(RIGHT * 3.32 + DOWN * 0.12)
        divider = Line(UP * 2.08, DOWN * 2.08, color=ACCENT_BLUE, stroke_width=2.2).set_opacity(0.65)
        left_head = en_label("Tolerant", color=ACCENT_MINT, scale=0.5, bold=True).move_to(left_panel.get_top() + DOWN * 0.36)
        right_head = en_label("Sharp", color=ACCENT_CYAN, scale=0.5, bold=True).move_to(right_panel.get_top() + DOWN * 0.36)
        beat_to(
            T["segments"][6]["start"],
            FadeOut(variance_lbl),
            FadeOut(variance_box),
            FadeIn(paradox_lbl, scale=0.86),
            FadeIn(left_panel),
            FadeIn(right_panel),
            FadeIn(divider),
        )
        self.play(sweep.animate.shift(RIGHT * 13.6), run_time=0.5, rate_func=linear)
        elapsed = max(elapsed, T["segments"][6]["start"] + 0.5)
        beat_to(
            19.4,
            FadeIn(left_head, shift=UP * 0.05),
            FadeIn(right_head, shift=UP * 0.05),
        )

        tolerant_imgs = [
            face_card("s2_same_neutral", fallback_style="neutral", color=ACCENT_MINT, height=1.22, frame_color=ACCENT_MINT).move_to(LEFT * 4.34 + UP * 0.56),
            face_card("s2_same_smile", fallback_style="smile", color=ACCENT_MINT, height=1.22, frame_color=ACCENT_MINT).move_to(LEFT * 2.78 + UP * 0.56),
            face_card("s2_same_frown", fallback_style="frown", color=ACCENT_MINT, height=1.22, frame_color=ACCENT_MINT).move_to(LEFT * 4.34 + DOWN * 0.76),
            face_card("s2_same_lowlight", fallback_style="under-lit", color=ACCENT_MINT, height=1.22, frame_color=ACCENT_MINT).move_to(LEFT * 2.78 + DOWN * 0.76),
        ]
        tolerant_glow = RoundedRectangle(width=3.45, height=2.95, corner_radius=0.14, color=ACCENT_MINT, stroke_width=2.2, fill_color=ACCENT_MINT, fill_opacity=0.04).move_to(LEFT * 3.55 + DOWN * 0.1)
        forgive = VGroup(MathTex(r"\checkmark", color=ACCENT_MINT).scale(0.55), en_label("forgive variation", color=ACCENT_MINT, scale=0.32, bold=True)).arrange(RIGHT, buff=0.18)
        forgive.move_to(LEFT * 3.55 + DOWN * 1.95)
        beat_to(
            T["segments"][7]["start"],
            FadeIn(tolerant_glow),
            LaggedStart(*[FadeIn(m, shift=UP * 0.05) for m in tolerant_imgs], lag_ratio=0.08),
            FadeIn(forgive, shift=UP * 0.05),
        )
        beat_to(
            23.1,
            Indicate(forgive[0], color=ACCENT_MINT),
            tolerant_glow.animate.set_stroke(ACCENT_MINT, width=2.8),
        )
        beat_to(
            seg_end(T, 7),
            left_panel.animate.set_fill(BG_NAVY_SOFT, opacity=0.72),
            right_panel.animate.set_fill(BG_NAVY_SOFT, opacity=0.48),
        )

        sharp_imgs = [
            face_card("s2_personA", fallback_style="smile", color=ACCENT_CYAN, height=1.48, frame_color=ACCENT_CYAN).move_to(RIGHT * 2.05 + UP * 0.26),
            face_card("s2_personB", fallback_style="pose", color=ACCENT_LAVENDER, height=1.48, frame_color=ACCENT_LAVENDER).move_to(RIGHT * 4.52 + UP * 0.26),
        ]
        tiny_lbl = en_label("tiniest detail", color=ACCENT_CORAL, scale=0.34, bold=True).move_to(RIGHT * 3.0 + DOWN * 1.05)
        detail_circle = Circle(radius=0.18, color=ACCENT_CORAL, stroke_width=2.4).move_to(RIGHT * 4.72 + UP * 0.48)
        detail_arrow = thin_curved_arrow(RIGHT * 3.0 + DOWN * 0.52, detail_circle.get_center(), color=ACCENT_CORAL, stroke_width=2.3, tip_length=0.14, angle=0.55)
        beat_to(
            T["segments"][8]["start"],
            FadeOut(Group(*tolerant_imgs), shift=DOWN * 0.05),
            FadeOut(forgive),
            FadeOut(tolerant_glow),
            FadeIn(sharp_imgs[0], shift=LEFT * 0.08),
            FadeIn(sharp_imgs[1], shift=RIGHT * 0.08),
            FadeIn(detail_circle),
            FadeIn(detail_arrow),
            FadeIn(tiny_lbl, shift=UP * 0.05),
        )
        beat_to(
            26.0,
            self.camera.frame.animate.scale(0.68).move_to(detail_circle.get_center() + LEFT * 0.24 + DOWN * 0.08),
            detail_circle.animate.set_stroke(ACCENT_CORAL, width=3.4),
            sharp_imgs[1].animate.set_opacity(0.92),
        )
        beat_to(
            28.72,
            right_head.animate.set_color(ACCENT_CORAL),
            tiny_lbl.animate.set_color(ACCENT_CORAL),
        )

        tail = max(0.0, T["duration"] - elapsed - 0.05)
        if tail > 0.05:
            self.wait(tail)
