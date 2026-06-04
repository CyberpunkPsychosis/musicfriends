"""SMF 写入器单测：用 mido 回读，验证生成的 .mid 真实合法且内容正确。

mido 是独立实现，能解析说明我们的字节流是标准 SMF（FL/Ardour 也就能读）。
"""
import mido
import pytest

from ardour_ai.commands import Note
from ardour_ai.midi import write_smf, MidiTrack, _vlq, PPQ
from ardour_ai import compose


def test_vlq_encoding():
    assert _vlq(0) == b"\x00"
    assert _vlq(127) == b"\x7F"
    assert _vlq(128) == b"\x81\x00"
    assert _vlq(0x3FFF) == b"\xFF\x7F"


def test_smf_roundtrip_tempo_and_notes(tmp_path):
    track = MidiTrack(name="Lead", notes=[
        Note(pitch=60, start=0.0, length=1.0, velocity=100),
        Note(pitch=64, start=1.0, length=1.0, velocity=90),
        Note(pitch=67, start=2.0, length=2.0, velocity=80),
    ])
    p = write_smf(tmp_path / "x.mid", [track], bpm=120)

    mf = mido.MidiFile(p)
    assert mf.ticks_per_beat == PPQ
    # 速度：120 BPM -> 500000 微秒/四分音符
    tempos = [m.tempo for tr in mf.tracks for m in tr if m.type == "set_tempo"]
    assert tempos and tempos[0] == 500000

    # 收集 note_on（velocity>0）
    note_ons = [(m.note, m.velocity) for tr in mf.tracks for m in tr
                if m.type == "note_on" and m.velocity > 0]
    assert (60, 100) in note_ons
    assert (64, 90) in note_ons
    assert (67, 80) in note_ons


def test_note_durations_in_ticks(tmp_path):
    track = MidiTrack(name="t", notes=[Note(pitch=60, start=0.0, length=1.0)])
    p = write_smf(tmp_path / "d.mid", [track], bpm=120)
    mf = mido.MidiFile(p)
    # 找到乐器轨，累计 tick，确认音符时值 = 1 拍 = PPQ tick
    inst = mf.tracks[1]
    on_t = off_t = None
    t = 0
    for m in inst:
        t += m.time
        if m.type == "note_on" and m.velocity > 0:
            on_t = t
        elif (m.type == "note_off") or (m.type == "note_on" and m.velocity == 0):
            off_t = t
    assert off_t - on_t == PPQ


def test_drum_track_on_channel_9(tmp_path):
    dr = compose.drums_four_on_floor(bars=1)
    assert dr.channel == 9
    p = write_smf(tmp_path / "drums.mid", [dr], bpm=140)
    mf = mido.MidiFile(p)
    channels = {m.channel for tr in mf.tracks for m in tr
                if m.type in ("note_on", "note_off")}
    assert channels == {9}


def test_compose_progression_lengths():
    prog = compose.DEFAULT_PROGRESSION
    ch = compose.chords_track(prog, bars=4)
    # 4 小节，每小节一个 min7/maj7（4 音）-> 16 个音
    assert len(ch.notes) == 16
    bass = compose.bass_track(prog, bars=4)
    # 4 小节 x 4 拍 = 16 个低音
    assert len(bass.notes) == 16


def test_buildup_gets_denser():
    """buildup 后半的音符间隔应比前半更密。"""
    bu = compose.drum_buildup(bars=2)
    starts = sorted(n.start for n in bu.notes)
    gaps = [b - a for a, b in zip(starts, starts[1:])]
    first_gap = gaps[0]
    last_gap = gaps[-1]
    assert last_gap < first_gap  # 越往后越密
