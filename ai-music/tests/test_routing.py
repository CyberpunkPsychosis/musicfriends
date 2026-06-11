"""生成路由优先级单测：出声音优先选已配置 key 的专业模型。"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from providers import preferred_provider, PRIORITY  # noqa: E402

_ALL_ENV = ("ACESTEP_API_BASE", "REPLICATE_API_TOKEN", "STABILITY_API_KEY",
            "ELEVENLABS_API_KEY", "SUNO_API_BASE", "SUNO_API_KEY")


def _clear(monkeypatch):
    monkeypatch.setattr("providers.config._loaded", True)  # 跳过 .env 加载
    for env in _ALL_ENV:
        monkeypatch.delenv(env, raising=False)


def test_none_when_no_keys(monkeypatch):
    _clear(monkeypatch)
    assert preferred_provider() is None


def test_picks_highest_priority_configured(monkeypatch):
    _clear(monkeypatch)
    # 只配 stable_audio：应选它
    monkeypatch.setenv("STABILITY_API_KEY", "x")
    assert preferred_provider().name == "stable_audio"
    # 再配 elevenlabs(优先级更高)：应改选 elevenlabs
    monkeypatch.setenv("ELEVENLABS_API_KEY", "y")
    assert preferred_provider().name == "elevenlabs"
    # 配上 ace_step(居首)：应改选 ace_step
    monkeypatch.setenv("ACESTEP_API_BASE", "http://127.0.0.1:8001")
    assert preferred_provider().name == "ace_step"


def test_priority_order_starts_with_ace_step():
    # 2026-06 复检：ACE-Step 居首（开源可商用、cover/repaint 全能），
    # MusicGen 因不可商用降级到 stable_audio 之后。
    assert PRIORITY[0] == "ace_step"
    assert PRIORITY.index("replicate") > PRIORITY.index("elevenlabs")
