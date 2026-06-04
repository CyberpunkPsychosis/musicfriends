"""段落重生成编排单测：用"假模型"把整条链路(模型→拼接)测通，不需要 key。"""
import sys
from pathlib import Path

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from providers import MusicProvider, MusicSpec, GenerationResult  # noqa: E402
from regenerate import (section_to_seconds, regenerate_and_splice,  # noqa: E402
                        DEFAULT_LAYOUT)
from splice import save_wav, load_wav  # noqa: E402

SR = 44100


def _tone(freq, secs, ch=2):
    t = np.arange(int(secs * SR)) / SR
    return np.column_stack([0.5 * np.sin(2 * np.pi * freq * t)] * ch)


class FakeProvider(MusicProvider):
    """假模型：把"重生成的一段"写成一个 880Hz 纯音文件。"""
    name = "fake"
    supports_inpaint = True

    def generate(self, spec):  # 抽象方法必须实现
        return self.regenerate_section(spec)

    def regenerate_section(self, spec: MusicSpec) -> GenerationResult:
        out = Path(spec.output_dir); out.mkdir(parents=True, exist_ok=True)
        dur = spec.region[1] - spec.region[0]
        p = out / "fake_section.wav"
        save_wav(p, SR, _tone(880, dur))
        return GenerationResult(self.name, spec, output_path=str(p))


def test_section_to_seconds_drop():
    # drop 在 bar8 起、8 小节；150 BPM 下每小节 1.6s
    start, end = section_to_seconds("drop", bpm=150)
    assert abs(start - 12.8) < 1e-6
    assert abs(end - 25.6) < 1e-6


def test_section_to_seconds_unknown():
    with pytest.raises(ValueError):
        section_to_seconds("chorus", bpm=120)


def test_full_orchestration_only_changes_region(tmp_path):
    # 原曲：220Hz 30 秒
    full = tmp_path / "song.wav"
    save_wav(full, SR, _tone(220, 30.0))
    out = tmp_path / "new.wav"

    result = regenerate_and_splice(
        FakeProvider(), str(full), start_s=12.8, end_s=25.6,
        prompt="new drop", out_path=str(out), out_dir=str(tmp_path / "gen"),
        crossfade_ms=20)

    _, orig = load_wav(full)
    _, new = load_wav(result)
    assert len(orig) == len(new)
    cf = int(0.02 * SR)
    a, b = int(12.8 * SR), int(25.6 * SR)
    # 区间外逐样本不变
    np.testing.assert_array_equal(orig[:a - cf], new[:a - cf])
    np.testing.assert_array_equal(orig[b + cf:], new[b + cf:])
    # 区间内已变
    assert not np.array_equal(orig[a:b], new[a:b])


def test_orchestration_errors_on_url_only(tmp_path):
    """模型只回 URL（没下成文件）时应明确报错。"""
    full = tmp_path / "s.wav"
    save_wav(full, SR, _tone(220, 5.0))

    class UrlProvider(FakeProvider):
        name = "urlonly"
        def regenerate_section(self, spec):
            return GenerationResult(self.name, spec, url="http://x/y.wav")

    with pytest.raises(RuntimeError):
        regenerate_and_splice(UrlProvider(), str(full), 1.0, 2.0, "x",
                              out_path=str(tmp_path / "o.wav"))


def test_default_layout_matches_song_structure():
    """布局应与 ardour-ai/song.py 的默认结构一致（镜像不能漂）。"""
    sys.path.insert(0, str(ROOT.parent / "ardour-ai"))
    from ardour_ai import song
    expected = {}
    bar = 0
    for s in song.DEFAULT_STRUCTURE:
        expected[s.name] = (bar, s.bars)
        bar += s.bars
    assert DEFAULT_LAYOUT == expected
