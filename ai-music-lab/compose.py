#!/usr/bin/env python3
"""
AI 编曲概念验证 —— 对话驱动的算法作曲引擎 (proof of concept)

不依赖任何外部合成器：自己写加法合成 + ADSR 包络，直接输出可播放的 WAV。
后续可把 describe() 的参数接到聊天里：用户说"来点悲伤的/欢快的"，
就改 mood / tempo / scale，引擎实时出曲。

用法:
    python3 compose.py --mood chill   --out song.wav
    python3 compose.py --mood happy   --out song.wav
    python3 compose.py --mood sad     --out song.wav
"""
import argparse
import wave
import struct
import math
import random

SR = 44100  # 采样率


# ----------------------------- 乐理 -----------------------------
NOTE_BASE = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}

def note_freq(name, octave):
    """音名 -> 频率, A4=440Hz"""
    semitone = NOTE_BASE[name] + (octave - 4) * 12 - 9  # 相对 A4 的半音数
    return 440.0 * (2 ** (semitone / 12.0))

# 不同情绪对应的音阶(相对根音的半音) / 速度 / 和弦走向
MOODS = {
    "chill": {
        "tempo": 78, "root": ("A", 3),
        "scale": [0, 2, 3, 5, 7, 8, 10],            # A 自然小调
        # ii-style lo-fi 走向: Am7 - Dm7 - G7 - Cmaj7
        "progression": [[0, 3, 7, 10], [5, 8, 12, 15], [10, 14, 17, 19], [3, 7, 10, 14]],
        "wave": "soft",
    },
    "happy": {
        "tempo": 120, "root": ("C", 3),
        "scale": [0, 2, 4, 5, 7, 9, 11],            # C 大调
        # I - V - vi - IV  (经典流行走向)
        "progression": [[0, 4, 7, 11], [7, 11, 14, 17], [9, 12, 16, 19], [5, 9, 12, 16]],
        "wave": "bright",
    },
    "sad": {
        "tempo": 66, "root": ("D", 3),
        "scale": [0, 2, 3, 5, 7, 8, 10],            # D 小调
        "progression": [[0, 3, 7], [8, 12, 15], [5, 8, 12], [7, 10, 14]],
        "wave": "soft",
    },
}


# --------------------------- 合成 ---------------------------
def adsr(n, a=0.01, d=0.1, s=0.7, r=0.2):
    """生成长度 n 的 ADSR 包络"""
    env = [0.0] * n
    ai, di, ri = int(a * SR), int(d * SR), int(r * SR)
    for i in range(n):
        if i < ai:
            env[i] = i / max(ai, 1)
        elif i < ai + di:
            env[i] = 1 - (1 - s) * ((i - ai) / max(di, 1))
        elif i < n - ri:
            env[i] = s
        else:
            env[i] = s * (1 - (i - (n - ri)) / max(ri, 1))
    return env

def tone(freq, dur, amp=0.3, kind="soft"):
    """加法合成一个音：基频 + 若干泛音，略微失谐增加温暖感"""
    n = int(dur * SR)
    if kind == "bright":
        partials = [(1, 1.0), (2, 0.5), (3, 0.3), (4, 0.15)]
        env = adsr(n, a=0.005, d=0.06, s=0.6, r=0.15)
    else:  # soft
        partials = [(1, 1.0), (2, 0.25), (3, 0.08)]
        env = adsr(n, a=0.02, d=0.12, s=0.7, r=0.25)
    buf = [0.0] * n
    detune = 1.0 + random.uniform(-0.0015, 0.0015)
    for k, (mult, pamp) in enumerate(partials):
        f = freq * mult * detune
        w = 2 * math.pi * f / SR
        for i in range(n):
            buf[i] += pamp * math.sin(w * i)
    norm = sum(p for _, p in partials)
    for i in range(n):
        buf[i] = buf[i] / norm * amp * env[i]
    return buf

def add_into(track, src, start, pan=0.5):
    """把 src 混入立体声 track（[L],[R]），start 为起始采样点"""
    L, R = track
    for i, v in enumerate(src):
        j = start + i
        if j < len(L):
            L[j] += v * (1 - pan)
            R[j] += v * pan


# --------------------------- 作曲 ---------------------------
def compose(mood, bars=8, seed=None):
    if seed is not None:
        random.seed(seed)
    cfg = MOODS[mood]
    beat = 60.0 / cfg["tempo"]
    bar_len = beat * 4
    total = bar_len * bars
    n_total = int(total * SR) + SR
    track = ([0.0] * n_total, [0.0] * n_total)

    root_name, root_oct = cfg["root"]
    root_hz = note_freq(root_name, root_oct)

    def hz(semi, oct_shift=0):
        return root_hz * (2 ** ((semi + 12 * oct_shift) / 12.0))

    prog = cfg["progression"]
    for b in range(bars):
        t0 = b * bar_len
        chord = prog[b % len(prog)]

        # 1) 和弦铺底（pad）
        for semi in chord:
            add_into(track, tone(hz(semi, 1), bar_len, amp=0.10, kind=cfg["wave"]),
                     int(t0 * SR), pan=random.uniform(0.35, 0.65))

        # 2) 低音（每拍踩根音）
        for beat_i in range(4):
            bass = chord[0] - 12
            add_into(track, tone(hz(bass), beat * 0.9, amp=0.22, kind="soft"),
                     int((t0 + beat_i * beat) * SR), pan=0.5)

        # 3) 旋律（在音阶上做加权随机游走，落在和弦音上更稳）
        pos = 0.0
        scale = cfg["scale"]
        while pos < bar_len - 1e-6:
            dur = random.choice([beat * 0.5, beat * 0.5, beat, beat * 1.5])
            dur = min(dur, bar_len - pos)
            # 倾向于选当前和弦内的音
            if random.random() < 0.6:
                semi = random.choice(chord)
            else:
                semi = random.choice(scale) + random.choice([0, 12])
            if random.random() < 0.12:  # 偶尔留白
                pass
            else:
                add_into(track, tone(hz(semi, 1), dur, amp=0.18, kind=cfg["wave"]),
                         int((t0 + pos) * SR), pan=random.uniform(0.4, 0.6))
            pos += dur

    return track


# --------------------------- 输出 ---------------------------
def write_wav(track, path):
    L, R = track
    peak = max(1e-6, max(max(abs(x) for x in L), max(abs(x) for x in R)))
    g = 0.9 / peak  # 归一化防削顶
    with wave.open(path, "w") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        frames = bytearray()
        for i in range(len(L)):
            l = int(max(-1, min(1, L[i] * g)) * 32767)
            r = int(max(-1, min(1, R[i] * g)) * 32767)
            frames += struct.pack("<hh", l, r)
        w.writeframes(bytes(frames))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mood", default="chill", choices=list(MOODS))
    ap.add_argument("--bars", type=int, default=8)
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--out", default="song.wav")
    args = ap.parse_args()
    print(f"作曲中: mood={args.mood} bars={args.bars} seed={args.seed}")
    tr = compose(args.mood, bars=args.bars, seed=args.seed)
    write_wav(tr, args.out)
    print(f"已生成 -> {args.out}")
