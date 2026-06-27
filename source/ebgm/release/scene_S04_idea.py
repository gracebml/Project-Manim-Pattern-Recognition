import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from manim import *
import numpy as np
from _common import *
ASSET_DIR = Path(__file__).resolve().parents[2] / "assets"


class S04_Idea(MovingCameraScene):
    SCENE_KEY = "scene_04"

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

        def label(text, pos, color=TEXT_PRIMARY, scale=0.38, bold=False):
            return en_label(text, color=color, scale=scale, bold=bold).move_to(pos)

        def panel(width=3.35, height=4.2, color=ACCENT_BLUE, fill=0.045):
            return RoundedRectangle(
                width=width,
                height=height,
                corner_radius=0.12,
                color=color,
                stroke_width=1.7,
                fill_color=color,
                fill_opacity=fill,
            )

        def load_face(name, fallback_style="neutral", color=ACCENT_CYAN, height=2.00):
            for ext in (".png", ".jpg", ".jpeg"):
                p = ASSET_DIR / f"{name}{ext}"
                if p.exists():
                    img = ImageMobject(str(p))
                    img.scale_to_fit_height(height)
                    return img

            def stylized_face_2d(style="neutral", color=ACCENT_CYAN):
                face = Ellipse(width=1.45, height=1.85, color=color, stroke_width=2.0, fill_color=color, fill_opacity=0.04)
                eyes = VGroup(
                    Dot([-0.28, 0.22, 0], radius=0.04, color=color),
                    Dot([0.28, 0.22, 0], radius=0.04, color=color),
                )
                nose = Line([0, 0.12, 0], [0, -0.12, 0], color=color, stroke_width=1.8)
                if style == "smile":
                    mouth = Arc(radius=0.25, start_angle=PI, angle=-PI, color=color, stroke_width=1.8).shift(DOWN * 0.38)
                elif style == "frown":
                    mouth = Arc(radius=0.25, start_angle=0, angle=PI, color=color, stroke_width=1.8).shift(DOWN * 0.28)
                else:
                    mouth = Line([-0.16, -0.42, 0], [0.16, -0.42, 0], color=color, stroke_width=1.8)
                return VGroup(face, eyes, nose, mouth)

            return stylized_face_2d(style=fallback_style, color=color)

        def face_frame(img, width=2.55, height=2.85, color=ACCENT_BLUE, fill=0.05):
            frame = RoundedRectangle(
                width=width,
                height=height,
                corner_radius=0.08,
                color=color,
                stroke_width=1.8,
                fill_color=color,
                fill_opacity=fill,
            )
            # Use a mask or crop to fit exactly inside the frame
            content = img.copy()
            content.set_height(height - 0.12)
            content.move_to(frame.get_center())
            return Group(frame, content)

        def make_bad_pixels(face):
            # Show a pixelated/mosaic grid over the face to represent raw pixels
            card = face_frame(face, width=2.5, height=2.8, color=ACCENT_BLUE, fill=0.05)
            # Render a grid of colored pixel squares to show pixelation
            grid = VGroup()
            rows, cols = 12, 12
            square_w = 2.38 / cols
            square_h = 2.68 / rows
            for r in range(rows):
                for c in range(cols):
                    opacity = 0.28 + 0.12 * np.cos(r * 0.5) * np.sin(c * 0.5)
                    color = ACCENT_BLUE if (r + c) % 2 == 0 else ACCENT_CYAN
                    sq = Rectangle(
                        width=square_w, height=square_h,
                        stroke_color=BG_NAVY, stroke_width=0.4,
                        fill_color=color, fill_opacity=opacity
                    )
                    sq.move_to(card[1].get_center() + np.array([(c - cols/2 + 0.5) * square_w, (r - rows/2 + 0.5) * square_h, 0]))
                    grid.add(sq)
            cross = Cross(card[0], color=ACCENT_CORAL, stroke_width=4.5).scale(0.9)
            lbl = label(r"raw pixels", card[0].get_bottom() + DOWN * 0.28, color=TEXT_MUTED, scale=0.26)
            return Group(card, grid, cross, lbl)

        def make_pca_thumb(face):
            # Represent PCA via blurred/eigenface-like ghosting overlay
            card = face_frame(face, width=2.5, height=2.8, color=ACCENT_LAVENDER, fill=0.05)
            card[1].set_opacity(0.35) # Dim face to represent loss of details
            ghosts = Group()
            for i in range(3):
                g = card[1].copy().set_opacity(0.18 - i * 0.04).shift(LEFT * (0.08 * i) + UP * (0.05 * i))
                ghosts.add(g)
            halo = Circle(radius=0.92, color=ACCENT_LAVENDER, stroke_width=2.5).set_opacity(0.3).move_to(card[1].get_center())
            cross = Cross(card[0], color=ACCENT_CORAL, stroke_width=4.5).scale(0.9)
            lbl = label(r"linear PCA", card[0].get_bottom() + DOWN * 0.28, color=TEXT_MUTED, scale=0.26)
            return Group(card, ghosts, halo, cross, lbl)

        def load_pose_face(pose_name, fallback_img, height=1.80):
            p = ASSET_DIR / f"{pose_name}.png"
            if p.exists():
                img = ImageMobject(str(p))
            else:
                p = ASSET_DIR / f"{pose_name}.jpg"
                if p.exists():
                    img = ImageMobject(str(p))
                else:
                    img = fallback_img.copy()
            img.scale_to_fit_height(height)
            return img

        def make_landmark_graph(face_img, color=ACCENT_CYAN):
            img = face_img.copy().set_height(2.00)
            nodes = VGroup(
                Dot(np.array([-0.32, 0.34, 0]), radius=0.045, color=color),
                Dot(np.array([0.32, 0.34, 0]), radius=0.045, color=color),
                Dot(np.array([0.00, 0.08, 0]), radius=0.045, color=color),
                Dot(np.array([-0.18, -0.20, 0]), radius=0.045, color=color),
                Dot(np.array([0.18, -0.20, 0]), radius=0.045, color=color),
                Dot(np.array([0.00, -0.45, 0]), radius=0.045, color=color),
            )
            edges = VGroup(
                Line(nodes[0].get_center(), nodes[2].get_center(), color=color, stroke_width=2.0).set_opacity(0.72),
                Line(nodes[1].get_center(), nodes[2].get_center(), color=color, stroke_width=2.0).set_opacity(0.72),
                Line(nodes[0].get_center(), nodes[1].get_center(), color=color, stroke_width=1.4).set_opacity(0.45),
                Line(nodes[2].get_center(), nodes[3].get_center(), color=color, stroke_width=1.7).set_opacity(0.68),
                Line(nodes[2].get_center(), nodes[4].get_center(), color=color, stroke_width=1.7).set_opacity(0.68),
                Line(nodes[3].get_center(), nodes[5].get_center(), color=color, stroke_width=1.7).set_opacity(0.68),
                Line(nodes[4].get_center(), nodes[5].get_center(), color=color, stroke_width=1.7).set_opacity(0.68),
            )
            nodes.move_to(img.get_center())
            edges.move_to(img.get_center())
            return Group(img, edges, nodes)

        def make_wavelet_psi(color=ACCENT_LAVENDER, scale=1.0):
            x = np.linspace(-1.4, 1.4, 120)
            y = 0.58 * np.sin(4.1 * x) * np.exp(-0.8 * x**2)
            points = np.array([[x[i], y[i], 0] for i in range(len(x))])
            wave = VMobject(color=color, stroke_width=2.5)
            wave.set_points_smoothly(points)
            envelope = ParametricFunction(
                lambda t: np.array([t, 0.58 * np.exp(-0.75 * t**2), 0]),
                t_range=[-1.35, 1.35],
                color=ACCENT_TEAL,
                stroke_width=1.4,
            ).set_opacity(0.65)
            base = Line(LEFT * 1.5, RIGHT * 1.5, color=TEXT_MUTED, stroke_width=0.8).set_opacity(0.35)
            label_psi = label(r"$\psi$", UP * 1.0, color=color, scale=0.52, bold=True)
            return VGroup(base, envelope, wave, label_psi).scale(scale)

        def make_jet_stack(color=ACCENT_TEAL):
            stack = VGroup()
            for i in range(6):
                width = 0.58 - i * 0.05
                height = 0.18 + i * 0.02
                pill = RoundedRectangle(
                    width=width,
                    height=height,
                    corner_radius=0.08,
                    color=color,
                    stroke_width=1.1,
                    fill_color=color,
                    fill_opacity=0.12 + 0.08 * i,
                ).shift(UP * (i * 0.18 - 0.45))
                stack.add(pill)
            glow = Circle(radius=0.48, color=color, stroke_width=1.0).set_opacity(0.35)
            glow2 = Circle(radius=0.68, color=ACCENT_LAVENDER, stroke_width=1.0).set_opacity(0.18)
            return VGroup(glow2, glow, stack)

        def result_chip(text, color):
            box = RoundedRectangle(
                width=2.6,
                height=0.62,
                corner_radius=0.12,
                color=color,
                stroke_width=1.6,
                fill_color=color,
                fill_opacity=0.08,
            )
            txt = label(text, box.get_center(), color=color, scale=0.26, bold=True)
            return VGroup(box, txt)

        face_img = load_face("face", fallback_style="neutral", color=ACCENT_CYAN)
        face_frontal = load_pose_face("s4_pose_frontal", face_img, height=2.00)
        face_half = load_pose_face("s4_pose_half", face_img, height=2.00)
        face_profile = load_pose_face("s4_pose_profile", face_img, height=2.00)

        title = label(r"Three Pillars", UP * 2.55, color=TEXT_PRIMARY, scale=0.70, bold=True)
        intro = label(r"EBGM is not pixels or PCA.", UP * 1.95, color=TEXT_MUTED, scale=0.34)
        face_center = face_frame(face_img, width=2.55, height=2.95, color=ACCENT_BLUE, fill=0.06).move_to([0, -0.05, 0])
        left_bad = make_bad_pixels(face_img).move_to([-4.0, -0.08, 0])
        right_bad = make_pca_thumb(face_img).move_to([4.0, -0.08, 0])
        
        beat_to(
            seg_end(T, 0),
            FadeIn(title, shift=DOWN * 0.08),
            FadeIn(intro, shift=DOWN * 0.05),
            FadeIn(face_center, shift=DOWN * 0.04),
            FadeIn(left_bad, shift=DOWN * 0.04),
            FadeIn(right_bad, shift=DOWN * 0.04),
        )

        xs = [-4.6, 0.0, 4.6]
        p1 = panel(width=3.55, height=4.0, color=ACCENT_CYAN).move_to([xs[0], 0.0, 0])
        p2 = panel(width=3.55, height=4.0, color=ACCENT_TEAL).move_to([xs[1], 0.0, 0])
        p3 = panel(width=3.55, height=4.0, color=ACCENT_LAVENDER).move_to([xs[2], 0.0, 0])
        pillars = VGroup(p1, p2, p3)

        heads = VGroup(
            label(r"1. Image Graph", [xs[0], 1.68, 0], color=ACCENT_CYAN, scale=0.30, bold=True),
            label(r"2. Wavelet Jet", [xs[1], 1.68, 0], color=ACCENT_TEAL, scale=0.30, bold=True),
            label(r"3. Bunch Graph", [xs[2], 1.68, 0], color=ACCENT_LAVENDER, scale=0.30, bold=True),
        )

        # Pillar 1 elements
        graph = make_landmark_graph(face_img, color=ACCENT_CYAN).move_to([xs[0], 0.0, 0])
        graph_note = label("landmarks + edges", [xs[0], -1.62, 0], color=TEXT_MUTED, scale=0.24)

        beat_to(
            seg_end(T, 1),
            FadeOut(left_bad),
            FadeOut(right_bad),
            FadeOut(intro),
            FadeOut(face_center),
            FadeIn(p1, shift=UP * 0.08),
            FadeIn(heads[0]),
            FadeIn(graph[0]),
            Create(graph[1]),
            LaggedStart(*[GrowFromCenter(n) for n in graph[2]], lag_ratio=0.08),
            FadeIn(graph_note),
        )

        # Pillar 2 elements
        input_patch = face_frame(face_img, width=0.85, height=0.85, color=ACCENT_BLUE, fill=0.04).move_to([xs[1] - 0.65, 0.65, 0])
        patch_lbl = label("image patch", [xs[1] - 0.65, 1.25, 0], color=TEXT_MUTED, scale=0.18)
        not_color_box = RoundedRectangle(
            width=0.95,
            height=0.85,
            corner_radius=0.08,
            color=ACCENT_CORAL,
            stroke_width=1.4,
            fill_color=ACCENT_CORAL,
            fill_opacity=0.12,
        ).move_to([xs[1] + 0.65, 0.65, 0])
        not_color_cross = Cross(not_color_box, color=ACCENT_CORAL, stroke_width=2.5).scale(0.8)
        not_color_lbl = label("not color", not_color_box.get_center(), color=ACCENT_CORAL, scale=0.18, bold=True)
        psi_inset = make_wavelet_psi(color=ACCENT_LAVENDER, scale=0.22).move_to(input_patch.get_center())
        jet = make_jet_stack(color=ACCENT_TEAL).scale(1.22).move_to([xs[1], -0.65, 0])
        psi_symbol = MathTex(r"\psi", tex_template=EN_TEX_TEMPLATE, color=ACCENT_LAVENDER).scale(0.55).next_to(jet, RIGHT, buff=0.15)
        arrow_to_jet = thin_curved_arrow(np.array([xs[1] - 0.65, 0.15, 0]), np.array([xs[1] - 0.2, -0.3, 0]), color=ACCENT_TEAL, stroke_width=2.0, angle=-45*DEGREES)
        jet_note = label("wavelet jet — texture DNA", [xs[1], -1.62, 0], color=TEXT_MUTED, scale=0.24)

        beat_to(
            seg_end(T, 2),
            p1.animate.set_opacity(0.3),
            graph.animate.set_opacity(0.3),
            graph_note.animate.set_opacity(0.3),
            heads[0].animate.set_opacity(0.3),
            FadeIn(p2, shift=UP * 0.08),
            FadeIn(heads[1]),
            FadeIn(input_patch),
            FadeIn(patch_lbl),
            FadeIn(not_color_box),
            FadeIn(not_color_cross),
            FadeIn(not_color_lbl),
            FadeIn(psi_inset),
            Create(arrow_to_jet),
            FadeIn(jet),
            FadeIn(psi_symbol),
            FadeIn(jet_note, shift=UP * 0.05),
        )

        # Pillar 3 elements
        def make_bunch_stack():
            g3 = make_landmark_graph(face_profile, color=ACCENT_LAVENDER).scale(0.72).move_to([xs[2] + 0.22, -0.15 + 0.15, 0]).set_opacity(0.4)
            g2 = make_landmark_graph(face_half, color=ACCENT_TEAL).scale(0.72).move_to([xs[2], -0.15, 0]).set_opacity(0.7)
            g1 = make_landmark_graph(face_frontal, color=ACCENT_CYAN).scale(0.72).move_to([xs[2] - 0.22, -0.15 - 0.15, 0])
            return Group(g3, g2, g1)

        bunch = make_bunch_stack()
        bunch_note = label("pose samples stacked", [xs[2], -1.62, 0], color=TEXT_MUTED, scale=0.24)
        pose_labs = VGroup(
            label("frontal", [xs[2] - 1.25, -0.65, 0], color=ACCENT_CYAN, scale=0.18, bold=True),
            label("half-profile", [xs[2] - 1.15, -0.15, 0], color=ACCENT_TEAL, scale=0.18, bold=True),
            label("profile", [xs[2] - 1.05, 0.35, 0], color=ACCENT_LAVENDER, scale=0.18, bold=True),
        )

        beat_to(
            seg_end(T, 3),
            p2.animate.set_opacity(0.3),
            heads[1].animate.set_opacity(0.3),
            input_patch.animate.set_opacity(0.3),
            patch_lbl.animate.set_opacity(0.3),
            not_color_box.animate.set_opacity(0.3),
            not_color_cross.animate.set_opacity(0.3),
            not_color_lbl.animate.set_opacity(0.3),
            psi_inset.animate.set_opacity(0.3),
            arrow_to_jet.animate.set_opacity(0.3),
            jet.animate.set_opacity(0.3),
            psi_symbol.animate.set_opacity(0.3),
            jet_note.animate.set_opacity(0.3),
            FadeIn(p3, shift=UP * 0.08),
            FadeIn(heads[2]),
            LaggedStart(*[FadeIn(g, shift=UP * 0.08 + RIGHT * 0.05) for g in bunch], lag_ratio=0.15),
            FadeIn(bunch_note),
            LaggedStart(*[FadeIn(l) for l in pose_labs], lag_ratio=0.12),
        )

        strengths = VGroup(
            result_chip(r"Robust to light", ACCENT_CYAN).move_to([xs[0], -2.62, 0]),
            result_chip(r"< 100 images", ACCENT_TEAL).move_to([xs[1], -2.62, 0]),
            result_chip(r"High accuracy", ACCENT_MINT).move_to([xs[2], -2.62, 0]),
        )
        system_box = SurroundingRectangle(pillars, color=ACCENT_LAVENDER, buff=0.18, stroke_width=2.0)
        balance = label(r"design + signal, before big training", UP * 3.32, color=TEXT_MUTED, scale=0.28)

        beat_to(
            seg_end(T, 4),
            p1.animate.set_opacity(0.72),
            p2.animate.set_opacity(0.72),
            p3.animate.set_opacity(0.72),
            heads[0].animate.set_opacity(1.0),
            heads[1].animate.set_opacity(1.0),
            heads[2].animate.set_opacity(1.0),
            graph.animate.set_opacity(0.78),
            graph_note.animate.set_opacity(1.0),
            input_patch.animate.set_opacity(0.78),
            patch_lbl.animate.set_opacity(1.0),
            not_color_box.animate.set_opacity(0.78),
            not_color_cross.animate.set_opacity(0.78),
            not_color_lbl.animate.set_opacity(1.0),
            psi_inset.animate.set_opacity(0.78),
            arrow_to_jet.animate.set_opacity(1.0),
            jet.animate.set_opacity(0.78),
            psi_symbol.animate.set_opacity(1.0),
            jet_note.animate.set_opacity(1.0),
            bunch.animate.set_opacity(0.88),
            bunch_note.animate.set_opacity(1.0),
            pose_labs.animate.set_opacity(1.0),
            Create(system_box),
            FadeIn(balance, shift=DOWN * 0.05),
            LaggedStart(*[FadeIn(c, shift=UP * 0.07) for c in strengths], lag_ratio=0.16),
        )

        tail = max(0.0, T["duration"] - elapsed - 0.18)
        if tail > 0.05:
            self.wait(tail)
