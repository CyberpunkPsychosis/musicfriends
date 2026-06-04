#!/usr/bin/env python3
"""AI 驱动 Ardour 的 MCP server。

在你本地（Mac）运行，配进本地 Claude 客户端（Claude Desktop / Claude Code）后，
你就能在对话里驱动 Ardour 编曲。

  混音/走带  → OSC（需 Ardour 打开 OSC，端口 3819）
  编曲       → Lua 命令队列（需 Ardour 加载 lua/ai_bridge.lua）

跑法：
    pip install -r requirements.txt
    python server.py            # stdio MCP server
"""
from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from ardour_ai import ArdourOSC, LuaBridge, LuaBridgeTimeout, Note, notes_to_payload

mcp = FastMCP("ardour-ai")
osc = ArdourOSC()
lua = LuaBridge()


# ============ 走带 / 混音（OSC，实时）============

@mcp.tool()
def transport_play() -> str:
    """开始播放。"""
    osc.play()
    return "▶️ 播放"


@mcp.tool()
def transport_stop() -> str:
    """停止播放。"""
    osc.stop()
    return "⏹️ 停止"


@mcp.tool()
def locate(seconds: float) -> str:
    """把播放头跳到指定秒数。"""
    osc.locate(seconds)
    return f"📍 定位 → {seconds}s"


@mcp.tool()
def set_track_gain(track: int, db: float) -> str:
    """设某轨增益（dB）。track 从 1 开始。"""
    osc.set_gain(track, db)
    return f"🎚️ 轨{track} 增益 = {db}dB"


@mcp.tool()
def set_track_mute(track: int, mute: bool) -> str:
    """静音/取消静音某轨。track 从 1 开始。"""
    osc.set_mute(track, mute)
    return f"🔇 轨{track} mute = {mute}"


@mcp.tool()
def set_track_solo(track: int, solo: bool) -> str:
    """独奏/取消独奏某轨。track 从 1 开始。"""
    osc.set_solo(track, solo)
    return f"🎧 轨{track} solo = {solo}"


# ============ 编曲（Lua 命令队列）============

def _lua(op: str, **args) -> str:
    try:
        r = lua.call(op, **args)
    except LuaBridgeTimeout as e:
        return f"⛔ {e}"
    if not r.ok:
        return f"⛔ Ardour 执行失败：{r.error}"
    return f"✅ {op} 完成" + (f"：{r.data}" if r.data is not None else "")


@mcp.tool()
def set_tempo(bpm: float) -> str:
    """设置工程速度（BPM）。"""
    return _lua("set_tempo", bpm=bpm)


@mcp.tool()
def add_midi_track(name: str) -> str:
    """新建一条 MIDI 轨，返回轨道信息。"""
    return _lua("add_midi_track", name=name)


@mcp.tool()
def add_audio_track(name: str) -> str:
    """新建一条音频轨。"""
    return _lua("add_audio_track", name=name)


@mcp.tool()
def write_notes(track: int, notes: list[dict]) -> str:
    """把一段 MIDI 音符写入某轨。

    notes 每项: {"pitch":60, "start":0.0, "length":1.0, "velocity":100}
    时间单位为拍(beat)。pitch 60 = 中央 C。
    """
    parsed = [Note(**n) for n in notes]  # 校验范围
    return _lua("write_notes", track=track, notes=notes_to_payload(parsed))


@mcp.tool()
def import_audio(track: int, file_path: str) -> str:
    """把一个音频文件（如大模型产出的 stem）导入到某轨。"""
    return _lua("import_audio", track=track, file_path=file_path)


@mcp.tool()
def save_arrangement(bpm: float, tracks: list[dict], out_dir: str,
                     render: bool = False) -> str:
    """把我（对话中的 Claude）写出的编排落地成 .mid 文件（不需要 Ardour）。

    tracks 每项: {"name":"Melody", "channel":2, "notes":[
                   {"pitch":60,"start":0.0,"length":1.0,"velocity":100}, ...]}
    鼓轨 channel=9。render=True 时另出 full.wav 试听。
    用于「文件流」：产出 .mid 让你拖进 FL / Ardour。
    """
    from ardour_ai.arrangement import materialize
    paths = materialize({"bpm": bpm, "tracks": tracks}, out_dir, render=render)
    return "✅ 已落地：" + ", ".join(p.name for p in paths) + f"（{out_dir}/）"


@mcp.tool()
def regenerate_section(target: str, new_seed: int, out_dir: str,
                       style: str = "melodic") -> str:
    """段落级模块化：只重做某一段（intro/buildup/drop/break/drop2），其它段不动。

    产出整首 full.mid + 仅该段的 <target>.mid（可拖进 DAW 替换那一段）。
    用默认歌曲结构；体现"只让 AI 改某个部分"的灵活性。
    """
    from ardour_ai import song
    from ardour_ai.midi import write_smf
    from pathlib import Path
    full, bpm, section_only, _ = song.regenerate_section(
        song.DEFAULT_STRUCTURE, target=target, new_seed=new_seed, style=style)
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    write_smf(out / "full.mid", full, bpm=bpm)
    write_smf(out / f"{target}.mid", section_only, bpm=bpm)
    return f"✅ 只重做了「{target}」段（其它段不变）→ {out_dir}/full.mid + {target}.mid"


@mcp.tool()
def regenerate_audio_section(full_audio: str, prompt: str, out_path: str,
                             section: str = "", bpm: float = 0.0,
                             start_s: float = -1.0, end_s: float = -1.0,
                             melody: str = "", provider: str = "auto") -> str:
    """音频路段落重生成（迭代循环第⑤步）：大模型只重生成一段 → 拼回原曲。

    区间二选一：section+bpm（intro/buildup/drop/break/drop2）或 start_s+end_s。
    melody=你的旋律（旋律条件，你主导旋律）。provider=auto 自动选已配置 key 的专业模型。
    模型调用需 key；拼接（只换这一段）不需要 key。区间外逐样本不变。
    """
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "ai-music"))
    try:
        from regenerate import (section_to_seconds, regenerate_and_splice,
                                _resolve_provider)
        from providers import MissingAPIKey
    except ImportError as e:
        return f"⛔ 无法加载 ai-music（{e}）。确认仓库结构完整。"

    if section:
        if not bpm:
            return "⛔ 用 section 时需要 bpm"
        a, b = section_to_seconds(section, bpm)
    elif start_s >= 0 and end_s >= 0:
        a, b = start_s, end_s
    else:
        return "⛔ 需 section+bpm 或 start_s+end_s"

    try:
        p = _resolve_provider(provider)
        out = regenerate_and_splice(p, full_audio, a, b, prompt,
                                    melody_path=melody or None, out_path=out_path)
    except MissingAPIKey as e:
        return f"⛔ {e}"
    except SystemExit as e:
        return f"⛔ {e}"
    return f"✅ 只重生成 [{a:.1f}s,{b:.1f}s] 并拼回 → {out}"


if __name__ == "__main__":
    mcp.run()
