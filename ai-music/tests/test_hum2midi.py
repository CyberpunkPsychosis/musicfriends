"""灵感输入管道单测：调性估计纯函数（无依赖即可测）。

basic-pitch / librosa 属于"用户机器上装"的重依赖，转录与 BPM 检测
在本地冒烟；这里测的是不依赖它们的 Krumhansl-Schmuckler 调性逻辑。
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from hum2midi import estimate_key_from_chroma  # noqa: E402


def _chroma_for(pitch_classes: set[int], strong: float = 1.0) -> list[float]:
    return [strong if i in pitch_classes else 0.05 for i in range(12)]


def test_c_major_triad_scale():
    # C 大调音阶音级：C D E F G A B
    chroma = _chroma_for({0, 2, 4, 5, 7, 9, 11})
    note, mode = estimate_key_from_chroma(chroma)
    assert (note, mode) == ("C", "major")


def test_a_minor_emphasis():
    # 自然 a 小调，主音 A 显著加重（与 C 大调同音级，靠侧写权重区分）
    chroma = _chroma_for({0, 2, 4, 5, 7, 9, 11}, strong=0.8)
    chroma[9] = 2.0   # A
    chroma[4] = 1.2   # E（属音）
    note, mode = estimate_key_from_chroma(chroma)
    assert (note, mode) == ("A", "minor")


def test_transposition_consistency():
    # 把 C 大调集体移到 G：应识别为 G major
    c_major = {0, 2, 4, 5, 7, 9, 11}
    g_major = {(p + 7) % 12 for p in c_major}
    note, mode = estimate_key_from_chroma(_chroma_for(g_major))
    assert (note, mode) == ("G", "major")


def test_rejects_wrong_length():
    with pytest.raises(ValueError):
        estimate_key_from_chroma([1.0] * 11)
