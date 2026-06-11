#!/usr/bin/env python3
"""灵感输入管道：你的哼唱/弹奏 → 可编辑 MIDI + BPM/调性。

这是「旋律你主导」的进系统通道（docs/research-2026-06.md P0-4）：

    python hum2midi.py my_hum.wav                 # 转 MIDI + 报 BPM/调性
    python hum2midi.py my_hum.wav -o melody.mid   # 指定输出

产出的 .mid 可以：
  - 直接拖进 FL 精修（你的地盘）
  - 喂给符号层（../ardour-ai/）当旋律骨架
  - 原始 wav 同时可作 ace_step cover / MusicGen melody 的旋律条件

依赖（按需装，缺哪个提示哪个）：
  pip install basic-pitch   # Spotify 开源转录模型（哼唱/单音乐器→MIDI 的事实标准）
  pip install librosa       # BPM / 调性检测
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Krumhansl-Schmuckler 调性侧写（标准做法：chroma 与大/小调模板做相关）
_MAJOR_PROFILE = (6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88)
_MINOR_PROFILE = (6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17)
_NOTE_NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")


def _correlate(a: list[float], b: list[float]) -> float:
    """皮尔逊相关系数（不依赖 numpy，便于零依赖单测）。"""
    n = len(a)
    ma, mb = sum(a) / n, sum(b) / n
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    va = sum((x - ma) ** 2 for x in a) ** 0.5
    vb = sum((y - mb) ** 2 for y in b) ** 0.5
    if va == 0 or vb == 0:
        return 0.0
    return cov / (va * vb)


def estimate_key_from_chroma(chroma: list[float]) -> tuple[str, str]:
    """12 维 chroma 向量 -> (音名, "major"/"minor")。纯函数，无依赖。"""
    if len(chroma) != 12:
        raise ValueError("chroma 需要 12 维（C..B 的能量）")
    best = (-2.0, "C", "major")
    for shift in range(12):
        rotated = chroma[shift:] + chroma[:shift]
        for profile, mode in ((_MAJOR_PROFILE, "major"), (_MINOR_PROFILE, "minor")):
            score = _correlate(list(profile), rotated)
            if score > best[0]:
                best = (score, _NOTE_NAMES[shift], mode)
    return best[1], best[2]


def detect_bpm_key(audio_path: str) -> tuple[float, str, str]:
    """音频 -> (BPM, 音名, 调式)。需要 librosa。"""
    try:
        import librosa
    except ImportError as e:
        raise RuntimeError("缺少依赖：pip install librosa") from e

    y, sr = librosa.load(audio_path, mono=True)
    tempo = librosa.feature.tempo(y=y, sr=sr)
    bpm = float(tempo[0]) if hasattr(tempo, "__len__") else float(tempo)
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr).mean(axis=1)
    note, mode = estimate_key_from_chroma([float(v) for v in chroma])
    return bpm, note, mode


def hum_to_midi(audio_path: str, out_mid: str | None = None) -> str:
    """哼唱/单音乐器音频 -> .mid。需要 basic-pitch。"""
    try:
        from basic_pitch.inference import predict
        from basic_pitch import ICASSP_2022_MODEL_PATH
    except ImportError as e:
        raise RuntimeError("缺少依赖：pip install basic-pitch") from e

    _, midi_data, _ = predict(audio_path, ICASSP_2022_MODEL_PATH)
    out = out_mid or str(Path(audio_path).with_suffix(".mid"))
    midi_data.write(out)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="哼唱 → MIDI + BPM/调性")
    ap.add_argument("audio", help="你的哼唱/弹奏录音（wav/mp3 等）")
    ap.add_argument("-o", "--out", help="输出 .mid 路径（默认同名 .mid）")
    ap.add_argument("--no-midi", action="store_true", help="只测 BPM/调性，不转 MIDI")
    args = ap.parse_args()

    try:
        bpm, note, mode = detect_bpm_key(args.audio)
        print(f"🎚  BPM ≈ {bpm:.0f}    调性 ≈ {note} {mode}")
    except RuntimeError as e:
        print(f"⚠️ BPM/调性检测跳过：{e}", file=sys.stderr)

    if not args.no_midi:
        try:
            out = hum_to_midi(args.audio, args.out)
            print(f"🎹  MIDI → {out}（拖进 FL，或作符号层旋律骨架）")
        except RuntimeError as e:
            print(f"⛔ {e}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
