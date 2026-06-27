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
TMP_IMG_DIR = Path("/tmp/video_manim_s08_imgs")
TMP_IMG_DIR.mkdir(parents=True, exist_ok=True)



class S08_ImageGraph(ThreeDScene):
    SCENE_KEY = "scene_08"

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

        def make_face_card(img):
            frame = RoundedRectangle(
                width=img.get_width() + 0.12,
                height=img.get_height() + 0.12,
                corner_radius=0.10,
                color=ACCENT_BLUE,
                stroke_width=1.6,
                fill_color=BG_NAVY_SOFT,
                fill_opacity=0.6,
            )
            img.move_to(frame.get_center())
            return Group(frame, img)

        def label(text, pos, color=TEXT_PRIMARY, scale=0.36, bold=False):
            return en_label(text, color=color, scale=scale, bold=bold).move_to(pos)

        def panel(width, height, pos, color, fill=0.06):
            return RoundedRectangle(
                width=width,
                height=height,
                corner_radius=0.12,
                color=color,
                stroke_width=1.7,
                fill_color=color,
                fill_opacity=fill,
            ).move_to(pos)

        def jet_icon(color=ACCENT_CYAN, scale=1.0):
            rays = VGroup()
            for i in range(8):
                a = i * TAU / 8
                start = ORIGIN
                end = np.array([0.38 * np.cos(a), 0.38 * np.sin(a), 0])
                rays.add(Line(start, end, color=color, stroke_width=1.6))
            return VGroup(rays, Dot(ORIGIN, radius=0.035, color=color), Circle(radius=0.17, color=color, stroke_width=1.1)).scale(scale)

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

        face_img = load_face("s8_face", fallback_style="neutral", color=ACCENT_CYAN, height=4.6)
        face_card = make_face_card(face_img).move_to(DOWN * 0.05)

        img_mob = face_card[1]
        def L(u, v):
            tl = img_mob.get_corner(UL)
            br = img_mob.get_corner(DR)
            return np.array([tl[0] + u*(br[0]-tl[0]), tl[1] + v*(br[1]-tl[1]), 0])

        pts = {name: L(u, v) for name, (u, v) in lm_coords.items()}

        edges = [
            ("forehead", "eye_l"), ("forehead", "eye_r"), ("eye_l", "eye_r"),
            ("eye_l", "nose"), ("eye_r", "nose"), ("nose", "mouth_l"),
            ("nose", "mouth_r"), ("mouth_l", "mouth_r"), ("mouth_l", "chin"),
            ("mouth_r", "chin"), ("eye_l", "cheek_l"), ("mouth_l", "cheek_l"),
            ("eye_r", "cheek_r"), ("mouth_r", "cheek_r"),
        ]

        title = label(r"Image Graph", UP * 3.05, color=TEXT_PRIMARY, scale=0.72, bold=True)
        nodes = VGroup(*[Dot(p, radius=0.075, color=ACCENT_LAVENDER) for p in pts.values()])
        jets = VGroup(*[jet_icon(ACCENT_CYAN, scale=0.40).move_to(p) for p in pts.values()])

        # B0: sprinkle jets onto landmarks.
        sprinkle = label(r"sprinkle jets onto landmarks", DOWN * 2.72, color=ACCENT_CYAN, scale=0.48, bold=True)
        beat_to(
            seg_end(T, 0),
            FadeIn(title, shift=DOWN * 0.05),
            FadeIn(face_card),
            LaggedStart(*[FadeIn(j, shift=UP * 0.18) for j in jets], lag_ratio=0.035),
            FadeIn(sprinkle),
        )

        # B1: connect eyes, nose, mouth.
        edge_lines = VGroup(*[Line(pts[a], pts[b], color=ACCENT_BLUE, stroke_width=2.0).set_opacity(0.72) for a, b in edges])
        landmarks = label(r"eyes | nose | mouth", UP * 2.42, color=TEXT_MUTED, scale=0.42)
        beat_to(
            seg_end(T, 1),
            FadeOut(sprinkle),
            FadeIn(landmarks, shift=DOWN * 0.05),
            LaggedStart(*[GrowFromCenter(n) for n in nodes], lag_ratio=0.035),
            LaggedStart(*[Create(e) for e in edge_lines], lag_ratio=0.02),
        )

        # B2: name the graph.
        graph_box = SurroundingRectangle(title, color=ACCENT_LAVENDER, buff=0.18, stroke_width=2.0)
        beat_to(
            seg_end(T, 2),
            title.animate.set_color(ACCENT_LAVENDER).scale(1.08),
            Create(graph_box),
            landmarks.animate.set_opacity(0.35),
        )

        # B3: node = texture barcode / jet.
        node_panel = panel(3.2, 1.8, LEFT * 4.55 + DOWN * 0.8, ACCENT_CYAN)
        node_label = label(r"node = jet", node_panel.get_top() + DOWN * 0.32, color=ACCENT_CYAN, scale=0.48, bold=True)
        bars = VGroup()
        for i, h in enumerate([0.22, 0.48, 0.30, 0.62, 0.38, 0.54, 0.26, 0.58]):
            b = Rectangle(width=0.06, height=h, stroke_width=0, fill_color=ACCENT_CYAN, fill_opacity=0.75)
            b.move_to(LEFT * 5.0 + RIGHT * i * 0.13 + DOWN * 1.05)
            bars.add(b)
        node_ring = Circle(radius=0.24, color=ACCENT_CYAN, stroke_width=3).move_to(pts["eye_l"])
        beat_to(
            seg_end(T, 3),
            Create(node_ring),
            FadeIn(node_panel),
            FadeIn(node_label, shift=UP * 0.05),
            LaggedStart(*[GrowFromEdge(b, DOWN) for b in bars], lag_ratio=0.04),
        )

        # B4: edge = geometric distance.
        edge_panel = panel(3.2, 1.8, RIGHT * 4.55 + DOWN * 0.8, ACCENT_MINT)
        edge_label = label(r"edge = distance", edge_panel.get_top() + DOWN * 0.32, color=ACCENT_MINT, scale=0.48, bold=True)
        delta = MathTex(r"\Delta x", tex_template=EN_TEX_TEMPLATE, color=ACCENT_MINT).scale(1.05).move_to(RIGHT * 4.55 + DOWN * 1.05)
        edge_hi = Line(pts["eye_l"], pts["nose"], color=ACCENT_MINT, stroke_width=5.0)
        beat_to(
            seg_end(T, 4),
            FadeIn(edge_panel),
            FadeIn(edge_label, shift=UP * 0.05),
            FadeIn(delta),
            Create(edge_hi),
            node_ring.animate.set_opacity(0.35).set_stroke(width=1.4),
        )

        # B5: EBGM separates skin surface.
        skin_face_grp = Group(face_card, jets)
        face_center = face_card.get_center()
        bone_pts = {name: (p - face_center) * 0.82 + np.array([2.45, -0.15, 0]) for name, p in pts.items()}

        sep = Line(UP * 2.15, DOWN * 2.35, color=GRID_LINE, stroke_width=1.2)
        skin_title = label(r"skin surface", LEFT * 2.45 + UP * 2.12, color=ACCENT_CYAN, scale=0.52, bold=True)
        beat_to(
            seg_end(T, 5),
            FadeOut(node_panel),
            FadeOut(edge_panel),
            FadeOut(node_label),
            FadeOut(edge_label),
            FadeOut(delta),
            FadeOut(bars),
            FadeOut(node_ring),
            FadeOut(edge_hi),
            FadeOut(graph_box),
            FadeOut(nodes),
            FadeOut(edge_lines),
            skin_face_grp.animate.scale(0.82).move_to(LEFT * 2.45 + DOWN * 0.15),
            FadeIn(sep),
            FadeIn(skin_title, shift=DOWN * 0.05),
        )

        # B6: bone structure.
        bone_edges = VGroup(*[Line(bone_pts[a], bone_pts[b], color=ACCENT_MINT, stroke_width=2.4).set_opacity(0.85) for a, b in edges])
        bone_nodes = VGroup(*[Dot(bone_pts[name], radius=0.065, color=ACCENT_MINT) for name in pts.keys()])
        bone_title = label(r"bone structure", RIGHT * 2.45 + UP * 2.12, color=ACCENT_MINT, scale=0.52, bold=True)
        beat_to(seg_end(T, 6), FadeIn(bone_edges), FadeIn(bone_nodes), FadeIn(bone_title, shift=DOWN * 0.05))

        # B7: independently processed.
        independent = label(r"processed independently", DOWN * 2.72, color=ACCENT_LAVENDER, scale=0.52, bold=True)
        beat_to(
            seg_end(T, 7),
            jets.animate.set_opacity(0.92),
            bone_edges.animate.set_opacity(0.92),
            FadeIn(independent, shift=UP * 0.05),
            title.animate.set_color(ACCENT_LAVENDER),
        )

        tail = max(0.0, T["duration"] - elapsed - 0.18)
        if tail > 0.05:
            self.wait(tail)
