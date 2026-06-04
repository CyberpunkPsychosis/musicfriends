"""段落级模块化：整首歌 = 一串段落(intro/buildup/drop/break)，可单独重做某一段。

这是"灵活"的关键：重做 buildup 时，只有 buildup 那段的音符变，其它段一个音不动。
每段带自己的 seed —— 改 seed 重建即得到新内容，而其它段因 seed 不变而逐字节相同。

段落的"能量"由 kind 决定：
  intro  : 和弦铺底 + 轻底鼓
  buildup: 军鼓滚奏渐密渐强（节奏痛点专用）
  drop   : 满编(风格鼓 + bass + 和弦 + 可选旋律)
  break  : 和弦 + bass，无鼓
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field

from .commands import Note
from .midi import MidiTrack
from . import compose

BEATS_PER_BAR = 4


@dataclass
class Section:
    name: str             # 唯一标签，如 "drop1"
    kind: str             # intro / buildup / drop / break
    bars: int = 4
    seed: int | None = None


def _offset(track: MidiTrack, beats: float) -> MidiTrack:
    """整轨在时间上平移 beats 拍（用于把段落放到它在歌里的位置）。"""
    return MidiTrack(name=track.name, channel=track.channel,
                     notes=[Note(n.pitch, n.start + beats, n.length, n.velocity)
                            for n in track.notes])


def _light_kick(bars: int, name: str = "Drums") -> MidiTrack:
    notes = [Note(compose.KICK, b * BEATS_PER_BAR, 0.25, 90) for b in range(bars)]
    return MidiTrack(name=name, notes=notes, channel=9)


def _buildup_with_seed(bars: int, seed: int | None, name: str = "Drums") -> MidiTrack:
    """带变化的 buildup：基础滚奏 + 由 seed 决定的 ghost 闭镲，改 seed 就换花样。"""
    base = compose.drum_buildup(bars=bars, name=name)
    rng = random.Random(seed)
    for b in range(bars * BEATS_PER_BAR):
        if rng.random() < 0.4:
            base.notes.append(Note(compose.CHH, b * 1.0 + 0.5, 0.2,
                                   rng.choice([40, 55, 70])))
    return base


def section_tracks(section: Section, style: str, with_melody: bool) -> list[MidiTrack]:
    """生成某段的轨道（局部时间从 0 拍起），名字按角色统一以便跨段合并。"""
    cfg = compose.STYLES[style]
    prog = cfg["progression"]
    bars = section.bars
    drum_fn, drum_kw = cfg["drums"]
    bass_fn, bass_kw = cfg["bass"]
    k = section.kind

    tracks: list[MidiTrack] = []
    if k == "intro":
        tracks += [compose.chords_track(prog, octave=cfg["chord_octave"], bars=bars),
                   _light_kick(bars)]
    elif k == "buildup":
        tracks += [_buildup_with_seed(bars, section.seed),
                   compose.chords_track(prog, octave=cfg["chord_octave"], bars=bars)]
    elif k == "drop":
        tracks += [drum_fn(bars=bars, **drum_kw),
                   compose.chords_track(prog, octave=cfg["chord_octave"], bars=bars),
                   bass_fn(prog, bars=bars, **bass_kw)]
        if with_melody:
            tracks.append(compose.melody_track(prog, bars=bars, seed=section.seed))
    elif k == "break":
        tracks += [compose.chords_track(prog, octave=cfg["chord_octave"], bars=bars),
                   bass_fn(prog, bars=bars, **bass_kw)]
    else:
        raise ValueError(f"未知段落类型 {k!r}（intro/buildup/drop/break）")
    return tracks


def build_song(sections: list[Section], style: str = "melodic",
               with_melody: bool = True) -> tuple[list[MidiTrack], float, list[dict]]:
    """把段落按顺序拼成整首。返回 (合并后的轨道, bpm, 段落布局)。"""
    merged: dict[tuple[str, int], MidiTrack] = {}
    layout: list[dict] = []
    bar_cursor = 0
    for sec in sections:
        beats = bar_cursor * BEATS_PER_BAR
        for tr in section_tracks(sec, style, with_melody):
            shifted = _offset(tr, beats)
            key = (tr.name, tr.channel)
            if key not in merged:
                merged[key] = MidiTrack(name=tr.name, channel=tr.channel, notes=[])
            merged[key].notes.extend(shifted.notes)
        layout.append({"name": sec.name, "kind": sec.kind,
                       "start_bar": bar_cursor, "bars": sec.bars})
        bar_cursor += sec.bars
    return list(merged.values()), float(compose.STYLES[style]["bpm"]), layout


def regenerate_section(sections: list[Section], target: str, new_seed: int,
                       style: str = "melodic", with_melody: bool = True):
    """只重做名为 target 的段：返回 (整首新轨道, bpm, 仅该段的轨道, 该段起始拍)。

    仅 target 段内容变化；其它段 seed 不变 → 逐字节相同。
    "仅该段的轨道" 可单独写成 .mid，拖进 DAW 替换那一段。
    """
    if not any(s.name == target for s in sections):
        raise ValueError(f"没有名为 {target!r} 的段落")
    new_sections = [
        Section(s.name, s.kind, s.bars, new_seed if s.name == target else s.seed)
        for s in sections
    ]
    full, bpm, layout = build_song(new_sections, style, with_melody)

    start_bar = next(L["start_bar"] for L in layout if L["name"] == target)
    sec_obj = next(s for s in new_sections if s.name == target)
    section_only = section_tracks(sec_obj, style, with_melody)  # 局部时间从 0 起
    return full, bpm, section_only, start_bar * BEATS_PER_BAR


# 一个默认歌曲结构（可改）
DEFAULT_STRUCTURE: list[Section] = [
    Section("intro", "intro", bars=4, seed=1),
    Section("buildup", "buildup", bars=4, seed=2),
    Section("drop", "drop", bars=8, seed=3),
    Section("break", "break", bars=4, seed=4),
    Section("drop2", "drop", bars=8, seed=5),
]
