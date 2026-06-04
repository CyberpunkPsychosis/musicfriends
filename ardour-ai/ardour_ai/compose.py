"""EDM 作曲助手：把高层描述（调、和弦走向、小节数）变成 MIDI 轨。

定位（呼应 docs/workflow.md 的角色分工）：
  - AI 负责你的痛点 —— 节奏(鼓/groove) 与 和声(和弦/bass) 的脚手架
  - 旋律留给你（这里默认不生成主旋律）

所有函数返回 midi.MidiTrack，可直接 write_smf 成 .mid 拖进 FL / Ardour。
"""
from __future__ import annotations

from .commands import Note
from .midi import MidiTrack

# 音名 -> 八度内半音
_NOTE = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5,
         "F#": 6, "Gb": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11}

# GM 打击乐音符号
KICK, SNARE, CLAP, CHH, OHH, CRASH = 36, 38, 39, 42, 46, 49

# 三和弦/七和弦的半音叠加
_TRIAD = {"maj": [0, 4, 7], "min": [0, 3, 7],
          "maj7": [0, 4, 7, 11], "min7": [0, 3, 7, 10], "dom7": [0, 4, 7, 10]}


def note_number(name: str, octave: int) -> int:
    """音名+八度 -> MIDI 号。C4=60（中央 C）。"""
    return _NOTE[name] + (octave + 1) * 12


def chord_notes(root: str, octave: int, quality: str = "min7") -> list[int]:
    base = note_number(root, octave)
    return [base + iv for iv in _TRIAD[quality]]


def chords_track(progression: list[tuple[str, str]], octave: int = 4,
                 bars: int = 8, beats_per_bar: int = 4,
                 velocity: int = 80, name: str = "Chords") -> MidiTrack:
    """每小节铺一个和弦。progression 每项 = (根音, 和弦性质)，按小节循环。"""
    notes: list[Note] = []
    for bar in range(bars):
        root, qual = progression[bar % len(progression)]
        start = bar * beats_per_bar
        for pitch in chord_notes(root, octave, qual):
            notes.append(Note(pitch=pitch, start=float(start),
                              length=float(beats_per_bar), velocity=velocity))
    return MidiTrack(name=name, notes=notes, channel=0)


def bass_track(progression: list[tuple[str, str]], octave: int = 2,
               bars: int = 8, beats_per_bar: int = 4,
               velocity: int = 100, name: str = "Bass") -> MidiTrack:
    """每拍踩一下当前和弦根音的低音。"""
    notes: list[Note] = []
    for bar in range(bars):
        root, _ = progression[bar % len(progression)]
        pitch = note_number(root, octave)
        for beat in range(beats_per_bar):
            notes.append(Note(pitch=pitch, start=float(bar * beats_per_bar + beat),
                              length=0.9, velocity=velocity))
    return MidiTrack(name=name, notes=notes, channel=1)


def drums_four_on_floor(bars: int = 8, beats_per_bar: int = 4,
                        name: str = "Drums") -> MidiTrack:
    """经典 EDM 鼓：四踩底鼓 + 反拍开镲 + 2/4 拍军鼓拍手 + 16 分闭镲。"""
    notes: list[Note] = []

    def hit(pitch: int, start: float, vel: int, length: float = 0.25) -> None:
        notes.append(Note(pitch=pitch, start=start, length=length, velocity=vel))

    for bar in range(bars):
        b0 = bar * beats_per_bar
        for beat in range(beats_per_bar):
            hit(KICK, b0 + beat, 112)                 # 每拍底鼓
            hit(OHH, b0 + beat + 0.5, 70)             # 反拍开镲
        hit(CLAP, b0 + 1, 100)                        # 第 2 拍拍手
        hit(CLAP, b0 + 3, 100)                        # 第 4 拍拍手
        for i in range(beats_per_bar * 4):            # 16 分闭镲
            hit(CHH, b0 + i * 0.25, 55 if i % 2 else 75)
    return MidiTrack(name=name, notes=notes, channel=9)  # 鼓走 GM 通道 10(index 9)


