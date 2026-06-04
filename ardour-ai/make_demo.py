#!/usr/bin/env python3
"""生成一组 EDM 脚手架 MIDI（按轨分文件，符合模块化原则）。

产出可直接拖进 FL / Ardour 的 .mid。旋律默认留空——那是你的地盘（--melody 可出引子）。

    python make_demo.py --style house --bars 8 --render
    python make_demo.py --style future_bass --melody --seed 7 --render
    风格可选: melodic(默认) / house / future_bass / dubstep
"""
from __future__ import annotations

import argparse
from pathlib import Path

from ardour_ai import compose
from ardour_ai.midi import write_smf


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--style", default="melodic", choices=list(compose.STYLES),
                    help="风格（决定 BPM / 鼓型 / bass 型 / 走向）")
    ap.add_argument("--bpm", type=float, default=None, help="覆盖风格默认 BPM")
    ap.add_argument("--bars", type=int, default=8)
    ap.add_argument("--melody", action="store_true", help="额外生成一版旋律引子")
    ap.add_argument("--seed", type=int, default=None, help="旋律随机种子（可复现）")
    ap.add_argument("--out", default="demo_midi")
    ap.add_argument("--render", action="store_true",
                    help="同时渲染 full.wav 试听（需 numpy）")
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    tracks, bpm = compose.build_arrangement(
        style=args.style, bars=args.bars, with_melody=args.melody, seed=args.seed)
    if args.bpm is not None:
        bpm = args.bpm

    written = []
    # 每轨单独成文件 —— 方便你只替换其中一块（如只重做某段）
    for tr in tracks:
        fname = tr.name.split()[0].lower().replace("(", "") + ".mid"
        written.append(write_smf(out / fname, [tr], bpm=bpm))
    # buildup 段单独给（节奏积木）
    written.append(write_smf(out / "buildup.mid", [compose.drum_buildup(bars=1)], bpm=bpm))
    # 合并版
    written.append(write_smf(out / "full.mid", tracks, bpm=bpm))

    print(f"风格={args.style}  {bpm} BPM  {args.bars} 小节"
          f"{'  +旋律引子' if args.melody else ''}")
    print(f"已生成 {len(written)} 个 MIDI 到 {out}/ :")
    for p in written:
        print("  •", p.name)

    if args.render:
        from ardour_ai.render import render_tracks, write_wav
        wav = write_wav(out / "full.wav", render_tracks(tracks, bpm=bpm))
        print(f"试听已渲染 -> {wav.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
