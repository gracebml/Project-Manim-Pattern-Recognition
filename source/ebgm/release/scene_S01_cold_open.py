import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from manim import *
import numpy as np
from _common import *


class S01_ColdOpen(MovingCameraScene):
    SCENE_KEY = "scene_01"

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

        def tiny_person(color=ACCENT_BLUE):
            head = Circle(radius=0.18, color=color, stroke_width=2, fill_opacity=0.08)
            body = Line(DOWN * 0.15, DOWN * 0.95, color=color, stroke_width=3)
            legs = VGroup(
                Line(DOWN * 0.95, DOWN * 1.35 + LEFT * 0.18, color=color, stroke_width=2),
                Line(DOWN * 0.95, DOWN * 1.35 + RIGHT * 0.18, color=color, stroke_width=2),
            )
            return VGroup(head, body, legs)

        def mini_face(color=ACCENT_BLUE):
            face = Ellipse(width=1.2, height=1.55, color=color, stroke_width=2, fill_opacity=0.04)
            eyes = VGroup(
                Dot(LEFT * 0.22 + UP * 0.18, radius=0.04, color=color),
                Dot(RIGHT * 0.22 + UP * 0.18, radius=0.04, color=color),
            )
            nose = Line(UP * 0.15, DOWN * 0.12, color=color, stroke_width=2)
            mouth = Arc(radius=0.2, start_angle=210 * DEGREES, angle=120 * DEGREES, color=color, stroke_width=2).shift(DOWN * 0.38)
            return VGroup(face, eyes, nose, mouth)

        # ---- 45°-from-above perspective floor (synthwave) the two people stand on ----
        HY, BY, HW = 1.4, -4.4, 15.0   # horizon y, near-floor y, half-width at near edge

        def hw_at(y):
            return HW * (HY - y) / (HY - BY)

        floor_h = VGroup()
        rr, kk = 1.26, 0
        while kk < 48:
            y = HY - (HY - BY) / (rr ** kk)
            if y > HY - 0.05:
                break
            t = (HY - y) / (HY - BY)
            ln = Line([-hw_at(y), y, 0], [hw_at(y), y, 0], stroke_width=1.6)
            ln.set_stroke(interpolate_color(ManimColor(ACCENT_LAVENDER), ManimColor(ACCENT_CYAN), t),
                          opacity=0.14 + 0.36 * t)
            floor_h.add(ln)
            kk += 1
        floor_v = VGroup()
        for fx in np.linspace(-1.0, 1.0, 19):
            ln = Line([fx * HW, BY, 0], [0, HY, 0], stroke_width=1.6)
            d = abs(fx)
            ln.set_stroke(interpolate_color(ManimColor(ACCENT_LAVENDER), ManimColor(ACCENT_CYAN), d),
                          opacity=0.40 - 0.20 * d)
            floor_v.add(ln)
        horizon_glow = Line([-HW, HY, 0], [HW, HY, 0], color=MATH_YELLOW, stroke_width=4).set_opacity(0.34)
        floor = VGroup(floor_v, floor_h, horizon_glow)

        # faint night skyline, far away at the horizon
        buildings = VGroup()
        for i, x in enumerate([-5.0, -3.5, -2.1, 2.3, 3.8, 5.2]):
            h = 0.55 + 0.22 * ((i * 3) % 4)
            b = Rectangle(width=0.66, height=h, color=ACCENT_BLUE, stroke_width=0.7,
                          fill_color=BG_NAVY_SOFT, fill_opacity=0.14).move_to([x, HY + h / 2, 0])
            b.set_opacity(0.12)
            buildings.add(b)
        window_glints = VGroup()
        for x, y in [(-3.5, HY + 0.45), (2.3, HY + 0.4), (5.2, HY + 0.55)]:
            window_glints.add(Square(side_length=0.09, color=ACCENT_BLUE, stroke_width=0.7).move_to([x, y, 0]).set_opacity(0.12))

        def make_person(color, as_face=False):
            p = tiny_person(color)
            if as_face:
                p[0].become(mini_face(color).scale(0.30)[0])
            return p

        def stand(p, fx, foot_y, scale):
            """Plant a figure so its feet rest on the floor at lateral fraction fx, depth foot_y."""
            p.scale(scale)
            cx = fx * hw_at(foot_y)
            p.shift([cx - p.get_center()[0], foot_y - p.get_bottom()[1], 0])
            return p

        def make_shadow(p):
            prox = (HY - p.get_bottom()[1]) / (HY - BY)
            sh = Ellipse(width=p.width * 1.25, height=max(0.07, 0.20 * prox), stroke_width=0)
            sh.set_fill(BLACK, opacity=0.30)
            sh.move_to([p.get_center()[0], p.get_bottom()[1] + 0.03, 0])
            return sh

        # they walk toward the camera: far state -> near (met) state
        A_FAR = dict(fx=-0.60, foot_y=0.15, scale=1.00)
        B_FAR = dict(fx=0.60, foot_y=0.15, scale=1.00)
        A_NEAR = dict(fx=-0.42, foot_y=-1.15, scale=1.28)
        B_NEAR = dict(fx=0.42, foot_y=-1.15, scale=1.28)

        person_a = stand(make_person(ACCENT_CYAN), **A_FAR)
        person_b = stand(make_person(ACCENT_LAVENDER, as_face=True), **B_FAR)
        person_b[0].move_to([person_b[1].get_center()[0], person_a[0].get_center()[1], 0])
        shadow_a = make_shadow(person_a)
        shadow_b = make_shadow(person_b)

        a_near = stand(make_person(ACCENT_CYAN), **A_NEAR)
        b_near = stand(make_person(ACCENT_LAVENDER, as_face=True), **B_NEAR)
        b_near[0].move_to([b_near[1].get_center()[0], a_near[0].get_center()[1], 0])
        shadow_a_near = make_shadow(a_near)
        shadow_b_near = make_shadow(b_near)

        recog_t = word_start(T, "recogn") or 3.5
        self.add(floor, buildings, window_glints, shadow_a, shadow_b, person_a, person_b)
        self.bring_to_back(floor)
        beat_to(
            recog_t,
            Transform(person_a, a_near),
            Transform(person_b, b_near),
            Transform(shadow_a, shadow_a_near),
            Transform(shadow_b, shadow_b_near),
            buildings.animate.set_opacity(0.10),
            window_glints.animate.set_opacity(0.10),
            rate_func=smooth,
        )

        gaze_path = Line(
            person_a[0].get_center() + RIGHT * 0.14,
            person_b[0].get_center() + LEFT * 0.14,
            color=ACCENT_LAVENDER,
            stroke_width=4.0,
        )
        gaze_glow = gaze_path.copy().set_stroke(ACCENT_LAVENDER, width=10, opacity=0.18)
        spark = Dot(gaze_path.get_start(), radius=0.075, color=ACCENT_MINT)
        self.play(Create(gaze_glow), Create(gaze_path), run_time=0.38, rate_func=linear)
        elapsed += 0.38
        self.play(MoveAlongPath(spark, gaze_path), run_time=0.42, rate_func=smooth)
        elapsed += 0.42

        pulse = Circle(radius=0.36, color=ACCENT_MINT, stroke_width=3.2).move_to(person_b[0].get_center())
        recognized = en_label("Recognized!", color=MATH_YELLOW, scale=0.74, bold=True)
        recognized.move_to(UP * 1.25)
        recognized_glow = recognized.copy().set_stroke(MATH_YELLOW, width=6, opacity=0.30).set_fill(opacity=0)
        self.play(
            GrowFromCenter(pulse),
            pulse.animate.scale(1.85).set_opacity(0),
            person_b[0].animate.scale(1.18),
            run_time=0.36,
            rate_func=smooth,
        )
        elapsed += 0.36
        self.play(
            FadeIn(recognized, scale=0.8),
            FadeIn(recognized_glow, scale=0.8),
            person_b[0].animate.scale(1 / 1.18),
            self.camera.frame.animate.scale(0.92).move_to(person_b.get_center()),
            run_time=max(0.2, seg_end(T, 0) - elapsed),
            rate_func=smooth,
        )
        elapsed = seg_end(T, 0)

        face_image = ImageMobject(FACE_PATH)
        face_image.height = 4.3
        face_image.move_to(ORIGIN)
        image_frame = RoundedRectangle(width=6.6, height=4.55, corner_radius=0.12, color=ACCENT_BLUE, stroke_width=1.5)
        image_frame.set_opacity(0.45)

        beat_to(
            T["segments"][1]["start"],
            FadeOut(gaze_glow),
            FadeOut(gaze_path),
            FadeOut(spark),
            FadeOut(pulse),
            FadeOut(recognized),
            FadeOut(recognized_glow),
            person_a.animate.set_opacity(0.62),
            person_b.animate.set_opacity(0.70),
            shadow_a.animate.set_opacity(0.14),
            shadow_b.animate.set_opacity(0.16),
            rate_func=smooth,
        )
        beat_to(
            seg_end(T, 1),
            FadeOut(person_a),
            FadeOut(person_b),
            FadeOut(shadow_a),
            FadeOut(shadow_b),
            FadeOut(buildings),
            FadeOut(window_glints),
            FadeOut(floor),
            self.camera.frame.animate.move_to(ORIGIN).set(width=config.frame_width),
            FadeIn(face_image),
            Create(image_frame),
        )

        landmark_points = [
            LEFT * 0.85 + UP * 0.55,
            LEFT * 0.35 + UP * 0.6,
            RIGHT * 0.35 + UP * 0.58,
            RIGHT * 0.85 + UP * 0.55,
            UP * 0.1,
            LEFT * 0.42 + DOWN * 0.58,
            RIGHT * 0.42 + DOWN * 0.58,
        ]
        landmarks = VGroup(*[Dot(p, radius=0.045, color=ACCENT_LAVENDER) for p in landmark_points])
        landmark_edges = VGroup(*[
            Line(landmarks[i].get_center(), landmarks[j].get_center(), color=ACCENT_LAVENDER, stroke_width=1.5).set_opacity(0.55)
            for i, j in [(0, 1), (1, 4), (4, 2), (2, 3), (4, 5), (4, 6), (5, 6)]
        ])
        teaser = VGroup(landmark_edges, landmarks)

        beat_to(
            T["segments"][2]["start"],
            LaggedStart(*[GrowFromCenter(d) for d in landmarks], Create(landmark_edges), lag_ratio=0.08),
            face_image.animate.set_opacity(0.86),
        )

        mini = mini_face(ACCENT_BLUE).scale(0.55).move_to(UP * 2.0)
        trunk = Line(UP * 1.22, UP * 0.6, color=ACCENT_BLUE, stroke_width=2)
        left_branch = Line(UP * 0.6, LEFT * 3.25 + UP * 0.6, color=ACCENT_CYAN, stroke_width=2)
        right_branch = Line(UP * 0.6, RIGHT * 3.25 + UP * 0.6, color=ACCENT_LAVENDER, stroke_width=2)
        two_branches = en_label("Two branches", color=MATH_YELLOW, scale=0.60, bold=True).move_to(UP * 2.85)

        beat_to(
            seg_end(T, 2),
            FadeOut(teaser),
            FadeOut(face_image),
            FadeOut(image_frame),
            FadeIn(mini, shift=DOWN * 0.08),
            Create(trunk),
            Create(left_branch),
            Create(right_branch),
            FadeIn(two_branches, shift=DOWN * 0.08),
        )

        left_card = RoundedRectangle(width=4.4, height=2.45, corner_radius=0.12, color=ACCENT_CYAN, stroke_width=1.6)
        left_card.move_to(LEFT * 3.2 + DOWN * 0.65)
        left_title = en_label("Verification 1:1", color=ACCENT_CYAN, scale=0.48, bold=True).move_to(left_card.get_top() + DOWN * 0.38)
        phone = VGroup(
            RoundedRectangle(width=0.78, height=1.35, corner_radius=0.11, color=ACCENT_TEAL, stroke_width=2),
            Circle(radius=0.18, color=ACCENT_MINT, stroke_width=2).shift(UP * 0.08),
            MathTex(r"\checkmark", color=ACCENT_MINT).scale(0.55).shift(UP * 0.08),
        ).move_to(left_card.get_center() + DOWN * 0.12)
        owner = en_label("phone owner?", color=TEXT_MUTED, scale=0.34).move_to(left_card.get_bottom() + UP * 0.32)

        beat_to(
            seg_end(T, 3),
            Create(left_card),
            FadeIn(left_title, shift=DOWN * 0.08),
            FadeIn(phone, shift=UP * 0.08),
        )
        beat_to(
            seg_end(T, 4),
            FadeIn(owner, shift=UP * 0.05),
            Indicate(phone[2], color=ACCENT_MINT),
            left_card.animate.set_stroke(ACCENT_CYAN, width=2.4),
        )

        right_card = RoundedRectangle(width=4.4, height=2.45, corner_radius=0.12, color=ACCENT_LAVENDER, stroke_width=1.6)
        right_card.move_to(RIGHT * 3.2 + DOWN * 0.65)
        right_title = en_label("Identification 1:N", color=ACCENT_LAVENDER, scale=0.46, bold=True).move_to(right_card.get_top() + DOWN * 0.38)
        gallery = VGroup()
        for r in range(3):
            for c in range(5):
                item = mini_face(ACCENT_BLUE).scale(0.12)
                item.move_to(right_card.get_center() + LEFT * 1.1 + RIGHT * c * 0.55 + UP * (0.42 - r * 0.42))
                item.set_opacity(0.55)
                gallery.add(item)
        probe = mini_face(ACCENT_CYAN).scale(0.18).move_to(right_card.get_center() + LEFT * 1.65)
        ray = thin_arrow(
            probe.get_right() + RIGHT * 0.05,
            gallery[7].get_left() + LEFT * 0.05,
            color=ACCENT_CYAN,
            buff=0.05,
            stroke_width=2.4,
            max_tip_length_to_length_ratio=0.08,
        )

        beat_to(
            seg_end(T, 5),
            Create(right_card),
            FadeIn(right_title, shift=DOWN * 0.08),
            FadeIn(probe),
            LaggedStart(*[FadeIn(g) for g in gallery], lag_ratio=0.025),
        )

        target_ring = SurroundingRectangle(gallery[7], color=ACCENT_LAVENDER, buff=0.06, stroke_width=2.2)
        among = en_label("among millions", color=TEXT_MUTED, scale=0.33).move_to(right_card.get_bottom() + UP * 0.32)
        beat_to(
            seg_end(T, 6),
            Create(ray),
            Create(target_ring),
            FadeIn(among, shift=UP * 0.05),
            Indicate(gallery[7], color=ACCENT_LAVENDER),
        )

        final_box = RoundedRectangle(width=3.25, height=0.78, corner_radius=0.12, color=ACCENT_LAVENDER, stroke_width=2.2, fill_color=ACCENT_LAVENDER, fill_opacity=0.08)
        final_text = en_label("1:N Identification", color=ACCENT_LAVENDER, scale=0.5, bold=True)
        final_text.move_to(final_box.get_center())
        final_badge = VGroup(final_box, final_text)
        final_badge.move_to(DOWN * 2.55)

        beat_to(
            seg_end(T, 7),
            left_card.animate.set_opacity(0.26),
            left_title.animate.set_opacity(0.35),
            phone.animate.set_opacity(0.25),
            owner.animate.set_opacity(0.25),
            right_card.animate.set_stroke(ACCENT_LAVENDER, width=3.0),
            FadeIn(final_badge, shift=UP * 0.1),
        )
        beat_to(
            seg_end(T, 8),
            Indicate(final_badge, color=ACCENT_LAVENDER),
            right_title.animate.scale(1.04),
            target_ring.animate.set_stroke(ACCENT_LAVENDER, width=3.5),
        )

        tail = max(0.0, T["duration"] - elapsed - 0.33)
        if tail > 0.05:
            self.wait(tail)
