"""ElevenLabs Music 适配器 —— 2026-06 复检后「转正」：商业选项中的第一顺位。

转正依据（docs/research-2026-06.md）：官方 API 已可用，且是目前唯一同时具备
官方 API + 段落级编辑 + stems 分离端点（two_stems/six_stems，返回 ZIP）的商业服务。
docs: https://elevenlabs.io/docs/overview/capabilities/music
      https://elevenlabs.io/docs/api-reference/music/separate-stems
TODO(接 key 后核对): SDK 的 music 接口签名与 stems 端点参数以当时文档为准。
"""
from __future__ import annotations

from pathlib import Path

from .base import MusicProvider, MusicSpec, GenerationResult
from .config import get_key


class ElevenLabsProvider(MusicProvider):
    name = "elevenlabs"
    required_env = ("ELEVENLABS_API_KEY",)
    blurb = "Eleven Music：官方 API + 段落编辑 + stems 端点，商业选项第一顺位"
    supports_inpaint = True  # API 层 inpainting：段落重绘

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
