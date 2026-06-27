import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from manim import *
import numpy as np
from _common import *


class S13_Feret(Scene):
    SCENE_KEY = "scene_13"

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

        def label(text, pos, color=TEXT_PRIMARY, scale=0.36, bold=False):
            return en_label(text, color=color, scale=scale, bold=bold).move_to(pos)

        def silhouette(kind, color=TEXT_MUTED, scale=1.0):
            if kind == "frontal":
                face = Ellipse(width=0.62, height=0.78, color=color, stroke_width=1.1)
                eyes = VGroup(Dot(LEFT * 0.13 + UP * 0.10, radius=0.022, color=color), Dot(RIGHT * 0.13 + UP * 0.10, radius=0.022, color=color))
                nose = Line(UP * 0.02, DOWN * 0.13, color=color, stroke_width=1.0)
                mouth = Arc(radius=0.11, start_angle=205 * DEGREES, angle=130 * DEGREES, color=color, stroke_width=1.0).shift(DOWN * 0.22)
                return VGroup(face, eyes, nose, mouth).scale(scale)
            if kind == "half":
                face = Ellipse(width=0.54, height=0.78, color=color, stroke_width=1.1)
                eye = Dot(LEFT * 0.05 + UP * 0.10, radius=0.024, color=color)
                nose = VMobject(color=color, stroke_width=1.1).set_points_as_corners([UP * 0.06, LEFT * 0.24 + DOWN * 0.02, LEFT * 0.08 + DOWN * 0.13])
                mouth = Line(LEFT * 0.12 + DOWN * 0.24, RIGHT * 0.06 + DOWN * 0.22, color=color, stroke_width=1.0)
                return VGroup(face, eye, nose, mouth).scale(scale)
            line = VMobject(color=color, stroke_width=1.3)
            line.set_points_as_corners([
                np.array([0.04, 0.42, 0]),
                np.array([-0.14, 0.30, 0]),
                np.array([-0.17, 0.11, 0]),
                np.array([-0.38, 0.02, 0]),
                np.array([-0.16, -0.08, 0]),
                np.array([-0.22, -0.20, 0]),
                np.array([-0.06, -0.35, 0]),
            ])
            back = Arc(radius=0.42, start_angle=-70 * DEGREES, angle=142 * DEGREES, color=color, stroke_width=1.1).shift(RIGHT * 0.09)
            eye = Dot(LEFT * 0.11 + UP * 0.16, radius=0.021, color=color)
            return VGroup(back, line, eye).scale(scale)

        def result_row(y, title, detail, value, color, kinds):
            left_x = -5.55
            row = VGroup()
            pose_icons = VGroup()
            for i, kind in enumerate(kinds):
                icon = silhouette(kind, color=color, scale=0.65).move_to(np.array([left_x + i * 0.62, y, 0]))
                pose_icons.add(icon)
                
            name = label(title, ORIGIN, color=TEXT_PRIMARY, scale=0.28, bold=True).move_to(np.array([-4.3, y + 0.12, 0]), aligned_edge=LEFT)
            sub = label(detail, ORIGIN, color=TEXT_MUTED, scale=0.20).move_to(np.array([-4.3, y - 0.18, 0]), aligned_edge=LEFT)
            
            bar_bg = RoundedRectangle(width=4.35, height=0.34, corner_radius=0.06, color=GRID_LINE, stroke_width=0.8, fill_color=GRID_LINE, fill_opacity=0.15).move_to(np.array([0.35, y, 0]))
            bar = Rectangle(width=4.35 * value / 100, height=0.34, color=color, stroke_width=0, fill_color=color, fill_opacity=0.82)
            bar.align_to(bar_bg, LEFT).move_to(bar_bg.get_left() + RIGHT * bar.width / 2)
            
            val = label(f"{value}\\%", ORIGIN, color=color, scale=0.34, bold=True).move_to(np.array([2.8, y, 0]), aligned_edge=LEFT)
            row.add(pose_icons, name, sub, bar_bg, bar, val)
            return row, bar

        title = label("FERET Reality Check", UP * 3.05, color=TEXT_PRIMARY, scale=0.56, bold=True)
        question = label("beautiful theory, but what happens in tests?", ORIGIN, color=TEXT_PRIMARY, scale=0.44, bold=True)
        beat_to(seg_end(T, 0), FadeIn(title), FadeIn(question, shift=UP * 0.08))

        feret_card = RoundedRectangle(width=8.8, height=1.4, corner_radius=0.14, color=ACCENT_LAVENDER, stroke_width=1.6, fill_color=BG_NAVY_SOFT, fill_opacity=0.78).move_to(UP * 0.35)
        feret = label("U.S. Tough FERET", feret_card.get_center() + UP * 0.22, color=ACCENT_LAVENDER, scale=0.47, bold=True)
        test = label("one stored image per person", feret_card.get_center() + DOWN * 0.28, color=TEXT_PRIMARY, scale=0.34)
        database = VGroup(*[
            RoundedRectangle(width=0.34, height=0.44, corner_radius=0.03, color=ACCENT_BLUE, stroke_width=0.8, fill_color=ACCENT_BLUE, fill_opacity=0.20).move_to(np.array([-4.2 + i * 0.42, -1.25, 0]))
            for i in range(21)
        ])
        one_image = label("exactly one gallery image", DOWN * 1.85, color=TEXT_MUTED, scale=0.31, bold=True)
        beat_to(seg_end(T, 2), FadeOut(question), FadeIn(feret_card), FadeIn(feret), FadeIn(test), LaggedStart(*[FadeIn(d) for d in database], lag_ratio=0.02), FadeIn(one_image))

        results_lbl = label("Rank-1 results", UP * 2.45, color=TEXT_PRIMARY, scale=0.44, bold=True)
        axis = Line(LEFT * 2.0 + DOWN * 2.2, RIGHT * 2.45 + DOWN * 2.2, color=GRID_LINE, stroke_width=1)
        beat_to(seg_end(T, 3), FadeOut(feret_card), FadeOut(feret), FadeOut(test), FadeOut(database), FadeOut(one_image), FadeIn(results_lbl), Create(axis))

        rows = []
        bars = []
        specs = [
            (1.25, "Frontal", "same frontal pose", 98, ACCENT_MINT, ["frontal", "frontal"]),
            (0.34, "Profile", "profile left vs right", 84, ACCENT_CYAN, ["profile", "profile"]),
            (-0.57, "Half-profile R/L", "same half-profile angle", 57, ACCENT_LAVENDER, ["half", "half"]),
            (-1.48, "Half-profile vs Frontal", "cross-pose gallery mismatch", 18, ACCENT_CORAL, ["half", "frontal"]),
        ]
        for spec in specs:
            row, bar = result_row(*spec)
            rows.append(row)
            bars.append(bar)

        beat_to(seg_end(T, 4), FadeIn(rows[0][0]), FadeIn(rows[0][1]), FadeIn(rows[0][2]), FadeIn(rows[0][3]), GrowFromEdge(bars[0], LEFT), FadeIn(rows[0][5]))
        beat_to(seg_end(T, 5), FadeIn(rows[1][0]), FadeIn(rows[1][1]), FadeIn(rows[1][2]), FadeIn(rows[1][3]), GrowFromEdge(bars[1], LEFT), FadeIn(rows[1][5]))
        beat_to(seg_end(T, 6), FadeIn(rows[2][0]), FadeIn(rows[2][1]), FadeIn(rows[2][2]), FadeIn(rows[2][3]), GrowFromEdge(bars[2], LEFT), FadeIn(rows[2][5]))

        warning = label("large pose gap", RIGHT * 4.90 + DOWN * 1.48, color=ACCENT_CORAL, scale=0.28, bold=True)
        cliff = VGroup(
            Line(RIGHT * 3.72 + DOWN * 0.55, RIGHT * 4.35 + DOWN * 1.38, color=ACCENT_CORAL, stroke_width=2.4),
            thin_arrow(RIGHT * 4.35 + DOWN * 1.38, RIGHT * 4.35 + DOWN * 2.25, color=ACCENT_CORAL, stroke_width=2.2, buff=0.02),
        )
        beat_to(seg_end(T, 8), FadeIn(rows[3][0]), FadeIn(rows[3][1]), FadeIn(rows[3][2]), FadeIn(rows[3][3]), GrowFromEdge(bars[3], LEFT), FadeIn(rows[3][5]), Create(cliff), FadeIn(warning))

        king = RoundedRectangle(width=4.2, height=0.9, corner_radius=0.13, color=ACCENT_MINT, stroke_width=1.5, fill_color=ACCENT_MINT, fill_opacity=0.08).move_to(LEFT * 2.3 + DOWN * 2.90)
        king_lbl = label("strong: expression + lighting", king.get_center(), color=ACCENT_MINT, scale=0.31, bold=True)
        achilles = RoundedRectangle(width=4.2, height=0.9, corner_radius=0.13, color=ACCENT_CORAL, stroke_width=1.5, fill_color=ACCENT_CORAL, fill_opacity=0.08).move_to(RIGHT * 2.1 + DOWN * 2.90)
        achilles_lbl = label("weak: large 3D rotation", achilles.get_center(), color=ACCENT_CORAL, scale=0.31, bold=True)
        beat_to(seg_end(T, 10), FadeIn(king), FadeIn(king_lbl), FadeIn(achilles), FadeIn(achilles_lbl))

        tail = max(0.0, T["duration"] - elapsed - 0.18)
        if tail > 0.05:
            self.wait(tail)
