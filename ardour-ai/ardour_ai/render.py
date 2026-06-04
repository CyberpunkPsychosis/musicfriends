"""MIDI → WAV 试听渲染器。

目的：把作曲层产出的 Note/MidiTrack 直接合成成可听的立体声 WAV，
让「AI 生成 → 你听 → 迭代」闭环，不必先导进 DAW 配音色。

- 直接吃我们的 Note 模型（零 MIDI 解析），核心仅依赖 numpy。
- 鼓轨（channel 9）按 GM 鼓号合成打击乐；其余轨加法合成 + ADSR。
- 这是**试听**音质（粗合成），不是成品音色 —— 成品仍在 FL/Ardour 里用你的音色做。
"""
from __future__ import annotations

import wave
from pathlib import Path

import numpy as np

from .midi import MidiTrack
from .compose import KICK, SNARE, CLAP, CHH, OHH, CRASH

SR = 44100


def _env(n: int, a: float, d: float, s: float, r: float) -> np.ndarray:
    """ADSR 包络（采样数 n）。"""
    ai, di, ri = int(a * SR), int(d * SR), int(r * SR)
    si = max(0, n - ai - di - ri)
    parts = [
        np.linspace(0, 1, ai, endpoint=False),
        np.linspace(1, s, di, endpoint=False),
        np.full(si, s),
        np.linspace(s, 0, ri, endpoint=False),
    ]
    env = np.concatenate(parts) if any(len(p) for p in parts) else np.zeros(n)
    if len(env) < n:
        env = np.pad(env, (0, n - len(env)))
    return env[:n]


def _pitched(freq: float, dur_s: float, vel: int) -> np.ndarray:
    """加法合成一个乐音：基频 + 几个泛音 + ADSR。"""
    n = max(1, int(dur_s * SR))
    t = np.arange(n) / SR
    sig = np.zeros(n)
    for mult, amp in ((1, 1.0), (2, 0.3), (3, 0.12), (4, 0.05)):
        sig += amp * np.sin(2 * np.pi * freq * mult * t)
    sig *= _env(n, 0.005, 0.08, 0.6, max(0.05, dur_s * 0.3))
    return sig * (vel / 127.0) * 0.25


def _drum(pitch: int, dur_s: float, vel: int) -> np.ndarray:
    """按 GM 鼓号合成打击乐。"""
    amp = vel / 127.0
    if pitch == KICK:
        n = int(0.18 * SR); t = np.arange(n) / SR
        f = 120 * np.exp(-t * 30) + 45            # 音高快速下滑
        sig = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 16)
        return sig * amp * 0.9
    if pitch in (SNARE, CLAP):
        n = int(0.16 * SR); t = np.arange(n) / SR
        noise = np.random.uniform(-1, 1, n) * np.exp(-t * 28)
        tone = np.sin(2 * np.pi * 180 * t) * np.exp(-t * 30) * 0.3
        return (noise + tone) * amp * 0.55
    if pitch in (CHH, OHH):
        decay = 60 if pitch == CHH else 12        # 闭镲短、开镲长
        n = int((0.05 if pitch == CHH else 0.3) * SR); t = np.arange(n) / SR
        return np.random.uniform(-1, 1, n) * np.exp(-t * decay) * amp * 0.3
    if pitch == CRASH:
        n = int(1.0 * SR); t = np.arange(n) / SR
        return np.random.uniform(-1, 1, n) * np.exp(-t * 3) * amp * 0.4
    # 未知鼓号：短噪声
    n = int(0.1 * SR); t = np.arange(n) / SR
    return np.random.uniform(-1, 1, n) * np.exp(-t * 30) * amp * 0.3


def render_tracks(tracks: list[MidiTrack], bpm: float, tail_s: float = 1.5) -> np.ndarray:
    """把多轨 Note 渲染成 stereo float 数组 [N,2]。"""
    beat = 60.0 / bpm
    # 估算总长
    end_beat = 0.0
    for tr in tracks:
        for nt in tr.notes:
            end_beat = max(end_beat, nt.start + nt.length)
    total = int((end_beat * beat + tail_s) * SR) + 1
    buf = np.zeros(total)

    for tr in tracks:
        is_drum = (tr.channel == 9)
        for nt in tr.notes:
            start = int(nt.start * beat * SR)
            if is_drum:
                seg = _drum(nt.pitch, nt.length * beat, nt.velocity)
            else:
                freq = 440.0 * 2 ** ((nt.pitch - 69) / 12.0)
                seg = _pitched(freq, nt.length * beat, nt.velocity)
            end = min(total, start + len(seg))
            buf[start:end] += seg[: end - start]

    # 归一化防削顶
    peak = float(np.max(np.abs(buf))) or 1.0
    buf = buf / peak * 0.89
    return np.column_stack([buf, buf])  # 简单单声道铺到立体声


def write_wav(path: str | Path, audio: np.ndarray) -> Path:
    """写 16-bit 立体声 WAV。audio: [N,2] float in [-1,1]。"""
    path = Path(path)
    data = np.clip(audio, -1, 1)
    pcm = (data * 32767).astype("<i2")
    with wave.open(str(path), "w") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    return path


def render_midi_file(in_path: str | Path, out_path: str | Path) -> Path:
    """渲染任意标准 .mid（用 mido 解析；mido 为可选依赖）。"""
    import mido
    mf = mido.MidiFile(str(in_path))
    bpm = 120.0
    for tr in mf.tracks:
        for m in tr:
            if m.type == "set_tempo":
                bpm = 60_000_000 / m.tempo
                break
    from .commands import Note
    tracks: list[MidiTrack] = []
    for ti, tr in enumerate(mf.tracks):
        notes, on = [], {}
        abs_tick = 0
        ch = 0
        for m in tr:
            abs_tick += m.time
            if m.type == "note_on" and m.velocity > 0:
                on[(m.channel, m.note)] = (abs_tick, m.velocity)
                ch = m.channel
            elif m.type in ("note_off",) or (m.type == "note_on" and m.velocity == 0):
                key = (m.channel, m.note)
                if key in on:
                    st, vel = on.pop(key)
                    beats = (abs_tick - st) / mf.ticks_per_beat
                    if beats > 0:
                        notes.append(Note(pitch=m.note,
                                          start=st / mf.ticks_per_beat,
                                          length=beats, velocity=vel))
        if notes:
            tracks.append(MidiTrack(name=f"t{ti}", notes=notes, channel=ch))
    return write_wav(out_path, render_tracks(tracks, bpm))


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="渲染 .mid 为可听 WAV")
    ap.add_argument("infile")
    ap.add_argument("-o", "--out", default=None)
    args = ap.parse_args()
    out = args.out or (Path(args.infile).with_suffix(".wav"))
    render_midi_file(args.infile, out)
    print(f"已渲染 -> {out}")
