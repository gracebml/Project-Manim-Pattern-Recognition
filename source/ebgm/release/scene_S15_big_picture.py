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
TMP_IMG_DIR = Path("/tmp/video_manim_s15_imgs")
TMP_IMG_DIR.mkdir(parents=True, exist_ok=True)


class S15_BigPicture(Scene):
    SCENE_KEY = "scene_15"

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

        def load_face(name, height=2.2):
            for ext in (".png", ".jpg", ".jpeg"):
                p = ASSET_DIR / f"{name}{ext}"
                if p.exists():
                    img = ImageMobject(str(square_cache(p) if p.name.startswith("s2_") or p.name in ("face.png", "face_hd.png", "s8_face.png", "s15_animal", "s15_vehicle") else p))
                    img.scale_to_fit_height(height)
                    return img
            raise FileNotFoundError(f"Asset {name} not found in {ASSET_DIR}")

        def make_face_card(img, color=ACCENT_BLUE):
            frame = RoundedRectangle(
                width=img.get_width() + 0.10,
                height=img.get_height() + 0.10,
                corner_radius=0.08,
                color=color,
                stroke_width=1.4,
                fill_color=BG_NAVY_SOFT,
                fill_opacity=0.60,
            )
            img.move_to(frame.get_center())
            return Group(frame, img)

        def graph_icon(pos, color=ACCENT_CYAN, scale=1.0):
            pts = [LEFT * 0.35 + UP * 0.28, RIGHT * 0.35 + UP * 0.28, ORIGIN, LEFT * 0.25 + DOWN * 0.34, RIGHT * 0.25 + DOWN * 0.34]
            edges = [(0, 1), (0, 2), (1, 2), (2, 3), (2, 4), (3, 4)]
            lines = VGroup(*[Line(pts[a], pts[b], color=color, stroke_width=1.6) for a, b in edges])
            dots = VGroup(*[Dot(p, radius=0.045, color=color) for p in pts])
            return VGroup(lines, dots).scale(scale).move_to(pos)
            
        def get_sunglasses(pos):
            p = ASSET_DIR / "s15_sunglasses.png"
            if p.exists():
                img = ImageMobject(str(p))
                img.scale_to_fit_width(0.9)
                img.move_to(pos)
                return img
            # Fallback vector sunglasses (filled black)
            return VGroup(
                Circle(radius=0.18, color=TEXT_PRIMARY, stroke_width=1.8, fill_color="#111111", fill_opacity=0.95),
                Circle(radius=0.18, color=TEXT_PRIMARY, stroke_width=1.8, fill_color="#111111", fill_opacity=0.95).shift(RIGHT * 0.44),
                Line(RIGHT * 0.18, RIGHT * 0.26, color=TEXT_PRIMARY, stroke_width=1.8)
            ).move_to(pos)

        title = label("The Big Picture", UP * 3.05, color=TEXT_PRIMARY, scale=0.72, bold=True)
        broad = label("one idea, many in-class recognition problems", UP * 2.45, color=TEXT_MUTED, scale=0.45)
        
        # B0-B1: Broad examples with real images
        cards = Group()
        
        c0_face = load_face("s8_face", height=0.9)
        c0_card = make_face_card(c0_face, color=ACCENT_CYAN).move_to(LEFT * 4.5 + UP * 0.22)
        c0_txt = label("faces", LEFT * 4.5 + DOWN * 0.82, color=ACCENT_CYAN, scale=0.42, bold=True)
        c0_box = RoundedRectangle(width=2.35, height=2.1, corner_radius=0.14, color=ACCENT_CYAN, stroke_width=1.5, fill_color=BG_NAVY_SOFT, fill_opacity=0.68).move_to(LEFT * 4.5 + DOWN * 0.15)
        c0_group = Group(c0_box, c0_card, c0_txt)
        cards.add(c0_group)

        c1_face = load_face("s15_animal", height=0.9)
        c1_card = make_face_card(c1_face, color=ACCENT_LAVENDER).move_to(LEFT * 1.5 + UP * 0.22)
        c1_txt = label("animals", LEFT * 1.5 + DOWN * 0.82, color=ACCENT_LAVENDER, scale=0.42, bold=True)
        c1_box = RoundedRectangle(width=2.35, height=2.1, corner_radius=0.14, color=ACCENT_LAVENDER, stroke_width=1.5, fill_color=BG_NAVY_SOFT, fill_opacity=0.68).move_to(LEFT * 1.5 + DOWN * 0.15)
        c1_group = Group(c1_box, c1_card, c1_txt)
        cards.add(c1_group)

        c2_face = load_face("s15_vehicle", height=0.9)
        c2_card = make_face_card(c2_face, color=ACCENT_MINT).move_to(RIGHT * 1.5 + UP * 0.22)
        c2_txt = label("vehicles", RIGHT * 1.5 + DOWN * 0.82, color=ACCENT_MINT, scale=0.42, bold=True)
        c2_box = RoundedRectangle(width=2.35, height=2.1, corner_radius=0.14, color=ACCENT_MINT, stroke_width=1.5, fill_color=BG_NAVY_SOFT, fill_opacity=0.68).move_to(RIGHT * 1.5 + DOWN * 0.15)
        c2_group = Group(c2_box, c2_card, c2_txt)
        cards.add(c2_group)

        c3_icon = graph_icon(RIGHT * 4.5 + UP * 0.22, color=ACCENT_BLUE, scale=0.92)
        c3_txt = label("variants", RIGHT * 4.5 + DOWN * 0.82, color=ACCENT_BLUE, scale=0.42, bold=True)
        c3_box = RoundedRectangle(width=2.35, height=2.1, corner_radius=0.14, color=ACCENT_BLUE, stroke_width=1.5, fill_color=BG_NAVY_SOFT, fill_opacity=0.68).move_to(RIGHT * 4.5 + DOWN * 0.15)
        c3_group = Group(c3_box, c3_icon, c3_txt)
        cards.add(c3_group)

        beat_to(seg_end(T, 1), FadeIn(title), FadeIn(broad), LaggedStart(*[FadeIn(c, scale=0.85) for c in cards], lag_ratio=0.12))

        # B2-B5: PCA vs EBGM Comparison
        pca_panel = RoundedRectangle(width=5.35, height=3.7, corner_radius=0.14, color=ACCENT_BLUE, stroke_width=1.6, fill_color=BG_NAVY_SOFT, fill_opacity=0.78).move_to(LEFT * 3.15 + DOWN * 0.15)
        ebgm_panel = RoundedRectangle(width=5.35, height=3.7, corner_radius=0.14, color=ACCENT_LAVENDER, stroke_width=1.6, fill_color=BG_NAVY_SOFT, fill_opacity=0.78).move_to(RIGHT * 3.15 + DOWN * 0.15)
        pca_lbl = label("PCA", pca_panel.get_top() + DOWN * 0.42, color=ACCENT_BLUE, scale=0.55, bold=True)
        ebgm_lbl = label("EBGM", ebgm_panel.get_top() + DOWN * 0.42, color=ACCENT_LAVENDER, scale=0.55, bold=True)
        
        pca_face_card = make_face_card(load_face("s8_face", height=2.2)).move_to(pca_panel.get_center() + DOWN * 0.05)
        pca_face = pca_face_card[1]
        
        ebgm_face_card = make_face_card(load_face("s8_face", height=2.2)).move_to(ebgm_panel.get_center() + DOWN * 0.05)
        ebgm_face = ebgm_face_card[1]

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

        def make_graph(pts_dict, color=ACCENT_CYAN, stroke=1.5, node_radius=0.045, opacity=0.82):
            lines = VGroup(*[
                Line(pts_dict[a], pts_dict[b], color=color, stroke_width=stroke).set_opacity(opacity)
                for a, b in edges
            ])
            dots = VGroup(*[
                Dot(pts_dict[name], radius=node_radius, color=color).set_opacity(0.96)
                for name in pts_dict.keys()
            ])
            return VGroup(lines, dots)

        def L_pca(u, v):
            tl = pca_face.get_corner(UL)
            br = pca_face.get_corner(DR)
            return np.array([tl[0] + u * (br[0] - tl[0]), tl[1] + v * (br[1] - tl[1]), 0])

        def L_ebgm(u, v):
            tl = ebgm_face.get_corner(UL)
            br = ebgm_face.get_corner(DR)
            return np.array([tl[0] + u * (br[0] - tl[0]), tl[1] + v * (br[1] - tl[1]), 0])

        pts_pca = {name: L_pca(u, v) for name, (u, v) in lm_coords.items()}
        pts_ebgm = {name: L_ebgm(u, v) for name, (u, v) in lm_coords.items()}

        pca_grid = NumberPlane(
            x_range=[-1.0, 1.0, 0.18],
            y_range=[-1.1, 1.1, 0.18],
            background_line_style={"stroke_color": ACCENT_BLUE, "stroke_width": 0.8, "stroke_opacity": 0.42},
        ).scale(0.78).move_to(pca_face.get_center())

        ebgm_graph = make_graph(pts_ebgm, color=ACCENT_LAVENDER, stroke=1.5, node_radius=0.05)

        # Sunglasses positioned dynamically over eye midpoints
        pos_glasses_l = (pts_pca["eye_l"] + pts_pca["eye_r"]) / 2 + UP * 0.05
        pos_glasses_r = (pts_ebgm["eye_l"] + pts_ebgm["eye_r"]) / 2 + UP * 0.05

        glasses_l = get_sunglasses(pos_glasses_l)
        glasses_r = get_sunglasses(pos_glasses_r)
        
        # B2 entry: PCA and EBGM cards with grid and graph
        beat_to(seg_end(T, 2), FadeOut(cards), FadeOut(broad), FadeIn(pca_panel), FadeIn(ebgm_panel), FadeIn(pca_lbl), FadeIn(ebgm_lbl), FadeIn(pca_face_card), Create(pca_grid), FadeIn(ebgm_face_card), Create(ebgm_graph[0]), FadeIn(ebgm_graph[1]), FadeIn(glasses_l), FadeIn(glasses_r))

        # PCA global damage red loang overlay
        pca_damage = Rectangle(
            width=pca_face.get_width(),
            height=pca_face.get_height(),
            color=ACCENT_CORAL,
            stroke_width=0,
            fill_color=ACCENT_CORAL,
            fill_opacity=0.35
        ).move_to(pca_face.get_center())
        
        pca_bad = label("global vector disturbed", pca_panel.get_bottom() + UP * 0.45, color=ACCENT_CORAL, scale=0.38, bold=True)
        
        # EBGM safe/coral nodes
        eye_ring = VGroup(
            Circle(radius=0.18, color=ACCENT_CORAL, stroke_width=2.0).move_to(pts_ebgm["eye_l"]),
            Circle(radius=0.18, color=ACCENT_CORAL, stroke_width=2.0).move_to(pts_ebgm["eye_r"])
        )
        safe = label("only eye jets disturbed", ebgm_panel.get_bottom() + UP * 0.45, color=ACCENT_MINT, scale=0.38, bold=True)

        idx_eye_l = list(lm_coords.keys()).index("eye_l")
        idx_eye_r = list(lm_coords.keys()).index("eye_r")
        eye_dots = VGroup(ebgm_graph[1][idx_eye_l], ebgm_graph[1][idx_eye_r])
        other_dots = VGroup(*[ebgm_graph[1][i] for i in range(len(ebgm_graph[1])) if i not in (idx_eye_l, idx_eye_r)])

        # B3-B5 PCA global damage loang flash first, then EBGM compartmentalized risk
        beat_to(
            T["segments"][3]["start"] + 1.5,
            FadeIn(pca_damage),
            Flash(pca_face.get_center(), color=ACCENT_CORAL, num_lines=12, line_length=0.4, flash_radius=1.5),
            FadeIn(pca_bad)
        )

        beat_to(
            seg_end(T, 5),
            ebgm_graph[0].animate.set_color(ACCENT_MINT),
            other_dots.animate.set_color(ACCENT_MINT),
            eye_dots.animate.set_color(ACCENT_CORAL).scale(1.2),
            Create(eye_ring),
            FadeIn(safe)
        )

        # B6-B9: Summary card (Limits & Strengths)
        limits_panel = RoundedRectangle(width=10.0, height=4.5, corner_radius=0.16, color=GRID_LINE, stroke_width=1.0, fill_color=BG_NAVY_SOFT, fill_opacity=0.5).move_to(DOWN * 0.35)
        
        cons_title = label("Limits \\& Strengths", UP * 2.60, color=TEXT_PRIMARY, scale=0.72, bold=True)
        
        limits_lbl = label("Limits", LEFT * 2.5 + UP * 1.15, color=ACCENT_CORAL, scale=0.58, bold=True)
        lim_x1 = VGroup(Line(LEFT * 0.10 + DOWN * 0.10, RIGHT * 0.10 + UP * 0.10, color=ACCENT_CORAL, stroke_width=3.0), Line(LEFT * 0.10 + UP * 0.10, RIGHT * 0.10 + DOWN * 0.10, color=ACCENT_CORAL, stroke_width=3.0)).move_to(LEFT * 4.3 + UP * 0.45)
        lim_lbl1 = label("Weak beyond 22 degrees rotation", LEFT * 3.9 + UP * 0.45, color=TEXT_PRIMARY, scale=0.38).move_to(LEFT * 3.9 + UP * 0.45, aligned_edge=LEFT)
        lim_x2 = VGroup(Line(LEFT * 0.10 + DOWN * 0.10, RIGHT * 0.10 + UP * 0.10, color=ACCENT_CORAL, stroke_width=3.0), Line(LEFT * 0.10 + UP * 0.10, RIGHT * 0.10 + DOWN * 0.10, color=ACCENT_CORAL, stroke_width=3.0)).move_to(LEFT * 4.3 + DOWN * 0.25)
        lim_lbl2 = label("Fragile when landmarks are occluded", LEFT * 3.9 + DOWN * 0.25, color=TEXT_PRIMARY, scale=0.38).move_to(LEFT * 3.9 + DOWN * 0.25, aligned_edge=LEFT)
        
        strengths_lbl = label("Strengths", RIGHT * 2.5 + UP * 1.15, color=ACCENT_MINT, scale=0.58, bold=True)
        str_check1 = MathTex(r"\checkmark", tex_template=EN_TEX_TEMPLATE, color=ACCENT_MINT).scale(0.9).move_to(RIGHT * 0.8 + UP * 0.45)
        str_lbl1 = label("Robust to lighting \\& expression", RIGHT * 1.2 + UP * 0.45, color=TEXT_PRIMARY, scale=0.38).move_to(RIGHT * 1.2 + UP * 0.45, aligned_edge=LEFT)
        str_check2 = MathTex(r"\checkmark", tex_template=EN_TEX_TEMPLATE, color=ACCENT_MINT).scale(0.9).move_to(RIGHT * 0.8 + DOWN * 0.25)
        str_lbl2 = label("Compartmentalized localized risk", RIGHT * 1.2 + DOWN * 0.25, color=TEXT_PRIMARY, scale=0.38).move_to(RIGHT * 1.2 + DOWN * 0.25, aligned_edge=LEFT)
        
        no_training = RoundedRectangle(width=8.0, height=0.8, corner_radius=0.10, color=ACCENT_MINT, stroke_width=1.6, fill_color=ACCENT_MINT, fill_opacity=0.08).move_to(DOWN * 1.40)
        no_training_lbl = label("No massive training dataset required", no_training.get_center(), color=ACCENT_MINT, scale=0.45, bold=True)

        old = Group(pca_panel, ebgm_panel, pca_lbl, ebgm_lbl, pca_face_card, pca_grid, ebgm_face_card, ebgm_graph, glasses_l, glasses_r, pca_damage, pca_bad, eye_ring, safe)

        # 1. Clear old elements quickly and decisively
        self.play(FadeOut(old, shift=DOWN*0.2), run_time=0.4); elapsed += 0.4

        # 2. Panel + Title entry
        self.play(
            GrowFromCenter(limits_panel),
            FadeIn(cons_title, scale=0.8),
            run_time=0.6
        ); elapsed += 0.6
        self.play(
            Indicate(cons_title, color=ACCENT_LAVENDER, scale_factor=1.05),
            run_time=0.5
        ); elapsed += 0.5

        # 3. Two columns reveal with rhythm
        left_anims = [
            FadeIn(limits_lbl, scale=0.9),
            AnimationGroup(Create(lim_x1), FadeIn(lim_lbl1)),
            AnimationGroup(Create(lim_x2), FadeIn(lim_lbl2)),
        ]
        right_anims = [
            FadeIn(strengths_lbl, scale=0.9),
            AnimationGroup(Write(str_check1), FadeIn(str_lbl1)),
            AnimationGroup(Write(str_check2), FadeIn(str_lbl2)),
        ]
        self.play(
            LaggedStart(*left_anims, lag_ratio=0.15, run_time=1.8),
            LaggedStart(*right_anims, lag_ratio=0.15, run_time=1.8),
        ); elapsed += 1.8

        # 4. no_training mint banner entry
        self.play(
            GrowFromEdge(no_training, DOWN),
            FadeIn(no_training_lbl, scale=0.9),
            run_time=0.6
        ); elapsed += 0.6
        self.play(
            Indicate(no_training_lbl, color=ACCENT_MINT, scale_factor=1.05),
            run_time=0.5
        ); elapsed += 0.5

        # 5. Absorb remaining segment budget
        beat_to(seg_end(T, 9))

        tail = max(0.0, T["duration"] - elapsed - 0.18)
        if tail > 0.05:
            self.wait(tail)