def drum_buildup(bars: int = 1, beats_per_bar: int = 4, name: str = "Buildup") -> MidiTrack:
    """buildup 段：军鼓从 8 分逐步加密到 16/32 分，力度渐强（节奏痛点专用积木）。"""
    notes: list[Note] = []
    total_beats = bars * beats_per_bar
    # 分辨率随时间加密：前半 8 分，后半 16 分，最后一拍 32 分
    t = 0.0
    while t < total_beats:
        frac = t / total_beats
        step = 0.5 if frac < 0.5 else (0.25 if frac < 0.875 else 0.125)
        vel = int(60 + 60 * frac)  # 渐强 60 -> 120
        notes.append(Note(pitch=SNARE, start=round(t, 4), length=step * 0.9,
                          velocity=min(vel, 127)))
        t += step
    return MidiTrack(name=name, notes=notes, channel=9)


# 一个默认的 melodic-house/dubstep 走向：Fm7 - Dbmaj7 - Abmaj7 - Ebmaj7（vi-IV-I-V 感）
DEFAULT_PROGRESSION: list[tuple[str, str]] = [
    ("F", "min7"), ("Db", "maj7"), ("Ab", "maj7"), ("Eb", "maj7"),
]


# ============ 风格库 ============
# 每种风格定义：BPM、和弦走向、鼓型、bass 型。鼓/bass 型用下面的具名生成器。

def _drums_halftime(bars: int, beats_per_bar: int = 4, name: str = "Drums") -> MidiTrack:
    """半拍速鼓（future bass / dubstep 感）：底鼓在拍1，军鼓在拍3，16 分闭镲。"""
    notes: list[Note] = []

    def hit(p: int, s: float, v: int, ln: float = 0.25) -> None:
        notes.append(Note(pitch=p, start=s, length=ln, velocity=v))

    for bar in range(bars):
        b0 = bar * beats_per_bar
        hit(KICK, b0 + 0, 115)                       # 拍1 底鼓
        hit(SNARE, b0 + 2, 105)                      # 拍3 军鼓（半拍速）
        for i in range(beats_per_bar * 4):           # 16 分闭镲
            hit(CHH, b0 + i * 0.25, 50 if i % 2 else 70)
        hit(OHH, b0 + 2.5, 65)
    return MidiTrack(name=name, notes=notes, channel=9)


def _bass_offbeat(progression, octave=2, bars=8, beats_per_bar=4,
                  velocity=100, name="Bass") -> MidiTrack:
    """house 反拍 bass：每拍的「与」(+0.5) 上弹根音，弹跳感。"""
    notes: list[Note] = []
    for bar in range(bars):
        root, _ = progression[bar % len(progression)]
        pitch = note_number(root, octave)
        for beat in range(beats_per_bar):
            notes.append(Note(pitch=pitch, start=bar * beats_per_bar + beat + 0.5,
                              length=0.45, velocity=velocity))
    return MidiTrack(name=name, notes=notes, channel=1)


def _bass_halftime(progression, octave=2, bars=8, beats_per_bar=4,
                   velocity=110, name="Bass") -> MidiTrack:
    """半拍速 bass：每 2 拍一个长根音（dubstep/future bass 感）。"""
    notes: list[Note] = []
    for bar in range(bars):
        root, _ = progression[bar % len(progression)]
        pitch = note_number(root, octave)
        for half in range(0, beats_per_bar, 2):
            notes.append(Note(pitch=pitch, start=float(bar * beats_per_bar + half),
                              length=1.9, velocity=velocity))
    return MidiTrack(name=name, notes=notes, channel=1)


