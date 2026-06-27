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
TMP_IMG_DIR = Path("/tmp/video_manim_s09_imgs")
TMP_IMG_DIR.mkdir(parents=True, exist_ok=True)



class S09_BunchGraph(ThreeDScene):
    SCENE_KEY = "scene_09"

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
                    img = ImageMobject(str(square_cache(p) if p.name.startswith("s2_") or p.name in ("face.png", "face_hd.png", "s8_face.png", "s9_face_other.png") or p.name.startswith("s9_sample") else p))
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

        def make_eye_frame(img, color=ACCENT_CYAN):
            frame = RoundedRectangle(
                width=img.get_width() + 0.08,
                height=img.get_height() + 0.08,
                corner_radius=0.06,
                color=color,
                stroke_width=1.4,
                fill_color=BG_NAVY_SOFT,
                fill_opacity=1.0,
            )
            img.move_to(frame.get_center())
            return Group(frame, img)

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

        title = label(r"Face Bunch Graph", UP * 3.05, color=TEXT_PRIMARY, scale=0.72, bold=True)

        # B0: one graph cannot fit another face.
        face_img_a = load_face("s8_face", fallback_style="neutral", color=ACCENT_CYAN, height=2.4)
        face_img_b = load_face("s9_face_other", fallback_style="neutral", color=ACCENT_CYAN, height=2.4)
        
        face_card_a = make_face_card(face_img_a, ACCENT_BLUE).move_to(LEFT * 2.8 + DOWN * 0.1)
        face_card_b = make_face_card(face_img_b, ACCENT_LAVENDER).move_to(RIGHT * 2.8 + DOWN * 0.1)

        img_mob_a = face_card_a[1]
        def L_a(u, v):
            tl = img_mob_a.get_corner(UL)
            br = img_mob_a.get_corner(DR)
            return np.array([tl[0] + u*(br[0]-tl[0]), tl[1] + v*(br[1]-tl[1]), 0])

        img_mob_b = face_card_b[1]
        def L_b(u, v):
            tl = img_mob_b.get_corner(UL)
            br = img_mob_b.get_corner(DR)
            return np.array([tl[0] + u*(br[0]-tl[0]), tl[1] + v*(br[1]-tl[1]), 0])

        pts_a = {name: L_a(u, v) for name, (u, v) in lm_coords.items()}
        pts_b_bad = {name: L_b(u, v) + np.array([-0.25, 0.22, 0]) for name, (u, v) in lm_coords.items()}

        g_a_edges = VGroup(*[Line(pts_a[x], pts_a[y], color=ACCENT_CYAN, stroke_width=2.0) for x, y in edges])
        g_a_nodes = VGroup(*[Dot(p, radius=0.065, color=ACCENT_CYAN) for p in pts_a.values()])
        g_a = VGroup(g_a_edges, g_a_nodes)

        bad_edges = VGroup(*[Line(pts_b_bad[x], pts_b_bad[y], color=ACCENT_CORAL, stroke_width=2.0) for x, y in edges])
        bad_nodes = VGroup(*[Dot(p, radius=0.065, color=ACCENT_CORAL) for p in pts_b_bad.values()])
        bad_g = VGroup(bad_edges, bad_nodes)

        mismatch = label(r"one graph cannot fit every face", DOWN * 2.45, color=ACCENT_CORAL, scale=0.52, bold=True)
        beat_to(seg_end(T, 0), FadeIn(title, shift=DOWN * 0.05), FadeIn(face_card_a), FadeIn(g_a), FadeIn(face_card_b), FadeIn(bad_g), FadeIn(mismatch))

        # B1-B2: solution and name.
        solution = label(r"The solution:", UP * 1.95, color=TEXT_MUTED, scale=0.48)
        fbg_name = label(r"FACE BUNCH GRAPH", ORIGIN, color=ACCENT_LAVENDER, scale=0.85, bold=True)
        box = SurroundingRectangle(fbg_name, color=ACCENT_LAVENDER, buff=0.22, stroke_width=2.0)
        beat_to(seg_end(T, 1), FadeOut(face_card_a), FadeOut(face_card_b), FadeOut(g_a), FadeOut(bad_g), FadeOut(mismatch), FadeIn(solution), FadeIn(fbg_name, shift=DOWN * 0.05))
        beat_to(seg_end(T, 2), Create(box), fbg_name.animate.set_color(ACCENT_MINT))

        # B3: stack dozens of graphs.
        sample_imgs = []
        for i in range(5):
            img = load_face(f"s9_sample{i+1}", height=2.2)
            sample_imgs.append(img)

        stack = Group()
        colors = [ACCENT_BLUE, ACCENT_TEAL, ACCENT_CYAN, ACCENT_LAVENDER, ACCENT_MINT]
        top_pts_local = None
        for i in range(5):
            img = sample_imgs[i]
            color = colors[i]
            scale_val = 0.72 + i * 0.07
            pos = np.array([-1.2 + i * 0.6, -0.2 + i * 0.1, 0])
            opacity = 0.3 + 0.17 * i

            card = make_face_card(img, color=color).scale(scale_val).move_to(pos)
            card.set_opacity(opacity)

            img_mob = card[1]
            def L_local(u, v, im=img_mob):
                tl = im.get_corner(UL)
                br = im.get_corner(DR)
                return np.array([tl[0] + u*(br[0]-tl[0]), tl[1] + v*(br[1]-tl[1]), 0])

            pts_local = {name: L_local(u, v) for name, (u, v) in lm_coords.items()}
            if i == 4:
                top_pts_local = pts_local

            g_edges = VGroup(*[Line(pts_local[x], pts_local[y], color=color, stroke_width=1.6).set_opacity(opacity) for x, y in edges])
            g_nodes = VGroup(*[Dot(p, radius=0.045 * scale_val, color=color).set_opacity(opacity) for p in pts_local.values()])

            stack_element = Group(card, g_edges, g_nodes)
            stack.add(stack_element)

        stack_lbl = label(r"stack many sample graphs", DOWN * 2.4, color=ACCENT_CYAN, scale=0.52, bold=True)
        beat_to(seg_end(T, 3), FadeOut(solution), FadeOut(fbg_name), FadeOut(box), LaggedStart(*[FadeIn(g, shift=UP * 0.08) for g in stack], lag_ratio=0.08), FadeIn(stack_lbl))

        # B4: eye node becomes a whole bunch.
        bunch_card = RoundedRectangle(width=7.4, height=2.2, corner_radius=0.12, color=ACCENT_LAVENDER, stroke_width=1.8, fill_color=BG_NAVY, fill_opacity=0.92).move_to(DOWN * 0.15)
        
        eye_narrow = ImageMobject(str(ASSET_DIR / "s9_eye_narrow.png")).set_height(1.1)
        eye_round = ImageMobject(str(ASSET_DIR / "s9_eye_round.png")).set_height(1.1)
        eye_glasses = ImageMobject(str(ASSET_DIR / "s9_eye_glasses.png")).set_height(1.1)

        eye_narrow_frame = make_eye_frame(eye_narrow).move_to(LEFT * 2.2 + DOWN * 0.05)
        eye_round_frame = make_eye_frame(eye_round).move_to(DOWN * 0.05)
        eye_glasses_frame = make_eye_frame(eye_glasses).move_to(RIGHT * 2.2 + DOWN * 0.05)

        eyes = Group(eye_narrow_frame, eye_round_frame, eye_glasses_frame)
        eye_bunch_lbl = label(r"eye node = a bunch", UP * 1.35, color=ACCENT_LAVENDER, scale=0.58, bold=True)
        
        beat_to(
            seg_end(T, 4),
            FadeOut(stack_lbl),
            FadeOut(stack),
            FadeIn(bunch_card, shift=UP * 0.06),
            LaggedStart(*[FadeIn(e, shift=UP * 0.06) for e in eyes], lag_ratio=0.12),
            FadeIn(eye_bunch_lbl),
        )

        # B5: show examples.
        labs = VGroup(
            label(r"narrow", LEFT * 2.2 + DOWN * 0.8, color=ACCENT_CYAN, scale=0.38),
            label(r"round", DOWN * 0.8, color=ACCENT_TEAL, scale=0.38),
            label(r"spectacled", RIGHT * 2.2 + DOWN * 0.8, color=ACCENT_LAVENDER, scale=0.38),
        )
        beat_to(seg_end(T, 5), LaggedStart(*[FadeIn(l, shift=UP * 0.04) for l in labs], lag_ratio=0.10), eye_glasses_frame.animate.scale(1.08))

        # B6-B7: search the bunch and elect a local expert.
        stranger_img = load_face("s9_face_other", fallback_style="neutral", color=TEXT_MUTED, height=2.2)
        stranger = make_face_card(stranger_img, color=TEXT_MUTED).move_to(LEFT * 5.0 + DOWN * 0.15).set_opacity(0.4)
        
        search_beam = thin_arrow(LEFT * 3.8 + DOWN * 0.15, LEFT * 2.8 + DOWN * 0.15, color=ACCENT_MINT, stroke_width=2.0, buff=0.05)
        search_lbl = label(r"search the bunch", LEFT * 4.3 + UP * 1.25, color=ACCENT_MINT, scale=0.42, bold=True)
        beat_to(seg_end(T, 6), FadeIn(stranger), GrowArrow(search_beam), FadeIn(search_lbl))

        expert_box = SurroundingRectangle(eye_glasses_frame, color=ACCENT_MINT, buff=0.15, stroke_width=2.5)
        expert_lbl = label(r"Local Expert", RIGHT * 2.2 + UP * 0.88, color=ACCENT_MINT, scale=0.45, bold=True)
        beat_to(
            seg_end(T, 7),
            Create(expert_box),
            FadeIn(expert_lbl, shift=DOWN * 0.05),
            eye_glasses_frame[0].animate.set_color(ACCENT_MINT)
        )

        # B8: best fit for each landmark.
        selected = VGroup(
            Dot(LEFT * 2.2 + DOWN * 1.8, radius=0.08, color=ACCENT_CYAN),
            Dot(DOWN * 1.8, radius=0.08, color=ACCENT_MINT),
            Dot(RIGHT * 2.2 + DOWN * 1.8, radius=0.08, color=ACCENT_LAVENDER)
        )
        fit_arrows = VGroup(*[
            thin_arrow(
                start=np.array([x_pos, -0.9, 0]),
                end=np.array([x_pos, -1.6, 0]),
                color=color,
                stroke_width=2.0,
                buff=0.05
            )
            for x_pos, color in [(-2.2, ACCENT_CYAN), (0.0, ACCENT_MINT), (2.2, ACCENT_LAVENDER)]
        ])
        fit_lbl = label(r"best fit for each landmark", DOWN * 2.45, color=MATH_YELLOW, scale=0.45, bold=True)
        beat_to(seg_end(T, 8), LaggedStart(*[GrowArrow(a) for a in fit_arrows], lag_ratio=0.10), FadeIn(selected), FadeIn(fit_lbl))

        # B9: coverage through cross-combination.
        coverage = label(r"almost limitless coverage", UP * 2.55, color=ACCENT_LAVENDER, scale=0.66, bold=True)
        combo_lines = VGroup(
            Line(LEFT * 2.2 + DOWN * 0.5, DOWN * 1.8, color=ACCENT_LAVENDER, stroke_width=1.5).set_opacity(0.35),
            Line(LEFT * 2.2 + DOWN * 0.5, RIGHT * 2.2 + DOWN * 1.8, color=ACCENT_LAVENDER, stroke_width=1.5).set_opacity(0.35),
            Line(DOWN * 0.5, LEFT * 2.2 + DOWN * 1.8, color=ACCENT_LAVENDER, stroke_width=1.5).set_opacity(0.35),
            Line(DOWN * 0.5, RIGHT * 2.2 + DOWN * 1.8, color=ACCENT_LAVENDER, stroke_width=1.5).set_opacity(0.35),
            Line(RIGHT * 2.2 + DOWN * 0.5, LEFT * 2.2 + DOWN * 1.8, color=ACCENT_LAVENDER, stroke_width=1.5).set_opacity(0.35),
            Line(RIGHT * 2.2 + DOWN * 0.5, DOWN * 1.8, color=ACCENT_LAVENDER, stroke_width=1.5).set_opacity(0.35),
        )
        beat_to(
            seg_end(T, 9),
            FadeOut(search_beam),
            FadeOut(search_lbl),
            FadeIn(coverage, shift=DOWN * 0.05),
            LaggedStart(*[Create(l) for l in combo_lines], lag_ratio=0.02),
            expert_box.animate.set_stroke(ACCENT_LAVENDER, width=2.0),
        )

        tail = max(0.0, T["duration"] - elapsed - 0.18)
        if tail > 0.05:
            self.wait(tail)
