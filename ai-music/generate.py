#!/usr/bin/env python3
"""对话/命令驱动的音乐生成入口 —— 统一调度各家大模型。

key 还没配也能用：
    python generate.py --list          # 看哪些 provider 就绪、哪些缺 key

配好任意一家 key 后：
    python generate.py --provider replicate \\
        --prompt "140 BPM melodic dubstep, dark intro to euphoric drop" \\
        --bpm 140 --duration 30 --out output
    # 以你自己的旋律为基础（旋律你主导）：
    python generate.py --provider replicate --prompt "..." --melody my_lead.wav
"""
from __future__ import annotations

import argparse
import sys

from providers import get_provider, all_providers, MusicSpec, MissingAPIKey


def cmd_list() -> None:
    print("可用 provider（✅=key 已就绪，⛔=待填 key）:\n")
    for p in all_providers():
        flag = "✅" if p.is_configured() else "⛔"
        need = ", ".join(p.required_env)
        print(f"  {flag}  {p.name:<13} {p.blurb}")
        print(f"       需要: {need}\n")
    print("填 key：编辑 ai-music/.env（参考 .env.example）")


def main() -> int:
    ap = argparse.ArgumentParser(description="AI 音乐生成统一入口")
    ap.add_argument("--list", action="store_true", help="列出 provider 及就绪状态")
    ap.add_argument("--provider", help="replicate / stable_audio / elevenlabs / suno")
    ap.add_argument("--prompt", help="文本描述")
    ap.add_argument("--duration", type=int, default=30, help="时长(秒)")
    ap.add_argument("--bpm", type=int)
    ap.add_argument("--genre")
    ap.add_argument("--melody", help="你的旋律音频/MIDI，用于旋律条件生成")
    ap.add_argument("--chords", help='和弦进行，如 "Am F C G"')
    ap.add_argument("--vocal", action="store_true", help="要人声（默认纯器乐）")
    ap.add_argument("--seed", type=int)
    ap.add_argument("--out", default="output", help="输出目录")
    args = ap.parse_args()

    if args.list or not args.provider:
        cmd_list()
        return 0

    if not args.prompt:
        print("缺少 --prompt", file=sys.stderr)
        return 2

    spec = MusicSpec(
        prompt=args.prompt,
        duration_s=args.duration,
        bpm=args.bpm,
        genre=args.genre,
        melody_path=args.melody,
        chords=args.chords,
        instrumental=not args.vocal,
        seed=args.seed,
        output_dir=args.out,
    )
    provider = get_provider(args.provider)
    try:
        result = provider.generate(spec)
    except MissingAPIKey as e:
        print(f"\n⛔ {e}\n", file=sys.stderr)
        return 1
    print(f"\n🎵 完成：{result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
