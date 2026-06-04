"""渲染器单测：验证输出是合法、非静音、不削顶的立体声音频。

听感没法自动测，但「有声音、长度对、范围合法、无 NaN」可以测。
"""
import wave

import numpy as np
import pytest

from ardour_ai.commands import Note
from ardour_ai.midi import MidiTrack
from ardour_ai import compose
from ardour_ai.render import render_tracks, write_wav, SR


def test_render_pitched_is_audible():
    tr = MidiTrack(name="lead", notes=[
        Note(60, 0.0, 1.0, 100), Note(64, 1.0, 1.0, 100)])
    audio = render_tracks([tr], bpm=120)
    assert audio.ndim == 2 and audio.shape[1] == 2      # 立体声
    assert np.max(np.abs(audio)) > 0.1                  # 非静音
    assert np.max(np.abs(audio)) <= 1.0                 # 不削顶
    assert not np.isnan(audio).any()


def test_render_length_matches_tempo():
    # 4 拍 @ 120BPM = 2 秒 + tail
    tr = MidiTrack(name="t", notes=[Note(60, 0.0, 4.0, 100)])
    audio = render_tracks([tr], bpm=120, tail_s=1.0)
    seconds = audio.shape[0] / SR
    assert 2.9 < seconds < 3.2


def test_render_drums_audible():
    dr = compose.drums_four_on_floor(bars=1)
    audio = render_tracks([dr], bpm=140)
    assert np.max(np.abs(audio)) > 0.1


def test_write_wav_is_valid(tmp_path):
    tr = MidiTrack(name="t", notes=[Note(60, 0.0, 1.0, 100)])
    audio = render_tracks([tr], bpm=120)
    p = write_wav(tmp_path / "o.wav", audio)
    with wave.open(str(p)) as w:
        assert w.getnchannels() == 2
        assert w.getframerate() == SR
        assert w.getsampwidth() == 2
        assert w.getnframes() > 0


def test_full_arrangement_renders():
    prog = compose.DEFAULT_PROGRESSION
    tracks = [
        compose.drums_four_on_floor(bars=2),
        compose.chords_track(prog, bars=2),
        compose.bass_track(prog, bars=2),
    ]
    audio = render_tracks(tracks, bpm=140)
    assert np.max(np.abs(audio)) > 0.1
    assert not np.isnan(audio).any()