# style -> 配置。drums/bass 为 (生成器, 额外kwargs)
STYLES: dict[str, dict] = {
    "house": {
        "bpm": 124, "progression": DEFAULT_PROGRESSION,
        "drums": (drums_four_on_floor, {}),
        "bass": (_bass_offbeat, {}),
        "chord_octave": 4,
    },
    "future_bass": {
        "bpm": 150, "progression": [("F", "min7"), ("Ab", "maj7"),
                                    ("Eb", "maj7"), ("Db", "maj7")],
        "drums": (_drums_halftime, {}),
        "bass": (_bass_halftime, {}),
        "chord_octave": 4,
    },
    "dubstep": {
        "bpm": 140, "progression": [("F", "min"), ("C", "min"),
                                    ("Db", "maj"), ("Eb", "maj")],
        "drums": (_drums_halftime, {}),
        "bass": (_bass_halftime, {"octave": 1}),
        "chord_octave": 3,
    },
    "melodic": {  # 默认（之前的行为）
        "bpm": 140, "progression": DEFAULT_PROGRESSION,
        "drums": (drums_four_on_floor, {}),
        "bass": (bass_track, {}),
        "chord_octave": 4,
    },
}


# ============ 旋律（可选档：「给我一版引子」）============

# 自然小调音阶（相对根音的半音）
_MINOR_SCALE = [0, 2, 3, 5, 7, 8, 10]


def minor_scale_pitches(root: str, octave: int) -> list[int]:
    base = note_number(root, octave)
    return [base + s for s in _MINOR_SCALE]


def melody_track(progression, bars: int = 8, beats_per_bar: int = 4, octave: int = 5,
                 seed: int | None = None, velocity: int = 95,
                 name: str = "Melody (AI 引子)") -> MidiTrack:
    """在小调音阶上做加权随机游走生成主旋律引子。

    —— 这是「引子」，旋律最终是你的地盘（见 workflow 角色分工）。
    强拍倾向落在当前和弦音上；偶尔留白。seed 固定则结果可复现。
    """
    import random
    rng = random.Random(seed)
    notes: list[Note] = []
    for bar in range(bars):
        root, qual = progression[bar % len(progression)]
        scale = minor_scale_pitches(root, octave)
        chord = [note_number(root, octave) + iv for iv in _TRIAD.get(qual, _TRIAD["min"])]
        pos = 0.0
        while pos < beats_per_bar - 1e-6:
            dur = rng.choice([0.5, 0.5, 1.0, 1.0, 1.5])
            dur = min(dur, beats_per_bar - pos)
            on_strong = abs(pos - round(pos)) < 1e-6
            if rng.random() < 0.12:                      # 留白
                pos += dur
                continue
            if on_strong and rng.random() < 0.6:
                pitch = rng.choice(chord)                # 强拍落和弦音
            else:
                pitch = rng.choice(scale)
            notes.append(Note(pitch=pitch, start=bar * beats_per_bar + pos,
                              length=dur * 0.95, velocity=velocity))
            pos += dur
    return MidiTrack(name=name, notes=notes, channel=2)


# ============ 统一编排 ============

def build_arrangement(style: str = "melodic", bars: int = 8, with_melody: bool = False,
                      seed: int | None = None) -> tuple[list[MidiTrack], float]:
    """按风格组装多轨编排，返回 (tracks, bpm)。melody 默认关闭（你的地盘）。"""
    if style not in STYLES:
        raise ValueError(f"未知风格 {style!r}，可选：{', '.join(STYLES)}")
    cfg = STYLES[style]
    prog = cfg["progression"]
    drum_fn, drum_kw = cfg["drums"]
    bass_fn, bass_kw = cfg["bass"]

    tracks = [
        drum_fn(bars=bars, **drum_kw),
        chords_track(prog, octave=cfg["chord_octave"], bars=bars),
        bass_fn(prog, bars=bars, **bass_kw),
    ]
    if with_melody:
        tracks.append(melody_track(prog, bars=bars, seed=seed))
    return tracks, float(cfg["bpm"])
