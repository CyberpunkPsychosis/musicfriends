"""Provider 注册表：名字 -> 适配器实例。

加一家大模型 = 写个适配器 + 在这里登记一行。
"""
from .base import MusicProvider, MusicSpec, GenerationResult, MissingAPIKey
from .replicate_provider import ReplicateProvider
from .stable_audio import StableAudioProvider
from .elevenlabs import ElevenLabsProvider
from .suno import SunoProvider

_REGISTRY: dict[str, MusicProvider] = {
    p.name: p for p in (
        ReplicateProvider(),
        StableAudioProvider(),
        ElevenLabsProvider(),
        SunoProvider(),
    )
}


def get_provider(name: str) -> MusicProvider:
    try:
        return _REGISTRY[name]
    except KeyError:
        raise SystemExit(
            f"未知 provider「{name}」。可选：{', '.join(_REGISTRY)}"
        )


def all_providers() -> list[MusicProvider]:
    return list(_REGISTRY.values())


__all__ = [
    "MusicProvider", "MusicSpec", "GenerationResult", "MissingAPIKey",
    "get_provider", "all_providers",
]
