"""段落级模块化单测：核心是「重做一段，其它段一个音不动」。"""
import pytest

from ardour_ai import song
from ardour_ai.song import Section, build_song, regenerate_section, BEATS_PER_BAR


def _notes_in_bar_range(tracks, start_bar, bars):
    """取出落在 [start_bar, start_bar+bars) 小节内的音符（用于比较某段）。"""
    lo = start_bar * BEATS_PER_BAR
    hi = (start_bar + bars) * BEATS_PER_BAR
    out = []
    for t in tracks:
        for n in t.notes:
            if lo <= n.start < hi:
                out.append((t.name, n.pitch, round(n.start, 4), round(n.length, 4)))
    return sorted(out)


def test_song_spans_total_bars():
    tracks, bpm, layout = build_song(song.DEFAULT_STRUCTURE, style="melodic")
    total = sum(s.bars for s in song.DEFAULT_STRUCTURE)
    assert bpm > 0
    assert layout[-1]["start_bar"] + layout[-1]["bars"] == total
    last_beat = max(n.start for t in tracks for n in t.notes)
    assert last_beat < total * BEATS_PER_BAR


def test_regenerate_only_changes_target_section():
    structure = song.DEFAULT_STRUCTURE
    base, _, base_layout = build_song(structure, style="melodic")

    new_full, _, section_only, start_beats = regenerate_section(
        structure, target="buildup", new_seed=999, style="melodic")

    # 找到各段范围
    spans = {L["name"]: (L["start_bar"], L["bars"]) for L in base_layout}

    # 1) buildup 段应当变化
    bu_before = _notes_in_bar_range(base, *spans["buildup"])
    bu_after = _notes_in_bar_range(new_full, *spans["buildup"])
    assert bu_before != bu_after, "重做后 buildup 应有变化"

    # 2) 其它每一段都应逐字节相同
    for name in ("intro", "drop", "break", "drop2"):
        assert _notes_in_bar_range(base, *spans[name]) == \
               _notes_in_bar_range(new_full, *spans[name]), f"{name} 不应被改动"


def test_regenerate_returns_isolated_section_for_replace():
    """返回的"仅该段轨道"局部时间从 0 起，可单独写成 .mid 拖进去替换。"""
    full, bpm, section_only, start_beats = regenerate_section(
        song.DEFAULT_STRUCTURE, target="drop", new_seed=7, style="house")
    assert section_only and any(t.notes for t in section_only)
    assert min(n.start for t in section_only for n in t.notes) >= 0
    assert start_beats == 8 * BEATS_PER_BAR  # drop 在 intro(4)+buildup(4) 之后


def test_drums_track_is_continuous_across_sections():
    """同名 Drums 轨应跨段合并成一条连续轨，而非每段一条。"""
    tracks, _, _ = build_song(song.DEFAULT_STRUCTURE, style="melodic")
    drum_tracks = [t for t in tracks if t.name == "Drums"]
    assert len(drum_tracks) == 1


def test_unknown_target_raises():
    with pytest.raises(ValueError):
        regenerate_section(song.DEFAULT_STRUCTURE, target="nope", new_seed=1)
