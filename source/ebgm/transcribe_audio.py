"""STT 16 audio scene bằng faster-whisper large-v3-turbo → JSON (word-level timestamps).

Dùng để căn (sync) animation Manim theo từng câu/từ khi ghép sound.
Chạy:  conda run -n vid python transcribe_audio.py
Output: audio/en/transcript.json
"""
import json, glob, os, time
from faster_whisper import WhisperModel

AUDIO_DIR = "audio/en"
OUT = os.path.join(AUDIO_DIR, "transcript.json")
MODEL = "large-v3-turbo"

# CPU, int8 để nhanh & nhẹ RAM
model = WhisperModel(MODEL, device="cpu", compute_type="int8")

files = sorted(glob.glob(os.path.join(AUDIO_DIR, "scene_*.mp3")))
result = {"model": MODEL, "language": "en", "scenes": []}

for f in files:
    name = os.path.splitext(os.path.basename(f))[0]  # scene_01
    t0 = time.time()
    segments, info = model.transcribe(
        f, language="en", word_timestamps=True,
        vad_filter=True, beam_size=5,
    )
    segs, words, full = [], [], []
    for s in segments:
        segs.append({"start": round(s.start, 3), "end": round(s.end, 3),
                     "text": s.text.strip()})
        full.append(s.text.strip())
        for w in (s.words or []):
            words.append({"word": w.word.strip(),
                          "start": round(w.start, 3),
                          "end": round(w.end, 3)})
    dur = round(info.duration, 3)
    result["scenes"].append({
        "scene": name,
        "file": os.path.relpath(f),
        "duration": dur,
        "text": " ".join(full).strip(),
        "segments": segs,
        "words": words,
    })
    print(f"{name}: dur={dur:>6.1f}s  words={len(words):>3}  segs={len(segs):>2}  ({time.time()-t0:.1f}s)")

with open(OUT, "w") as fp:
    json.dump(result, fp, ensure_ascii=False, indent=2)

tot = sum(s["duration"] for s in result["scenes"])
print(f"\nWrote {OUT}  |  {len(result['scenes'])} scenes  |  total {int(tot)//60}:{int(tot)%60:02d}")
