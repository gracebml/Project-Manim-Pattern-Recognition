"""
Common configuration and helper functions for EBGM Video.
Toàn bộ text dùng LaTeX thuần (Latin Modern Roman) qua XeLaTeX.
"""

from manim import *
import numpy as np

# ============================================================
# COLOR PALETTE — Cool & Premium Tone
# ============================================================
BG_NAVY         = "#0D1B2A"   # Main background
BG_NAVY_SOFT    = "#1B263B"   # Panel/Card background

TEXT_PRIMARY    = "#E0E1DD"   # Main text color
TEXT_MUTED      = "#A9B4C2"   # Dimmed secondary text

# Accent colors (cool tone)
ACCENT_CYAN     = "#48CAE4"   # Main highlight cyan
ACCENT_TEAL     = "#76C5BF"   # Soft teal
ACCENT_BLUE     = "#778DA9"   # Secondary blue-grey
ACCENT_MINT     = "#95D5B2"   # Mint green for "Correct" / "Advantages"
ACCENT_LAVENDER = "#B8B5FF"   # Signature lavender for EBGM, Bunch Graph
ACCENT_CORAL    = "#E29578"   # Coral muted for "Wrong" / "Limitations"
MATH_YELLOW     = "#FFF056"   # Bright yellow for math formulas & explanations

# ============================================================
# LATEX TEMPLATE — XeLaTeX + Latin Modern (hỗ trợ tiếng Việt)
# ============================================================
VN_TEX_TEMPLATE = TexTemplate(
    tex_compiler="xelatex",
    output_format=".xdv",
    documentclass=r"\documentclass[preview]{standalone}",
    preamble=r"""
\usepackage{fontspec}
\usepackage{polyglossia}
\setdefaultlanguage{vietnamese}
\setmainfont{Latin Modern Roman}
\setsansfont{Latin Modern Sans}
\setmonofont{Latin Modern Mono}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{amsfonts}
\usepackage{mathtools}
\usepackage{unicode-math}
\setmathfont{Latin Modern Math}
"""
)

# ============================================================
# TEXT HELPERS — Mọi text đều qua LaTeX (Latin Modern Roman)
# ============================================================
def vn_tex(text_str, color=None, scale=1.0):
    """
    Render chuỗi bất kỳ (tiếng Việt hoặc Anh) qua XeLaTeX,
    font Latin Modern Roman. Trả về Tex mobject.
    """
    color = color or TEXT_PRIMARY
    obj = Tex(text_str, tex_template=VN_TEX_TEMPLATE, color=color)
    if scale != 1.0:
        obj.scale(scale)
    return obj

def vn_tex_bold(text_str, color=None, scale=1.0):
    """Bold variant."""
    color = color or TEXT_PRIMARY
    obj = Tex(r"\textbf{" + text_str + "}", tex_template=VN_TEX_TEMPLATE, color=color)
    if scale != 1.0:
        obj.scale(scale)
    return obj

def vn_tex_italic(text_str, color=None, scale=1.0):
    """Italic variant."""
    color = color or TEXT_PRIMARY
    obj = Tex(r"\textit{" + text_str + "}", tex_template=VN_TEX_TEMPLATE, color=color)
    if scale != 1.0:
        obj.scale(scale)
    return obj

def vn_tex_mono(text_str, color=None, scale=1.0):
    """Monospace variant (Latin Modern Mono)."""
    color = color or TEXT_PRIMARY
    obj = Tex(r"\texttt{" + text_str + "}", tex_template=VN_TEX_TEMPLATE, color=color)
    if scale != 1.0:
        obj.scale(scale)
    return obj

def vn_math(latex_str, color=None, scale=1.0):
    """MathTex with Vietnamese template."""
    color = color or MATH_YELLOW
    obj = MathTex(latex_str, tex_template=VN_TEX_TEMPLATE, color=color)
    if scale != 1.0:
        obj.scale(scale)
    return obj

# ============================================================
# SUBTITLE & TITLE HELPERS
# ============================================================
def make_subtitle(text_str, scale=0.55, color=None):
    """
    Phụ đề với viền bo tròn bán trong suốt ở mép dưới màn hình.
    Text bằng LaTeX (Latin Modern Roman).
    """
    # Subtitles are disabled for the release render. Keep returning an invisible
    # mobject so existing FadeIn/ReplacementTransform calls preserve timing.
    return VGroup(Dot(ORIGIN, radius=0.001, fill_opacity=0, stroke_opacity=0))

def section_title(text_str, color=None, scale=0.9):
    """Tiêu đề section — LaTeX bold."""
    color = color or ACCENT_CYAN
    return vn_tex_bold(text_str, color=color, scale=scale)

