"""Lua 命令队列 IPC —— MCP server 侧。

编曲类操作（建轨、写音符、设速度）OSC 做不到，必须进 Ardour 内部跑 Lua。
机制（见 docs/ardour-ai-daw-design.md §6）：
  1. 本类把命令写成 JSON 到  QUEUE/requests/<id>.json
  2. Ardour 里常驻的 ai_bridge.lua 轮询该目录，执行，把回执写到 QUEUE/responses/<id>.json
  3. 本类轮询 responses 取回结果

这一侧（写请求/等回执）不依赖 Ardour，可独立单测。
"""
from __future__ import annotations

import time
from pathlib import Path

from . import config
from .commands import Command, Result


class LuaBridgeTimeout(TimeoutError):
    pass


class LuaBridge:
    def __init__(self, req_dir: Path | None = None, resp_dir: Path | None = None,
                 timeout_s: float | None = None):
        self.req_dir = req_dir or config.REQ_DIR
        self.resp_dir = resp_dir or config.RESP_DIR
        self.timeout_s = timeout_s if timeout_s is not None else config.LUA_TIMEOUT_S
        self.req_dir.mkdir(parents=True, exist_ok=True)
        self.resp_dir.mkdir(parents=True, exist_ok=True)

    def submit(self, cmd: Command) -> Path:
        """原子写入一条命令，返回请求文件路径。"""
        final = self.req_dir / f"{cmd.id}.json"
        tmp = self.req_dir / f"{cmd.id}.json.tmp"
        tmp.write_text(cmd.to_json(), encoding="utf-8")
        tmp.rename(final)  # rename 是原子的，避免 Lua 读到半截文件
        return final

    def wait(self, cmd_id: str, poll_s: float = 0.05) -> Result:
        """轮询等待回执，超时抛 LuaBridgeTimeout。"""
        resp = self.resp_dir / f"{cmd_id}.json"
        deadline = time.time() + self.timeout_s
        while time.time() < deadline:
            if resp.exists():
                result = Result.from_json(resp.read_text(encoding="utf-8"))
                resp.unlink(missing_ok=True)
                return result
            time.sleep(poll_s)
        raise LuaBridgeTimeout(
            f"等待 Lua 回执超时({self.timeout_s}s)，命令 {cmd_id}。"
            f"\n  → 确认 Ardour 已加载 ai_bridge.lua 且在轮询 {self.req_dir}"
        )

    def call(self, op: str, **args) -> Result:
        """提交命令并等回执（同步）。"""
        cmd = Command(op=op, args=args)
        self.submit(cmd)
        return self.wait(cmd.id)
