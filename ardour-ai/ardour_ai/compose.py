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
