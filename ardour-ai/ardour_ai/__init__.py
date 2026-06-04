"""ardour_ai —— 驱动 Ardour 的 MCP 后端：OSC(混音/走带) + Lua 桥(编曲)。"""
from .osc_client import ArdourOSC
from .lua_bridge import LuaBridge, LuaBridgeTimeout
from .commands import Command, Result, Note, notes_to_payload

__all__ = [
    "ArdourOSC", "LuaBridge", "LuaBridgeTimeout",
    "Command", "Result", "Note", "notes_to_payload",
]
