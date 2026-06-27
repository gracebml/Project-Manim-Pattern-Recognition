import os
import sys
import json
from pathlib import Path
from PIL import Image, ImageOps

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from manim import *
import numpy as np
from _common import *

ASSET_DIR = Path(__file__).resolve().parents[2] / "assets"
TMP_IMG_DIR = Path("/tmp/video_manim_s11_imgs")
TMP_IMG_DIR.mkdir(parents=True, exist_ok=True)


class S11_Elastic(ThreeDScene):
    SCENE_KEY = "scene_11"

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

        def label(text, pos, color=TEXT_PRIMARY, scale=0.36, bold=False):
            return en_label(text, color=color, scale=scale, bold=bold).move_to(pos)

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
                    img = ImageMobject(str(square_cache(p) if p.name.startswith("s2_") or p.name in ("face.png", "face_hd.png", "s8_face.png") else p))
                    img.scale_to_fit_height(height)
                    return img
            raise FileNotFoundError(f"Asset {name} not found in {ASSET_DIR}")

        def make_face_card(img, color=ACCENT_BLUE):
            frame = RoundedRectangle(
                width=img.get_width() + 0.12,
                height=img.get_height() + 0.12,
                corner_radius=0.10,
                color=color,
                stroke_width=1.6,
                fill_color=BG_NAVY_SOFT,
                fill_opacity=0.6,
            )
            img.move_to(frame.get_center())
            return Group(frame, img)

        def spring_between(start, end, color=ACCENT_LAVENDER, amp=0.04, cycles=6, stroke_width=2.5):
            start = np.array(start)
            end = np.array(end)
            delta = end - start
            length = max(np.linalg.norm(delta[:2]), 0.001)
            unit = delta / length
            perp = np.array([-unit[1], unit[0], 0])
            return ParametricFunction(
                lambda t: start + delta * t + perp * amp * np.sin(cycles * TAU * t),
                t_range=[0, 1],
                color=color,
                stroke_width=stroke_width,
            )

        # Load landmarks coordinates
        landmarks_file = ASSET_DIR / "s8_landmarks.json"
        if landmarks_file.exists():
            with open(landmarks_file, "r") as f:
                lm_coords = json.load(f)["landmarks"]
        else:
            lm_coords = {
                "forehead": [0.50, 0.22],
                "eye_l": [0.40, 0.39],
                "eye_r": [0.60, 0.39],
                "nose": [0.50, 0.49],
                "mouth_l": [0.43, 0.58],
                "mouth_r": [0.57, 0.58],
                "chin": [0.50, 0.69],
                "cheek_l": [0.30, 0.49],
                "cheek_r": [0.70, 0.49],
            }

        edges = [
            ("forehead", "eye_l"), ("forehead", "eye_r"), ("eye_l", "eye_r"),
            ("eye_l", "nose"), ("eye_r", "nose"), ("nose", "mouth_l"),
            ("nose", "mouth_r"), ("mouth_l", "mouth_r"), ("mouth_l", "chin"),
            ("mouth_r", "chin"), ("eye_l", "cheek_l"), ("mouth_l", "cheek_l"),
            ("eye_r", "cheek_r"), ("mouth_r", "cheek_r"),
        ]

        local_base = {
            name: np.array([(u - 0.5) * 3.45, (0.5 - v) * 3.45, 0])
            for name, (u, v) in lm_coords.items()
        }

        def make_graph(pts_dict, color=ACCENT_CYAN, stroke=2.1, node_radius=0.065, opacity=0.82):
            lines = VGroup(*[
                Line(pts_dict[a], pts_dict[b], color=color, stroke_width=stroke).set_opacity(opacity)
                for a, b in edges
            ])
            dots = VGroup(*[
                Dot(pts_dict[name], radius=node_radius, color=color).set_opacity(0.96)
                for name in pts_dict.keys()
            ])
            return VGroup(lines, dots)

        def make_graph_local(pos=ORIGIN, scale=1.0, color=ACCENT_CYAN, stroke=2.1, opacity=0.82):
            pts = {k: v * scale + pos for k, v in local_base.items()}
            return make_graph(pts, color=color, stroke=stroke, opacity=opacity), pts

        def scan_grid(pos=ORIGIN, scale=1.0, color=ACCENT_BLUE):
            g, _ = make_graph_local(pos, scale, color, stroke=1.8)
            box = SurroundingRectangle(g, color=color, buff=0.22, stroke_width=1.4)
            return VGroup(box, g)

        title = label(r"Elastic Matching", UP * 3.0, color=TEXT_PRIMARY, scale=0.58, bold=True)

        # B0: heart of algorithm, rigid to supple.
        face_img = load_face("s8_face", fallback_style="neutral", color=ACCENT_CYAN, height=4.0)
        face_card = make_face_card(face_img).move_to(DOWN * 0.10)
        
        img_mob = face_card[1]
        def L(u, v):
            tl = img_mob.get_corner(UL)
            br = img_mob.get_corner(DR)
            return np.array([tl[0] + u * (br[0] - tl[0]), tl[1] + v * (br[1] - tl[1]), 0])

        pts_true = {name: L(u, v) for name, (u, v) in lm_coords.items()}
        g0 = make_graph(pts_true, color=ACCENT_LAVENDER, stroke=2.2)

        mode_bar = VGroup(
            RoundedRectangle(width=4.6, height=0.40, corner_radius=0.16, color=ACCENT_BLUE, stroke_width=1.0, fill_color=BG_NAVY_SOFT, fill_opacity=0.85),
            Dot(LEFT * 2.0, radius=0.10, color=ACCENT_CORAL),
        ).move_to(DOWN * 2.40)
        rigid = label(r"Rigid", LEFT * 2.05 + DOWN * 2.80, color=ACCENT_CORAL, scale=0.28, bold=True)
        supple = label(r"Supple", RIGHT * 2.05 + DOWN * 2.80, color=ACCENT_MINT, scale=0.28, bold=True)
        
        beat_to(seg_end(T, 0), FadeIn(title, shift=DOWN * 0.05), FadeIn(face_card), Create(g0[0]), FadeIn(g0[1]), FadeIn(mode_bar), FadeIn(rigid), FadeIn(supple))

        # B1: rigid block sliding.
        scale_fac = 4.0 / 3.45
        rigid_grid = scan_grid(LEFT * 4.25 + UP * 0.35, scale=0.9 * scale_fac, color=ACCENT_CORAL)
        heat = VGroup(
            Circle(radius=0.35, color=ACCENT_CORAL, fill_color=ACCENT_CORAL, fill_opacity=0.10, stroke_width=0).move_to(LEFT * 4.25 + UP * 0.35),
            Circle(radius=0.42, color=ACCENT_CYAN, fill_color=ACCENT_CYAN, fill_opacity=0.10, stroke_width=0).move_to(LEFT * 1.15 + DOWN * 0.10),
            Circle(radius=0.55, color=ACCENT_MINT, fill_color=ACCENT_MINT, fill_opacity=0.16, stroke_width=0).move_to(DOWN * 0.10),
        )
        lam_inf = MathTex(r"\lambda=\infty", tex_template=EN_TEX_TEMPLATE, color=ACCENT_CORAL).scale(0.66).move_to(RIGHT * 4.5 + UP * 2.0)
        scan_lbl = label(r"rigid scan", LEFT * 3.8 + UP * 2.15, color=ACCENT_CORAL, scale=0.34, bold=True)
        beat_to(seg_end(T, 1), FadeOut(g0), FadeIn(heat), FadeIn(rigid_grid), FadeIn(scan_lbl), Write(lam_inf), rigid_grid.animate.move_to(DOWN * 0.10))

        # B2: scale globally and stretch aspect ratio.
        g_size = scan_grid(DOWN * 0.10, scale=1.10 * scale_fac, color=ACCENT_CYAN)
        g_aspect = scan_grid(DOWN * 0.10, scale=1.10 * scale_fac, color=ACCENT_CYAN)
        g_aspect.stretch(1.22, dim=0)
        g_aspect.stretch(0.88, dim=1)
        size_lbl = label(r"global scale", LEFT * 3.35 + UP * 2.15, color=ACCENT_CYAN, scale=0.34, bold=True)
        aspect_lbl = label(r"width / height", RIGHT * 3.25 + UP * 2.15, color=ACCENT_CYAN, scale=0.34, bold=True)
        beat_to(seg_end(T, 2), FadeOut(heat), FadeOut(scan_lbl), ReplacementTransform(rigid_grid, g_size), FadeIn(size_lbl), mode_bar[1].animate.move_to(DOWN * 2.40 + LEFT * 0.7))
        beat_to(T["segments"][3]["start"], ReplacementTransform(g_size, g_aspect), FadeOut(size_lbl), FadeIn(aspect_lbl))

        # B3-B4: elastic final step, graph released.
        elastic = label(r"ELASTIC", UP * 2.20, color=ACCENT_LAVENDER, scale=0.72, bold=True)
        locks = VGroup(
            Arc(radius=0.18, start_angle=0, angle=PI, color=ACCENT_CORAL, stroke_width=2).move_to(LEFT * 3.6 + DOWN * 1.95),
            Rectangle(width=0.42, height=0.30, color=ACCENT_CORAL, stroke_width=2).move_to(LEFT * 3.6 + DOWN * 2.13),
        )
        release = label(r"released", LEFT * 3.6 + DOWN * 2.55, color=ACCENT_MINT, scale=0.28, bold=True)
        beat_to(seg_end(T, 3), FadeOut(lam_inf), FadeOut(aspect_lbl), FadeIn(elastic, shift=DOWN * 0.08), g_aspect.animate.set_color(ACCENT_LAVENDER), mode_bar[1].animate.move_to(DOWN * 2.40 + RIGHT * 1.15))
        beat_to(seg_end(T, 4), FadeIn(locks), Rotate(locks[0], angle=-35 * DEGREES, about_point=locks[0].get_left()), FadeIn(release), mode_bar[1].animate.set_color(ACCENT_MINT))

        # B5: nodes crawl to true landmarks.
        initial_offsets = {
            "forehead": RIGHT * 0.15 + UP * 0.10,
            "eye_l": LEFT * 0.12 + DOWN * 0.08,
            "eye_r": RIGHT * 0.18 + UP * 0.05,
            "nose": LEFT * 0.10 + UP * 0.15,
            "mouth_l": LEFT * 0.08 + DOWN * 0.12,
            "mouth_r": RIGHT * 0.14 + DOWN * 0.08,
            "chin": DOWN * 0.15 + LEFT * 0.10,
            "cheek_l": LEFT * 0.18 + UP * 0.05,
            "cheek_r": RIGHT * 0.15 + DOWN * 0.12,
        }
        pts_initial = {
            name: pts_true[name] + initial_offsets[name]
            for name in lm_coords
        }

        crawl_dots = VGroup(*[
            Dot(pts_initial[name], radius=0.075, color=ACCENT_MINT)
            for name in lm_coords
        ])
        
        crawl_lines = VGroup()
        for a, b in edges:
            idx_a = list(lm_coords.keys()).index(a)
            idx_b = list(lm_coords.keys()).index(b)
            line = always_redraw(
                lambda idx_a=idx_a, idx_b=idx_b: Line(
                    crawl_dots[idx_a].get_center(),
                    crawl_dots[idx_b].get_center(),
                    color=ACCENT_MINT,
                    stroke_width=2.1
                ).set_opacity(0.82)
            )
            crawl_lines.add(line)

        targets = VGroup(*[
            Circle(radius=0.12, color=ACCENT_CYAN, stroke_width=1.2).move_to(pts_true[name])
            for name in lm_coords
        ])
        crawl_lbl = label(r"nodes crawl to landmarks", DOWN * 2.55, color=ACCENT_MINT, scale=0.36, bold=True)

        beat_to(
            seg_end(T, 5) - 3.0,
            FadeOut(g_aspect),
            FadeOut(locks),
            FadeOut(release),
            FadeIn(targets),
            FadeIn(crawl_dots),
            FadeIn(crawl_lines),
            FadeIn(crawl_lbl)
        )
        beat_to(
            seg_end(T, 5),
            *[
                crawl_dots[i].animate.move_to(pts_true[name])
                for i, name in enumerate(lm_coords)
            ],
            rate_func=linear
        )

        # B6: edges as springs.
        springs = VGroup(*[
            spring_between(pts_true[a], pts_true[b], color=ACCENT_LAVENDER, amp=0.04, cycles=6)
            for a, b in [("eye_l", "nose"), ("nose", "mouth_l"), ("nose", "mouth_r")]
        ])
        
        final_graph = make_graph(pts_true, color=ACCENT_MINT, stroke=2.1, opacity=0.45)
        lam2 = MathTex(r"\lambda=2", tex_template=EN_TEX_TEMPLATE, color=ACCENT_LAVENDER).scale(0.70).move_to(RIGHT * 4.2 + UP * 2.1)
        springs_lbl = label(r"edges act as springs", DOWN * 2.55, color=ACCENT_LAVENDER, scale=0.36, bold=True)

        beat_to(
            seg_end(T, 6),
            FadeOut(crawl_lbl),
            FadeOut(crawl_lines),
            FadeOut(crawl_dots),
            FadeIn(final_graph),
            FadeIn(springs),
            FadeIn(lam2),
            FadeIn(springs_lbl)
        )

        # B7: two phases.
        phase_title = label(r"Two Phases", UP * 2.80, color=TEXT_PRIMARY, scale=0.54, bold=True)
        timeline = Line(LEFT * 4.4, RIGHT * 4.4, color=ACCENT_BLUE, stroke_width=3).shift(UP * 1.6)
        p1_dot = Dot(LEFT * 2.2 + UP * 1.6, radius=0.11, color=ACCENT_CYAN)
        p2_dot = Dot(RIGHT * 2.2 + UP * 1.6, radius=0.11, color=ACCENT_LAVENDER)
        p1_lbl = label(r"Phase 1", LEFT * 2.2 + UP * 2.05, color=ACCENT_CYAN, scale=0.36, bold=True)
        p2_lbl = label(r"Phase 2", RIGHT * 2.2 + UP * 2.05, color=ACCENT_LAVENDER, scale=0.36, bold=True)

        beat_to(
            seg_end(T, 7),
            FadeOut(title),
            FadeOut(face_card),
            FadeOut(final_graph),
            FadeOut(targets),
            FadeOut(springs),
            FadeOut(springs_lbl),
            FadeOut(lam2),
            FadeOut(elastic),
            FadeOut(mode_bar),
            FadeOut(rigid),
            FadeOut(supple),
            FadeIn(phase_title),
            Create(timeline),
            FadeIn(p1_dot),
            FadeIn(p2_dot),
            FadeIn(p1_lbl),
            FadeIn(p2_lbl)
        )

        # B8: Normalization
        p1_card = RoundedRectangle(width=3.6, height=3.2, corner_radius=0.12, color=ACCENT_CYAN, stroke_width=1.8, fill_color=BG_NAVY_SOFT, fill_opacity=0.6).move_to(LEFT * 2.5 + DOWN * 0.8)
        norm_face = load_face("s8_face", height=1.8).move_to(LEFT * 2.5 + DOWN * 0.5)
        crop_box = Square(side_length=1.1, color=ACCENT_CYAN, stroke_width=2.2).move_to(LEFT * 2.5 + DOWN * 0.5)
        norm_lbl = label(r"Normalization", LEFT * 2.5 + DOWN * 1.7, color=ACCENT_CYAN, scale=0.34, bold=True)
        size_lbl2 = label(r"crop: 128 x 128", LEFT * 2.5 + DOWN * 2.1, color=TEXT_MUTED, scale=0.28)

        arrow = thin_arrow(LEFT * 0.55 + DOWN * 0.8, RIGHT * 0.55 + DOWN * 0.8, color=TEXT_MUTED, stroke_width=2.2)

        p2_card = RoundedRectangle(width=3.6, height=3.2, corner_radius=0.12, color=ACCENT_LAVENDER, stroke_width=1.8, fill_color=BG_NAVY_SOFT, fill_opacity=0.6).move_to(RIGHT * 2.5 + DOWN * 0.8)
        recog_lbl = label(r"Recognition", RIGHT * 2.5 + DOWN * 1.7, color=ACCENT_LAVENDER, scale=0.34, bold=True)
        recog_face = load_face("s8_face", height=1.8).move_to(RIGHT * 2.5 + DOWN * 0.5)

        beat_to(
            seg_end(T, 8),
            p1_dot.animate.scale(1.35),
            FadeIn(p1_card),
            FadeIn(norm_face),
            Create(crop_box),
            FadeIn(norm_lbl),
            FadeIn(size_lbl2),
            GrowArrow(arrow),
            FadeIn(p2_card),
            FadeIn(recog_lbl),
            FadeIn(recog_face),
            p2_dot.animate.scale(1.20)
        )

        # B9: Recognition
        def L_recog(u, v):
            tl = recog_face.get_corner(UL)
            br = recog_face.get_corner(DR)
            return np.array([tl[0] + u * (br[0] - tl[0]), tl[1] + v * (br[1] - tl[1]), 0])

        pts_recog = {name: L_recog(u, v) for name, (u, v) in lm_coords.items()}
        recog_graph = make_graph(pts_recog, color=ACCENT_LAVENDER, stroke=1.8, node_radius=0.04)
        final_lbl = label(r"final detailed graph", RIGHT * 2.5 + DOWN * 2.1, color=TEXT_MUTED, scale=0.28)

        beat_to(
            seg_end(T, 9),
            Create(recog_graph[0]),
            LaggedStart(*[GrowFromCenter(d) for d in recog_graph[1]], lag_ratio=0.05),
            FadeIn(final_lbl),
            p2_lbl.animate.set_color(ACCENT_MINT)
        )

        tail = max(0.0, T["duration"] - elapsed - 0.18)
        if tail > 0.05:
            self.wait(tail)
