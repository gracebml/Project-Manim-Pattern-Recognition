import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from manim import *
import numpy as np
from PIL import Image, ImageOps

from _common import *


ASSET_DIR = Path(__file__).resolve().parents[2] / "assets"
TMP_IMG_DIR = Path("/tmp/video_manim_s03_imgs")
TMP_IMG_DIR.mkdir(parents=True, exist_ok=True)


class S03_PreDL(MovingCameraScene):
    SCENE_KEY = "scene_03"

    def construct(self):
        T = load_scene_timing(self.SCENE_KEY)
        self.add_sound(T["audio_path"])
        add_subtitles(self, T)
        self.camera.background_color = BG_NAVY

        elapsed = 0.0
        # Beats run on real transcript time (load_scene_timing): targets are absolute
        # seconds into the 57.214s audio track, so every reveal lands on the spoken word.

        def beat_to(t_target, *anims, **kw):
            nonlocal elapsed
            if t_target <= elapsed:
                rt = 0.2
                next_elapsed = elapsed + rt
            else:
                rt = max(0.2, t_target - elapsed)
                next_elapsed = t_target
            if anims:
                self.play(*anims, run_time=rt, **kw)
            else:
                self.wait(rt)
            elapsed = next_elapsed

        def ws(substr, fallback):
            t = word_start(T, substr)
            return t if t is not None else fallback

        def ss(k):
            segs = T["segments"]
            return segs[k]["start"] if k < len(segs) else T["duration"]

        def label(text, pos, color=TEXT_PRIMARY, scale=0.42, bold=False):
            return en_label(text, color=color, scale=scale, bold=bold).move_to(pos)

        def stylized_face(style="neutral", color=ACCENT_CYAN):
            hair = Ellipse(width=2.0, height=2.52, color=color, stroke_width=2, fill_opacity=0.06)
            face = Ellipse(width=1.66, height=2.12, color=color, stroke_width=2.2, fill_opacity=0.03)
            left_eye = Dot(LEFT * 0.26 + UP * 0.17, radius=0.04, color=color)
            right_eye = Dot(RIGHT * 0.26 + UP * 0.17, radius=0.04, color=color)
            nose = Line(UP * 0.12, DOWN * 0.12, color=color, stroke_width=2)
            if style == "smile":
                mouth = Arc(radius=0.24, start_angle=200 * DEGREES, angle=140 * DEGREES, color=color, stroke_width=2.8).shift(DOWN * 0.38)
            elif style == "frown":
                mouth = Arc(radius=0.24, start_angle=20 * DEGREES, angle=140 * DEGREES, color=color, stroke_width=2.8).shift(DOWN * 0.6)
            elif style == "lowlight":
                mouth = Arc(radius=0.2, start_angle=210 * DEGREES, angle=120 * DEGREES, color=color, stroke_width=2.5).shift(DOWN * 0.34)
                hair.set_fill(color, opacity=0.12)
                face.set_fill(color, opacity=0.02)
            elif style == "pose":
                hair = Ellipse(width=2.16, height=2.42, color=color, stroke_width=2, fill_opacity=0.06).shift(RIGHT * 0.08)
                face = Ellipse(width=1.62, height=2.04, color=color, stroke_width=2.2, fill_opacity=0.03).shift(RIGHT * 0.06)
                left_eye = Dot(LEFT * 0.21 + UP * 0.17, radius=0.04, color=color)
                right_eye = Dot(RIGHT * 0.17 + UP * 0.2, radius=0.04, color=color)
                mouth = Arc(radius=0.2, start_angle=205 * DEGREES, angle=125 * DEGREES, color=color, stroke_width=2.6).shift(DOWN * 0.34 + RIGHT * 0.02)
            else:
                mouth = Arc(radius=0.22, start_angle=205 * DEGREES, angle=130 * DEGREES, color=color, stroke_width=2.6).shift(DOWN * 0.46)
            neck = Rectangle(width=0.42, height=0.34, color=color, stroke_width=1.2, fill_opacity=0.04).shift(DOWN * 1.0)
            shoulders = Arc(radius=0.95, start_angle=200 * DEGREES, angle=140 * DEGREES, color=color, stroke_width=2).shift(DOWN * 1.2)
            return VGroup(hair, face, left_eye, right_eye, nose, mouth, neck, shoulders)

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

        def load_face(name, fallback_style="neutral", color=ACCENT_CYAN, height=2.55):
            for ext in (".png", ".jpg", ".jpeg"):
                p = ASSET_DIR / f"{name}{ext}"
                if p.exists():
                    img = ImageMobject(str(square_cache(p) if p.name.startswith("s2_") or p.name == "face.png" else p))
                    img.scale_to_fit_height(height)
                    return img
            mob = stylized_face(style=fallback_style, color=color)
            mob.scale_to_fit_height(height)
            return mob

        def load_asset_image(name, height=2.0):
            for ext in (".png", ".jpg", ".jpeg"):
                p = ASSET_DIR / f"{name}{ext}"
                if p.exists():
                    img = ImageMobject(str(p))
                    img.scale_to_fit_height(height)
                    return img
            return load_face("face", height=height)

        def load_paper(height=3.65):
            p = ASSET_DIR / "ebgm_paper_p1.png"
            img = ImageMobject(str(p))
            img.scale_to_fit_height(height)
            return img

        def image_card(mob, color=ACCENT_BLUE, pad=0.14, fill=BG_NAVY_SOFT, opacity=0.72):
            frame = RoundedRectangle(
                width=mob.width + pad,
                height=mob.height + pad,
                corner_radius=0.12,
                color=color,
                stroke_width=1.8,
                fill_color=fill,
                fill_opacity=opacity,
            ).move_to(mob)
            border = RoundedRectangle(
                width=mob.width + pad,
                height=mob.height + pad,
                corner_radius=0.12,
                color=color,
                stroke_width=1.8,
                fill_opacity=0.0,
            ).move_to(mob)
            return Group(frame, mob, border)

        def iso_box(w=1.0, h=1.4, d=0.5, color=ACCENT_CYAN, fill=0.18):
            offset = np.array([0.65 * d, 0.36 * d, 0])
            front = Rectangle(
                width=w,
                height=h,
                stroke_color=color,
                stroke_width=2,
                fill_color=color,
                fill_opacity=fill,
            )
            top = Polygon(
                front.get_corner(UL),
                front.get_corner(UL) + offset,
                front.get_corner(UR) + offset,
                front.get_corner(UR),
                stroke_color=color,
                stroke_width=2,
                fill_color=color,
                fill_opacity=min(0.55, fill * 1.8),
            )
            side = Polygon(
                front.get_corner(UR),
                front.get_corner(UR) + offset,
                front.get_corner(DR) + offset,
                front.get_corner(DR),
                stroke_color=color,
                stroke_width=2,
                fill_color=color,
                fill_opacity=max(0.05, fill * 0.6),
            )
            return Group(side, top, front)

        def conv_stack(center, color=ACCENT_CYAN, width=1.1, height=1.45, depth=0.42, n=4, label_text=None, label_color=None):
            g = Group()
            for i in range(n):
                box = iso_box(width - i * 0.08, height - i * 0.08, depth, color=color, fill=max(0.05, 0.18 - i * 0.025))
                box.shift(RIGHT * i * 0.14 + UP * i * 0.045)
                g.add(box)
            g.move_to(center)
            if label_text:
                lab = label(label_text, center + DOWN * (height * 0.72), color=label_color or color, scale=0.25, bold=True)
                return Group(g, lab)
            return g

        def gpu_3d(color=ACCENT_TEAL):
            body = iso_box(2.55, 1.0, 0.52, color=color, fill=0.11)
            for part in body:
                part.set_stroke(width=1.45)
            fan1 = Group(
                Circle(radius=0.23, color=color, stroke_width=1.5),
                *[
                    Line(
                        ORIGIN,
                        0.22 * np.array([np.cos(a), np.sin(a), 0]),
                        color=color,
                        stroke_width=1.0,
                    )
                    for a in np.linspace(0, TAU, 7, endpoint=False)
                ],
            ).move_to(body.get_center() + LEFT * 0.6)
            fan2 = fan1.copy().move_to(body.get_center() + RIGHT * 0.6)
            pcie = RoundedRectangle(
                width=1.1,
                height=0.14,
                corner_radius=0.03,
                color=color,
                stroke_width=0.9,
                fill_color=color,
                fill_opacity=0.32,
            ).next_to(body, DOWN, buff=0.02)
            fins = Group(*[
                Line(LEFT * 0.78 + UP * (0.24 - i * 0.1), RIGHT * 0.78 + UP * (0.24 - i * 0.1), color=color, stroke_width=0.9).move_to(body.get_center() + DOWN * 0.02)
                for i in range(3)
            ])
            bus = VGroup(*[
                Rectangle(width=0.08, height=0.16, color=color, stroke_width=0.8, fill_color=color, fill_opacity=0.28)
                for _ in range(8)
            ]).arrange(RIGHT, buff=0.03).next_to(pcie, DOWN, buff=0.01)
            return Group(body, fan1, fan2, pcie, bus, fins)

        def dataset_stack(color=ACCENT_CORAL):
            tray = RoundedRectangle(width=2.75, height=1.7, corner_radius=0.1, color=color, stroke_width=1.35, fill_color=color, fill_opacity=0.05)
            drawers = Group()
            for i in range(3):
                drawer = RoundedRectangle(
                    width=2.25,
                    height=0.32,
                    corner_radius=0.045,
                    color=ACCENT_BLUE,
                    stroke_width=1.0,
                    fill_color=BG_NAVY_SOFT,
                    fill_opacity=0.55,
                ).move_to(tray.get_center() + UP * (0.42 - i * 0.42))
                handle = Line(drawer.get_left() + RIGHT * 0.28, drawer.get_left() + RIGHT * 0.62, color=color, stroke_width=1.1)
                drawers.add(Group(drawer, handle))
            few_faces = Group(*[
                image_card(load_face(name, fallback_style="neutral", color=ACCENT_CYAN, height=0.5), color=ACCENT_BLUE, pad=0.04, opacity=0.12).scale(0.42)
                for name in ("s2_personA", "s2_same_smile", "s2_personB")
            ]).arrange(RIGHT, buff=0.12).next_to(tray, UP, buff=0.12)
            counter = label("only small archives", tray.get_bottom() + DOWN * 0.25, color=color, scale=0.23, bold=True)
            return Group(tray, drawers, few_faces, counter)

        def pixel_grid(mob, rows=8, cols=8, opacity=0.16):
            grid = Group()
            w = mob.width
            h = mob.height
            dx = w / cols
            dy = h / rows
            side = min(dx, dy) * 0.92
            origin = mob.get_center() + LEFT * (w / 2) + DOWN * (h / 2)
            for r in range(rows):
                for c in range(cols):
                    sq = Square(side_length=side, stroke_width=0.5, stroke_color=GRID_LINE)
                    sq.set_fill(ACCENT_BLUE, opacity=opacity)
                    sq.move_to(origin + RIGHT * (dx * (c + 0.5)) + UP * (dy * (r + 0.5)))
                    grid.add(sq)
            return grid

        def face_with_mesh(mob, color=ACCENT_BLUE):
            points = VGroup()
            edge_pairs = []
            coords = [
                LEFT * 0.38 + UP * 0.28,
                ORIGIN + UP * 0.34,
                RIGHT * 0.38 + UP * 0.28,
                LEFT * 0.34 + ORIGIN,
                ORIGIN,
                RIGHT * 0.34 + ORIGIN,
                LEFT * 0.26 + DOWN * 0.3,
                ORIGIN + DOWN * 0.32,
                RIGHT * 0.26 + DOWN * 0.3,
            ]
            for p in coords:
                points.add(Dot(mob.get_center() + p, radius=0.034, color=color))
            for a, b in [(0, 1), (1, 2), (3, 4), (4, 5), (6, 7), (7, 8), (0, 3), (3, 6), (2, 5), (5, 8), (1, 4), (4, 7)]:
                edge_pairs.append(Line(points[a].get_center(), points[b].get_center(), color=color, stroke_width=1.3).set_opacity(0.55))
            mesh = Group(*edge_pairs, points)
            return mesh

        def brain_icon(color=ACCENT_LAVENDER):
            lobe1 = Ellipse(width=1.45, height=1.1, color=color, stroke_width=2, fill_color=color, fill_opacity=0.05).shift(LEFT * 0.45 + UP * 0.08)
            lobe2 = Ellipse(width=1.42, height=1.08, color=color, stroke_width=2, fill_color=color, fill_opacity=0.05).shift(RIGHT * 0.42 + UP * 0.04)
            stem = Rectangle(width=0.3, height=0.42, color=color, stroke_width=2, fill_color=color, fill_opacity=0.06).shift(DOWN * 0.7)
            squiggle = ParametricFunction(
                lambda t: np.array([0.62 * np.cos(t) * 0.65, 0.22 * np.sin(3 * t), 0]),
                t_range=[0, TAU],
                color=ACCENT_CYAN,
                stroke_width=1.5,
            ).scale(0.65).move_to(lobe1.get_center())
            cortex = Circle(radius=0.18, color=ACCENT_CYAN, stroke_width=2, fill_color=ACCENT_CYAN, fill_opacity=0.12).move_to(LEFT * 0.88 + UP * 0.2)
            return Group(lobe1, lobe2, stem, squiggle, cortex)

        def ranking_bars():
            bg = RoundedRectangle(width=4.2, height=2.45, corner_radius=0.1, color=ACCENT_BLUE, stroke_width=1.1, fill_color=BG_NAVY_SOFT, fill_opacity=0.42)
            axis = VGroup(
                Line(LEFT * 1.85 + DOWN * 1.0, RIGHT * 1.9 + DOWN * 1.0, color=GRID_LINE, stroke_width=1.0),
                Line(LEFT * 1.85 + DOWN * 1.0, LEFT * 1.85 + UP * 1.0, color=GRID_LINE, stroke_width=1.0),
            )
            bars = Group()
            specs = [
                ("EBGM", 1.55, ACCENT_MINT),
                ("A", 0.95, ACCENT_BLUE),
                ("B", 0.74, ACCENT_CYAN),
                ("C", 0.56, ACCENT_LAVENDER),
            ]
            for i, (name, h, c) in enumerate(specs):
                x = -1.25 + i * 0.82
                bar = RoundedRectangle(width=0.46, height=h, corner_radius=0.045, color=c, stroke_width=0.9, fill_color=c, fill_opacity=0.72).move_to(np.array([x, -1.0 + h / 2, 0]))
                bars.add(bar)
                bars.add(label(name, bar.get_bottom() + DOWN * 0.2, color=c, scale=0.18, bold=True))
            return Group(bg, axis, bars)

        # Intro — seg0 (0.00-4.22) "what's our first instinct?"
        title = label("Modern instinct?", UP * 2.85, color=TEXT_PRIMARY, scale=0.64, bold=True)
        input_face = image_card(load_face("face", fallback_style="neutral", color=ACCENT_CYAN, height=1.7), color=ACCENT_BLUE, pad=0.12).move_to(LEFT * 4.85 + DOWN * 0.1)
        intro_sub = label("face recognition before deep learning", UP * 2.2, color=TEXT_MUTED, scale=0.3)
        beat_to(1.5, FadeIn(title, scale=0.85), FadeIn(input_face, shift=LEFT * 0.08), FadeIn(intro_sub, shift=DOWN * 0.06))
        beat_to(seg_end(T, 0), intro_sub.animate.set_opacity(0.85))

        # B1: build CNN — seg1 (4.96-12.26) "Build a CNN, gather millions, loss, backpropagation"
        ROW_Y = 0.45
        title2 = label("Build a CNN", UP * 2.86, color=ACCENT_CYAN, scale=0.58, bold=True)
        board = RoundedRectangle(width=12.35, height=4.55, corner_radius=0.14, color=ACCENT_BLUE, stroke_width=1.25, fill_color=BG_NAVY_SOFT, fill_opacity=0.42).shift(DOWN * 0.28)
        dataset_input = image_card(load_asset_image("face_recognition_dataset", height=1.78), color=ACCENT_TEAL, pad=0.1, opacity=0.54).move_to(np.array([-5.05, ROW_Y, 0]))
        dataset_tag = label("image dataset", dataset_input.get_top() + UP * 0.22, color=ACCENT_TEAL, scale=0.24, bold=True)
        conv1 = conv_stack(np.array([-2.85, ROW_Y, 0]), color=ACCENT_TEAL, width=0.92, height=1.42, depth=0.36, n=3, label_text="conv1", label_color=ACCENT_TEAL)
        conv2 = conv_stack(np.array([-1.08, ROW_Y, 0]), color=ACCENT_CYAN, width=0.84, height=1.22, depth=0.36, n=3, label_text="conv2", label_color=ACCENT_CYAN)
        conv3 = conv_stack(np.array([0.6, ROW_Y, 0]), color=ACCENT_LAVENDER, width=0.76, height=1.02, depth=0.36, n=3, label_text="conv3", label_color=ACCENT_LAVENDER)
        classifier = Group(
            RoundedRectangle(width=0.92, height=1.45, corner_radius=0.08, color=ACCENT_LAVENDER, stroke_width=1.5, fill_color=ACCENT_LAVENDER, fill_opacity=0.1),
            VGroup(*[Dot([-0.16, 0.5 - i * 0.28, 0], radius=0.05, color=ACCENT_LAVENDER) for i in range(4)]),
            VGroup(*[Dot([0.18, 0.36 - i * 0.24, 0], radius=0.05, color=ACCENT_LAVENDER) for i in range(3)]),
            label("face ID", ORIGIN + DOWN * 1.0, color=ACCENT_LAVENDER, scale=0.24, bold=True),
        ).move_to(np.array([2.15, ROW_Y, 0]))

        def harrow(a, b, color):
            return thin_arrow(
                np.array([a.get_right()[0] + 0.04, ROW_Y, 0]),
                np.array([b.get_left()[0] - 0.04, ROW_Y, 0]),
                color=color, stroke_width=2.2, buff=0.06, max_tip_length_to_length_ratio=0.16,
            )

        forward_arrows = Group(
            harrow(dataset_input, conv1[0], ACCENT_TEAL),
            harrow(conv1[0], conv2[0], ACCENT_CYAN),
            harrow(conv2[0], conv3[0], ACCENT_LAVENDER),
            harrow(conv3[0], classifier, ACCENT_LAVENDER),
        )
        out_chip = Group(
            RoundedRectangle(width=1.6, height=0.6, corner_radius=0.1, color=ACCENT_MINT, stroke_width=1.8, fill_color=ACCENT_MINT, fill_opacity=0.1),
            label("prediction", ORIGIN, color=ACCENT_MINT, scale=0.26, bold=True),
        ).move_to(np.array([4.4, ROW_Y + 0.35, 0]))
        loss_chip = Group(
            RoundedRectangle(width=1.4, height=0.56, corner_radius=0.1, color=ACCENT_CORAL, stroke_width=1.6, fill_color=ACCENT_CORAL, fill_opacity=0.09),
            label(r"Loss $\downarrow$", ORIGIN, color=ACCENT_CORAL, scale=0.24, bold=True),
        ).move_to(np.array([4.4, ROW_Y - 0.5, 0]))
        out_arrow = harrow(classifier, out_chip, ACCENT_MINT)
        back_arrow = thin_arrow(
            np.array([4.4, -1.55, 0]),
            np.array([-5.05, -1.55, 0]),
            color=ACCENT_CORAL,
            stroke_width=2.2,
            buff=0.08,
            max_tip_length_to_length_ratio=0.055,
        )
        back_label = label("backpropagation", DOWN * 1.95, color=ACCENT_CORAL, scale=0.26, bold=True)
        million_badge = Group(
            RoundedRectangle(width=2.0, height=0.42, corner_radius=0.08, color=ACCENT_TEAL, stroke_width=1.1, fill_color=ACCENT_TEAL, fill_opacity=0.08),
            label("millions of images", ORIGIN, color=ACCENT_TEAL, scale=0.22, bold=True),
        ).move_to(np.array([-4.92, -0.82, 0]))
        beat_to(
            ss(1),
            FadeOut(title),
            FadeOut(intro_sub),
            FadeOut(input_face),
            FadeIn(title2, scale=0.85),
            FadeIn(board),
            FadeIn(dataset_input, shift=LEFT * 0.06),
            FadeIn(dataset_tag, shift=UP * 0.04),
            FadeIn(conv1, shift=UP * 0.06),
            FadeIn(forward_arrows[0]),
        )
        beat_to(ws("CNN", 5.88), FadeIn(conv2, shift=UP * 0.06), FadeIn(forward_arrows[1]))
        beat_to(ws("millions", 7.18), FadeIn(million_badge, scale=0.86), dataset_input.animate.scale(1.03))
        beat_to(ws("loss", 9.08), FadeIn(conv3, shift=UP * 0.06), FadeIn(forward_arrows[2]), FadeIn(classifier), FadeIn(forward_arrows[3]), FadeIn(out_arrow), FadeIn(out_chip, shift=UP * 0.05), FadeIn(loss_chip, shift=UP * 0.05))
        beat_to(ws("backprop", 10.72), Create(back_arrow), FadeIn(back_label, shift=UP * 0.05))
        beat_to(seg_end(T, 1))

        # B2 rewind
        rewind_title = label("Rewind", ORIGIN, color=ACCENT_LAVENDER, scale=0.58, bold=True).to_edge(UP, buff=0.48)
        rewind_panel = RoundedRectangle(
            width=7.4,
            height=2.25,
            corner_radius=0.18,
            color=ACCENT_LAVENDER,
            stroke_width=1.25,
            fill_color=BG_NAVY_SOFT,
            fill_opacity=0.34,
        ).next_to(rewind_title, DOWN, buff=0.42)

        clock_face = Circle(radius=0.62, color=ACCENT_LAVENDER, stroke_width=2.1, fill_color=ACCENT_LAVENDER, fill_opacity=0.035)
        clock_ticks = VGroup()
        for k in range(12):
            a = TAU * k / 12
            tick = Line(
                0.48 * np.array([np.cos(a), np.sin(a), 0]),
                0.58 * np.array([np.cos(a), np.sin(a), 0]),
                color=ACCENT_BLUE,
                stroke_width=0.95,
            )
            clock_ticks.add(tick)
        clock_hand = Line(ORIGIN, UP * 0.38, color=ACCENT_CYAN, stroke_width=2.7)
        clock_dot = Dot(ORIGIN, radius=0.035, color=ACCENT_CYAN)
        clock = VGroup(clock_face, clock_ticks, clock_hand, clock_dot)

        y97_box = RoundedRectangle(
            width=2.1,
            height=0.92,
            corner_radius=0.16,
            color=ACCENT_LAVENDER,
            stroke_width=1.35,
            fill_color=ACCENT_LAVENDER,
            fill_opacity=0.08,
        )
        y97 = label("1997", ORIGIN, color=ACCENT_LAVENDER, scale=0.92, bold=True)
        y97_card = VGroup(y97_box, y97)

        rewind_row = VGroup(clock, y97_card).arrange(RIGHT, buff=2.15).move_to(rewind_panel)
        rewind_arc = ArcBetweenPoints(
            y97_card.get_left() + LEFT * 0.24,
            clock.get_right() + RIGHT * 0.24,
            angle=-TAU / 3.6,
            color=ACCENT_LAVENDER,
            stroke_width=2.0,
        ).set_fill(opacity=0).set_stroke(color=ACCENT_LAVENDER, width=2.0, opacity=0.9)
        rewind_tip = Triangle(color=ACCENT_LAVENDER, fill_color=ACCENT_LAVENDER, fill_opacity=1.0, stroke_width=0).scale(0.075)
        rewind_tip.rotate(135 * DEGREES).move_to(clock.get_right() + RIGHT * 0.24 + UP * 0.02)
        rewind_arrow = VGroup(rewind_arc, rewind_tip)
        rewind_caption = label("before deep learning infrastructure", ORIGIN, color=TEXT_MUTED, scale=0.25).next_to(rewind_row, DOWN, buff=0.18)
        beat_to(
            13.1,
            FadeOut(Group(title2, board, dataset_input, dataset_tag, million_badge, conv1, conv2, conv3, classifier, out_chip, loss_chip, forward_arrows, out_arrow, back_arrow, back_label), shift=DOWN * 0.05),
            FadeIn(rewind_title, scale=0.85),
            FadeIn(rewind_panel),
            FadeIn(clock, shift=UP * 0.04),
            Create(rewind_arrow),
            FadeIn(y97_card, shift=UP * 0.04),
            FadeIn(rewind_caption, shift=UP * 0.03),
        )
        beat_to(ws("1997", 13.74), Rotate(clock_hand, angle=-TAU * 0.95, about_point=clock.get_center()), y97_card.animate.scale(1.08))
        beat_to(seg_end(T, 2), rewind_arrow.animate.set_opacity(0.28), clock_hand.animate.rotate(-TAU * 0.35, about_point=clock.get_center()))

        # B3/B4 GPU and dataset shortages
        gpu_title = label("No powerful GPUs", UP * 2.55, color=ACCENT_CORAL, scale=0.58, bold=True)
        gpu_panel = RoundedRectangle(width=4.1, height=2.45, corner_radius=0.12, color=ACCENT_BLUE, stroke_width=1.1, fill_color=BG_NAVY_SOFT, fill_opacity=0.36).move_to(ORIGIN + DOWN * 0.12)
        gpu = gpu_3d(color=ACCENT_TEAL).scale(1.05).move_to(LEFT * 0.15 + DOWN * 0.05)
        x_gpu = VGroup(
            Line(LEFT * 0.62 + UP * 0.74, RIGHT * 0.62 + DOWN * 0.74, color=ACCENT_CORAL, stroke_width=3.2),
            Line(LEFT * 0.62 + DOWN * 0.74, RIGHT * 0.62 + UP * 0.74, color=ACCENT_CORAL, stroke_width=3.2),
        ).move_to(gpu)
        cpu_chip = Group(
            RoundedRectangle(width=1.22, height=0.44, corner_radius=0.06, color=ACCENT_LAVENDER, stroke_width=1.0, fill_color=ACCENT_LAVENDER, fill_opacity=0.08),
            label("CPU era", ORIGIN, color=ACCENT_LAVENDER, scale=0.22, bold=True),
        ).next_to(gpu_panel, DOWN, buff=0.12)
        dataset_title = label("No massive datasets", UP * 2.55, color=ACCENT_CORAL, scale=0.58, bold=True)
        dataset_panel = RoundedRectangle(width=4.35, height=2.55, corner_radius=0.12, color=ACCENT_BLUE, stroke_width=1.1, fill_color=BG_NAVY_SOFT, fill_opacity=0.34).move_to(RIGHT * 2.55 + DOWN * 0.06)
        dataset = dataset_stack().scale(1.06).move_to(RIGHT * 2.55 + UP * 0.03)
        x_data = VGroup(
            Line(LEFT * 0.62 + UP * 0.68, RIGHT * 0.62 + DOWN * 0.68, color=ACCENT_CORAL, stroke_width=3.2),
            Line(LEFT * 0.62 + DOWN * 0.68, RIGHT * 0.62 + UP * 0.68, color=ACCENT_CORAL, stroke_width=3.2),
        ).move_to(dataset)
        beat_to(15.7, FadeOut(Group(rewind_title, rewind_panel, rewind_row, rewind_arrow, rewind_caption), shift=DOWN * 0.06), FadeIn(gpu_title, scale=0.85), FadeIn(gpu_panel), FadeIn(gpu, shift=UP * 0.08), FadeIn(x_gpu), FadeIn(cpu_chip))
        beat_to(seg_end(T, 3))
        beat_to(17.95, Group(gpu_panel, gpu, x_gpu, cpu_chip).animate.shift(LEFT * 2.65).set_opacity(0.58), FadeOut(gpu_title), FadeIn(dataset_title, scale=0.85), FadeIn(dataset_panel), FadeIn(dataset, shift=RIGHT * 0.08), FadeIn(x_data))
        beat_to(seg_end(T, 4))

        # B5 pixel compare fails
        compare_title = label("Pixel comparison breaks", UP * 2.58, color=ACCENT_CORAL, scale=0.56, bold=True)
        face_a = image_card(load_face("s2_same_smile", fallback_style="neutral", color=ACCENT_CYAN, height=2.45), color=ACCENT_CYAN, pad=0.12).move_to(LEFT * 2.8 + UP * 0.18)
        face_b = image_card(load_face("s2_same_lowlight", fallback_style="lowlight", color=ACCENT_CYAN, height=2.45), color=ACCENT_LAVENDER, pad=0.12).move_to(RIGHT * 2.8 + UP * 0.18)
        face_a_tag = label("same face", face_a.get_top() + DOWN * 0.24, color=ACCENT_CYAN, scale=0.24, bold=True)
        face_b_tag = label("different light", face_b.get_top() + DOWN * 0.24, color=ACCENT_LAVENDER, scale=0.24, bold=True)
        pixel_badge = Group(
            RoundedRectangle(width=2.05, height=0.48, corner_radius=0.08, color=ACCENT_CORAL, stroke_width=1.2, fill_color=ACCENT_CORAL, fill_opacity=0.08),
            label("pixel compare", ORIGIN, color=ACCENT_CORAL, scale=0.24, bold=True),
        ).move_to(DOWN * 2.05)
        beat_to(20.2, FadeOut(Group(dataset_title, dataset_panel, dataset, x_data, gpu_panel, gpu, x_gpu, cpu_chip), shift=LEFT * 0.08), FadeIn(compare_title, scale=0.85), FadeIn(face_a, shift=LEFT * 0.08), FadeIn(face_b, shift=RIGHT * 0.08), FadeIn(face_a_tag, shift=UP * 0.04), FadeIn(face_b_tag, shift=UP * 0.04), FadeIn(pixel_badge))
        grid_a = pixel_grid(face_a[1], rows=8, cols=8, opacity=0.13)
        grid_b = pixel_grid(face_b[1], rows=8, cols=8, opacity=0.13)
        beat_to(22.0, FadeIn(grid_a), FadeIn(grid_b))
        beat_to(
            ws("pixels", 24.28),
            AnimationGroup(
                *[sq.animate.set_fill(ACCENT_CORAL, opacity=0.5).set_stroke(ACCENT_CORAL, opacity=0.8) for sq in list(grid_a) + list(grid_b)],
                lag_ratio=0.008,
            ),
            pixel_badge.animate.scale(1.08).set_opacity(0.95),
        )
        beat_to(seg_end(T, 5), compare_title.animate.set_color(ACCENT_LAVENDER), face_a.animate.set_opacity(0.84), face_b.animate.set_opacity(0.72))

        # B6 geometric variance
        geo_title = label("Geometric variance?", UP * 2.64, color=ACCENT_LAVENDER, scale=0.62, bold=True)
        geo_face = image_card(load_face("s2_same_pose", fallback_style="pose", color=ACCENT_CYAN, height=2.25), color=ACCENT_BLUE, pad=0.12).move_to(LEFT * 1.8 + UP * 0.05)
        mesh = face_with_mesh(geo_face[1], color=ACCENT_LAVENDER).move_to(geo_face[1])
        warp_ring = Ellipse(width=2.0, height=2.42, color=ACCENT_CYAN, stroke_width=1.6).move_to(geo_face[1]).set_opacity(0.45)
        warp_spots = VGroup(*[
            Dot(geo_face[1].get_center() + p, radius=0.03, color=ACCENT_CYAN).set_opacity(0.8)
            for p in [
                LEFT * 0.34 + UP * 0.3,
                LEFT * 0.1 + UP * 0.42,
                RIGHT * 0.18 + UP * 0.26,
                LEFT * 0.28 + DOWN * 0.08,
                RIGHT * 0.08 + DOWN * 0.18,
                RIGHT * 0.3 + DOWN * 0.02,
            ]
        ])
        beat_to(
            26.0,
            FadeOut(Group(face_a, face_b, face_a_tag, face_b_tag, grid_a, grid_b, pixel_badge, compare_title), shift=DOWN * 0.04),
            FadeIn(geo_title, scale=0.85),
            FadeIn(geo_face, shift=LEFT * 0.08),
            FadeIn(mesh),
            FadeIn(warp_ring),
            FadeIn(warp_spots),
        )
        beat_to(seg_end(T, 6))

        # B7 pure math and signal processing
        math_title = label("Pure math + signal processing", ORIGIN, color=ACCENT_TEAL, scale=0.52, bold=True).to_edge(UP, buff=0.48)
        math_panel = RoundedRectangle(
            width=11.65,
            height=2.85,
            corner_radius=0.18,
            color=ACCENT_BLUE,
            stroke_width=1.05,
            fill_color=BG_NAVY_SOFT,
            fill_opacity=0.3,
        ).next_to(math_title, DOWN, buff=0.34)

        left_panel = RoundedRectangle(
            width=3.8,
            height=2.28,
            corner_radius=0.14,
            color=ACCENT_BLUE,
            stroke_width=0.95,
            fill_color=BG_NAVY,
            fill_opacity=0.22,
        )
        right_panel = RoundedRectangle(
            width=5.95,
            height=2.28,
            corner_radius=0.14,
            color=ACCENT_MINT,
            stroke_width=1.1,
            fill_color=ACCENT_MINT,
            fill_opacity=0.035,
        )
        transition_mark = VGroup(
            Line(UP * 0.95, DOWN * 0.95, color=GRID_LINE, stroke_width=1.0),
            MathTex(r"\to", tex_template=EN_TEX_TEMPLATE, color=ACCENT_LAVENDER).scale(0.72),
        ).arrange(DOWN, buff=0.12)
        b7_frame = Group(left_panel, transition_mark, right_panel).arrange(RIGHT, buff=0.38).move_to(math_panel)

        dl_title = label("Deep learning", ORIGIN, color=TEXT_MUTED, scale=0.27, bold=True).next_to(left_panel.get_top(), DOWN, buff=0.18)
        input_nodes = VGroup(*[Dot(radius=0.04, color=ACCENT_BLUE) for _ in range(3)]).arrange(DOWN, buff=0.16)
        hidden_nodes = VGroup(*[Dot(radius=0.04, color=ACCENT_BLUE) for _ in range(4)]).arrange(DOWN, buff=0.12)
        output_nodes = VGroup(*[Dot(radius=0.04, color=ACCENT_BLUE) for _ in range(2)]).arrange(DOWN, buff=0.22)
        net_layers = VGroup(input_nodes, hidden_nodes, output_nodes).arrange(RIGHT, buff=0.42)
        net_edges = VGroup()
        for left_layer, right_layer in [(input_nodes, hidden_nodes), (hidden_nodes, output_nodes)]:
            for a in left_layer:
                for b in right_layer:
                    net_edges.add(Line(a.get_center(), b.get_center(), color=ACCENT_BLUE, stroke_width=0.72).set_opacity(0.5))
        dl_net = VGroup(net_edges, net_layers)

        data_icon = VGroup(
            RoundedRectangle(width=0.5, height=0.34, corner_radius=0.045, color=ACCENT_TEAL, stroke_width=0.9, fill_color=ACCENT_TEAL, fill_opacity=0.09),
            VGroup(*[Line(LEFT * 0.16, RIGHT * 0.16, color=ACCENT_TEAL, stroke_width=0.7) for _ in range(3)]).arrange(DOWN, buff=0.055),
        )
        gpu_icon = VGroup(
            RoundedRectangle(width=0.58, height=0.34, corner_radius=0.045, color=ACCENT_LAVENDER, stroke_width=0.9, fill_color=ACCENT_LAVENDER, fill_opacity=0.08),
            Circle(radius=0.075, color=ACCENT_LAVENDER, stroke_width=0.85),
        )
        data_gpu = VGroup(data_icon, gpu_icon).arrange(RIGHT, buff=0.18)
        dl_stack = VGroup(dl_net, data_gpu).arrange(DOWN, buff=0.2).next_to(dl_title, DOWN, buff=0.18)
        dl_cross = Cross(dl_stack, stroke_color=ACCENT_CORAL, stroke_width=2.4).scale(0.72).move_to(dl_stack)
        dl_tag = label("not the path", ORIGIN, color=ACCENT_CORAL, scale=0.2, bold=True).next_to(dl_stack, DOWN, buff=0.13)
        dl_group = VGroup(dl_title, dl_stack, dl_cross, dl_tag).move_to(left_panel)

        math_title_right = label("Mathematics + Signal processing", ORIGIN, color=ACCENT_MINT, scale=0.26, bold=True).next_to(right_panel.get_top(), DOWN, buff=0.17)
        signal_patch = image_card(load_face("face", fallback_style="neutral", color=ACCENT_CYAN, height=0.48), color=ACCENT_BLUE, pad=0.04, opacity=0.16)
        signal_wave = ParametricFunction(
            lambda t: np.array([0.25 * t, 0.11 * np.sin(4.4 * t) * np.exp(-0.03 * t * t), 0]),
            t_range=[-3.0, 3.0],
            color=ACCENT_CYAN,
            stroke_width=2.0,
        )
        input_signal = Group(signal_patch, signal_wave).arrange(RIGHT, buff=0.24)

        psi = ParametricFunction(
            lambda t: np.array([0.32 * t, 0.22 * np.sin(7.0 * t) * np.exp(-0.58 * t * t), 0]),
            t_range=[-1.7, 1.7],
            color=ACCENT_LAVENDER,
            stroke_width=2.25,
        )
        psi_label = MathTex(r"\psi", tex_template=EN_TEX_TEMPLATE, color=ACCENT_LAVENDER).scale(0.62)
        psi_note = label("wave filter", ORIGIN, color=ACCENT_LAVENDER, scale=0.18, bold=True)
        psi_group = VGroup(psi_label, psi, psi_note).arrange(DOWN, buff=0.05)

        response = ParametricFunction(
            lambda t: np.array([0.28 * t, 0.07 * np.sin(5.0 * t) * np.exp(-0.08 * t * t), 0]),
            t_range=[-3.0, 3.0],
            color=ACCENT_MINT,
            stroke_width=2.05,
        )
        response_note = label("response", ORIGIN, color=ACCENT_MINT, scale=0.18, bold=True).next_to(response, DOWN, buff=0.06)
        response_group = VGroup(response, response_note)

        conv_formula = MathTex(r"\mathcal{I} * \psi", tex_template=EN_TEX_TEMPLATE, color=ACCENT_CYAN).scale(0.74)
        process_flow = Group(input_signal, psi_group, response_group).arrange(RIGHT, buff=0.36)
        conv_label = label("convolve with wave filters", ORIGIN, color=ACCENT_MINT, scale=0.2, bold=True)
        right_stack = Group(math_title_right, process_flow, conv_formula, conv_label).arrange(DOWN, buff=0.14).move_to(right_panel)

        conv_arrow = thin_arrow(
            input_signal.get_right(),
            psi_group.get_left(),
            color=ACCENT_LAVENDER,
            stroke_width=1.55,
            buff=0.06,
            max_tip_length_to_length_ratio=0.18,
        )
        out_arrow = thin_arrow(
            psi_group.get_right(),
            response_group.get_left(),
            color=ACCENT_MINT,
            stroke_width=1.55,
            buff=0.06,
            max_tip_length_to_length_ratio=0.18,
        )
        sweep = Dot(signal_wave.get_left(), radius=0.045, color=ACCENT_CYAN)

        b7_objects = Group(
            math_title, math_panel, b7_frame,
            dl_group,
            right_stack, conv_arrow, out_arrow, sweep,
        )

        beat_to(
            30.0,
            FadeOut(Group(geo_title, geo_face, mesh, warp_ring, warp_spots), shift=DOWN * 0.04),
            FadeIn(math_title, scale=0.85),
            FadeIn(math_panel),
            FadeIn(left_panel),
            FadeIn(transition_mark),
            FadeIn(right_panel),
            FadeIn(dl_title, shift=UP * 0.03),
            FadeIn(dl_stack, shift=UP * 0.04),
            Create(dl_cross),
            FadeIn(dl_tag, shift=UP * 0.03),
            FadeIn(math_title_right, shift=UP * 0.03),
            FadeIn(signal_patch, shift=UP * 0.04),
            Create(signal_wave),
            FadeIn(psi, shift=UP * 0.04),
            FadeIn(psi_label, shift=UP * 0.04),
            FadeIn(psi_note, shift=UP * 0.03),
            FadeIn(response, shift=UP * 0.04),
            FadeIn(response_note, shift=UP * 0.03),
            FadeIn(conv_formula, shift=UP * 0.04),
            Create(conv_arrow),
            Create(out_arrow),
            FadeIn(sweep),
        )
        beat_to(32.15, dl_title.animate.set_opacity(0.35), dl_stack.animate.set_opacity(0.22), dl_cross.animate.set_opacity(0.85), Indicate(signal_patch, color=ACCENT_CYAN, scale_factor=1.03), psi_group.animate.shift(RIGHT * 0.32), sweep.animate.move_to(signal_wave.get_right()), response.animate.set_color(ACCENT_TEAL))
        beat_to(seg_end(T, 7), math_title.animate.set_color(ACCENT_MINT), math_title_right.animate.set_color(ACCENT_MINT), Indicate(conv_formula, color=ACCENT_LAVENDER, scale_factor=1.08), psi_note.animate.set_opacity(0.95))

        # B8 paper / journal
        paper_title = label("IEEE PAMI · 1997", UP * 2.6, color=ACCENT_LAVENDER, scale=0.56, bold=True)
        
        # Stylized paper cover (replaces ebgm_paper_p1.png frame)
        paper_bg = RoundedRectangle(
            width=3.2,
            height=4.2,
            corner_radius=0.15,
            color=ACCENT_BLUE,
            stroke_width=2.0,
            fill_color=BG_NAVY_SOFT,
            fill_opacity=0.9
        ).move_to(LEFT * 2.6 + DOWN * 0.1)
        
        paper_header = label(
            "IEEE TRANSACTIONS ON PAMI",
            paper_bg.get_top() + DOWN * 0.4,
            color=TEXT_MUTED,
            scale=0.18,
            bold=True
        )
        header_line = Line(
            paper_bg.get_left() + RIGHT * 0.3,
            paper_bg.get_right() + LEFT * 0.3,
            color=GRID_LINE,
            stroke_width=1.0
        ).next_to(paper_header, DOWN, buff=0.1)
        
        paper_title_text = VGroup(
            label("Face Recognition by", ORIGIN, color=ACCENT_CYAN, scale=0.22, bold=True),
            label("Elastic Bunch", ORIGIN, color=ACCENT_LAVENDER, scale=0.22, bold=True),
            label("Graph Matching", ORIGIN, color=ACCENT_LAVENDER, scale=0.22, bold=True)
        ).arrange(DOWN, buff=0.08).next_to(header_line, DOWN, buff=0.4)
        
        text_lines = VGroup()
        line_widths = [2.4, 2.6, 2.2, 2.5, 1.8]
        for w in line_widths:
            text_lines.add(
                Line(
                    LEFT * (w/2),
                    RIGHT * (w/2),
                    color=TEXT_MUTED,
                    stroke_width=1.2
                ).set_opacity(0.4)
            )
        text_lines.arrange(DOWN, buff=0.12).next_to(paper_title_text, DOWN, buff=0.5)
        
        authors = label(
            "Wiskott et al. · 1997",
            paper_bg.get_bottom() + UP * 0.35,
            color=ACCENT_TEAL,
            scale=0.18,
            bold=True
        )
        
        paper_card = Group(paper_bg, paper_header, header_line, paper_title_text, text_lines, authors)
        
        paper_highlight = RoundedRectangle(
            width=2.8,
            height=0.9,
            corner_radius=0.08,
            color=ACCENT_CYAN,
            stroke_width=1.5,
            fill_color=ACCENT_CYAN,
            fill_opacity=0.12
        ).move_to(paper_title_text.get_center())
        
        stamp = Group(
            RoundedRectangle(width=1.86, height=0.7, corner_radius=0.08, color=ACCENT_LAVENDER, stroke_width=2, fill_color=ACCENT_LAVENDER, fill_opacity=0.08),
            label("IEEE PAMI", ORIGIN + UP * 0.08, color=ACCENT_LAVENDER, scale=0.28, bold=True),
            label("1997", ORIGIN + DOWN * 0.16, color=ACCENT_MINT, scale=0.26, bold=True),
        ).move_to(RIGHT * 2.6 + UP * 0.95)
        
        beat_to(
            35.5,
            FadeOut(b7_objects, shift=DOWN * 0.05),
            FadeIn(paper_title, scale=0.85),
            FadeIn(paper_card, shift=RIGHT * 0.08),
            Create(paper_highlight),
            FadeIn(stamp, shift=UP * 0.05),
        )
        self.camera.frame.save_state()
        beat_to(ws("published", 36.84), self.camera.frame.animate.scale(0.95).move_to(paper_bg.get_center() + RIGHT * 0.15))
        beat_to(40.5)
        beat_to(seg_end(T, 8), self.camera.frame.animate.restore())

        # B9 visual cortex
        cortex_title = label("Visual cortex", UP * 2.6, color=ACCENT_CYAN, scale=0.56, bold=True)
        brain = brain_icon(color=ACCENT_LAVENDER).scale(1.35).move_to(LEFT * 3.0 + UP * 0.1)
        v1 = Circle(radius=0.22, color=ACCENT_CYAN, stroke_width=2, fill_color=ACCENT_CYAN, fill_opacity=0.12).move_to(brain[4].get_center())
        v1_tag = label("V1", v1.get_center() + UP * 0.32, color=ACCENT_CYAN, scale=0.22, bold=True)
        face_for_brain = image_card(load_face("s2_personB", fallback_style="neutral", color=ACCENT_CYAN, height=2.2), color=ACCENT_BLUE, pad=0.12).move_to(RIGHT * 2.7 + DOWN * 0.05)
        rays = Group(*[
            Line(brain[4].get_center(), face_for_brain[1].get_left() + RIGHT * 0.1 + UP * (0.35 - i * 0.16), color=ACCENT_CYAN, stroke_width=1.8).set_opacity(0.65)
            for i in range(5)
        ])
        teach = label("teach the computer to see a face like the cortex does", DOWN * 2.1, color=TEXT_MUTED, scale=0.29)
        beat_to(
            44.0,
            FadeOut(Group(paper_title, paper_card, paper_highlight, stamp), shift=DOWN * 0.05),
            FadeIn(cortex_title, scale=0.85),
            FadeIn(brain, shift=LEFT * 0.08),
            FadeIn(v1),
            FadeIn(v1_tag),
            FadeIn(face_for_brain, shift=RIGHT * 0.08),
            LaggedStart(*[Create(ray) for ray in rays], lag_ratio=0.08),
            FadeIn(teach, shift=UP * 0.04),
        )

        # B10 algorithm name
        algo_title = label("Elastic Bunch Graph Matching", UP * 2.55, color=ACCENT_LAVENDER, scale=0.56, bold=True)
        graph_face = Group(
            Circle(radius=0.74, color=ACCENT_CYAN, stroke_width=2, fill_color=ACCENT_CYAN, fill_opacity=0.03),
            Dot(LEFT * 0.24 + UP * 0.16, radius=0.03, color=ACCENT_CYAN),
            Dot(RIGHT * 0.24 + UP * 0.16, radius=0.03, color=ACCENT_CYAN),
            Dot(ORIGIN + DOWN * 0.04, radius=0.03, color=ACCENT_CYAN),
            Line(LEFT * 0.18 + UP * 0.12, RIGHT * 0.18 + UP * 0.12, color=ACCENT_CYAN, stroke_width=1.8),
            Line(LEFT * 0.2 + UP * 0.05, ORIGIN + DOWN * 0.03, color=ACCENT_CYAN, stroke_width=1.6),
            Line(RIGHT * 0.2 + UP * 0.05, ORIGIN + DOWN * 0.03, color=ACCENT_CYAN, stroke_width=1.6),
        ).scale(0.9).move_to(LEFT * 0.15 + DOWN * 0.05)
        glow = Circle(radius=0.9, color=ACCENT_LAVENDER, stroke_width=3, fill_opacity=0.0).move_to(graph_face)
        beat_to(seg_end(T, 9))
        beat_to(47.7, FadeOut(Group(cortex_title, brain, v1, v1_tag, face_for_brain, rays, teach), shift=DOWN * 0.05), FadeIn(algo_title, scale=0.82), FadeIn(graph_face, shift=UP * 0.06), Create(glow))
        beat_to(49.0, glow.animate.set_opacity(0.2).scale(1.05), algo_title.animate.set_color(ACCENT_CYAN))
        beat_to(seg_end(T, 10))

        # B11 FERET ranking
        feret_title = label("FERET blind tests", UP * 2.5, color=ACCENT_MINT, scale=0.56, bold=True)
        rank = ranking_bars().scale(0.94).move_to(LEFT * 1.6 + DOWN * 0.04)
        feret_sheet = Group(
            RoundedRectangle(width=2.0, height=2.1, corner_radius=0.1, color=ACCENT_BLUE, stroke_width=1.1, fill_color=BG_NAVY_SOFT, fill_opacity=0.38),
            label("blind test", UP * 0.68, color=ACCENT_CYAN, scale=0.25, bold=True),
            label("hidden labels", UP * 0.2, color=TEXT_MUTED, scale=0.21),
            label("rank by identity", DOWN * 0.23, color=TEXT_MUTED, scale=0.21),
        ).move_to(RIGHT * 2.05 + DOWN * 0.05)
        medal = Group(
            Circle(radius=0.3, color=ACCENT_MINT, stroke_width=1.6, fill_color=ACCENT_MINT, fill_opacity=0.08),
            MathTex(r"\star", tex_template=EN_TEX_TEMPLATE, color=ACCENT_MINT).scale(0.48),
        ).move_to(RIGHT * 4.05 + UP * 0.55)
        top_badge = Group(
            RoundedRectangle(width=1.58, height=0.46, corner_radius=0.08, color=ACCENT_LAVENDER, stroke_width=1.1, fill_color=ACCENT_LAVENDER, fill_opacity=0.08),
            label("top-ranked", ORIGIN, color=ACCENT_LAVENDER, scale=0.21, bold=True),
        ).move_to(RIGHT * 4.05 + DOWN * 0.1)
        beat_to(51.2, FadeOut(Group(algo_title, graph_face, glow), shift=DOWN * 0.05), FadeIn(feret_title, scale=0.82), FadeIn(rank), FadeIn(feret_sheet), FadeIn(medal), FadeIn(top_badge))
        beat_to(ws("ferret", 52.78), medal.animate.scale(1.12))
        beat_to(seg_end(T, 11))

        # B12 close
        close_title = label("Today, we dissect it.", UP * 2.65, color=TEXT_PRIMARY, scale=0.58, bold=True)
        close_face = image_card(load_face("face", fallback_style="neutral", color=ACCENT_CYAN, height=2.15), color=ACCENT_BLUE, pad=0.12).move_to(LEFT * 1.9 + DOWN * 0.05)
        close_graph = Group(
            Circle(radius=0.74, color=ACCENT_LAVENDER, stroke_width=2, fill_color=ACCENT_LAVENDER, fill_opacity=0.03),
            Dot(LEFT * 0.25 + UP * 0.15, radius=0.03, color=ACCENT_LAVENDER),
            Dot(RIGHT * 0.25 + UP * 0.15, radius=0.03, color=ACCENT_LAVENDER),
            Dot(ORIGIN + DOWN * 0.05, radius=0.03, color=ACCENT_LAVENDER),
            Line(LEFT * 0.18 + UP * 0.12, RIGHT * 0.18 + UP * 0.12, color=ACCENT_LAVENDER, stroke_width=1.8),
            Line(LEFT * 0.2 + UP * 0.05, ORIGIN + DOWN * 0.03, color=ACCENT_LAVENDER, stroke_width=1.6),
            Line(RIGHT * 0.2 + UP * 0.05, ORIGIN + DOWN * 0.03, color=ACCENT_LAVENDER, stroke_width=1.6),
        ).scale(0.9).move_to(RIGHT * 2.45 + DOWN * 0.05)
        closing_rays = Group(*[
            Line(close_graph.get_left() + RIGHT * 0.1, close_face[1].get_right() + LEFT * 0.1 + UP * (0.2 - i * 0.13), color=ACCENT_CYAN, stroke_width=1.6).set_opacity(0.55)
            for i in range(4)
        ])
        beat_to(
            55.5,
            FadeOut(Group(feret_title, rank, feret_sheet, medal, top_badge), shift=DOWN * 0.05),
            FadeIn(close_title, scale=0.82),
            FadeIn(close_face, shift=LEFT * 0.05),
            FadeIn(close_graph, shift=RIGHT * 0.05),
            LaggedStart(*[Create(ray) for ray in closing_rays], lag_ratio=0.08),
        )
        beat_to(T["duration"], self.camera.frame.animate.scale(0.94).move_to(close_graph.get_center() + LEFT * 0.1), close_title.animate.set_opacity(0.95))

        tail = max(0.0, T["duration"] - elapsed - 0.08)
        if tail > 0.05:
            self.wait(tail)