def cool_glow(mob, color=ACCENT_CYAN):
    """Adds a soft glowing duplicate outline to a mobject."""
    return mob.copy().set_stroke(color, width=8, opacity=0.3)

# ============================================================
# TECHNICAL COLORS & CONSTANTS FOR PART 2 (ALGORITHM DETAIL)
# ============================================================
GABOR_REAL    = "#48CAE4"   # cyan cho phần real của Gabor wavelet
GABOR_IMAG    = "#B8B5FF"   # lavender cho phần imaginary
JET_GLOW      = "#76C5BF"   # teal glow cho jet
GRID_LINE     = "#778DA9"   # blue-grey cho lưới grid mờ
HIGHLIGHT_HOT = "#FCBF49"   # vàng ấm RẤT THƯA THỚT, chỉ dùng nhấn mạnh focus điểm

# Math constants
FONT_MATH_SCALE = 0.8

# Font settings for Text Mobject
SUBTITLE_FONT   = "Be Vietnam Pro"
TITLE_FONT      = "EB Garamond"
MONO_FONT       = "JetBrains Mono"

# ============================================================
# PART 2 HELPERS
# ============================================================
def make_jet_visual(n_freq=5, n_orient=8, scale=1.0, color=GABOR_REAL):
    """
    Visualize jet: 40 wavelets xếp theo lưới (n_freq hàng x n_orient cột).
    Mỗi ô là 1 mini Gabor wavelet pattern.
    """
    grid = VGroup()
    for nu in range(n_freq):
        for mu in range(n_orient):
            kx = np.cos(mu * np.pi / n_orient)
            ky = np.sin(mu * np.pi / n_orient)
            freq = 0.5 + nu * 0.3
            wavelet = ParametricFunction(
                lambda t, kx=kx, freq=freq: np.array([
                    t * 0.3,
                    0.15 * np.sin(freq * t * 8) * np.exp(-(t**2)/0.5),
                    0
                ]),
                t_range=[-0.8, 0.8],
                color=color, stroke_width=1.2
            ).rotate(mu * np.pi / n_orient)
            wavelet.move_to([mu * 0.4 - 1.5, nu * 0.4 - 0.8, 0])
            grid.add(wavelet)
    return grid.scale(scale)

def make_face_graph_node(pos, jet_size=0.15, color=ACCENT_LAVENDER):
    """Một node trên image graph: chấm trung tâm + ring + mini jet."""
    return VGroup(
        Dot(pos, radius=0.06, color=color),
        Circle(radius=jet_size, color=color, stroke_width=1.5).move_to(pos),
    )

def vietnamese_label(text_str, scale=0.45, color=None):
    """Nhãn tiếng Việt nhỏ, dùng cho chú thích."""
    color = color or TEXT_MUTED
    return vn_tex(text_str, color=color, scale=scale)

# ============================================================
# REWORK HELPERS — audio timing + English labels + 3D utils
# ============================================================
import json
from pathlib import Path

EN_TEX_TEMPLATE = TexTemplate(
    tex_compiler="xelatex",
    output_format=".xdv",
    documentclass=r"\documentclass[preview]{standalone}",
    preamble=r"""
\usepackage{fontspec}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{amsfonts}
\usepackage{mathtools}
\usepackage{unicode-math}
\usepackage[HTML]{xcolor}
\setmainfont{Latin Modern Roman}
\setsansfont{Latin Modern Sans}
\setmonofont{Latin Modern Mono}
\setmathfont{Latin Modern Math}
\definecolor{accentcyan}{HTML}{48CAE4}
"""
)

FACE_PATH = str(Path(__file__).resolve().parent.parent / "assets" / "face.png")

_TRANSCRIPT = None

def load_scene_timing(scene_key):
    """scene_key vd 'scene_01'. Trả dict {duration, segments[], words[], audio_path}."""
    global _TRANSCRIPT
    if _TRANSCRIPT is None:
        p = Path(__file__).resolve().parent / "audio" / "en" / "transcript.json"
        with open(p, "r", encoding="utf-8") as f:
            _TRANSCRIPT = json.load(f)
    sc = next(s for s in _TRANSCRIPT["scenes"] if s["scene"] == scene_key)
    sc = dict(sc)
    sc["audio_path"] = str(Path(__file__).resolve().parent / "audio" / "en" / f"{scene_key}.mp3")
    return sc

def seg_end(timing, k):
    """Mốc kết thúc câu thứ k (0-indexed); k>=len → duration."""
    segs = timing["segments"]
    return segs[k]["end"] if k < len(segs) else timing["duration"]

def word_start(timing, substr):
    """Mốc bắt đầu của từ chứa substr (lowercase match) — để bật hiệu ứng đúng lúc đọc."""
    for w in timing["words"]:
        if substr.lower() in w["word"].lower():
            return w["start"]
    return None

