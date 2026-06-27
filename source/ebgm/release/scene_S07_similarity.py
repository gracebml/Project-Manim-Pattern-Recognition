import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from manim import *
import numpy as np
from _common import *

ASSET_DIR = Path(__file__).resolve().parents[2] / "assets"

class S07_Similarity(ThreeDScene):
    SCENE_KEY = "scene_07"

    def construct(self):
        T = load_scene_timing(self.SCENE_KEY)
        self.add_sound(T["audio_path"])
        self.camera.background_color = BG_NAVY
        self.set_camera_orientation(phi=62 * DEGREES, theta=-48 * DEGREES, zoom=0.86)

        elapsed = 0.0

        def beat_to(t_target, *anims, **kw):
            nonlocal elapsed
            rt = max(0.2, t_target - elapsed)
            if anims:
                self.play(*anims, run_time=rt, **kw)
            else:
                self.wait(rt)
            elapsed = t_target

        def fixed_label(text, pos, color=TEXT_PRIMARY, scale=0.36, bold=False):
            mob = en_label(text, color=color, scale=scale, bold=bold).move_to(pos)
            self.add_fixed_in_frame_mobjects(mob)
            return mob

        def fixed_card(width, height, pos, color=ACCENT_BLUE, fill=0.055):
            mob = RoundedRectangle(
                width=width,
                height=height,
                corner_radius=0.12,
                color=color,
                stroke_width=1.7,
                fill_color=color,
                fill_opacity=fill,
            ).move_to(pos)
            self.add_fixed_in_frame_mobjects(mob)
            return mob

        def fixed_math(tex, pos, color=TEXT_PRIMARY, scale=0.72):
            mob = MathTex(tex, tex_template=EN_TEX_TEMPLATE, color=color).scale(scale).move_to(pos)
            self.add_fixed_in_frame_mobjects(mob)
            return mob

        def mini_jet(color=ACCENT_CYAN):
            jet = VGroup()
            for r in range(3):
                disk = VGroup()
                for s in range(8):
                    disk.add(
                        AnnularSector(
                            inner_radius=0.14,
                            outer_radius=0.42,
                            start_angle=s * TAU / 8,
                            angle=TAU / 8,
                            color=interpolate_color(ManimColor(color), ManimColor(ACCENT_LAVENDER), s / 9),
                            fill_opacity=0.48,
                            stroke_color=BG_NAVY,
                            stroke_width=0.5,
                        )
                    )
                disk.scale([1.22, 0.38, 1]).shift(UP * r * 0.17 + RIGHT * r * 0.08)
                jet.add(disk)
            return jet

        def load_eye(height=0.6):
            p = ASSET_DIR / "s7_eye.png"
            if p.exists():
                img = ImageMobject(str(p))
                img.scale_to_fit_height(height)
                return img
            eye_white = Ellipse(width=height * 1.5, height=height, color=ACCENT_CYAN, stroke_width=2.0, fill_color=BG_NAVY_SOFT, fill_opacity=0.9)
            iris = Circle(radius=height * 0.3, color=ACCENT_CYAN, stroke_width=2.0, fill_color=ACCENT_TEAL, fill_opacity=0.6)
            pupil = Circle(radius=height * 0.12, color=BG_NAVY, fill_color=BG_NAVY, fill_opacity=1.0)
            return VGroup(eye_white, iris, pupil)

        title = en_label(r"Two similarity functions", color=TEXT_PRIMARY, scale=0.50, bold=True).to_edge(UP, buff=0.42)
        self.add_fixed_in_frame_mobjects(title)

        # B0: two jets, one question.
        jet_l = mini_jet(ACCENT_CYAN).scale(1.35).move_to(LEFT * 2.5 + DOWN * 0.25)
        jet_r = mini_jet(ACCENT_LAVENDER).scale(1.35).move_to(RIGHT * 2.5 + DOWN * 0.25)
        q = fixed_label(r"match?", DOWN * 0.25, color=TEXT_PRIMARY, scale=0.62, bold=True)
        arrow_l = Arrow(LEFT * 1.8 + DOWN * 0.25, LEFT * 0.8 + DOWN * 0.25, color=ACCENT_BLUE, stroke_width=1.5, buff=0.08, tip_length=0.12)
        arrow_r = Arrow(RIGHT * 1.8 + DOWN * 0.25, RIGHT * 0.8 + DOWN * 0.25, color=ACCENT_BLUE, stroke_width=1.5, buff=0.08, tip_length=0.12)
        self.add_fixed_in_frame_mobjects(jet_l, jet_r, arrow_l, arrow_r)
        
        beat_to(seg_end(T, 0), FadeIn(title, scale=0.85), FadeIn(jet_l), FadeIn(jet_r), GrowArrow(arrow_l), GrowArrow(arrow_r), FadeIn(q))

        # B1-B2: similarity choice cards.
        def similarity_choice(tex, text, color, formula_scale=0.72):
            box = RoundedRectangle(
                width=5.6,
                height=1.9,
                corner_radius=0.16,
                color=color,
                stroke_width=1.9,
                fill_color=color,
                fill_opacity=0.055,
            )
            formula = MathTex(tex, tex_template=EN_TEX_TEMPLATE, color=color).scale(formula_scale)
            caption = en_label(text, color=color, scale=0.32, bold=True)
            content = VGroup(formula, caption).arrange(DOWN, buff=0.28).move_to(box)
            return VGroup(box, content), box, formula, caption

        choice_a, card_a, sa, sa_lbl = similarity_choice(
            r"S_a(\mathcal{J},\mathcal{J}') = \frac{\sum_j a_j a'_j}{\sqrt{\sum_j a_j^2 \,\sum_j {a'_j}^2}}",
            "amplitude only", ACCENT_CYAN, formula_scale=0.68
        )
        choice_p, card_p, sp, sp_lbl = similarity_choice(
            r"S_\phi(\mathcal{J},\mathcal{J}') = \frac{\sum_j a_j a'_j \cos(\phi_j - \phi'_j - \vec{d}\cdot \vec{k}_j)}{\sqrt{\sum_j a_j^2 \,\sum_j {a'_j}^2}}",
            "with phase", ACCENT_LAVENDER, formula_scale=0.58
        )
        choices = VGroup(choice_a, choice_p).arrange(RIGHT, buff=0.6).next_to(title, DOWN, buff=1.6)
        harmony = en_label(r"coarse first, precise second", color=TEXT_MUTED, scale=0.30).next_to(choices, DOWN, buff=0.45)
        self.add_fixed_in_frame_mobjects(choice_a, choice_p, harmony)
        
        beat_to(
            seg_end(T, 1),
            FadeOut(jet_l),
            FadeOut(jet_r),
            FadeOut(arrow_l),
            FadeOut(arrow_r),
            FadeOut(q),
            FadeIn(choice_a, shift=UP * 0.06),
            FadeIn(choice_p, shift=UP * 0.06),
            FadeIn(harmony),
        )

        # Amplitude illustration: ignoring phase
        amp_bars = VGroup(*[
            Rectangle(width=0.08, height=h, color=ACCENT_CYAN, fill_color=ACCENT_CYAN, fill_opacity=0.72, stroke_width=0)
            for h in [0.4, 0.7, 0.5, 0.8, 0.3]
        ]).arrange(RIGHT, buff=0.08).shift(LEFT * 2.8 + DOWN * 2.0)
        
        phase_circle = Circle(radius=0.34, color=ACCENT_LAVENDER, stroke_width=1.5).shift(LEFT * 1.3 + DOWN * 2.0)
        phase_hand = Line(phase_circle.get_center(), phase_circle.get_center() + 0.3 * (RIGHT + UP), color=ACCENT_LAVENDER, stroke_width=1.8)
        cross_lines = VGroup(
            Line(phase_circle.get_center() + LEFT*0.35 + DOWN*0.35, phase_circle.get_center() + RIGHT*0.35 + UP*0.35, color=ACCENT_CORAL, stroke_width=2.5),
            Line(phase_circle.get_center() + LEFT*0.35 + UP*0.35, phase_circle.get_center() + RIGHT*0.35 + DOWN*0.35, color=ACCENT_CORAL, stroke_width=2.5),
        )
        phase_ignore = Group(phase_circle, phase_hand, cross_lines)
        ignore_lbl = en_label("ignoring phase", color=ACCENT_CORAL, scale=0.22, bold=True).next_to(phase_circle, DOWN, buff=0.15)
        ignore_group = Group(amp_bars, phase_ignore, ignore_lbl)
        self.add_fixed_in_frame_mobjects(ignore_group)

        beat_to(
            seg_end(T, 2),
            card_a.animate.set_fill(ACCENT_CYAN, opacity=0.13).set_stroke(ACCENT_CYAN, width=2.7),
            card_p.animate.set_opacity(0.35),
            sp.animate.set_opacity(0.35),
            sp_lbl.animate.set_opacity(0.35),
            FadeIn(ignore_group, shift=UP * 0.05),
        )

        # B3: wide smooth basin.
        for mob in [choice_a, choice_p, harmony, ignore_group]:
            self.remove(mob)
            
        basin_title = fixed_label(r"$S_a$: smooth wide basin", UP * 2.78, color=ACCENT_CYAN, scale=0.44, bold=True)
        basin_note = fixed_label(r"large capture range", DOWN * 2.78, color=TEXT_MUTED, scale=0.32)

        # 3D Basin Setup
        axes = ThreeDAxes(
            x_range=[-2.5, 2.5, 1],
            y_range=[-2.5, 2.5, 1],
            z_range=[-1.0, 0.4, 0.5],
            x_length=4.5,
            y_length=4.5,
            z_length=1.9,
            axis_config={"color": GRID_LINE, "stroke_width": 0.8},
        )
        basin = Surface(
            lambda u, v: np.array([u, v, -0.88 * np.exp(-0.2 * (u * u + v * v))]),
            u_range=[-2.5, 2.5],
            v_range=[-2.5, 2.5],
            resolution=(28, 28),
            fill_color=ACCENT_CYAN,
            fill_opacity=0.55,
            stroke_width=0,
        )
        
        # Contour rings
        r1 = np.sqrt(np.log(0.8 / 0.88) / -0.2)
        r2 = np.sqrt(np.log(0.6 / 0.88) / -0.2)
        r3 = np.sqrt(np.log(0.4 / 0.88) / -0.2)
        
        ring1 = Circle(radius=r1, color=ACCENT_TEAL, stroke_width=1.0).set_opacity(0.4).shift(OUT * -0.8)
        ring2 = Circle(radius=r2, color=ACCENT_TEAL, stroke_width=1.0).set_opacity(0.4).shift(OUT * -0.6)
        ring3 = Circle(radius=r3, color=ACCENT_TEAL, stroke_width=1.0).set_opacity(0.4).shift(OUT * -0.4)
        
        basin_3d = Group(axes, basin, ring1, ring2, ring3).shift(LEFT * 2.6 + DOWN * 0.2)
        
        # 2D Profile
        axes_2d = Axes(
            x_range=[-2.5, 2.5, 1],
            y_range=[0, 1.5, 0.5],
            x_length=4.0,
            y_length=2.5,
            axis_config={"color": GRID_LINE, "stroke_width": 1.0},
        ).shift(RIGHT * 3.2 + DOWN * 0.2)
        
        curve_a = axes_2d.plot(lambda x: 1.0 - 0.8 * np.exp(-0.25 * x**2), color=ACCENT_CYAN, stroke_width=2.5)
        curve_a_lbl = en_label("basin profile", color=ACCENT_CYAN, scale=0.18).next_to(axes_2d.get_bottom(), UP, buff=0.15).shift(LEFT * 0.8)
        
        self.add(basin_3d)
        self.add_fixed_in_frame_mobjects(axes_2d, curve_a, curve_a_lbl)
        
        beat_to(seg_end(T, 3), FadeOut(title), FadeIn(basin_title), FadeIn(basin_note), Create(axes_2d), Create(curve_a), FadeIn(basin_3d))

        # B4: slide toward the eye.
        eye_3d = load_eye(height=0.55).move_to(np.array([-2.6, -0.2, -0.88 + (-0.15)]))
        eye_2d = load_eye(height=0.45).move_to(axes_2d.c2p(0.0, 0.2))
        
        # 3D Path
        z_start = -0.88 * np.exp(-0.2 * (1.8**2 + (-1.8)**2))
        ball_3d = Sphere(radius=0.10, color=ACCENT_MINT).move_to(np.array([-2.6 + 1.8, -0.2 - 1.8, z_start]))
        
        path_3d = VMobject(color=ACCENT_MINT, stroke_width=2.0)
        path_points_3d = []
        for t in np.linspace(0, 1, 30):
            u = 1.8 * (1 - t)
            v = -1.8 * (1 - t)
            z = -0.88 * np.exp(-0.2 * (u * u + v * v))
            path_points_3d.append(np.array([-2.6 + u, -0.2 + v, z]))
        path_3d.set_points_smoothly(path_points_3d)
        
        # 2D Path
        ball_2d = Dot(color=ACCENT_MINT, radius=0.08).move_to(axes_2d.c2p(2.0, 1.0 - 0.8 * np.exp(-0.25 * 2.0**2)))
        path_2d = VMobject()
        path_points_2d = [axes_2d.c2p(x, 1.0 - 0.8 * np.exp(-0.25 * x**2)) for x in np.linspace(2.0, 0.0, 30)]
        path_2d.set_points_smoothly(path_points_2d)
        
        self.add(eye_3d)
        self.add_fixed_in_frame_mobjects(eye_2d, ball_2d)
        
        beat_to(
            seg_end(T, 4),
            FadeIn(ball_3d),
            FadeIn(ball_2d),
            MoveAlongPath(ball_3d, path_3d),
            MoveAlongPath(ball_2d, path_2d),
            FadeIn(eye_3d),
            FadeIn(eye_2d),
        )

        # B5: coarse step.
        range_line = DoubleArrow(axes_2d.c2p(-2.2, 1.1), axes_2d.c2p(2.2, 1.1), color=ACCENT_CYAN, stroke_width=1.5, buff=0, tip_length=0.1)
        range_lbl = en_label("wide capture range", color=ACCENT_CYAN, scale=0.18, bold=True).next_to(range_line, UP, buff=0.08)
        
        coarse = fixed_label(r"COARSE", RIGHT * 5.2 + UP * 2.0, color=ACCENT_MINT, scale=0.25, bold=True)
        coarse_box = fixed_card(1.6, 0.5, RIGHT * 5.2 + UP * 2.0, color=ACCENT_MINT, fill=0.08)
        
        self.add_fixed_in_frame_mobjects(range_line, range_lbl)
        
        beat_to(
            seg_end(T, 5),
            FadeIn(coarse_box, shift=LEFT * 0.05),
            FadeIn(coarse),
            Create(range_line),
            FadeIn(range_lbl),
            basin.animate.set_opacity(0.35),
            ball_2d.animate.scale(1.2),
            ball_3d.animate.scale(1.2),
        )

        # B6: phase kicks in.
        self.remove(basin_3d, eye_3d)
        for mob in [basin_title, basin_note, coarse_box, coarse, range_line, range_lbl, axes_2d, curve_a, curve_a_lbl, ball_2d, eye_2d]:
            self.remove(mob)
            
        phase_title = fixed_label(r"$S_\phi$: phase kicks in", UP * 2.78, color=ACCENT_LAVENDER, scale=0.44, bold=True)
        phase_formula = fixed_math(
            r"S_\phi(\mathcal{J},\mathcal{J}') = \frac{\sum_j a_j a'_j \color{accentcyan}{\cos(\phi_j - \phi'_j - \vec{d}\cdot \vec{k}_j)}}{\sqrt{\sum_j a_j^2 \,\sum_j {a'_j}^2}}",
            DOWN * 2.6, color=ACCENT_LAVENDER, scale=0.68
        )
        
        beat_to(
            seg_end(T, 6),
            FadeIn(phase_title),
            FadeIn(phase_formula, shift=UP * 0.05),
        )

        # B7: razor sharp peak.
        self.remove(phase_title, phase_formula)
        
        sharp_title = fixed_label(r"$S_\phi$: razor sharp peak", UP * 2.78, color=ACCENT_LAVENDER, scale=0.44, bold=True)
        
        # 3D Peak
        sharp_axes = ThreeDAxes(
            x_range=[-1.8, 1.8, 0.9],
            y_range=[-1.8, 1.8, 0.9],
            z_range=[-0.2, 1.2, 0.5],
            x_length=4.5,
            y_length=4.5,
            z_length=2.4,
            axis_config={"color": GRID_LINE, "stroke_width": 0.8},
        )
        sharp = Surface(
            lambda u, v: np.array([u, v, 1.05 * np.exp(-4.2 * (u * u + v * v)) - 0.12 * (u * u + v * v)]),
            u_range=[-1.8, 1.8],
            v_range=[-1.8, 1.8],
            resolution=(28, 28),
            fill_color=ACCENT_LAVENDER,
            fill_opacity=0.55,
            stroke_width=0,
        )
        
        # Contour rings
        r1_s = np.sqrt(np.log(0.8 / 1.05) / -4.2)
        r2_s = np.sqrt(np.log(0.5 / 1.05) / -4.2)
        r3_s = np.sqrt(np.log(0.2 / 1.05) / -4.2)
        
        ring1_s = Circle(radius=r1_s, color=ACCENT_CYAN, stroke_width=1.0).set_opacity(0.4).shift(OUT * 0.8)
        ring2_s = Circle(radius=r2_s, color=ACCENT_CYAN, stroke_width=1.0).set_opacity(0.4).shift(OUT * 0.5)
        ring3_s = Circle(radius=r3_s, color=ACCENT_CYAN, stroke_width=1.0).set_opacity(0.4).shift(OUT * 0.2)
        
        sharp_3d = Group(sharp_axes, sharp, ring1_s, ring2_s, ring3_s).shift(LEFT * 2.6 + DOWN * 0.2)
        
        # 2D Profile
        axes_2d_s = Axes(
            x_range=[-2.5, 2.5, 1],
            y_range=[-0.4, 1.5, 0.5],
            x_length=4.0,
            y_length=2.5,
            axis_config={"color": GRID_LINE, "stroke_width": 1.0},
        ).shift(RIGHT * 3.2 + DOWN * 0.2)
        
        curve_p = axes_2d_s.plot(lambda x: 1.0 * np.exp(-3.5 * x**2) * np.cos(6.0 * x), color=ACCENT_LAVENDER, stroke_width=2.5)
        curve_p_lbl = en_label("phase profile", color=ACCENT_LAVENDER, scale=0.18).next_to(axes_2d_s.get_bottom(), UP, buff=0.15).shift(LEFT * 0.8)
        
        # Sensitivity dots
        dot_2d = Dot(color=ACCENT_CORAL, radius=0.08).move_to(axes_2d_s.c2p(0.0, 1.0))
        dot_3d = Sphere(radius=0.08, color=ACCENT_CORAL).move_to(np.array([-2.6, -0.2, 1.05]))
        
        self.add(sharp_3d, dot_3d)
        self.add_fixed_in_frame_mobjects(axes_2d_s, curve_p, curve_p_lbl, dot_2d)
        
        # Slide path 2D
        path_points_s2d = [axes_2d_s.c2p(x, 1.0 * np.exp(-3.5 * x**2) * np.cos(6.0 * x)) for x in np.linspace(0.0, 0.22, 20)]
        path_s2d = VMobject()
        path_s2d.set_points_smoothly(path_points_s2d)
        
        # Slide path 3D
        path_points_s3d = []
        for t in np.linspace(0, 1, 20):
            u = 0.22 * t
            v = 0.0
            z = 1.05 * np.exp(-4.2 * u * u) - 0.12 * u * u
            path_points_s3d.append(np.array([-2.6 + u, -0.2 + v, z]))
        path_s3d = VMobject()
        path_s3d.set_points_smoothly(path_points_s3d)
        
        beat_to(
            seg_end(T, 7),
            FadeIn(sharp_title),
            FadeIn(sharp_3d),
            FadeIn(axes_2d_s),
            FadeIn(curve_p),
            FadeIn(curve_p_lbl),
            MoveAlongPath(dot_2d, path_s2d),
            MoveAlongPath(dot_3d, path_s3d),
        )

        # B8: sub-pixel accuracy.
        subpixel = fixed_label(r"sub-pixel accuracy", RIGHT * 3.25 + UP * 1.95, color=ACCENT_LAVENDER, scale=0.25, bold=True)
        sub_box = fixed_card(2.6, 0.5, RIGHT * 3.25 + UP * 1.95, color=ACCENT_LAVENDER, fill=0.08)
        
        cross_2d = VGroup(
            Line(LEFT * 0.22, RIGHT * 0.22, color=ACCENT_CORAL, stroke_width=1.5),
            Line(DOWN * 0.22, UP * 0.22, color=ACCENT_CORAL, stroke_width=1.5),
            Circle(radius=0.15, color=ACCENT_CORAL, stroke_width=1.2),
        ).move_to(axes_2d_s.c2p(0.0, 1.0))
        
        grid_box = fixed_card(1.6, 1.6, RIGHT * 5.2 + DOWN * 1.9, color=ACCENT_BLUE, fill=0.04)
        grid_lines = VGroup(
            Line(grid_box.get_left() + RIGHT * 0.53 + UP * 0.8, grid_box.get_left() + RIGHT * 0.53 + DOWN * 0.8, color=GRID_LINE, stroke_width=0.8),
            Line(grid_box.get_left() + RIGHT * 1.07 + UP * 0.8, grid_box.get_left() + RIGHT * 1.07 + DOWN * 0.8, color=GRID_LINE, stroke_width=0.8),
            Line(grid_box.get_top() + DOWN * 0.53 + LEFT * 0.8, grid_box.get_top() + DOWN * 0.53 + RIGHT * 0.8, color=GRID_LINE, stroke_width=0.8),
            Line(grid_box.get_top() + DOWN * 1.07 + LEFT * 0.8, grid_box.get_top() + DOWN * 1.07 + RIGHT * 0.8, color=GRID_LINE, stroke_width=0.8),
        )
        target_dot = Dot(grid_box.get_center() + RIGHT * 0.24 + UP * 0.18, color=ACCENT_MINT, radius=0.06)
        grid_lbl = en_label("sub-pixel target", color=TEXT_MUTED, scale=0.16).next_to(grid_box, DOWN, buff=0.08)
        grid_group = Group(grid_box, grid_lines, target_dot, grid_lbl)
        
        self.add_fixed_in_frame_mobjects(cross_2d, grid_group)
        
        beat_to(
            seg_end(T, 8),
            FadeIn(sub_box),
            FadeIn(subpixel),
            dot_2d.animate.move_to(axes_2d_s.c2p(0.0, 1.0)),
            dot_3d.animate.move_to(np.array([-2.6, -0.2, 1.05])),
            Create(cross_2d),
            FadeIn(grid_group, shift=UP * 0.05),
        )

        # B9: Points the way.
        self.remove(grid_group)
        
        way_lbl = fixed_label(r"points the way", RIGHT * 3.25 + UP * 1.95, color=ACCENT_MINT, scale=0.25, bold=True)
        way_box = fixed_card(2.2, 0.5, RIGHT * 3.25 + UP * 1.95, color=ACCENT_MINT, fill=0.08)
        
        y_disp = 1.0 * np.exp(-3.5 * (-1.2)**2) * np.cos(6.0 * (-1.2))
        disp_start_2d = axes_2d_s.c2p(-1.2, y_disp)
        disp_end_2d = axes_2d_s.c2p(0.0, 1.0)
        
        arrow_disp = Arrow(
            disp_start_2d, disp_end_2d,
            color=ACCENT_MINT, stroke_width=1.5, buff=0.08, tip_length=0.12
        )
        d_lbl = MathTex(r"\vec{d}", tex_template=EN_TEX_TEMPLATE, color=ACCENT_MINT).scale(0.6).next_to(arrow_disp.get_center(), UP, buff=0.1)
        
        dot_disp_2d = Dot(disp_start_2d, color=ACCENT_CORAL, radius=0.08)
        
        self.add_fixed_in_frame_mobjects(arrow_disp, d_lbl, dot_disp_2d)
        
        beat_to(
            seg_end(T, 9),
            FadeOut(sub_box),
            FadeOut(subpixel),
            FadeOut(cross_2d),
            FadeIn(way_box),
            FadeIn(way_lbl),
            FadeIn(dot_disp_2d),
            GrowArrow(arrow_disp),
            FadeIn(d_lbl),
        )

        # B10: Move the jet.
        move_lbl = fixed_label(r"move the jet: $\vec{d} = (\Delta x, \Delta y)$", DOWN * 2.76, color=ACCENT_MINT, scale=0.38, bold=True)
        
        beat_to(
            seg_end(T, 10),
            FadeIn(move_lbl, shift=UP * 0.05),
            dot_disp_2d.animate.move_to(disp_end_2d).set_color(ACCENT_MINT),
            dot_3d.animate.move_to(np.array([-2.6, -0.2, 1.05])).set_color(ACCENT_MINT),
            sharp.animate.set_opacity(0.4),
            FadeOut(arrow_disp),
            FadeOut(d_lbl),
        )

        tail = max(0.0, T["duration"] - elapsed - 0.18)
        if tail > 0.05:
            self.wait(tail)
