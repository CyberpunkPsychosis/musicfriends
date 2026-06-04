"""音频拼接器单测：核心是「区间外逐样本不变，区间内被换掉」。"""
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from splice import splice_section, load_wav, save_wav, replace_region_in_file  # noqa: E402

SR = 44100


def _tone(freq, secs, ch=2):
    t = np.arange(int(secs * SR)) / SR
    sig = 0.5 * np.sin(2 * np.pi * freq * t)
    return np.column_stack([sig] * ch)


def test_outside_region_unchanged():
    full = _tone(220, 4.0)          # 原曲：A3
    new = _tone(880, 1.0)           # 新段：A5
    out = splice_section(full, SR, new, start_s=1.0, end_s=2.0, crossfade_ms=20)

    assert out.shape == full.shape
    cf = int(0.02 * SR)
    a, b = int(1.0 * SR), int(2.0 * SR)
    # 区间前（到交叉区之前）逐样本不变
    np.testing.assert_array_equal(out[:a - cf], full[:a - cf])
    # 区间后（交叉区之后）逐样本不变
    np.testing.assert_array_equal(out[b + cf:], full[b + cf:])


def test_region_center_is_new_content():
    full = _tone(220, 4.0)
    new = _tone(880, 1.0)
    out = splice_section(full, SR, new, 1.0, 2.0, crossfade_ms=20)
    mid = int(1.5 * SR)
    win = slice(mid - 200, mid + 200)
    # 中段应接近新内容(880Hz)，远离原内容(220Hz)
    assert np.corrcoef(out[win, 0], new[int(0.5 * SR) - 200:int(0.5 * SR) + 200, 0])[0, 1] > 0.9


def test_length_preserved_and_no_clip():
    full = _tone(220, 3.0)
    new = _tone(440, 5.0)           # 故意更长 -> 应裁到区间长
    out = splice_section(full, SR, new, 0.5, 1.5)
    assert len(out) == len(full)
    assert np.max(np.abs(out)) <= 1.0
    assert not np.isnan(out).any()


def test_short_section_padded():
    full = _tone(220, 3.0)
    new = _tone(440, 0.2)           # 比区间短 -> 补零
    out = splice_section(full, SR, new, 1.0, 2.0)
    assert len(out) == len(full)


def test_bad_region_raises():
    full = _tone(220, 2.0)
    with pytest.raises(ValueError):
        splice_section(full, SR, _tone(440, 1.0), 1.0, 1.0)  # end<=start


def test_file_roundtrip(tmp_path):
    save_wav(tmp_path / "full.wav", SR, _tone(220, 2.0))
    save_wav(tmp_path / "sec.wav", SR, _tone(660, 0.5))
    out = replace_region_in_file(tmp_path / "full.wav", tmp_path / "sec.wav",
                                 0.5, 1.0, tmp_path / "out.wav")
    sr, data = load_wav(out)
    assert sr == SR and len(data) == int(2.0 * SR)


def test_int16_roundtrip_is_lossless(tmp_path):
    """save→load 必须逐样本无损，否则区间外拼接会有 1-LSB 漂移。"""
    orig = _tone(220, 1.0)
    p = save_wav(tmp_path / "r.wav", SR, orig)
    _, back = load_wav(p)
    np.testing.assert_array_equal((np.clip(np.round(orig * 32768), -32768, 32767)),
                                  np.round(back * 32768))


def test_file_level_outside_region_unchanged(tmp_path):
    save_wav(tmp_path / "full.wav", SR, _tone(220, 3.0))
    save_wav(tmp_path / "sec.wav", SR, _tone(880, 1.0))
    out = replace_region_in_file(tmp_path / "full.wav", tmp_path / "sec.wav",
                                 1.0, 2.0, tmp_path / "o.wav", crossfade_ms=20)
    _, full = load_wav(tmp_path / "full.wav")
    _, sp = load_wav(out)
    cf = int(0.02 * SR)
    a, b = int(1.0 * SR), int(2.0 * SR)
    np.testing.assert_array_equal(full[:a - cf], sp[:a - cf])
    np.testing.assert_array_equal(full[b + cf:], sp[b + cf:])
