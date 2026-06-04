"""命令/结果序列化 + Note 校验的单测（不依赖 Ardour）。"""
import json
import pytest

from ardour_ai.commands import Command, Result, Note, notes_to_payload


def test_command_roundtrip():
    c = Command(op="set_tempo", args={"bpm": 140})
    c2 = Command.from_json(c.to_json())
    assert c2.op == "set_tempo"
    assert c2.args["bpm"] == 140
    assert c2.id == c.id


def test_result_roundtrip():
    r = Result(id="abc", ok=True, data={"track": 3})
    r2 = Result.from_json(r.to_json())
    assert r2.ok is True
    assert r2.data["track"] == 3
    assert r2.error is None


def test_note_validation():
    Note(pitch=60, start=0.0, length=1.0)  # ok
    with pytest.raises(ValueError):
        Note(pitch=200, start=0, length=1)
    with pytest.raises(ValueError):
        Note(pitch=60, start=0, length=0)
    with pytest.raises(ValueError):
        Note(pitch=60, start=-1, length=1)
    with pytest.raises(ValueError):
        Note(pitch=60, start=0, length=1, velocity=0)


def test_notes_payload_is_json_safe():
    notes = [Note(60, 0, 1), Note(64, 1, 0.5, velocity=80)]
    payload = notes_to_payload(notes)
    # 必须能被 json 序列化（要进命令文件）
    json.dumps(payload)
    assert payload[1]["pitch"] == 64
    assert payload[1]["velocity"] == 80
