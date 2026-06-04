"""生成路由优先级单测：出声音优先选已配置 key 的专业模型。"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from providers import preferred_provider, PRIORITY  # noqa: E402


def test_none_when_no_keys(monkeypatch):
    for env in ("REPLICATE_API_TOKEN", "STABILITY_API_KEY", "ELEVENLABS_API_KEY",
                "SUNO_API_BASE", "SUNO_API_KEY"):
        monkeypatch.delenv(env, raising=False)
    monkeypatch.setattr("providers.config._loaded", True)  # 跳过 .env 加载
    assert preferred_provider() is None


def test_picks_highest_priority_configured(monkeypatch):
    monkeypatch.setattr("providers.config._loaded", True)
    for env in ("REPLICATE_API_TOKEN", "STABILITY_API_KEY", "ELEVENLABS_API_KEY",
                "SUNO_API_BASE", "SUNO_API_KEY"):
        monkeypatch.delenv(env, raising=False)
    # 只配 stable_audio：应选它
    monkeypatch.setenv("STABILITY_API_KEY", "x")
    assert preferred_provider().name == "stable_audio"
    # 再配 replicate(优先级更高)：应改选 replicate
    monkeypatch.setenv("REPLICATE_API_TOKEN", "y")
    assert preferred_provider().name == "replicate"


def test_priority_order_starts_with_musicgen():
    assert PRIORITY[0] == "replicate"  # MusicGen 居首
