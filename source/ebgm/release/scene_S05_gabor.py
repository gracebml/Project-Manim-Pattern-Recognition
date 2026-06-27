import os
import sys
import json
from pathlib import Path
from PIL import Image, ImageOps, ImageEnhance

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from manim import *
import numpy as np
from _common import *

ASSET_DIR = Path(__file__).resolve().parents[2] / "assets"
TMP_IMG_DIR = Path("/tmp/video_manim_s05_imgs")
TMP_IMG_DIR.mkdir(parents=True, exist_ok=True)


def gabor_array(theta=0.0, freq=3.0, sigma=0.42, size=64, opacity=1.0):
    ys, xs = np.mgrid[-1:1:complex(size), -1:1:complex(size)]
    xr = xs * np.cos(theta) + ys * np.sin(theta)
    yr = -xs * np.sin(theta) + ys * np.cos(theta)
    gaussian = np.exp(-(xr * xr + yr * yr) / (2 * sigma * sigma))
    wave = np.cos(TAU * freq * xr)
    gabor = gaussian * wave
    gray = ((gabor + 1.0) * 127.5).clip(0, 255).astype(np.uint8)
    alpha = (np.ones_like(gray) * 255 * opacity).astype(np.uint8)
    rgba = np.stack([gray, gray, gray, alpha], axis=-1)
    return rgba


