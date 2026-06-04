"""风格库、旋律生成、编排 JSON 落地的单测（均不依赖 Ardour / API key）。"""
import pytest

from ardour_ai import compose
from ardour_ai.commands import Note
from ardour_ai.arrangement import arrangement_from_json, materialize


# ---- 风格库 ----

@pytest.mark.parametrize("style", list(compose.STYLES))
def test_each_style_builds_valid_arrangement(style):
    tracks, bpm = compose.build_arrangement(style=style, bars=4)
    assert bpm > 0
    assert len(tracks) >= 3                     # 至少 鼓/和弦/bass
    assert any(t.channel == 9 for t in tracks)  # 有鼓轨
    for t in tracks:
        for n in t.notes:
            assert 0 <= n.pitch <= 127          # Note 已校验，这里再确认


def test_styles_differ_in_tempo():
    bpms = {s: compose.build_arrangement(style=s, bars=2)[1] for s in compose.STYLES}
    assert bpms["house"] != bpms["future_bass"]  # 风格确实带来不同 BPM


def test_unknown_style_raises():
    with pytest.raises(ValueError):
        compose.build_arrangement(style="trance_xyz")


def test_halftime_drums_sparser_than_four_on_floor():
    four = compose.drums_four_on_floor(bars=1)
    half = compose._drums_halftime(bars=1)
    kicks_four = sum(1 for n in four.notes if n.pitch == compose.KICK)
    kicks_half = sum(1 for n in half.notes if n.pitch == compose.KICK)
    assert kicks_half < kicks_four              # 半拍速底鼓更少


# ---- 旋律 ----

def test_melody_in_scale_and_deterministic():
    prog = compose.DEFAULT_PROGRESSION
    m1 = compose.melody_track(prog, bars=4, seed=42)
    m2 = compose.melody_track(prog, bars=4, seed=42)
    assert [(n.pitch, n.start) for n in m1.notes] == \
           [(n.pitch, n.start) for n in m2.notes]      # 同种子可复现
    assert len(m1.notes) > 0
    # 不同种子应（极大概率）不同
    m3 = compose.melody_track(prog, bars=4, seed=7)
    assert [n.pitch for n in m1.notes] != [n.pitch for n in m3.notes]


def test_melody_pitches_within_minor_scale():
    prog = [("A", "min7")]
    m = compose.melody_track(prog, bars=2, seed=1, octave=5)
    scale = set(p % 12 for p in compose.minor_scale_pitches("A", 5))
    # 旋律音（含和弦音）都应落在 A 小调音级里
    for n in m.notes:
        assert (n.pitch % 12) in scale


def test_arrangement_with_melody_adds_track():
    base, _ = compose.build_arrangement(style="melodic", bars=2, with_melody=False)
    mel, _ = compose.build_arrangement(style="melodic", bars=2, with_melody=True, seed=3)
    assert len(mel) == len(base) + 1


# ---- 编排 JSON 落地（我在对话里产出音符 → MIDI；不需要 key）----

def test_arrangement_from_json_ok():
    data = {"bpm": 128, "tracks": [
        {"name": "Lead", "channel": 2, "notes": [
            {"pitch": 60, "start": 0.0, "length": 1.0, "velocity": 100},
            {"pitch": 67, "start": 1.0, "length": 0.5},
        ]}]}
    tracks, bpm = arrangement_from_json(data)
    assert bpm == 128
    assert tracks[0].name == "Lead"
    assert len(tracks[0].notes) == 2
    assert tracks[0].notes[1].velocity == 100   # 默认 velocity


def test_arrangement_from_json_rejects_bad_pitch():
    data = {"bpm": 120, "tracks": [
        {"name": "x", "notes": [{"pitch": 999, "start": 0, "length": 1}]}]}
    with pytest.raises(ValueError):
        arrangement_from_json(data)


def test_arrangement_from_json_empty_raises():
    with pytest.raises(ValueError):
        arrangement_from_json({"bpm": 120, "tracks": []})


def test_materialize_writes_midi(tmp_path):
    data = {"bpm": 140, "tracks": [
        {"name": "Lead", "channel": 2,
         "notes": [{"pitch": 60, "start": 0.0, "length": 1.0}]}]}
    paths = materialize(data, tmp_path)
    names = {p.name for p in paths}
    assert "lead.mid" in names and "full.mid" in names
    assert all(p.exists() for p in paths)
