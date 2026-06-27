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
TMP_IMG_DIR = Path("/tmp/video_manim_s16_imgs")
TMP_IMG_DIR.mkdir(parents=True, exist_ok=True)


class S16_Conclusion(Scene):
    SCENE_KEY = "scene_16"

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

        title = label("Elastic Bunch Graph Matching", UP * 3.0, color=TEXT_PRIMARY, scale=0.72, bold=True)
        subtitle = label("a symphony of three ideas", UP * 2.42, color=TEXT_MUTED, scale=0.45)

        # B0-B2: Symphony cards
        centers = [LEFT * 3.5 + UP * 0.45, ORIGIN + UP * 0.45, RIGHT * 3.5 + UP * 0.45]
        cards = VGroup()
        names = [("local signal", ACCENT_CYAN), ("wavelets", ACCENT_LAVENDER), ("geometry", ACCENT_MINT)]
        for center, (name, color) in zip(centers, names):
            box = RoundedRectangle(width=2.65, height=1.60, corner_radius=0.13, color=color, stroke_width=1.5, fill_color=BG_NAVY_SOFT, fill_opacity=0.80).move_to(center)
            if name == "local signal":
                icon = VGroup(*[Dot(center + np.array([x, y, 0]), radius=0.035, color=color) for x, y in [(-0.32, 0.18), (0.0, 0.25), (0.30, 0.12), (-0.10, -0.20), (0.28, -0.24)]])
            elif name == "wavelets":
                icon = ParametricFunction(lambda t: np.array([t, 0.18 * np.sin(12 * t) * np.exp(-t * t / 0.9), 0]), t_range=[-0.72, 0.72], color=color, stroke_width=2.0).move_to(center + UP * 0.18)
            else:
                pts = [center + LEFT * 0.36 + UP * 0.25, center + RIGHT * 0.36 + UP * 0.25, center + DOWN * 0.10, center + LEFT * 0.22 + DOWN * 0.36, center + RIGHT * 0.22 + DOWN * 0.36]
                icon = VGroup(*[Line(pts[a], pts[b], color=color, stroke_width=1.5) for a, b in [(0, 1), (0, 2), (1, 2), (2, 3), (2, 4), (3, 4)]], *[Dot(p, radius=0.035, color=color) for p in pts])
            txt = label(name, center + DOWN * 0.50, color=color, scale=0.38, bold=True)
            cards.add(VGroup(box, icon, txt))

        beat_to(seg_end(T, 2), FadeIn(title), FadeIn(subtitle), LaggedStart(*[FadeIn(c, scale=0.85) for c in cards], lag_ratio=0.10))

        # B3-B5: Crown and elastic landmarks live on
        crown = VGroup(
            Polygon(
                LEFT * 0.6,
                LEFT * 0.35 + UP * 0.40,
                LEFT * 0.12 + UP * 0.15,
                ORIGIN + UP * 0.48,
                RIGHT * 0.12 + UP * 0.15,
                RIGHT * 0.35 + UP * 0.40,
                RIGHT * 0.6,
                RIGHT * 0.45 + DOWN * 0.25,
                LEFT * 0.45 + DOWN * 0.25,
                color=ACCENT_CORAL,
                stroke_width=2.0,
                fill_color=ACCENT_CORAL,
                fill_opacity=0.12
            ),
            label("deep learning", ORIGIN + DOWN * 0.60, color=ACCENT_CORAL, scale=0.45, bold=True),
        ).move_to(UP * 0.20)
        lives = label("elastic landmarks still live on", DOWN * 1.65, color=ACCENT_LAVENDER, scale=0.55, bold=True)
        
        beat_to(seg_end(T, 5), FadeOut(cards), FadeIn(crown, shift=DOWN * 0.08), FadeIn(lives, shift=UP * 0.08))

        # B6: Final face grid on real face card
        final_face_card = make_face_card(load_face("s8_face", height=2.4)).move_to(ORIGIN + UP * 0.20)
        final_face = final_face_card[1]

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

        def L_final(u, v):
            tl = final_face.get_corner(UL)
            br = final_face.get_corner(DR)
            return np.array([tl[0] + u * (br[0] - tl[0]), tl[1] + v * (br[1] - tl[1]), 0])

        pts_final = {name: L_final(u, v) for name, (u, v) in lm_coords.items()}
        final_graph = make_graph(pts_final, color=ACCENT_LAVENDER, stroke=1.8, node_radius=0.05)

        # Keywords LOCAL · ELASTIC · GENERAL
        words = VGroup(
            label("LOCAL", LEFT * 3.0 + DOWN * 2.70, color=ACCENT_CYAN, scale=0.58, bold=True),
            label("ELASTIC", DOWN * 2.70, color=ACCENT_LAVENDER, scale=0.58, bold=True),
            label("GENERAL", RIGHT * 3.0 + DOWN * 2.70, color=ACCENT_MINT, scale=0.58, bold=True),
        )
        dots = VGroup(
            Dot(LEFT * 1.5 + DOWN * 2.70, radius=0.05, color=TEXT_MUTED),
            Dot(RIGHT * 1.5 + DOWN * 2.70, radius=0.05, color=TEXT_MUTED),
        )

        beat_to(
            seg_end(T, 6) - 1.0,
            FadeOut(crown),
            FadeOut(lives),
            FadeIn(final_face_card),
            Create(final_graph[0]),
            LaggedStart(*[GrowFromCenter(d) for d in final_graph[1]], lag_ratio=0.04)
        )
        beat_to(
            seg_end(T, 6),
            LaggedStart(
                FadeIn(words[0], shift=UP * 0.05),
                FadeIn(dots[0]),
                FadeIn(words[1], shift=UP * 0.05),
                FadeIn(dots[1]),
                FadeIn(words[2], shift=UP * 0.05),
                lag_ratio=0.15
            )
        )

        # B7-B8: Thanks & credits on clean background
        thanks = label("Thank you for watching", ORIGIN + UP * 0.45, color=TEXT_PRIMARY, scale=0.72, bold=True)
        next_video = label("See you in the next algorithm video", ORIGIN + DOWN * 0.35, color=TEXT_MUTED, scale=0.45)

        beat_to(
            seg_end(T, 8),
            FadeOut(final_face_card),
            FadeOut(final_graph),
            words.animate.set_opacity(0.25),
            dots.animate.set_opacity(0.25),
            FadeIn(thanks, shift=UP * 0.07),
            FadeIn(next_video, shift=UP * 0.05)
        )

        tail = max(0.0, T["duration"] - elapsed - 0.18)
        if tail > 0.05:
            self.wait(tail)
