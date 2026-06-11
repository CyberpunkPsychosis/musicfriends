#!/usr/bin/env python3
"""Stems 分离薄封装 —— 把整首拆成分轨，支撑「只重编某一轨」。

选型（docs/research-2026-06.md）：不自建模型。用社区标准 `audio-separator`
（python-audio-separator，活跃维护），默认跑 RoFormer 系 SOTA 权重；
官方 Demucs 已归档（2025-01），不再作为首选。

    python stems.py song.wav                 # 拆 stems 到 song_stems/
    python stems.py song.wav -m <model.ckpt> # 指定模型权重

依赖：pip install "audio-separator[cpu]"   # 或 [gpu]
提示：FL Studio 21.2+ / 2026 自带分轨，日常够用；这里是管线内的程序化通道。
"""
from __future__ import annotations

import argparse
from pathlib import Path

# audio-separator 的默认模型即可用；要最高质量可改用其文档列出的
# BS/Mel-Band RoFormer 权重（MVSEP 榜 SOTA 家族）。
DEFAULT_MODEL = None  # None = audio-separator 自带默认


def separate(audio_path: str, out_dir: str | None = None,
             model: str | None = DEFAULT_MODEL) -> list[str]:
    """整首音频 -> 分轨文件列表。需要 audio-separator。"""
    try:
        from audio_separator.separator import Separator
    except ImportError as e:
        raise RuntimeError('缺少依赖：pip install "audio-separator[cpu]"') from e

    out = out_dir or str(Path(audio_path).with_suffix("")) + "_stems"
    Path(out).mkdir(parents=True, exist_ok=True)
    sep = Separator(output_dir=out)
    if model:
        sep.load_model(model_filename=model)
    else:
        sep.load_model()
    files = sep.separate(audio_path)
    return [str(Path(out) / f) for f in files]


def main() -> int:
    ap = argparse.ArgumentParser(description="整首 → stems 分轨")
    ap.add_argument("audio", help="要拆的音频文件")
    ap.add_argument("-o", "--out", help="输出目录（默认 <名字>_stems/）")
    ap.add_argument("-m", "--model", help="指定 audio-separator 模型权重文件名")
    args = ap.parse_args()

    files = separate(args.audio, args.out, args.model)
    print("🎛  分轨完成：")
    for f in files:
        print(f"   {f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
