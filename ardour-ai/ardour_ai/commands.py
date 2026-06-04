"""命令与结果的数据结构 + 序列化。

MCP server 与 Ardour 内 Lua 脚本之间通过 JSON 命令文件通信。
这一层不依赖 Ardour，可独立单测。
"""
from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class Note:
    """一个 MIDI 音符，时间以拍(beat)为单位。"""
    pitch: int            # 0-127，60 = 中央 C
    start: float          # 起始拍
    length: float         # 时值(拍)
    velocity: int = 100   # 1-127

    def __post_init__(self) -> None:
        if not 0 <= self.pitch <= 127:
            raise ValueError(f"pitch 越界(0-127): {self.pitch}")
        if not 1 <= self.velocity <= 127:
            raise ValueError(f"velocity 越界(1-127): {self.velocity}")
        if self.length <= 0:
            raise ValueError(f"length 必须为正: {self.length}")
        if self.start < 0:
            raise ValueError(f"start 不能为负: {self.start}")


@dataclass
class Command:
    """一条发给 Ardour Lua 的命令。"""
    op: str                              # 操作名，如 "add_midi_track"
    args: dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    ts: float = field(default_factory=time.time)

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)

    @staticmethod
    def from_json(s: str) -> "Command":
        d = json.loads(s)
        return Command(op=d["op"], args=d.get("args", {}),
                       id=d.get("id", uuid.uuid4().hex), ts=d.get("ts", time.time()))


@dataclass
class Result:
    """Ardour Lua 执行后的回执。"""
    id: str                  # 对应 Command.id
    ok: bool
    data: Any = None         # 成功时的返回（如新轨的 index）
    error: str | None = None

    def to_json(self) -> str:
        return json.dumps(asdict(self), ensure_ascii=False)

    @staticmethod
    def from_json(s: str) -> "Result":
        d = json.loads(s)
        return Result(id=d["id"], ok=d["ok"], data=d.get("data"), error=d.get("error"))


def notes_to_payload(notes: list[Note]) -> list[dict[str, Any]]:
    """把 Note 列表转成 Lua 端好消费的纯 dict 列表。"""
    return [asdict(n) for n in notes]
