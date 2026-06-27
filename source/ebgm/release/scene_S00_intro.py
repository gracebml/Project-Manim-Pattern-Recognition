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
TMP_IMG_DIR = Path("/tmp/video_manim_s00_imgs")
TMP_IMG_DIR.mkdir(parents=True, exist_ok=True)

TITLE = "ELASTIC BUNCH GRAPH MATCHING"
SUBTITLE_1 = "Pattern Recognition Tutorial"
SUBTITLE_2 = "How a 1997 algorithm taught machines to see faces"


class S00_Intro(Scene):
    def construct(self):
        self.camera.background_color = BG_NAVY

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
                lm_data = json.load(f)
            lm_coords = lm_data["landmarks"]
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

        # Create face-graph motif centered in background
        face_img = load_face("s8_face", height=2.6).move_to(DOWN * 0.3)
        face_img.set_opacity(0.16)

        def L(u, v):
            tl = face_img.get_corner(UL)
            br = face_img.get_corner(DR)
            return np.array([tl[0] + u*(br[0]-tl[0]), tl[1] + v*(br[1]-tl[1]), 0])

        pts = {name: L(u, v) for name, (u, v) in lm_coords.items()}

        edges = [
            ("forehead", "eye_l"), ("forehead", "eye_r"), ("eye_l", "eye_r"),
            ("eye_l", "nose"), ("eye_r", "nose"), ("nose", "mouth_l"),
            ("nose", "mouth_r"), ("mouth_l", "mouth_r"), ("mouth_l", "chin"),
            ("mouth_r", "chin"), ("eye_l", "cheek_l"), ("mouth_l", "cheek_l"),
            ("eye_r", "cheek_r"), ("mouth_r", "cheek_r"),
        ]

        nodes = VGroup(*[Dot(p, radius=0.05, color=ACCENT_LAVENDER) for p in pts.values()])
        edge_lines = VGroup(*[Line(pts[a], pts[b], color=ACCENT_LAVENDER, stroke_width=1.5).set_opacity(0.4) for a, b in edges])

        # Soft glowing outline for nodes/edges
        glow_lines = VGroup(*[cool_glow(line, color=ACCENT_LAVENDER) for line in edge_lines])

        motif = Group(face_img, glow_lines, edge_lines, nodes)

        # Title — big bright gold, with a soft glow halo
        title_mob = label(TITLE, UP * 1.65, color=MATH_YELLOW, scale=0.92, bold=True)
        title_glow = title_mob.copy().set_stroke(MATH_YELLOW, width=7, opacity=0.30).set_fill(opacity=0)
        cyan_line = Line(LEFT * 4.0 + UP * 1.16, RIGHT * 4.0 + UP * 1.16, color=ACCENT_CYAN, stroke_width=1.8)

        # Caption line (tagline) — moved down, clear of the face motif
        subtitle_1 = label(SUBTITLE_1, DOWN * 2.18, color=ACCENT_CYAN, scale=0.40, bold=True)
        # two short flanking dashes that grow out from the caption for a clean accent
        cap_dash_l = Line(ORIGIN, RIGHT * 0.55, color=ACCENT_CYAN, stroke_width=1.6).next_to(subtitle_1, LEFT, buff=0.30)
        cap_dash_r = Line(ORIGIN, RIGHT * 0.55, color=ACCENT_CYAN, stroke_width=1.6).next_to(subtitle_1, RIGHT, buff=0.30)
        # Tagline — italic lavender, a touch larger; writes itself out gradually
        subtitle_2 = Tex(
            r"\textit{%s}" % SUBTITLE_2,
            tex_template=EN_TEX_TEMPLATE, color=ACCENT_LAVENDER,
        ).scale(0.40 * LABEL_SCALE_BOOST).move_to(DOWN * 2.84)

        # 0.0 - 1.2s: Motif entrance
        self.play(
            FadeIn(face_img, run_time=0.6),
            LaggedStart(*[GrowFromCenter(n) for n in nodes], lag_ratio=0.03, run_time=0.5),
            Create(edge_lines, run_time=0.6),
            FadeIn(glow_lines, run_time=0.7),
        )
        self.wait(0.5)

        # 1.2 - 3.2s: Title punch-in + gold shimmer sweep across the letters
        self.play(
            FadeIn(title_mob, scale=0.8),
            FadeIn(title_glow, scale=0.8),
            Create(cyan_line),
            run_time=0.8
        )
        try:
            glyphs = list(title_mob[0])
        except (TypeError, IndexError):
            glyphs = [title_mob]
        self.play(
            LaggedStart(*[Indicate(g, color=WHITE, scale_factor=1.12) for g in glyphs], lag_ratio=0.04),
            run_time=0.9
        )
        self.wait(0.4)

        # 3.2 - 5.0s: Caption — stroke reveal + flanking dashes, then italic tagline writes out
        self.play(
            Write(subtitle_1),
            GrowFromCenter(cap_dash_l),
            GrowFromCenter(cap_dash_r),
            run_time=0.9
        )
        self.play(
            Indicate(subtitle_1, color=ACCENT_LAVENDER, scale_factor=1.06),
            run_time=0.4
        )
        self.play(Write(subtitle_2), run_time=1.2)

        # Hold & clean fade out
        self.wait(0.6)
        self.play(
            FadeOut(motif),
            FadeOut(title_mob),
            FadeOut(title_glow),
            FadeOut(cyan_line),
            FadeOut(subtitle_1),
            FadeOut(cap_dash_l),
            FadeOut(cap_dash_r),
            FadeOut(subtitle_2),
            run_time=0.8
        )
