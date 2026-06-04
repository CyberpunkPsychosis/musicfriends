#!/usr/bin/env python3
"""按段落结构生成整首歌；或只重做某一段（段落级模块化）。

    # 生成整首（默认结构 intro/buildup/drop/break/drop2）
    python make_song.py --style future_bass --render --out song

    # 只重做 buildup 段（其它段一个音不动），并单独导出该段以便替换
    python make_song.py --style future_bass --regen buildup --seed 999 --render --out song
"""
from __future__ import annotations

import argparse
from pathlib import Path

from ardour_ai import song
from ardour_ai.midi import write_smf


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--style", default="melodic", choices=list(__import__(
        "ardour_ai.compose", fromlist=["STYLES"]).STYLES))
    ap.add_argument("--regen", help="只重做这一段（intro/buildup/drop/break/drop2）")
    ap.add_argument("--seed", type=int, default=999, help="重做该段用的新 seed")
    ap.add_argument("--no-melody", action="store_true")
    ap.add_argument("--out", default="song_out")
    ap.add_argument("--render", action="store_true")
    args = ap.parse_args()

    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    with_melody = not args.no_melody
    extra = []

    if args.regen:
        full, bpm, section_only, _ = song.regenerate_section(
            song.DEFAULT_STRUCTURE, target=args.regen, new_seed=args.seed,
            style=args.style, with_melody=with_melody)
        # 单独导出"仅该段"，可拖进 DAW 替换那一段
        extra.append(write_smf(out / f"{args.regen}_v{args.seed}.mid", section_only, bpm=bpm))
        print(f"♻️ 只重做了「{args.regen}」段（seed={args.seed}），其它段不变")
    else:
        full, bpm, layout = song.build_song(
            song.DEFAULT_STRUCTURE, style=args.style, with_melody=with_melody)
        print("段落布局：", " | ".join(f'{L["name"]}({L["kind"]},{L["bars"]}小节)'
                                      for L in layout))

    files = [write_smf(out / "full.mid", full, bpm=bpm), *extra]
    if args.render:
        from ardour_ai.render import render_tracks, write_wav
        files.append(write_wav(out / "full.wav", render_tracks(full, bpm=bpm)))

    print(f"已写出（{bpm} BPM）:")
    for p in files:
        print("  •", p.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
