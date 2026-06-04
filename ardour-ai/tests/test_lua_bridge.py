"""Lua 命令队列 IPC 单测。

用一个「假 Ardour」线程模拟 ai_bridge.lua：轮询 requests/，写回 responses/。
验证 MCP server 侧的 submit/wait/call 全链路（不需要真 Ardour）。
"""
import threading
import time

import pytest

from ardour_ai.lua_bridge import LuaBridge, LuaBridgeTimeout
from ardour_ai.commands import Command, Result


def fake_ardour(bridge: LuaBridge, stop: threading.Event, handler):
    """模拟 Ardour 内 Lua：排空 requests，按 handler 产出 Result 写回。"""
    while not stop.is_set():
        for req in list(bridge.req_dir.glob("*.json")):
            cmd = Command.from_json(req.read_text(encoding="utf-8"))
            req.unlink(missing_ok=True)
            res = handler(cmd)
            (bridge.resp_dir / f"{cmd.id}.json").write_text(
                res.to_json(), encoding="utf-8")
        time.sleep(0.01)


def test_call_success(tmp_path):
    bridge = LuaBridge(tmp_path / "req", tmp_path / "resp", timeout_s=3)
    stop = threading.Event()

    def handler(cmd: Command) -> Result:
        assert cmd.op == "add_midi_track"
        return Result(id=cmd.id, ok=True, data={"name": cmd.args["name"], "index": 1})

    t = threading.Thread(target=fake_ardour, args=(bridge, stop, handler), daemon=True)
    t.start()
    try:
        r = bridge.call("add_midi_track", name="Lead")
        assert r.ok
        assert r.data["index"] == 1
        assert r.data["name"] == "Lead"
    finally:
        stop.set()


def test_call_error_propagates(tmp_path):
    bridge = LuaBridge(tmp_path / "req", tmp_path / "resp", timeout_s=3)
    stop = threading.Event()

    def handler(cmd: Command) -> Result:
        return Result(id=cmd.id, ok=False, error="boom")

    t = threading.Thread(target=fake_ardour, args=(bridge, stop, handler), daemon=True)
    t.start()
    try:
        r = bridge.call("write_notes", track=1, notes=[])
        assert not r.ok
        assert r.error == "boom"
    finally:
        stop.set()


def test_timeout_when_no_ardour(tmp_path):
    """没有 Ardour 消费队列时，应在超时后明确报错。"""
    bridge = LuaBridge(tmp_path / "req", tmp_path / "resp", timeout_s=0.3)
    with pytest.raises(LuaBridgeTimeout):
        bridge.call("set_tempo", bpm=140)


def test_submit_is_atomic(tmp_path):
    """提交后队列里只应有最终 .json，不残留 .tmp。"""
    bridge = LuaBridge(tmp_path / "req", tmp_path / "resp", timeout_s=1)
    cmd = Command(op="set_tempo", args={"bpm": 128})
    path = bridge.submit(cmd)
    assert path.exists()
    assert path.suffix == ".json"
    assert list(bridge.req_dir.glob("*.tmp")) == []
