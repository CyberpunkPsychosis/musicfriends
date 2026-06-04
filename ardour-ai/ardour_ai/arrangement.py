"""把"一段编排(音符 JSON)"落地成 MIDI / 试听 —— 无需任何 API key。

为什么没有"调大模型"那一步：
  驱动本流程的本地客户端**就是 Claude(我)**。我在对话里直接产出音符即可，
  再调本模块落地，不必让 MCP server 反过来调 Anthropic API 去"问 Claude"
  （那是 Claude 调 Claude，多余）。

  → 要"成品音频/人声/stem"才需要外部大模型，那条在 ../ai-music/（MusicGen 等）。
  → 这里只管：我给出的音符 JSON → 校验 → .mid / .wav / 进 Ardour。

JSON 契约：
{
  "bpm": 140,
  "tracks": [
    {"name": "Melody", "channel": 2,
     "notes": [{"pitch": 65, "start": 0.0, "length": 1.0, "velocity": 100}]}
  ]
}
约定：start/length 以拍(beat)为单位，pitch 为 MIDI 号(60=中央C)，鼓轨 channel=9。
"""
from __future__ import annotations

import json
from pathlib import Path

from .commands import Note
from .midi import MidiTrack, write_smf


def arrangement_from_json(data: dict) -> tuple[list[MidiTrack], float]:
    """JSON → (tracks, bpm)。经 Note 校验，纯函数，可独立单测。"""
    bpm = float(data.get("bpm", 120))
    tracks: list[MidiTrack] = []
    for t in data.get("tracks", []):
        notes = [Note(pitch=int(n["pitch"]), start=float(n["start"]),
                      length=float(n["length"]), velocity=int(n.get("velocity", 100)))
                 for n in t.get("notes", [])]
        tracks.append(MidiTrack(name=str(t.get("name", "AI")),
                                notes=notes, channel=int(t.get("channel", 0))))
    if not tracks:
        raise ValueError("编排里没有任何轨道")
    return tracks, bpm


def extract_json(text: str) -> dict:
    """从一段文本里抠出 JSON（容忍 ```json 包裹 / 前后多余文字）。"""
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("文本里找不到 JSON")
    return json.loads(text[start:end + 1])


def materialize(data: dict, out_dir: str | Path, render: bool = False) -> list[Path]:
    """把编排落地：每轨一个 .mid + 合并 full.mid，可选 full.wav 试听。"""
    tracks, bpm = arrangement_from_json(data)
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for tr in tracks:
        fname = (tr.name.split()[0].lower() or "track") + ".mid"
        written.append(write_smf(out / fname, [tr], bpm=bpm))
    written.append(write_smf(out / "full.mid", tracks, bpm=bpm))
    if render:
        from .render import render_tracks, write_wav
        written.append(write_wav(out / "full.wav", render_tracks(tracks, bpm=bpm)))
    return written


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(
        description="把音符 JSON 文件落地成 MIDI(+试听)。JSON 由对话中的 Claude 产出。")
    ap.add_argument("json_file", help="编排 JSON 文件路径")
    ap.add_argument("-o", "--out", default="arrangement_out")
    ap.add_argument("--render", action="store_true")
    args = ap.parse_args()
    data = extract_json(Path(args.json_file).read_text(encoding="utf-8"))
    paths = materialize(data, args.out, render=args.render)
    print(f"✅ 落地 {len(paths)} 个文件到 {args.out}/:")
    for p in paths:
        print("  •", p.name)
