"""LLM 符号作曲「口子」—— 让 AI 直接产出 MIDI 音符（旋律/和弦）。

为什么单独做：ai-music/ 里的大模型出的是**音频**（→ 经 import_audio 进 Ardour 当 stem）；
而「AI 出旋律/和弦 → 落 MIDI → 试听」需要**符号**音乐，最合适的是让 LLM 直接产出音符。

口子模式（同 ai-music/）：key 走环境变量 ANTHROPIC_API_KEY，没 key 时给清晰提示，
但 JSON → 轨道 的解析逻辑（arrangement_from_json）不依赖 key，可独立单测。

    export ANTHROPIC_API_KEY=...
    python -m ardour_ai.llm_compose "暗到亮的 melodic dubstep 主旋律, F 小调, 8 小节" -o out
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from .commands import Note
from .midi import MidiTrack, write_smf

MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-6")


class MissingAPIKey(RuntimeError):
    pass


# LLM 被要求输出的 JSON 形态（也是 arrangement_from_json 的输入契约）
_SCHEMA_HINT = """只输出 JSON，形如：
{
  "bpm": 140,
  "tracks": [
    {"name": "Melody", "channel": 2,
     "notes": [{"pitch": 65, "start": 0.0, "length": 1.0, "velocity": 100}]}
  ]
}
约定：start/length 以拍(beat)为单位，pitch 为 MIDI 号(60=中央C)，鼓轨 channel=9。"""


def arrangement_from_json(data: dict) -> tuple[list[MidiTrack], float]:
    """把 LLM 返回的 JSON 解析成 (tracks, bpm)。纯函数，经 Note 校验，可独立单测。"""
    bpm = float(data.get("bpm", 120))
    tracks: list[MidiTrack] = []
    for t in data.get("tracks", []):
        notes = [Note(pitch=int(n["pitch"]), start=float(n["start"]),
                      length=float(n["length"]), velocity=int(n.get("velocity", 100)))
                 for n in t.get("notes", [])]
        tracks.append(MidiTrack(name=str(t.get("name", "AI")),
                                notes=notes, channel=int(t.get("channel", 0))))
    if not tracks:
        raise ValueError("LLM 返回里没有任何轨道")
    return tracks, bpm


def _extract_json(text: str) -> dict:
    """从模型回复里抠出 JSON（容忍前后多余文本 / ```json 包裹）。"""
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"模型回复里找不到 JSON：{text[:200]}")
    return json.loads(text[start:end + 1])


def compose_with_llm(prompt: str, bars: int = 8) -> tuple[list[MidiTrack], float]:
    """调用 Claude 产出一段编排。需 ANTHROPIC_API_KEY。"""
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise MissingAPIKey(
            "缺少 ANTHROPIC_API_KEY。\n"
            "  → export ANTHROPIC_API_KEY=... 后重试；\n"
            "  → 没 key 也能用本地算法作曲：python make_demo.py --style house --melody")
    try:
        import anthropic  # pip install anthropic
    except ImportError as e:
        raise RuntimeError("缺少依赖：pip install anthropic") from e

    client = anthropic.Anthropic(api_key=key)
    system = ("你是 EDM 编曲助手。根据需求产出 MIDI 音符数据。" + _SCHEMA_HINT)
    msg = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=[{"type": "text", "text": system,
                 "cache_control": {"type": "ephemeral"}}],  # 系统提示走缓存
        messages=[{"role": "user",
                   "content": f"需求：{prompt}\n小节数：{bars}\n只输出 JSON。"}],
    )
    text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
    return arrangement_from_json(_extract_json(text))


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="LLM 符号作曲 → MIDI(+试听)")
    ap.add_argument("prompt")
    ap.add_argument("--bars", type=int, default=8)
    ap.add_argument("-o", "--out", default="llm_out")
    ap.add_argument("--render", action="store_true")
    args = ap.parse_args()
    try:
        tracks, bpm = compose_with_llm(args.prompt, bars=args.bars)
    except MissingAPIKey as e:
        raise SystemExit(f"⛔ {e}")
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    write_smf(out / "llm.mid", tracks, bpm=bpm)
    print(f"✅ {bpm} BPM, {len(tracks)} 轨 -> {out}/llm.mid")
    if args.render:
        from .render import render_tracks, write_wav
        write_wav(out / "llm.wav", render_tracks(tracks, bpm=bpm))
        print(f"试听 -> {out}/llm.wav")
