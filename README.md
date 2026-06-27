# EBGM | Elastic Bunch Graph Matching (Manim visualization)

Đồ án cá nhân · CSC14006 Nhận dạng mẫu.
Trực quan hóa thuật toán **Elastic Bunch Graph Matching (EBGM)** cho nhận dạng khuôn mặt
bằng thư viện [Manim Community](https://www.manim.community/).

- **Thuật toán:** Elastic Bunch Graph Matching (EBGM).
- **Nguồn sách của môn học:** *Handbook of Face Recognition (2nd Edition)* - Stan Z. Li & Anil K. Jain (eds.),
  Springer, 2011 - chương về *Elastic Bunch Graph Matching / Gabor-jet face representations*.
  (Thuật toán cũng được nhắc trong *Handbook of Biometrics*.)
- **Bài báo gốc:** L. Wiskott, J.-M. Fellous, N. Krüger, C. von der Malsburg,
  *"Face Recognition by Elastic Bunch Graph Matching"*, IEEE Transactions on Pattern
  Analysis and Machine Intelligence (IEEE TPAMI), vol. 19, no. 7, pp. 775–779, 1997.
- **Video:** xem `url.txt` (cùng cấp với thư mục `source/`).

## Thông tin sinh viên

| | |
|---|---|
| **Họ và tên** | Bàng Mỹ Linh |
| **MSSV** | 23122009 |
| **Môn học** | CSC14006 - Nhận dạng |
| **Email** | 23122009@student.hcmus.edu.vn |

---

## 1. Cấu trúc thư mục

```
source/
├── README.md            <- file này
├── requirements.txt     <- thư viện Python cần cài
├── assets/              <- ảnh khuôn mặt / hình minh họa các scene nạp vào
└── ebgm/                <- project Manim (chạy từ trong đây)
    ├── _common.py       <- palette, helper, timing, phụ đề dùng chung
    ├── render.sh        <- render toàn bộ scene rồi ghép thành video
    ├── transcribe_audio.py  <- (tuỳ chọn) tạo lại timestamp phụ đề từ audio
    ├── audio/
    │   ├── _scenes_en.json      <- lời thuyết minh sạch (để TTS lại nếu cần)
    │   └── en/
    │       ├── scene_01..16.mp3 <- giọng đọc (ElevenLabs "Jessica")
    │       └── transcript.json  <- timestamp từng từ/câu → driver của phụ đề
    └── release/
        └── scene_S00..S16_*.py  <- 17 scene tạo nên video
```

Đường dẫn được tính tương đối trong `_common.py`, nên **không cần sửa path** - chỉ cần
giữ nguyên cấu trúc trên và chạy lệnh từ thư mục `ebgm/`.

---

## 2. Yêu cầu hệ thống

Cần 3 thứ: **Python 3.10–3.11 + Manim**, **ffmpeg**, và **một bản LaTeX**
(vì mọi nhãn/công thức dùng `Tex`/`MathTex`). Chọn 1 trong 2 cách tạo môi trường
Python (conda **hoặc** venv), rồi cài thêm ffmpeg + LaTeX theo hệ điều hành.

### 2a. Môi trường Python - cách A: conda (khuyến nghị)

```bash
conda create -n ebgm python=3.11 -y
conda activate ebgm
pip install -r requirements.txt
# Tiện lợi: conda cài luôn được ffmpeg + LaTeX, không cần bước 2c
conda install -c conda-forge ffmpeg texlive-core -y
```

### 2b. Môi trường Python - cách B: venv (pip thuần)

```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows (PowerShell):
#   .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2c. ffmpeg + LaTeX theo hệ điều hành (bỏ qua nếu đã dùng conda ở 2a)

**Ubuntu / Debian (Linux):**
```bash
sudo apt update
sudo apt install -y ffmpeg texlive texlive-latex-extra texlive-fonts-extra dvisvgm
```

**macOS** (dùng [Homebrew](https://brew.sh)):
```bash
brew install ffmpeg
brew install --cask mactex          # bản LaTeX đầy đủ (~4GB)
# hoặc gọn hơn: brew install --cask basictex   (rồi: sudo tlmgr install standalone preview dvisvgm)
```

**Windows:**
```powershell
# Dùng winget hoặc Chocolatey:
winget install Gyan.FFmpeg
winget install MiKTeX.MiKTeX
# (Choco: choco install ffmpeg miktex -y)
```
> MiKTeX sẽ tự hỏi cài thêm gói LaTeX còn thiếu trong lần render đầu - chọn "Install".
> Đảm bảo `ffmpeg` và `latex` nằm trong PATH (mở terminal mới sau khi cài).

Kiểm tra nhanh đã cài đủ:
```bash
python -c "import manim, numpy, PIL; print('python deps OK')"
ffmpeg -version | head -1
latex --version | head -1
```

---

## 3. Render video

Vào thư mục project rồi chạy script:

```bash
cd ebgm
chmod +x render.sh

./render.sh h     # 1080p60 (mặc định)
./render.sh k     # 2160p60 (4K - chậm, dùng khi cần bản chất lượng cao)
./render.sh l     # 480p15  (preview nhanh khi chỉnh sửa)
```

Script sẽ:
1. Render lần lượt 17 scene (`S00`->`S16`) - bỏ qua scene nào đã render mới hơn source.
2. Ghép các clip (audio đã nhúng sẵn trong từng scene qua `add_sound`) thành
   `EBGM_EN_<độ phân giải>.mp4` ngay trong `ebgm/`.

Render một scene đơn lẻ để xem nhanh:

```bash
manim -qh --disable_caching release/scene_S03_pre_deeplearning.py S03_PreDL
```

> **Windows:** `render.sh` là script bash. Chạy nó qua **Git Bash** hoặc **WSL**.
> Nếu dùng PowerShell/CMD thuần, render từng scene bằng lệnh `manim ...` ở trên
> (lặp cho `scene_S00..S16`), rồi ghép thủ công bằng ffmpeg concat - hoặc đơn giản
> nhất là render trong Git Bash/WSL.

---

## 4. Thứ tự & nội dung scene

| Scene | File | Nội dung |
|------|------|----------|
| S00 | scene_S00_intro | Tiêu đề mở đầu |
| S01 | scene_S01_cold_open | Bài toán: verification 1:1 vs identification 1:N |
| S02 | scene_S02_why_hard | Vì sao khó: intra-class variance |
| S03 | scene_S03_pre_deeplearning | Bối cảnh trước deep learning · IEEE TPAMI 1997 |
| S04 | scene_S04_idea | Ba trụ cột: Image Graph · Jet · Bunch Graph |
| S05 | scene_S05_gabor | Gabor wavelet |
| S06 | scene_S06_jet | Gabor jet (40 hệ số phức) |
| S07 | scene_S07_similarity | Độ tương đồng biên độ vs pha |
| S08 | scene_S08_image_graph | Image graph (đỉnh = jet, cạnh = Δx) |
| S09 | scene_S09_bunch_graph | Face Bunch Graph |
| S10 | scene_S10_graph_sim | Hàm mục tiêu so khớp đồ thị |
| S11 | scene_S11_elastic | Elastic graph matching (lõi thuật toán) |
| S12 | scene_S12_recognition | Bước nhận dạng |
| S13 | scene_S13_feret | Kết quả FERET |
| S14 | scene_S14_phase_speed | Vai trò của pha · hiệu năng |
| S15 | scene_S15_big_picture | Bức tranh tổng quát |
| S16 | scene_S16_conclusion | Kết luận |
