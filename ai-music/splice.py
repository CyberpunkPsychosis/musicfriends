"""音频拼接器 —— 把"重新生成的一段"无缝换回原曲，其它部分一秒不动。

这是音频路的"段落模块化"核心（对应符号路的 song.regenerate_section）：
大模型只重生成 region 那一段（旋律条件 / inpainting），本模块负责把它
等功率交叉淡入淡出地拼回原曲。

只依赖 numpy（不渲染/不拼接就不用装）。WAV I/O 用标准库 wave。
"""
from __future__ import annotations

import wave
from pathlib import Path

import numpy as np


def load_wav(path: str | Path) -> tuple[int, np.ndarray]:
    """读 WAV -> (采样率, float32 [N,ch] in [-1,1])。"""
    with wave.open(str(path)) as w:
        sr = w.getframerate()
        ch = w.getnchannels()
        n = w.getnframes()
        raw = w.readframes(n)
    data = np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768.0
    return sr, data.reshape(-1, ch)


def save_wav(path: str | Path, sr: int, audio: np.ndarray) -> Path:
    path = Path(path)
    # 与 load_wav 的 /32768 对称：保证 int16→float→int16 逐样本无损，
    # 这样区间外的样本拼接后真的逐样本不变。
    pcm = np.clip(np.round(audio * 32768.0), -32768, 32767).astype("<i2")
    with wave.open(str(path), "w") as w:
        w.setnchannels(audio.shape[1] if audio.ndim == 2 else 1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())
    return path


def _fit(section: np.ndarray, n: int, ch: int) -> np.ndarray:
    """把新段裁剪/补零到正好 n 帧、ch 声道。"""
    if section.ndim == 1:
        section = section[:, None]
    if section.shape[1] != ch:                       # 声道数对齐
        section = (section.mean(axis=1, keepdims=True).repeat(ch, axis=1)
                   if ch > section.shape[1] else section[:, :ch])
    if len(section) >= n:
        return section[:n]
    return np.vstack([section, np.zeros((n - len(section), ch), section.dtype)])


def splice_section(full: np.ndarray, sr: int, new_section: np.ndarray,
                   start_s: float, end_s: float, crossfade_ms: float = 25.0) -> np.ndarray:
    """用 new_section 替换 full 的 [start_s, end_s) 区间，边界做等功率交叉淡化。

    返回与 full 等长的新音频；区间外（除交叉区）逐样本不变。
    """
    if end_s <= start_s:
        raise ValueError("end_s 必须大于 start_s")
    ch = full.shape[1]
    a = int(start_s * sr)
    b = min(len(full), int(end_s * sr))
    region_n = b - a
    if region_n <= 0:
        raise ValueError("区间超出音频范围")

    out = full.copy()
    sec = _fit(new_section, region_n, ch)

    cf = min(int(crossfade_ms / 1000 * sr), region_n // 2)
    if cf > 0:
        # 等功率交叉淡化曲线
        t = np.linspace(0, np.pi / 2, cf)[:, None]
        fin, fout = np.sin(t) ** 2, np.cos(t) ** 2
        # 头部：原 -> 新
        sec[:cf] = sec[:cf] * fin + out[a:a + cf] * fout
        # 尾部：新 -> 原
        sec[-cf:] = sec[-cf:] * fout + out[b - cf:b] * fin

    out[a:b] = sec
    return out


def replace_region_in_file(full_path: str | Path, section_path: str | Path,
                           start_s: float, end_s: float, out_path: str | Path,
                           crossfade_ms: float = 25.0) -> Path:
    """文件级便捷封装：原曲 + 新段文件 -> 拼好的新曲文件。"""
    sr, full = load_wav(full_path)
    sr2, sec = load_wav(section_path)
    if sr2 != sr:
        raise ValueError(f"采样率不一致：{sr} vs {sr2}（先重采样）")
    spliced = splice_section(full, sr, sec, start_s, end_s, crossfade_ms)
    return save_wav(out_path, sr, spliced)