# Global multiplier to enlarge ALL on-screen illustration labels at once.
# (Subtitles use Tex directly in add_subtitles, so they are NOT affected.)
LABEL_SCALE_BOOST = 1.12

def en_label(text_str, color=None, scale=0.5, bold=False):
    """Nhãn/chú thích ngắn tiếng Anh trên sơ đồ — LaTeX Latin Modern."""
    color = color or TEXT_PRIMARY
    body = (r"\textbf{%s}" % text_str) if bold else text_str
    return Tex(body, tex_template=EN_TEX_TEMPLATE, color=color).scale(scale * LABEL_SCALE_BOOST)

def label3d(text_str, color=None, scale=0.5):
    """Nhãn dùng trong ThreeDScene — luôn quay mặt về camera."""
    lbl = en_label(text_str, color, scale)
    return lbl

from manim import StealthTip

def thin_arrow(start, end, color=TEXT_PRIMARY, stroke_width=2.2, buff=0.08,
               tip_ratio=0.16, **kw):
    """Mũi tên đầu mảnh (StealthTip), nét gọn — dùng thay Arrow mặc định."""
    kw.setdefault("tip_shape", StealthTip)
    kw.setdefault("max_tip_length_to_length_ratio", tip_ratio)
    return Arrow(
        start,
        end,
        color=color,
        stroke_width=stroke_width,
        buff=buff,
        **kw,
    )

def thin_curved_arrow(start, end, color=TEXT_PRIMARY, stroke_width=2.2, **kw):
    kw.setdefault("tip_shape", StealthTip)
    a = CurvedArrow(start, end, color=color, stroke_width=stroke_width, **kw)
    a.tip.scale(0.7)
    return a


# ============================================================
# SUBTITLES — realtime captions synced to transcript segments
# Pure LaTeX (Latin Modern via EN_TEX_TEMPLATE). No Text()/font=.
# ============================================================
def _latex_escape(s):
    repl = {
        "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$",
        "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
        "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
    }
    return "".join(repl.get(c, c) for c in s)


def add_subtitles(scene, timing, scale=0.42, width_cm=11,
                  color=TEXT_PRIMARY, lead=0.05, hold=0.30):
    """Realtime subtitle track synced to `timing` (transcript segments).

    Pure LaTeX captions (Latin Modern). Auto-picks how to pin to the screen:
      - ThreeDScene        -> add_fixed_in_frame_mobjects
      - MovingCameraScene  -> follows the camera frame (zoom/pan safe)
      - plain Scene        -> static bottom strip
    Call ONCE right after `self.add_sound(...)`. Each segment fades in/out via
    opacity, driven by an updater clock that matches the audio timing.
    """
    segs = (timing or {}).get("segments", [])
    if not segs:
        return None

    is_3d = isinstance(scene, ThreeDScene)
    is_cam = (not is_3d) and isinstance(scene, MovingCameraScene)
    y0 = -3.62

    items = []
    for seg in segs:
        body = _latex_escape(seg["text"])
        tex = Tex(
            r"\parbox{%dcm}{\centering %s}" % (width_cm, body),
            tex_template=EN_TEX_TEMPLATE, color=color,
        ).scale(scale)
        bg = RoundedRectangle(
            width=max(0.6, tex.width + 0.5), height=tex.height + 0.30,
            corner_radius=0.10, stroke_width=0,
            fill_color=BG_NAVY, fill_opacity=0.0,
        ).move_to(tex.get_center())
        grp = VGroup(bg, tex).move_to([0, y0, 0])
        grp.base_height = grp.height
        tex.set_opacity(0)
        items.append((seg["start"], seg["end"], grp, bg, tex))

    track = VGroup(*[it[2] for it in items])
    track.set_z_index(200)
    if is_3d:
        scene.add_fixed_in_frame_mobjects(track)
    else:
        scene.add(track)

    base_h = config.frame_height
    state = {"t": 0.0}

    def upd(mob, dt):
        state["t"] += dt
        t = state["t"]
        cx, sub_y, k = 0.0, y0, 1.0
        if is_cam:
            fr = scene.camera.frame
            k = fr.height / base_h
            cx, cy, _ = fr.get_center()
            sub_y = cy - fr.height * 0.44
        for s, e, grp, bg, tex in items:
            on = (s - lead) <= t <= (e + hold)
            tex.set_opacity(1.0 if on else 0.0)
            bg.set_fill(BG_NAVY, opacity=0.55 if on else 0.0)
            if is_cam:
                grp.scale_to_fit_height(grp.base_height * k)
                grp.move_to([cx, sub_y, 0])

    track.add_updater(upd)
    return track
