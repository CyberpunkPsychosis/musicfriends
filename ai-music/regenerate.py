#!/usr/bin/env python3
"""段落重生成一条龙：调模型(旋律条件/inpaint) → 拼回原曲 → 出新曲。

对应迭代循环第⑤步。一句话：

    python regenerate.py --full song.wav --section drop --bpm 150 \
        --prompt "euphoric melodic dubstep drop" --melody my_drop_lead.wav

或直接给秒区间（适用任意音频）：

    python regenerate.py --full song.wav --start 12.8 --end 25.6 --prompt "..."

--provider 默认 auto（按优先级选已配置 key 的专业模型）。模型调用需 key；
拼接那一环（决定"只换这一段"成立）不需要 key、已测通。
"""
from __future__ import annotations

import argparse
import sys

from providers import (get_provider, preferred_provider, MusicProvider,
                       MusicSpec, GenerationResult, MissingAPIKey)
from splice import replace_region_in_file

# 默认 EDM 歌曲布局（镜像 ../ardour-ai/ardour_ai/song.py 的 DEFAULT_STRUCTURE）
# name -> (start_bar, bars)
DEFAULT_LAYOUT: dict[str, tuple[int, int]] = {
    "intro": (0, 4), "buildup": (4, 4), "drop": (8, 8),
    "break": (16, 4), "drop2": (20, 8),
}


def section_to_seconds(section: str, bpm: float,
                       layout: dict[str, tuple[int, int]] = DEFAULT_LAYOUT,
                       beats_per_bar: int = 4) -> tuple[float, float]:
    """段名 + BPM -> (start_s, end_s)。"""
    if section not in layout:
        raise ValueError(f"未知段落 {section!r}，可选：{', '.join(layout)}（或用 --start/--end）")
    start_bar, bars = layout[section]
    spb = beats_per_bar * 60.0 / bpm          # 每小节秒数
    return start_bar * spb, (start_bar + bars) * spb


def regenerate_and_splice(provider: MusicProvider, full_audio: str,
                          start_s: float, end_s: float, prompt: str,
                          melody_path: str | None = None, out_path: str | None = None,
                          out_dir: str = "output", crossfade_ms: float = 30.0) -> str:
    """核心编排（provider 可注入，便于测试）：模型出新段 → 拼回原曲。"""
    spec = MusicSpec(
        prompt=prompt,
        duration_s=max(1, round(end_s - start_s)),
        melody_path=melody_path,         # 旋律条件：以你的旋律为基础
        source_audio=full_audio,         # inpaint 的底
        region=(start_s, end_s),
        output_dir=out_dir,
    )
    res: GenerationResult = provider.regenerate_section(spec)
    if not res.output_path:
        raise RuntimeError(
            f"{provider.name} 没有返回本地音频文件（拿到的是 URL: {res.url}）；"
            "需先下载成 .wav 再拼接。")
    out_path = out_path or full_audio.rsplit(".", 1)[0] + "_regen.wav"
    replace_region_in_file(full_audio, res.output_path, start_s, end_s,
                           out_path, crossfade_ms=crossfade_ms)
    return out_path


def _resolve_provider(name: str | None) -> MusicProvider:
    if not name or name == "auto":
        p = preferred_provider()
        if p is None:
            raise SystemExit("⛔ 没有已配置 key 的专业模型。填 key，或先在 ../ardour-ai/ "
                             "用符号路出 MIDI（无需 key）。")
        print(f"🎯 自动路由 → {p.name}")
        return p
    return get_provider(name)


def main() -> int:
    ap = argparse.ArgumentParser(description="段落重生成 + 拼回原曲")
    ap.add_argument("--full", required=True, help="原曲音频(.wav)")
    ap.add_argument("--prompt", required=True, help="这一段想要什么")
    ap.add_argument("--section", help="段名(intro/buildup/drop/break/drop2)，配合 --bpm")
    ap.add_argument("--bpm", type=float, help="用 --section 时的 BPM")
    ap.add_argument("--start", type=float, help="区间起(秒)，与 --section 二选一")
    ap.add_argument("--end", type=float, help="区间止(秒)")
    ap.add_argument("--melody", help="你的旋律(用于旋律条件，你主导旋律)")
    ap.add_argument("--provider", default="auto", help="auto / replicate / stable_audio / ...")
    ap.add_argument("--out", help="输出新曲路径")
    ap.add_argument("--crossfade", type=float, default=30.0, help="交叉淡化(毫秒)")
    args = ap.parse_args()

    if args.section:
        if args.bpm is None:
            print("用 --section 时需要 --bpm", file=sys.stderr)
            return 2
        start_s, end_s = section_to_seconds(args.section, args.bpm)
    elif args.start is not None and args.end is not None:
        start_s, end_s = args.start, args.end
    else:
        print("需指定 --section+--bpm 或 --start+--end", file=sys.stderr)
        return 2

    provider = _resolve_provider(args.provider)
    if not provider.supports_inpaint and not provider.supports_melody:
        print(f"⚠️ {provider.name} 未声明段落重生成能力，结果可能是整段新生成。")

    try:
        out = regenerate_and_splice(provider, args.full, start_s, end_s, args.prompt,
                                    melody_path=args.melody, out_path=args.out,
                                    crossfade_ms=args.crossfade)
    except MissingAPIKey as e:
        print(f"\n⛔ {e}\n", file=sys.stderr)
        return 1
    print(f"\n🎵 完成：只重生成了 [{start_s:.1f}s, {end_s:.1f}s] 这一段 → {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
