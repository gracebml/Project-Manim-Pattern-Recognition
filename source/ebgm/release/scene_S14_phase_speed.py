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
TMP_IMG_DIR = Path("/tmp/video_manim_s14_imgs")
TMP_IMG_DIR.mkdir(parents=True, exist_ok=True)


class S14_PhaseSpeed(Scene):
    SCENE_KEY = "scene_14"

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

        title = label("Rotation, Phase, Speed", UP * 3.05, color=TEXT_PRIMARY, scale=0.72, bold=True)
        
        # B0-B1: Chart setup (zoom to y=[80, 100, 5])
        axes = Axes(
            x_range=[0, 24, 11],
            y_range=[80, 100, 5],
            x_length=6.6,
            y_length=3.0,
            tips=False,
            axis_config={"color": GRID_LINE, "stroke_width": 1.2},
        ).move_to(LEFT * 0.4 + UP * 0.25)

        gridlines = VGroup(*[
            Line(axes.c2p(0, y_val), axes.c2p(24, y_val), color=GRID_LINE, stroke_width=0.8).set_opacity(0.20)
            for y_val in [80, 85, 90, 95, 100]
        ])
        gridlines_x = VGroup(*[
            Line(axes.c2p(x_val, 80), axes.c2p(x_val, 100), color=GRID_LINE, stroke_width=0.8).set_opacity(0.20)
            for x_val in [0, 11, 22]
        ])

        x0 = axes.c2p(0, 98)
        x11 = axes.c2p(11, 94)
        x22 = axes.c2p(22, 88)

        curve = VMobject(color=ACCENT_MINT, stroke_width=3.0).set_points_smoothly([x0, x11, x22])
        filled_area = Polygon(
            *[axes.c2p(0, 80), x0, x11, x22, axes.c2p(22, 80)],
            color=ACCENT_MINT,
            stroke_width=0,
            fill_color=ACCENT_MINT,
            fill_opacity=0.08
        )

        dots = VGroup(
            Dot(x0, radius=0.07, color=ACCENT_MINT),
            Dot(x11, radius=0.07, color=ACCENT_CYAN),
            Dot(x22, radius=0.07, color=ACCENT_LAVENDER)
        )

        deg0 = label("0°", x0 + UP * 0.45, color=ACCENT_MINT, scale=0.38, bold=True)
        deg11 = label("11°", x11 + UP * 0.45, color=ACCENT_CYAN, scale=0.38, bold=True)
        deg22 = label("22°", x22 + UP * 0.45, color=ACCENT_LAVENDER, scale=0.38, bold=True)

        acc98 = label("98\\%", x0 + LEFT * 0.65 + UP * 0.15, color=ACCENT_MINT, scale=0.42, bold=True)
        acc94 = label("94\\%", x11 + RIGHT * 0.65, color=ACCENT_CYAN, scale=0.42, bold=True)
        acc88 = label("88\\%", x22 + RIGHT * 0.65, color=ACCENT_LAVENDER, scale=0.42, bold=True)

        y_lbl = label("accuracy", axes.get_left() + LEFT * 0.55 + UP * 0.35, color=TEXT_MUTED, scale=0.38)
        x_lbl = label("rotation angle", axes.get_bottom() + DOWN * 0.38, color=TEXT_MUTED, scale=0.38)

        # Small pose thumbnails from real face rotated
        def pose_thumbnail(angle_deg, pos):
            face_img = load_face("s8_face", height=0.72)
            if angle_deg != 0:
                face_img.rotate(angle_deg * DEGREES)
            card = make_face_card(face_img, color=ACCENT_BLUE)
            card.scale(0.85).move_to(pos)
            return card

        poses = Group(
            pose_thumbnail(0, axes.c2p(0, 80) + DOWN * 1.1),
            pose_thumbnail(11, axes.c2p(11, 80) + DOWN * 1.1),
            pose_thumbnail(22, axes.c2p(22, 80) + DOWN * 1.1)
        )

        beat_to(seg_end(T, 1), FadeIn(title), Create(axes), FadeIn(gridlines), FadeIn(gridlines_x), FadeIn(filled_area), FadeIn(y_lbl), FadeIn(x_lbl), Create(curve), FadeIn(dots), FadeIn(deg0), FadeIn(deg11), FadeIn(deg22), FadeIn(acc98), FadeIn(acc94), FadeIn(acc88), LaggedStart(*[FadeIn(p) for p in poses], lag_ratio=0.08))

        # B2: is phase necessary?  (placed above the chart so it never overlaps
        # the pose thumbnails below the axis nor the bottom subtitle track)
        question = label("Is phase necessary?", UP * 2.35, color=TEXT_PRIMARY, scale=0.62, bold=True)
        beat_to(seg_end(T, 2), FadeIn(question, shift=DOWN * 0.08), curve.animate.set_stroke(width=5.0))

        # B3-B6: split comparison drift tests
        chart_group = Group(title, axes, gridlines, gridlines_x, filled_area, y_lbl, x_lbl, curve, dots, deg0, deg11, deg22, acc98, acc94, acc88, poses, question)
        
        split = Line(UP * 2.2, DOWN * 2.2, color=GRID_LINE, stroke_width=1.0).set_opacity(0.45)
        left_title = label("No phase", LEFT * 3.35 + UP * 2.35, color=ACCENT_CORAL, scale=0.58, bold=True)
        right_title = label("With phase", RIGHT * 3.35 + UP * 2.35, color=ACCENT_MINT, scale=0.58, bold=True)
        
        left_face_card = make_face_card(load_face("s8_face", height=2.2)).move_to(LEFT * 3.35 + UP * 0.35)
        left_face = left_face_card[1]
        
        right_face_card = make_face_card(load_face("s8_face", height=2.2)).move_to(RIGHT * 3.35 + UP * 0.35)
        right_face = right_face_card[1]

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

        def L_left(u, v):
            tl = left_face.get_corner(UL)
            br = left_face.get_corner(DR)
            return np.array([tl[0] + u * (br[0] - tl[0]), tl[1] + v * (br[1] - tl[1]), 0])

        def L_right(u, v):
            tl = right_face.get_corner(UL)
            br = right_face.get_corner(DR)
            return np.array([tl[0] + u * (br[0] - tl[0]), tl[1] + v * (br[1] - tl[1]), 0])

        pts_true_left = {name: L_left(u, v) for name, (u, v) in lm_coords.items()}
        pts_true_right = {name: L_right(u, v) for name, (u, v) in lm_coords.items()}

        drift_offsets_left = {
            "forehead": RIGHT * 0.35 + UP * 0.20,
            "eye_l": LEFT * 0.25 + DOWN * 0.15,
            "eye_r": RIGHT * 0.40 + UP * 0.20,
            "nose": LEFT * 0.22 + UP * 0.30,
            "mouth_l": LEFT * 0.20 + DOWN * 0.25,
            "mouth_r": RIGHT * 0.30 + DOWN * 0.15,
            "chin": DOWN * 0.35 + LEFT * 0.20,
            "cheek_l": LEFT * 0.40 + UP * 0.10,
            "cheek_r": RIGHT * 0.35 + DOWN * 0.20,
        }

        left_refs = VGroup(*[Dot(pts_true_left[name], radius=0.042, color=ACCENT_LAVENDER) for name in lm_coords])
        left_drifts = VGroup(*[Dot(pts_true_left[name] + drift_offsets_left[name], radius=0.042, color=ACCENT_CYAN) for name in lm_coords])
        left_lines = VGroup(*[Line(pts_true_left[name], pts_true_left[name] + drift_offsets_left[name], color=ACCENT_CORAL, stroke_width=1.5) for name in lm_coords])

        right_refs = VGroup(*[Dot(pts_true_right[name], radius=0.042, color=ACCENT_LAVENDER) for name in lm_coords])
        
        drift_offsets_right = {name: val * 0.15 for name, val in drift_offsets_left.items()}
        right_drifts = VGroup(*[Dot(pts_true_right[name] + drift_offsets_right[name], radius=0.042, color=ACCENT_CYAN) for name in lm_coords])
        right_lines = VGroup(*[Line(pts_true_right[name], pts_true_right[name] + drift_offsets_right[name], color=ACCENT_MINT, stroke_width=1.2) for name in lm_coords])

        err52 = label("5.2 px", LEFT * 3.35 + DOWN * 1.45, color=ACCENT_CORAL, scale=0.72, bold=True)
        rec67 = label("recognition 67\\%", LEFT * 3.35 + DOWN * 2.05, color=ACCENT_CORAL, scale=0.45, bold=True)

        self.play(
            FadeOut(chart_group),
            Create(split),
            FadeIn(left_title),
            FadeIn(right_title),
            FadeIn(left_face_card),
            FadeIn(right_face_card),
            FadeIn(left_refs),
            LaggedStart(*[Create(l) for l in left_lines], lag_ratio=0.05),
            FadeIn(left_drifts),
            FadeIn(err52),
            FadeIn(rec67),
            run_time=0.6
        )
        elapsed = seg_end(T, 2) + 0.6
        beat_to(seg_end(T, 3))
        beat_to(seg_end(T, 4))

        err16 = label("1.6 px", RIGHT * 3.35 + DOWN * 1.45, color=ACCENT_MINT, scale=0.72, bold=True)
        rec88 = label("recognition 88\\%", RIGHT * 3.35 + DOWN * 2.05, color=ACCENT_MINT, scale=0.45, bold=True)
        anchor = label("phase = anchor", ORIGIN + DOWN * 2.8, color=ACCENT_MINT, scale=0.58, bold=True)

        self.play(
            FadeIn(right_refs),
            LaggedStart(*[Create(l) for l in right_lines], lag_ratio=0.05),
            FadeIn(right_drifts),
            FadeIn(err16),
            FadeIn(rec88),
            FadeIn(anchor),
            right_title.animate.set_color(ACCENT_MINT),
            run_time=0.6
        )
        elapsed = seg_end(T, 4) + 0.6
        beat_to(seg_end(T, 5))
        beat_to(seg_end(T, 6))

        # B7-B8: Pipeline speed comparison
        old = Group(split, left_title, right_title, left_face_card, right_face_card, left_refs, left_drifts, left_lines, right_refs, right_drifts, right_lines, err52, rec67, err16, rec88, anchor)
        
        pipeline_title = label("Separate Work", UP * 2.8, color=TEXT_PRIMARY, scale=0.68, bold=True)
        
        pipeline_face = load_face("s8_face", height=1.2)
        pipeline_img = make_face_card(pipeline_face).move_to(LEFT * 5.3 + UP * 0.3)
        img_lbl = label("image", LEFT * 5.3 + DOWN * 0.8, color=TEXT_MUTED, scale=0.38, bold=True)
        
        extract = RoundedRectangle(width=2.9, height=1.5, corner_radius=0.10, color=ACCENT_CYAN, stroke_width=1.7, fill_color=ACCENT_CYAN, fill_opacity=0.08).move_to(LEFT * 2.0 + UP * 0.3)
        extract_lbl = label("Extraction", LEFT * 2.0 + UP * 0.65, color=ACCENT_CYAN, scale=0.42, bold=True)
        extract_sub = label("build the graph", LEFT * 2.0 + UP * 0.25, color=TEXT_MUTED, scale=0.32)
        extract_badge = label("once (x1)", LEFT * 2.0 + DOWN * 0.15, color=ACCENT_CYAN, scale=0.32, bold=True)
        
        match = RoundedRectangle(width=2.9, height=1.5, corner_radius=0.10, color=ACCENT_LAVENDER, stroke_width=1.7, fill_color=ACCENT_LAVENDER, fill_opacity=0.08).move_to(RIGHT * 1.5 + UP * 0.3)
        match_lbl = label("Matching", RIGHT * 1.5 + UP * 0.65, color=ACCENT_LAVENDER, scale=0.42, bold=True)
        match_sub = label("compare scores", RIGHT * 1.5 + UP * 0.25, color=TEXT_MUTED, scale=0.32)
        match_badge = label("many (xN)", RIGHT * 1.5 + DOWN * 0.15, color=ACCENT_LAVENDER, scale=0.32, bold=True)

        db = Group()
        gallery_assets = ["s9_face_other", "s2_personA", "s8_face", "s2_personB", "s2_same_neutral", "face"]
        for i in range(6):
            face_thumb = load_face(gallery_assets[i], height=0.42)
            card_thumb = make_face_card(face_thumb, color=ACCENT_LAVENDER).scale(0.85)
            r_thumb = i // 3
            c_thumb = i % 3
            pos_thumb = RIGHT * 4.5 + np.array([c_thumb * 0.52, 0.55 - r_thumb * 0.55, 0])
            card_thumb.move_to(pos_thumb)
            db.add(card_thumb)
            
        db_lbl = label("database", RIGHT * 5.02 + DOWN * 0.8, color=TEXT_MUTED, scale=0.38, bold=True)
        
        arrows = VGroup(
            thin_arrow(pipeline_img.get_right(), extract.get_left(), color=ACCENT_CYAN, stroke_width=2, buff=0.12),
            thin_arrow(extract.get_right(), match.get_left(), color=ACCENT_LAVENDER, stroke_width=2, buff=0.12),
            thin_arrow(match.get_right(), db.get_left() + LEFT * 0.05, color=ACCENT_LAVENDER, stroke_width=2, buff=0.12),
        )
        
        speed = label("~1000x faster", DOWN * 1.6, color=ACCENT_MINT, scale=0.75, bold=True)
        fast_enough = label("fast enough for large databases", DOWN * 2.15, color=TEXT_MUTED, scale=0.38)

        self.play(
            FadeOut(old),
            FadeIn(pipeline_title),
            FadeIn(pipeline_img),
            FadeIn(img_lbl),
            Create(arrows[0]),
            FadeIn(extract),
            FadeIn(extract_lbl),
            FadeIn(extract_sub),
            FadeIn(extract_badge),
            Create(arrows[1]),
            FadeIn(match),
            FadeIn(match_lbl),
            FadeIn(match_sub),
            FadeIn(match_badge),
            Create(arrows[2]),
            LaggedStart(*[FadeIn(d) for d in db], lag_ratio=0.02),
            FadeIn(db_lbl),
            FadeIn(speed, shift=UP * 0.08),
            FadeIn(fast_enough),
            run_time=0.6
        )
        elapsed = seg_end(T, 6) + 0.6
        beat_to(seg_end(T, 7))
        beat_to(seg_end(T, 8))

        tail = max(0.0, T["duration"] - elapsed - 0.18)
        if tail > 0.05:
            self.wait(tail)