class S05_Gabor(ThreeDScene):
    SCENE_KEY = "scene_05"

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

        def play_t(run_time, *anims, **kw):
            nonlocal elapsed
            self.play(*anims, run_time=run_time, **kw)
            elapsed += run_time

        def label(text, pos, color=TEXT_PRIMARY, scale=0.36, bold=False):
            return en_label(text, color=color, scale=scale, bold=bold).move_to(pos)

        def crop_patch(center_rel, size_px=110, name="patch", brightness=1.0):
            p_face = ASSET_DIR / "s8_face.png"
            if not p_face.exists():
                raise FileNotFoundError(f"Face image not found: {p_face}")
            
            cache_path = TMP_IMG_DIR / f"{name}_{size_px}_b{int(brightness*100)}.png"
            if not cache_path.exists():
                with Image.open(p_face) as im:
                    im_w, im_h = im.size
                    cx = int(center_rel[0] * im_w)
                    cy = int(center_rel[1] * im_h)
                    half = size_px // 2
                    box = (cx - half, cy - half, cx + half, cy + half)
                    cropped = im.crop(box)
                    if brightness != 1.0:
                        enhancer = ImageEnhance.Brightness(cropped)
                        cropped = enhancer.enhance(brightness)
                    cropped.save(cache_path)
            return cache_path

        def load_face(name, height=2.2):
            for ext in (".png", ".jpg", ".jpeg"):
                p = ASSET_DIR / f"{name}{ext}"
                if p.exists():
                    img = ImageMobject(str(p))
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

        def pixel_grid(rows=6, cols=6, side=0.18):
            grid = VGroup()
            for r in range(rows):
                for c in range(cols):
                    val = ((r * 13 + c * 19) % 100) / 100
                    color = interpolate_color(ManimColor(ACCENT_BLUE), ManimColor(ACCENT_CORAL), val)
                    sq = Square(side_length=side, stroke_width=0.35, stroke_color=BG_NAVY_SOFT)
                    sq.set_fill(color, opacity=min(0.85, 0.16 + 0.40 * val))
                    sq.move_to([c * side - (cols - 1) * side / 2, r * side - (rows - 1) * side / 2, 0])
                    grid.add(sq)
            return grid

        def graph_curve(fn, x0=-2.0, x1=2.0, n=96, color=ACCENT_CYAN, width=2.4):
            pts = []
            for x in np.linspace(x0, x1, n):
                pts.append([x, fn(x), 0])
            return VMobject(color=color, stroke_width=width).set_points_smoothly(pts)

        title = label("Gabor wavelets", UP * 2.75, color=TEXT_PRIMARY, scale=0.58, bold=True)

        # B0: a single point on a face.
        face_img = load_face("s8_face", height=3.8)
        face_card = make_face_card(face_img, color=ACCENT_BLUE).move_to(LEFT * 3.0 + DOWN * 0.30)
        
        # Calculate eye corner relative coordinates
        img_mob = face_card[1]
        def L(u, v):
            tl = img_mob.get_corner(UL)
            br = img_mob.get_corner(DR)
            return np.array([tl[0] + u * (br[0] - tl[0]), tl[1] + v * (br[1] - tl[1]), 0])

        focus_center = L(0.37, 0.39)
        focus = Circle(radius=0.15, color=ACCENT_CYAN, stroke_width=2.5).move_to(focus_center)
        
        # Crop patch
        patch_path = crop_patch([0.37, 0.39], size_px=110, name="eye_patch")
        patch_img = ImageMobject(str(patch_path)).scale_to_fit_height(2.2)
        patch_card = make_face_card(patch_img, color=ACCENT_CYAN).move_to(RIGHT * 2.5 + DOWN * 0.30)
        
        # Zoom lines
        zoom_line_top = Line(focus.get_top(), patch_card.get_top() + LEFT * 0.05, color=ACCENT_CYAN, stroke_width=1.2).set_opacity(0.4)
        zoom_line_bottom = Line(focus.get_bottom(), patch_card.get_bottom() + LEFT * 0.05, color=ACCENT_CYAN, stroke_width=1.2).set_opacity(0.4)
        
        question = label("How does AI see one point?", UP * 2.10, color=ACCENT_CYAN, scale=0.58, bold=True)
        patch_lbl = label("local patch", patch_card.get_center() + DOWN * 1.35, color=TEXT_MUTED, scale=0.38)
        
        play_t(1.0, FadeIn(title), FadeIn(question), FadeIn(face_card))
        play_t(0.8, Create(focus))
        
        patch_card_start = patch_card.copy().scale(0.08).move_to(focus_center)
        play_t(
            1.8,
            ReplacementTransform(patch_card_start, patch_card),
            Create(zoom_line_top),
            Create(zoom_line_bottom),
            FadeIn(patch_lbl)
        )
        beat_to(seg_end(T, 0))

        # B1: raw pixels vs biological cortex receptive field.
        raw_lbl = label("raw pixels", LEFT * 2.5 + DOWN * 1.40, color=ACCENT_CORAL, scale=0.42, bold=True)
        raw_grid = pixel_grid(rows=6, cols=6, side=0.20).move_to(LEFT * 2.5 + DOWN * 0.30)
        
        # Slim Cross instead of Line slash
        reject = Cross(raw_grid, color=ACCENT_CORAL, stroke_width=3.0).scale(0.92)
        
        bio_lbl = label("borrow from biology", RIGHT * 2.5 + DOWN * 1.40, color=ACCENT_LAVENDER, scale=0.42, bold=True)
        bio_node = Dot(RIGHT * 2.5 + UP * 0.25, radius=0.18, color=ACCENT_LAVENDER)
        bio_lines = VGroup(*[
            Line(RIGHT * 2.5 + UP * 0.25, RIGHT * 2.5 + np.array([x, y - 0.15, 0]), color=ACCENT_TEAL, stroke_width=2.0)
            for x, y in [(-0.8, -0.6), (-0.3, -0.7), (0.3, -0.7), (0.8, -0.6)]
        ])
        bio_dots = VGroup(*[Dot(l.get_end(), radius=0.07, color=ACCENT_TEAL) for l in bio_lines])
        bio_group = VGroup(bio_node, bio_lines, bio_dots)
        
        play_t(
            1.0,
            FadeOut(face_card), FadeOut(focus), FadeOut(zoom_line_top), FadeOut(zoom_line_bottom),
            FadeOut(patch_card), FadeOut(patch_lbl),
            question.animate.set_opacity(0.24)
        )
        
        play_t(
            1.0,
            FadeIn(raw_grid),
            FadeIn(raw_lbl)
        )
        
        # Pixels flashing erratically
        flash_anims = [sq.animate.set_fill(sq.fill_color, opacity=np.random.uniform(0.1, 0.9)) for sq in raw_grid]
        play_t(0.8, *flash_anims)
        
        # Reject Cross
        play_t(0.8, Create(reject), raw_lbl.animate.set_color(ACCENT_CORAL))
        
        play_t(
            1.2,
            FadeIn(bio_group, shift=LEFT * 0.1),
            FadeIn(bio_lbl)
        )
        beat_to(seg_end(T, 1))

        # B2: sine wave inside a Gaussian envelope.
        axis = NumberLine(x_range=[-2.4, 2.4, 1], length=4.5, color=GRID_LINE, stroke_width=1.2).shift(LEFT * 3.1 + UP * 0.3)
        sine = graph_curve(lambda x: 0.35 * np.sin(6 * x), x0=-2.4, x1=2.4, color=ACCENT_CYAN).shift(LEFT * 3.1 + UP * 0.3)
        
        envelope_up = graph_curve(lambda x: 0.8 * np.exp(-0.55 * x * x), x0=-2.4, x1=2.4, color=ACCENT_TEAL, width=2.0).shift(LEFT * 3.1 + UP * 0.3)
        envelope_down = graph_curve(lambda x: -0.8 * np.exp(-0.55 * x * x), x0=-2.4, x1=2.4, color=ACCENT_TEAL, width=2.0).shift(LEFT * 3.1 + UP * 0.3)
        
        sine_lbl = label("sine wave", LEFT * 3.1 + DOWN * 0.9, color=ACCENT_CYAN, scale=0.40)
        gauss_lbl = label("Gaussian envelope", LEFT * 3.1 + DOWN * 1.3, color=ACCENT_TEAL, scale=0.40)
        
        times = label(r"$\times$", LEFT * 0.35 + UP * 0.3, color=MATH_YELLOW, scale=0.85, bold=True)
        equals = label(r"$=$", RIGHT * 0.35 + UP * 0.3, color=MATH_YELLOW, scale=0.85, bold=True)
        
        gabor_axis = NumberLine(x_range=[-2.4, 2.4, 1], length=4.5, color=GRID_LINE, stroke_width=1.2).shift(RIGHT * 3.1 + UP * 0.3)
        gabor_curve = graph_curve(lambda x: 0.72 * np.exp(-0.55 * x * x) * np.sin(6 * x), x0=-2.4, x1=2.4, color=ACCENT_LAVENDER, width=2.8).shift(RIGHT * 3.1 + UP * 0.3)
        gabor_lbl = label("Gabor wavelet", RIGHT * 3.1 + DOWN * 0.9, color=ACCENT_LAVENDER, scale=0.52, bold=True)
        formula = MathTex(
            r"\psi(x)=e^{-x^2/2\sigma^2}\cos(kx)",
            tex_template=EN_TEX_TEMPLATE,
            color=MATH_YELLOW,
        ).scale(0.85).move_to(RIGHT * 3.1 + DOWN * 1.6)
        
        play_t(
            1.0,
            FadeOut(raw_grid), FadeOut(raw_lbl), FadeOut(reject), FadeOut(bio_group), FadeOut(bio_lbl), FadeOut(question)
        )
        play_t(1.0, Create(axis), Create(sine), FadeIn(sine_lbl))
        play_t(
            1.0,
            Create(envelope_up),
            Create(envelope_down),
            FadeIn(gauss_lbl)
        )
        play_t(0.6, FadeIn(times), FadeIn(equals))
        play_t(
            1.8,
            Create(gabor_axis),
            ReplacementTransform(sine.copy(), gabor_curve),
            FadeIn(gabor_lbl),
            Write(formula)
        )
        beat_to(seg_end(T, 2))

        # B3: interactive filter sweeps over the patch at different orientations.
        patch_card2 = make_face_card(ImageMobject(str(patch_path)).scale_to_fit_height(2.5), color=ACCENT_CYAN).move_to(LEFT * 3.0 + DOWN * 0.30)
        patch_lbl2 = label("eye patch", LEFT * 3.0 + DOWN * 1.85, color=TEXT_MUTED, scale=0.38)
        
        bg_bar = RoundedRectangle(width=0.45, height=2.5, corner_radius=0.1, color=GRID_LINE, stroke_width=1.0, fill_color=BG_NAVY_SOFT, fill_opacity=0.6).move_to(RIGHT * 2.5 + DOWN * 0.30)
        response_lbl = label("edge response", RIGHT * 2.5 + DOWN * 1.85, color=ACCENT_CYAN, scale=0.42, bold=True)
        
        orientation_lbl = label("one orientation", RIGHT * 0.1 + DOWN * 1.0, color=ACCENT_TEAL, scale=0.38, bold=True)
        freq_lbl = label("one frequency", RIGHT * 0.1 + DOWN * 1.4, color=ACCENT_CYAN, scale=0.38, bold=True)
        
        x_tracker = ValueTracker(-1.4)
        self.sweep_theta = 0.0
        
        def get_response_height(x):
            if abs(self.sweep_theta - 0.0) < 0.01:
                return 2.3 * np.exp(-8 * x**2)
            elif abs(self.sweep_theta - PI / 4) < 0.01:
                return 1.4 * np.exp(-8 * (x - 0.2)**2)
            else:
                return 0.4 * np.exp(-8 * (x - 0.4)**2)

        fg_bar = always_redraw(
            lambda: Rectangle(
                width=0.45,
                height=max(0.05, get_response_height(x_tracker.get_value())),
                color=ACCENT_MINT,
                stroke_width=0,
                fill_color=ACCENT_MINT,
                fill_opacity=0.82
            ).align_to(bg_bar, DOWN)
        )
        
        filter_size = 1.0
        def make_sweep_filter(theta):
            img = ImageMobject(gabor_array(theta=theta, freq=3.0, size=64, opacity=0.7)).scale_to_fit_height(filter_size)
            frame = Square(side_length=filter_size + 0.05, color=ACCENT_MINT, stroke_width=1.5)
            img.move_to(frame.get_center())
            return Group(frame, img)

        filter_obj = make_sweep_filter(self.sweep_theta)
        filter_obj.add_updater(lambda m: m.move_to(LEFT * 3.0 + DOWN * 0.30 + RIGHT * x_tracker.get_value()))
        
        play_t(
            1.0,
            FadeOut(axis), FadeOut(sine), FadeOut(envelope_up), FadeOut(envelope_down),
            FadeOut(times), FadeOut(equals), FadeOut(gabor_axis), FadeOut(gabor_curve),
            FadeOut(sine_lbl), FadeOut(gauss_lbl), FadeOut(gabor_lbl), FadeOut(formula)
        )
        
        play_t(
            1.0,
            FadeIn(patch_card2),
            FadeIn(patch_lbl2),
            FadeIn(bg_bar),
            FadeIn(response_lbl),
            FadeIn(orientation_lbl),
            FadeIn(freq_lbl),
            FadeIn(filter_obj)
        )
        
        # Sweep 1: 0 degrees
        play_t(0.2, FadeIn(fg_bar))
        play_t(1.4, x_tracker.animate.set_value(1.4), rate_func=linear)
        
        # Reset & Transform to 90 degrees (PI/2) (only 2 sweeps to strictly respect budget of 6.42s)
        filter_obj.clear_updaters()
        self.sweep_theta = PI / 2
        new_filter = make_sweep_filter(self.sweep_theta)
        new_filter.move_to(LEFT * 3.0 + DOWN * 0.30 + RIGHT * x_tracker.get_value())
        
        play_t(0.8, x_tracker.animate.set_value(-1.4), ReplacementTransform(filter_obj, new_filter))
        filter_obj = new_filter
        filter_obj.add_updater(lambda m: m.move_to(LEFT * 3.0 + DOWN * 0.30 + RIGHT * x_tracker.get_value()))
        
        # Sweep 2: 90 degrees
        play_t(1.4, x_tracker.animate.set_value(1.4), rate_func=linear)
        
        filter_obj.clear_updaters()
        fg_bar.clear_updaters()
        beat_to(seg_end(T, 3))

        # B4: DC-free: background illumination resilience.
        dark_path = crop_patch([0.37, 0.39], size_px=110, name="eye_patch_dark", brightness=0.6)
        bright_path = crop_patch([0.37, 0.39], size_px=110, name="eye_patch_bright", brightness=1.4)
        
        dark_img = ImageMobject(str(dark_path)).scale_to_fit_height(1.8)
        bright_img = ImageMobject(str(bright_path)).scale_to_fit_height(1.8)
        
        dark_card = make_face_card(dark_img, color=ACCENT_CYAN).move_to(LEFT * 3.4 + DOWN * 0.30)
        bright_card = make_face_card(bright_img, color=ACCENT_CYAN).move_to(LEFT * 1.4 + DOWN * 0.30)
        
        dark_lbl = label("dark patch", LEFT * 3.4 + DOWN * 1.45, color=TEXT_MUTED, scale=0.36)
        bright_lbl = label("bright patch", LEFT * 1.4 + DOWN * 1.45, color=TEXT_MUTED, scale=0.36)
        
        minus_mean = MathTex(r"-\ \mathrm{mean\ light}", tex_template=EN_TEX_TEMPLATE, color=ACCENT_CORAL).scale(0.65).move_to(RIGHT * 0.6 + DOWN * 0.30)
        
        bg_dark = RoundedRectangle(width=0.35, height=2.2, corner_radius=0.08, color=GRID_LINE, stroke_width=0.8, fill_color=BG_NAVY_SOFT, fill_opacity=0.5).move_to(RIGHT * 2.2 + DOWN * 0.30)
        bg_bright = RoundedRectangle(width=0.35, height=2.2, corner_radius=0.08, color=GRID_LINE, stroke_width=0.8, fill_color=BG_NAVY_SOFT, fill_opacity=0.5).move_to(RIGHT * 3.2 + DOWN * 0.30)
        
        # Raw pixel response bars (sensitive to illumination, different heights)
        bar_dark = Rectangle(width=0.35, height=0.7, color=ACCENT_CORAL, stroke_width=0, fill_color=ACCENT_CORAL, fill_opacity=0.8).align_to(bg_dark, DOWN)
        bar_bright = Rectangle(width=0.35, height=2.0, color=ACCENT_CORAL, stroke_width=0, fill_color=ACCENT_CORAL, fill_opacity=0.8).align_to(bg_bright, DOWN)
        
        dc_title = label("DC-free", UP * 2.10, color=ACCENT_MINT, scale=0.75, bold=True)
        same_resp_lbl = label("same edge response", RIGHT * 2.7 + DOWN * 1.65, color=ACCENT_MINT, scale=0.38, bold=True)
        
        play_t(
            1.0,
            FadeOut(patch_card2), FadeOut(patch_lbl2), FadeOut(filter_obj), FadeOut(bg_bar), FadeOut(fg_bar),
            FadeOut(response_lbl), FadeOut(orientation_lbl), FadeOut(freq_lbl)
        )
        
        play_t(
            1.0,
            FadeIn(dark_card), FadeIn(dark_lbl),
            FadeIn(bright_card), FadeIn(bright_lbl),
            FadeIn(bg_dark), FadeIn(bg_bright),
            FadeIn(bar_dark), FadeIn(bar_bright)
        )
        
        play_t(
            0.8,
            Write(minus_mean),
            FadeIn(dc_title, shift=DOWN * 0.05)
        )
        
        # DC-free normalization convergence
        play_t(
            1.4,
            bar_dark.animate.set_height(1.5).set_color(ACCENT_MINT).align_to(bg_dark, DOWN),
            bar_bright.animate.set_height(1.5).set_color(ACCENT_MINT).align_to(bg_bright, DOWN),
            FadeIn(same_resp_lbl)
        )
        beat_to(seg_end(T, 4))

        # B5: CNN first layers and visual cortex connection.
        grid_frames = VGroup()
        grid_images = Group()
        for r in range(3):
            for c in range(3):
                theta = (r * 3 + c) * PI / 8
                freq = 2.0 + r * 0.8
                g_img = ImageMobject(gabor_array(theta=theta, freq=freq, size=48, opacity=0.95))
                g_img.scale_to_fit_height(0.65)
                frame = Square(side_length=0.72, color=ACCENT_BLUE, stroke_width=1.0)
                pos = LEFT * 2.5 + DOWN * 0.30 + np.array([(c - 1) * 0.85, (1 - r) * 0.85, 0])
                frame.move_to(pos)
                g_img.move_to(pos)
                grid_frames.add(frame)
                grid_images.add(g_img)
                
        cnn_lbl = label("CNN first-layer filters", LEFT * 2.5 + DOWN * 1.75, color=ACCENT_CYAN, scale=0.52, bold=True)
        approx = label(r"$\approx$", ORIGIN + DOWN * 0.30, color=MATH_YELLOW, scale=0.85)
        
        cortex_x = 2.5
        cortex_cols = VGroup(
            RoundedRectangle(width=0.55, height=1.9, corner_radius=0.08, color=ACCENT_LAVENDER, stroke_width=1.2, fill_color=BG_NAVY_SOFT, fill_opacity=0.35).move_to(RIGHT * (cortex_x - 0.7) + DOWN * 0.30),
            RoundedRectangle(width=0.55, height=1.9, corner_radius=0.08, color=ACCENT_TEAL, stroke_width=1.2, fill_color=BG_NAVY_SOFT, fill_opacity=0.35).move_to(RIGHT * cortex_x + DOWN * 0.30),
            RoundedRectangle(width=0.55, height=1.9, corner_radius=0.08, color=ACCENT_MINT, stroke_width=1.2, fill_color=BG_NAVY_SOFT, fill_opacity=0.35).move_to(RIGHT * (cortex_x + 0.7) + DOWN * 0.30),
        )
        
        cortex_lines = VGroup()
        # Column 0: horizontal (0 degrees)
        for y in np.linspace(-0.6, 0.6, 4):
            cortex_lines.add(Line(LEFT * 0.18, RIGHT * 0.18, color=ACCENT_LAVENDER, stroke_width=1.5).move_to(RIGHT * (cortex_x - 0.7) + DOWN * (0.30 + y)))
        # Column 1: diagonal (45 degrees)
        for y in np.linspace(-0.6, 0.6, 4):
            cortex_lines.add(Line(LEFT * 0.13 + DOWN * 0.13, RIGHT * 0.13 + UP * 0.13, color=ACCENT_TEAL, stroke_width=1.5).move_to(RIGHT * cortex_x + DOWN * (0.30 + y)))
        # Column 2: vertical (90 degrees)
        for y in np.linspace(-0.6, 0.6, 4):
            cortex_lines.add(Line(DOWN * 0.18, UP * 0.18, color=ACCENT_MINT, stroke_width=1.5).move_to(RIGHT * (cortex_x + 0.7) + DOWN * (0.30 + y)))
            
        bio_lbl5 = label("visual cortex", RIGHT * cortex_x + DOWN * 1.75, color=ACCENT_LAVENDER, scale=0.52, bold=True)
        
        # Clear DC-free, then reveal the CNN first-layer Gabor filters.
        play_t(
            0.6,
            FadeOut(dark_card), FadeOut(dark_lbl), FadeOut(bright_card), FadeOut(bright_lbl),
            FadeOut(bg_dark), FadeOut(bg_bright), FadeOut(bar_dark), FadeOut(bar_bright),
            FadeOut(minus_mean), FadeOut(dc_title), FadeOut(same_resp_lbl)
        )

        beat_to(word_start(T, "CNN") or 30.94)
        play_t(
            1.0,
            LaggedStart(*[FadeIn(f, scale=0.8) for f in grid_frames], lag_ratio=0.04),
            LaggedStart(*[FadeIn(g, scale=0.8) for g in grid_images], lag_ratio=0.04),
            FadeIn(cnn_lbl),
        )

        beat_to(word_start(T, "visual") or 34.92)
        play_t(
            0.9,
            FadeIn(approx),
            FadeIn(cortex_cols),
            Create(cortex_lines),
            FadeIn(bio_lbl5),
        )
        beat_to(seg_end(T, 5))

        tail = max(0.0, T["duration"] - elapsed - 0.18)
        if tail > 0.05:
            self.wait(tail)
