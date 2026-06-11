"""ACE-Step 适配器单测：任务字段构造（纯函数）+ 能力声明。

不打真实 API（无本地 ACE-Step server）；HTTP 流程的字段名已按官方
docs/en/API.md 对齐，端到端在有卡的机器上冒烟。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from providers import get_provider  # noqa: E402
from providers.ace_step import build_task_fields  # noqa: E402
from providers.base import MusicSpec  # noqa: E402


def test_capabilities_declared():
    p = get_provider("ace_step")
    assert p.supports_melody and p.supports_inpaint


def test_text2music_fields():
    spec = MusicSpec(prompt="140 BPM melodic dubstep", duration_s=60, bpm=140, seed=7)
    f = build_task_fields(spec)
    assert f["task_type"] == "text2music"
    assert f["prompt"].startswith("140 BPM")
    assert f["audio_duration"] == 60.0
    assert f["bpm"] == 140 and f["seed"] == 7
    assert f["lyrics"] == "[instrumental]"  # EDM 默认纯器乐


def test_melody_routes_to_cover():
    spec = MusicSpec(prompt="rebuild around my hum", melody_path="hum.wav")
    f = build_task_fields(spec)
    assert f["task_type"] == "cover"
    assert 0.0 <= f["audio_cover_strength"] <= 1.0


def test_region_routes_to_repaint():
    spec = MusicSpec(prompt="harder drop", source_audio="song.wav",
                     region=(16.0, 32.0))
    f = build_task_fields(spec)
    assert f["task_type"] == "repaint"
    assert f["repainting_start"] == 16.0 and f["repainting_end"] == 32.0
    # repaint 以原曲为底，不该再传整曲时长
    assert "audio_duration" not in f


def test_repaint_wins_over_cover():
    # 同时给 region+source 和 melody：按段重做优先，melody 作参考
    spec = MusicSpec(prompt="x", source_audio="song.wav", region=(0.0, 8.0),
                     melody_path="hum.wav")
    assert build_task_fields(spec)["task_type"] == "repaint"


def test_vocal_track_keeps_lyrics_open():
    spec = MusicSpec(prompt="with vocals", instrumental=False)
    f = build_task_fields(spec)
    assert "lyrics" not in f
