"""集中配置：网络端口、命令队列路径。可用环境变量覆盖。"""
from __future__ import annotations

import os
from pathlib import Path

# --- Ardour OSC ---
# Ardour 默认在 UDP 3819 监听 OSC（Preferences ▸ Control Surfaces ▸ OSC 打开）
ARDOUR_OSC_HOST = os.environ.get("ARDOUR_OSC_HOST", "127.0.0.1")
ARDOUR_OSC_PORT = int(os.environ.get("ARDOUR_OSC_PORT", "3819"))

# --- Lua 命令队列（MCP server ↔ Ardour 内 Lua 脚本 的 IPC）---
# MCP server 往 requests/ 写命令 JSON；Ardour 里的 ai_bridge.lua 轮询执行，
# 把结果写到 responses/。详见 docs/ardour-ai-daw-design.md §6。
_default_queue = Path.home() / ".config" / "ardour-ai" / "queue"
QUEUE_DIR = Path(os.environ.get("ARDOUR_AI_QUEUE", str(_default_queue)))
REQ_DIR = QUEUE_DIR / "requests"
RESP_DIR = QUEUE_DIR / "responses"

# 等待 Lua 执行结果的超时（秒）
LUA_TIMEOUT_S = float(os.environ.get("ARDOUR_AI_LUA_TIMEOUT", "10"))


def ensure_queue_dirs() -> None:
    REQ_DIR.mkdir(parents=True, exist_ok=True)
    RESP_DIR.mkdir(parents=True, exist_ok=True)
