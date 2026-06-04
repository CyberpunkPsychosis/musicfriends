#!/usr/bin/env python3
"""生成一组 EDM 脚手架 MIDI（按轨分文件，符合模块化原则）。

产出可直接拖进 FL / Ardour 的 .mid。旋律留空——那是你的地盘。

    python make_demo.py --bpm 140 --bars 8 --out demo_midi
"""
from __future__ import annotations

import argparse
from pathlib import Path

from ardour_ai import compose
from ardour_ai.midi import write_smf


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bpm", type=float, default=140)
    ap.add_argument("--bars", type=int, default=8)
    ap.add_argument("--out", default="demo_midi")
    ap.add_argument("--render", action="store_true",
                    help="同时渲染 full.wav 试听（需 numpy）")
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    prog = compose.DEFAULT_PROGRESSION

    # 每轨单独成文件 —— 方便你只替换其中一块（如只重做 buildup）
    jobs = {
        "drums.mid":   [compose.drums_four_on_floor(bars=args.bars)],
        "chords.mid":  [compose.chords_track(prog, bars=args.bars)],
        "bass.mid":    [compose.bass_track(prog, bars=args.bars)],
        "buildup.mid": [compose.drum_buildup(bars=1)],
    }
    written = []
    for fname, tracks in jobs.items():
        p = write_smf(out / fname, tracks, bpm=args.bpm)
        written.append(p)

    # 再来一个合并版，方便整体试听
    combined = [
        compose.drums_four_on_floor(bars=args.bars),
        compose.chords_track(prog, bars=args.bars),
        compose.bass_track(prog, bars=args.bars),
    ]
    written.append(write_smf(out / "full.mid", combined, bpm=args.bpm))

    print(f"已生成 {len(written)} 个 MIDI 到 {out}/ （{args.bpm} BPM, {args.bars} 小节）:")
    for p in written:
        print("  •", p.name)

    if args.render:
        from ardour_ai.render import render_tracks, write_wav
        wav = write_wav(out / "full.wav", render_tracks(combined, bpm=args.bpm))
        print(f"试听已渲染 -> {wav.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
