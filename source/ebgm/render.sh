#!/usr/bin/env bash
# Render every scene then concatenate into the final video.
#
# Usage:
#   ./render.sh h     # 1080p60  (default)
#   ./render.sh k     # 2160p60  (4K, slow on CPU)
#   ./render.sh l     # 480p15   (fast preview)
#
# Requires Manim Community v0.20.x and ffmpeg on PATH (see README.md).
set -e
cd "$(dirname "$0")"

Q="${1:-h}"
case "$Q" in
  l) RES="480p15"  ;;
  m) RES="720p30"  ;;
  h) RES="1080p60" ;;
  k) RES="2160p60" ;;
  *) echo "Unknown quality '$Q' (use l|m|h|k)"; exit 1 ;;
esac

# scene_file : ManimClass  (order = final video order)
SCENES=(
  "scene_S00_intro.py:S00_Intro"
  "scene_S01_cold_open.py:S01_ColdOpen"
  "scene_S02_why_hard.py:S02_WhyHard"
  "scene_S03_pre_deeplearning.py:S03_PreDL"
  "scene_S04_idea.py:S04_Idea"
  "scene_S05_gabor.py:S05_Gabor"
  "scene_S06_jet.py:S06_Jet"
  "scene_S07_similarity.py:S07_Similarity"
  "scene_S08_image_graph.py:S08_ImageGraph"
  "scene_S09_bunch_graph.py:S09_BunchGraph"
  "scene_S10_graph_sim.py:S10_GraphSim"
  "scene_S11_elastic.py:S11_Elastic"
  "scene_S12_recognition.py:S12_Recognition"
  "scene_S13_feret.py:S13_Feret"
  "scene_S14_phase_speed.py:S14_PhaseSpeed"
  "scene_S15_big_picture.py:S15_BigPicture"
  "scene_S16_conclusion.py:S16_Conclusion"
)

CONCAT="concat.txt"; : > "$CONCAT"
for item in "${SCENES[@]}"; do
  file="release/${item%%:*}"
  cls="${item##*:}"
  stem="${item%%.py:*}"
  out="media/videos/${stem}/${RES}/${cls}.mp4"
  if [ -f "$out" ] && [ "$out" -nt "$file" ]; then
    echo "[skip ] $cls (up to date)"
  else
    echo "[render] $cls @ $RES ..."
    manim -q"${Q}" --disable_caching "$file" "$cls" >/dev/null
  fi
  echo "file '$(pwd)/$out'" >> "$CONCAT"
done

OUT="EBGM_EN_${RES}.mp4"
echo "=== concat -> $OUT ==="
# Audio is already embedded per-scene via add_sound; stream-copy concat.
ffmpeg -y -f concat -safe 0 -i "$CONCAT" -c copy "$OUT" 2>/dev/null \
  || ffmpeg -y -f concat -safe 0 -i "$CONCAT" -c:v libx264 -preset medium -crf 18 -c:a aac -b:a 192k "$OUT"
echo "DONE -> $OUT"
ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT"
