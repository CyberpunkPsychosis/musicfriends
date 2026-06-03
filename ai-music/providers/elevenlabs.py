"""ElevenLabs Music 适配器 —— 录音室级，API 层支持段落重绘(inpainting)。

注意：v2 自助 API 于 2026 年逐步开放，企业先行。接 key 前先确认你的账号已开通 Music API。
docs: https://elevenlabs.io/docs/overview/capabilities/music
TODO(接 key 后核对): 官方 python SDK(elevenlabs) 的 music 接口签名以当时文档为准。
"""
from __future__ import annotations

from pathlib import Path

from .base import MusicProvider, MusicSpec, GenerationResult
from .config import get_key


class ElevenLabsProvider(MusicProvider):
    name = "elevenlabs"
    required_env = ("ELEVENLABS_API_KEY",)
    blurb = "Eleven Music：录音室级，API 支持段落重绘（需账号开通 Music API）"

    def generate(self, spec: MusicSpec) -> GenerationResult:
        self.ensure_configured()
        try:
            from elevenlabs.client import ElevenLabs  # pip install elevenlabs
        except ImportError as e:
            raise RuntimeError("缺少依赖：pip install elevenlabs") from e

        client = ElevenLabs(api_key=get_key("ELEVENLABS_API_KEY"))

        # 接口签名以官方 SDK 当时版本为准；下面是占位形态
        audio = client.music.compose(
            prompt=spec.prompt,
            music_length_ms=spec.duration_s * 1000,
        )

        out_dir = Path(spec.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "elevenlabs_music.mp3"
        data = audio if isinstance(audio, (bytes, bytearray)) else b"".join(audio)
        out_path.write_bytes(data)
        return GenerationResult(self.name, spec, output_path=str(out_path))
