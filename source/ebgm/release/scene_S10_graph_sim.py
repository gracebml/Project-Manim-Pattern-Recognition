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
TMP_IMG_DIR = Path("/tmp/video_manim_s10_imgs")
TMP_IMG_DIR.mkdir(parents=True, exist_ok=True)


class S10_GraphSim(ThreeDScene):
    SCENE_KEY = "scene_10"

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

        def label(text, pos, color=TEXT_PRIMARY, scale=0.36, bold=False):
            return en_label(text, color=color, scale=scale, bold=bold).move_to(pos)

        def current_pts(base_pts, nose_pos=None):
            out = {k: p.copy() for k, p in base_pts.items()}
            if nose_pos is not None:
                out["nose"] = nose_pos
            return out

        def make_graph(base_pts, color=ACCENT_CYAN, stroke_width=2.1, node_radius=0.065, opacity=0.82, nose_pos=None):
            pts_now = current_pts(base_pts, nose_pos)
            lines = VGroup(*[
                Line(pts_now[a], pts_now[b], color=color, stroke_width=stroke_width).set_opacity(opacity)
                for a, b in edges
            ])
            dots = VGroup(*[
                Dot(pts_now[name], radius=node_radius, color=color).set_opacity(0.96)
                for name in pts_now.keys()
            ])
            return VGroup(lines, dots)

        def spring_between(start, end, color=ACCENT_CORAL, amp=0.045, cycles=7, stroke_width=3.0):
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

        face_img = load_face("s8_face", fallback_style="neutral", color=ACCENT_CYAN, height=4.4)
        face_card = make_face_card(face_img).move_to(DOWN * 0.10)
        img_mob = face_card[1]

        def L(u, v):
            tl = img_mob.get_corner(UL)
            br = img_mob.get_corner(DR)
            return np.array([tl[0] + u * (br[0] - tl[0]), tl[1] + v * (br[1] - tl[1]), 0])

        pts = {name: L(u, v) for name, (u, v) in lm_coords.items()}

        title = label(r"Graph Similarity", UP * 3.03, color=TEXT_PRIMARY, scale=0.72, bold=True)

        # B0: fitted graph question.
        fitted_graph = make_graph(pts, color=ACCENT_CYAN, stroke_width=2.0, node_radius=0.064)
        question = label(r"correctly fitted?", DOWN * 2.65, color=TEXT_PRIMARY, scale=0.40, bold=True)
        beat_to(
            seg_end(T, 0),
            FadeIn(title, shift=DOWN * 0.05),
            FadeIn(face_card),
            Create(fitted_graph[0]),
            LaggedStart(*[GrowFromCenter(d) for d in fitted_graph[1]], lag_ratio=0.035),
            FadeIn(question),
        )

        # B1-B2: formula and tug of war.
        formula = MathTex(
            r"S_B = \mathrm{Reward} - \lambda \cdot \mathrm{Penalty}",
            tex_template=EN_TEX_TEMPLATE,
            color=MATH_YELLOW,
        ).scale(0.92).move_to(UP * 1.85)

        reward_card = RoundedRectangle(
            width=3.4, height=2.2, corner_radius=0.12, color=ACCENT_MINT,
            stroke_width=1.8, fill_color=ACCENT_MINT, fill_opacity=0.07,
        ).move_to(LEFT * 4.0 + DOWN * 0.8)
        penalty_card = RoundedRectangle(
            width=3.4, height=2.2, corner_radius=0.12, color=ACCENT_CORAL,
            stroke_width=1.8, fill_color=ACCENT_CORAL, fill_opacity=0.07,
        ).move_to(RIGHT * 4.0 + DOWN * 0.8)

        reward_lbl = label(r"Reward", reward_card.get_top() + DOWN * 0.38, color=ACCENT_MINT, scale=0.48, bold=True)
        penalty_lbl = label(r"Penalty", penalty_card.get_top() + DOWN * 0.38, color=ACCENT_CORAL, scale=0.48, bold=True)

        rope = Line(LEFT * 2.3 + DOWN * 0.8, RIGHT * 2.3 + DOWN * 0.8, color=TEXT_MUTED, stroke_width=4)
        knot = Dot(DOWN * 0.8, radius=0.10, color=TEXT_PRIMARY)
        tug = label(r"optimization = tug of war", DOWN * 2.2, color=TEXT_MUTED, scale=0.42)

        b1_t0 = seg_end(T, 0)
        beat_to(
            b1_t0 + 0.6,
            FadeOut(face_card),
            FadeOut(fitted_graph),
            FadeOut(question),
        )
        beat_to(
            b1_t0 + 1.6,
            Write(formula),
            Create(rope),
            FadeIn(knot),
            FadeIn(reward_card),
            FadeIn(penalty_card),
            FadeIn(reward_lbl),
            FadeIn(penalty_lbl),
            FadeIn(tug),
        )
        beat_to(seg_end(T, 1))
        beat_to(seg_end(T, 2), knot.animate.shift(LEFT * 0.45), rope.animate.set_color(ACCENT_MINT))

        # B3-B5: reward and penalty terms.
        jet_match = label(r"jet similarity", reward_card.get_center() + UP * 0.12, color=ACCENT_MINT, scale=0.38, bold=True)
        match_bars = VGroup(
            Rectangle(width=1.6, height=0.12, stroke_width=0, fill_color=ACCENT_MINT, fill_opacity=0.68),
            Rectangle(width=1.3, height=0.12, stroke_width=0, fill_color=ACCENT_MINT, fill_opacity=0.48).shift(DOWN * 0.20),
            Rectangle(width=1.5, height=0.12, stroke_width=0, fill_color=ACCENT_MINT, fill_opacity=0.56).shift(DOWN * 0.40),
        ).move_to(reward_card.get_bottom() + UP * 0.55)
        beat_to(seg_end(T, 3), FadeIn(jet_match), FadeIn(match_bars), knot.animate.shift(LEFT * 0.25))

        distortion = label(r"geometric distortion", penalty_card.get_center() + UP * 0.12, color=ACCENT_CORAL, scale=0.38, bold=True)
        spring = ParametricFunction(
            lambda t: np.array([t, 0.075 * np.sin(28 * t), 0]),
            t_range=[-0.65, 0.65],
            color=ACCENT_CORAL,
            stroke_width=2.8,
        ).move_to(penalty_card.get_bottom() + UP * 0.55)
        beat_to(seg_end(T, 4), FadeIn(distortion), Create(spring), knot.animate.move_to(DOWN * 0.8), rope.animate.set_color(TEXT_MUTED))

        lambda_lbl = MathTex(r"\lambda", tex_template=EN_TEX_TEMPLATE, color=ACCENT_CORAL).scale(1.2).move_to(RIGHT * 4.0 + UP * 1.35)
        lambda_note = label(r"scales the penalty", RIGHT * 4.0 + UP * 0.70, color=ACCENT_CORAL, scale=0.38)
        beat_to(seg_end(T, 5), FadeIn(lambda_lbl), FadeIn(lambda_note), penalty_card.animate.set_stroke(ACCENT_CORAL, width=3.0))

        # B6: force nose onto forehead, keeping one graph on the face.
        face_img_bad = load_face("s8_face", fallback_style="neutral", color=ACCENT_CYAN, height=4.4)
        bad_face_card = make_face_card(face_img_bad).move_to(DOWN * 0.10)
        bad_img_mob = bad_face_card[1]

        def L_bad(u, v):
            tl = bad_img_mob.get_corner(UL)
            br = bad_img_mob.get_corner(DR)
            return np.array([tl[0] + u * (br[0] - tl[0]), tl[1] + v * (br[1] - tl[1]), 0])

        bad_base_pts = {name: L_bad(u, v) for name, (u, v) in lm_coords.items()}
        nose_start = bad_base_pts["nose"]
        nose_target = L_bad(0.50, 0.255)
        nose_alpha = ValueTracker(0.0)

        def warped_pts():
            a = nose_alpha.get_value()
            return current_pts(bad_base_pts, nose_start * (1 - a) + nose_target * a)

        moving_edges = VGroup(*[
            always_redraw(
                lambda x=x, y=y: Line(
                    warped_pts()[x],
                    warped_pts()[y],
                    color=ACCENT_CYAN,
                    stroke_width=2.0,
                ).set_opacity(0.78)
            )
            for x, y in edges
        ])
        moving_nodes = VGroup(*[
            always_redraw(
                lambda name=name: Dot(
                    warped_pts()[name],
                    radius=0.066,
                    color=ACCENT_CORAL if name == "nose" and nose_alpha.get_value() > 0.05 else ACCENT_CYAN,
                ).set_opacity(0.98)
            )
            for name in bad_base_pts.keys()
        ])
        moving_graph = VGroup(moving_edges, moving_nodes)
        
        nose_arrow = thin_arrow(
            start=nose_start + RIGHT * 0.3,
            end=nose_target + RIGHT * 0.3,
            color=ACCENT_CORAL,
            stroke_width=2.2,
            buff=0.08,
        )
        force_lbl = label(r"force nose onto forehead", DOWN * 2.9, color=ACCENT_CORAL, scale=0.48, bold=True)
        b6_switch = min(seg_end(T, 6) - 1.70, elapsed + 0.82)
        beat_to(
            b6_switch,
            FadeOut(formula),
            FadeOut(rope),
            FadeOut(knot),
            FadeOut(reward_card),
            FadeOut(penalty_card),
            FadeOut(reward_lbl),
            FadeOut(penalty_lbl),
            FadeOut(tug),
            FadeOut(jet_match),
            FadeOut(match_bars),
            FadeOut(distortion),
            FadeOut(spring),
            FadeOut(lambda_lbl),
            FadeOut(lambda_note),
            FadeIn(bad_face_card),
            FadeIn(moving_graph),
        )
        beat_to(
            seg_end(T, 6),
            GrowArrow(nose_arrow),
            FadeIn(force_lbl),
            nose_alpha.animate.set_value(1.0),
        )

        # B7: stretched edge.
        final_pts = warped_pts()
        stretched = always_redraw(
            lambda: Line(
                warped_pts()["eye_l"],
                warped_pts()["nose"],
                color=ACCENT_CORAL,
                stroke_width=6.0,
            ).set_opacity(0.92)
        )
        spring_edge = always_redraw(
            lambda: spring_between(
                warped_pts()["eye_l"],
                warped_pts()["nose"],
                color=ACCENT_CORAL,
                amp=0.035,
                cycles=6,
                stroke_width=3.0,
            )
        )
        stretch_lbl = label(r"edge stretches", LEFT * 3.8 + UP * 1.35, color=ACCENT_CORAL, scale=0.45, bold=True)
        stretch_hint = thin_arrow(
            start=stretch_lbl.get_right() + RIGHT * 0.1,
            end=(final_pts["eye_l"] + final_pts["nose"]) / 2 + LEFT * 0.2,
            color=ACCENT_CORAL,
            stroke_width=2.2,
            buff=0.08,
        )
        beat_to(
            seg_end(T, 7),
            Create(stretched),
            Create(spring_edge),
            GrowArrow(stretch_hint),
            FadeIn(stretch_lbl),
            moving_edges.animate.set_opacity(0.48),
        )

        # B8: enormous penalty.
        penalty_region = Circle(
            radius=1.18,
            color=ACCENT_CORAL,
            stroke_width=0,
            fill_color=ACCENT_CORAL,
            fill_opacity=0.15,
        ).move_to((final_pts["eye_l"] + final_pts["nose"]) / 2)
        
        huge = label(r"ENORMOUS PENALTY", RIGHT * 3.6 + UP * 1.6, color=ACCENT_CORAL, scale=0.58, bold=True)
        score = MathTex(r"S_B \downarrow", tex_template=EN_TEX_TEMPLATE, color=ACCENT_CORAL).scale(1.15).move_to(RIGHT * 3.6 + UP * 0.9)
        beat_to(
            seg_end(T, 8),
            FadeIn(penalty_region),
            FadeIn(huge, shift=DOWN * 0.06),
            Write(score),
            stretched.animate.set_stroke(width=8.0),
        )

        tail = max(0.0, T["duration"] - elapsed - 0.18)
        if tail > 0.05:
            self.wait(tail)
