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
TMP_IMG_DIR = Path("/tmp/video_manim_s12_imgs")
TMP_IMG_DIR.mkdir(parents=True, exist_ok=True)


class S12_Recognition(Scene):
    SCENE_KEY = "scene_12"

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
                    img = ImageMobject(str(square_cache(p) if p.name.startswith("s2_") or p.name in ("face.png", "face_hd.png", "s8_face.png") else p))
                    img.scale_to_fit_height(height)
                    return img
            raise FileNotFoundError(f"Asset {name} not found in {ASSET_DIR}")

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

        def candidate_card(pos, name, asset_name):
            box = RoundedRectangle(
                width=1.25,
                height=1.30,
                corner_radius=0.08,
                color=ACCENT_LAVENDER,
                stroke_width=1.2,
                fill_color=BG_NAVY_SOFT,
                fill_opacity=0.72,
            ).move_to(pos)
            
            face_img = load_face(asset_name, height=0.72).move_to(pos + UP * 0.08)
            
            def L_card(u, v):
                tl = face_img.get_corner(UL)
                br = face_img.get_corner(DR)
                return np.array([tl[0] + u * (br[0] - tl[0]), tl[1] + v * (br[1] - tl[1]), 0])
            
            pts_card = {name_lm: L_card(u, v) for name_lm, (u, v) in lm_coords.items()}
            graph = make_graph(pts_card, color=ACCENT_LAVENDER, stroke=1.0, node_radius=0.02)
            tag = label(name, pos + UP * 0.50, color=TEXT_MUTED, scale=0.22, bold=True)
            
            return Group(box, face_img, graph, tag)

        title = label("Recognition", UP * 3.05, color=TEXT_PRIMARY, scale=0.58, bold=True)
        
        # B0: PROBE (left side - x = -5.2)
        probe_box = RoundedRectangle(
            width=2.4,
            height=3.2,
            corner_radius=0.12,
            color=ACCENT_CYAN,
            stroke_width=1.8,
            fill_color=BG_NAVY_SOFT,
            fill_opacity=0.78,
        ).move_to(LEFT * 5.2 + DOWN * 0.15)
        probe_lbl = label("PROBE", LEFT * 5.2 + UP * 1.70, color=ACCENT_CYAN, scale=0.40, bold=True)
        probe_face = load_face("s8_face", height=2.2).move_to(LEFT * 5.2 + DOWN * 0.05)

        def L_probe(u, v):
            tl = probe_face.get_corner(UL)
            br = probe_face.get_corner(DR)
            return np.array([tl[0] + u * (br[0] - tl[0]), tl[1] + v * (br[1] - tl[1]), 0])

        pts_probe = {name: L_probe(u, v) for name, (u, v) in lm_coords.items()}
        probe_graph = make_graph(pts_probe, color=ACCENT_CYAN, stroke=1.8, node_radius=0.05)

        locked = label("elastic grid locked", LEFT * 5.2 + DOWN * 1.40, color=ACCENT_MINT, scale=0.28, bold=True)
        lock_icon = VGroup(
            RoundedRectangle(width=0.36, height=0.28, corner_radius=0.04, color=ACCENT_MINT, stroke_width=1.8),
            Arc(radius=0.18, start_angle=0, angle=PI, color=ACCENT_MINT, stroke_width=2.0).shift(UP * 0.14),
        ).move_to(LEFT * 5.2 + DOWN * 1.05)

        probe_group = Group(probe_box, probe_face, probe_graph)

        beat_to(seg_end(T, 0), FadeIn(title), FadeIn(probe_group), FadeIn(probe_lbl), FadeIn(locked), Create(lock_icon))

        # B1: featherlight
        feather = VGroup(
            ParametricFunction(
                lambda t: np.array([0.32 * np.sin(t), 0.82 * np.cos(t), 0]),
                t_range=[-1.05, 1.05],
                color=ACCENT_MINT,
                stroke_width=2.2,
            ),
            Line(ORIGIN, DOWN * 1.3, color=ACCENT_MINT, stroke_width=2.2),
            *[Line(DOWN * y, DOWN * y + RIGHT * (0.18 + y * 0.05), color=ACCENT_MINT, stroke_width=1.3) for y in np.linspace(0.25, 1.05, 5)],
        ).scale(0.8).move_to(RIGHT * 1.2 + UP * 0.15)
        light_lbl = label("featherlight", RIGHT * 1.2 + DOWN * 1.1, color=ACCENT_MINT, scale=0.46, bold=True)
        beat_to(seg_end(T, 1), DrawBorderThenFill(feather), FadeIn(light_lbl, shift=UP * 0.08))

        # B2: GALLERY (middle - x = 0.4, spans [-2.0, 2.8])
        gallery_frame = RoundedRectangle(
            width=4.8,
            height=3.9,
            corner_radius=0.13,
            color=ACCENT_LAVENDER,
            stroke_width=1.4,
            fill_color=BG_NAVY_SOFT,
            fill_opacity=0.35,
        ).move_to(RIGHT * 0.4 + DOWN * 0.05)
        # Place GALLERY label inside the frame to prevent colliding with formula
        gallery_lbl = label("GALLERY", RIGHT * 0.4 + UP * 1.62, color=ACCENT_LAVENDER, scale=0.38, bold=True)

        candidates = Group()
        gallery_assets = ["s9_face_other", "s2_personA", "s8_face", "s2_personB", "s2_same_neutral", "face"]
        for r in range(2):
            for c in range(3):
                idx = r * 3 + c + 1
                pos = np.array([0.4 + (c - 1) * 1.45, -0.05 + (0.45 - r) * 1.40, 0])
                candidates.add(candidate_card(pos, f"M{idx}", gallery_assets[idx - 1]))

        # Beams probe -> candidates
        beams = VGroup(*[
            Line(probe_box.get_right() + RIGHT * 0.08, candidates[i][0].get_left() + LEFT * 0.05, color=ACCENT_CYAN, stroke_width=1.2).set_opacity(0.18 + 0.06 * i)
            for i in range(len(candidates))
        ])

        beat_to(
            seg_end(T, 2),
            FadeOut(feather),
            FadeOut(light_lbl),
            FadeIn(gallery_frame),
            FadeIn(gallery_lbl),
            LaggedStart(*[FadeIn(c, shift=UP * 0.05) for c in candidates], lag_ratio=0.05),
            LaggedStart(*[Create(b) for b in beams], lag_ratio=0.04),
        )

        # B3: Formula (shift up to UP * 2.85)
        formula = MathTex(
            r"S_G = \frac{1}{N}\sum_i S_a(J_i^{probe},J_i^{gallery})",
            tex_template=EN_TEX_TEMPLATE,
            color=MATH_YELLOW,
        ).scale(0.58).move_to(UP * 2.48)
        
        # Chips placed at DOWN * 2.55 below the gallery frame
        phase_card = RoundedRectangle(width=2.25, height=0.65, corner_radius=0.08, color=ACCENT_CORAL, stroke_width=1.4, fill_color=ACCENT_CORAL, fill_opacity=0.08).move_to(LEFT * 0.7 + DOWN * 2.55)
        phase_lbl = label("drop phase", phase_card.get_center(), color=ACCENT_CORAL, scale=0.34, bold=True)
        amp_card = RoundedRectangle(width=2.65, height=0.65, corner_radius=0.08, color=ACCENT_MINT, stroke_width=1.7, fill_color=ACCENT_MINT, fill_opacity=0.10).move_to(RIGHT * 2.0 + DOWN * 2.55)
        amp_lbl = label("amplitude only", amp_card.get_center(), color=ACCENT_MINT, scale=0.34, bold=True)

        beat_to(seg_end(T, 3), Write(formula), FadeIn(phase_card), FadeIn(phase_lbl), FadeIn(amp_card), FadeIn(amp_lbl))

        # B4: expression robust comparison smile
        smile = Arc(radius=0.32, start_angle=205 * DEGREES, angle=130 * DEGREES, color=ACCENT_MINT, stroke_width=2.5).move_to(probe_face.get_center() + DOWN * 0.42)
        robust = label("robust to smiles", LEFT * 5.2 + DOWN * 2.45, color=ACCENT_MINT, scale=0.30, bold=True)
        beat_to(seg_end(T, 4), Create(smile), FadeIn(robust), amp_card.animate.set_stroke(ACCENT_MINT, width=3.0))

        # B5: RANK (right side - x = 5.3, spans [4.0, 6.6])
        scores = [0.64, 0.51, 0.92, 0.48, 0.73, 0.39]
        score_tags = VGroup()
        for i, score in enumerate(scores):
            color = ACCENT_MINT if score == max(scores) else TEXT_MUTED
            score_tags.add(label(f"{score:.2f}", candidates[i].get_bottom() + DOWN * 0.18, color=color, scale=0.25, bold=score == max(scores)))
            
        rank_panel = RoundedRectangle(width=2.6, height=3.05, corner_radius=0.12, color=TEXT_MUTED, stroke_width=1.0, fill_color=BG_NAVY_SOFT, fill_opacity=0.88).move_to(RIGHT * 5.3 + DOWN * 0.05)
        rank_title = label("RANK", RIGHT * 5.3 + UP * 1.28, color=TEXT_PRIMARY, scale=0.34, bold=True)
        
        rows = VGroup()
        ordered = [("1", "M3", "0.92", ACCENT_MINT), ("2", "M5", "0.73", TEXT_MUTED), ("3", "M1", "0.64", TEXT_MUTED)]
        for j, (rank, name, val, color) in enumerate(ordered):
            y = 0.66 - j * 0.58
            row = RoundedRectangle(width=2.1, height=0.40, corner_radius=0.05, color=color, stroke_width=1.0, fill_color=color, fill_opacity=0.08).move_to(RIGHT * 5.3 + UP * y)
            row_lbl = label(f"{rank}. {name}    {val}", row.get_center(), color=color, scale=0.24, bold=j == 0)
            rows.add(VGroup(row, row_lbl))
            
        winner = label("[WINNER]", RIGHT * 5.3 + DOWN * 1.35, color=ACCENT_MINT, scale=0.36, bold=True)
        # Winner ring inside the gallery surrounding M3 (candidates[2])
        ring = Circle(radius=0.72, color=ACCENT_MINT, stroke_width=3).move_to(candidates[2].get_center())

        beat_to(
            seg_end(T, 5),
            LaggedStart(*[FadeIn(s, shift=UP * 0.04) for s in score_tags], lag_ratio=0.05),
            FadeIn(rank_panel),
            FadeIn(rank_title),
            LaggedStart(*[FadeIn(r, shift=LEFT * 0.06) for r in rows], lag_ratio=0.10),
            Create(ring),
            FadeIn(winner, shift=UP * 0.08),
        )

        tail = max(0.0, T["duration"] - elapsed - 0.18)
        if tail > 0.05:
            self.wait(tail)
