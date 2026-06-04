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

# 路由优先级：出"声音"时，按这个顺序选第一个已配置 key 的专业模型。
# 原则：专业音乐模型 > 通用；MusicGen 因支持旋律/和弦条件、最契合工作流而居首。
PRIORITY: tuple[str, ...] = ("replicate", "stable_audio", "elevenlabs", "suno")


def get_provider(name: str) -> MusicProvider:
    try:
        return _REGISTRY[name]
    except KeyError:
        raise SystemExit(
            f"未知 provider「{name}」。可选：{', '.join(_REGISTRY)}"
        )


def all_providers() -> list[MusicProvider]:
    return list(_REGISTRY.values())


def preferred_provider(priority: tuple[str, ...] = PRIORITY) -> MusicProvider | None:
    """返回优先级最高且**已配置 key**的专业音频模型；都没配则 None。

    体现分工原则：key 配好后，出声音优先调专业模型，而不是用我（Claude）兜底。
    """
    for name in priority:
        p = _REGISTRY.get(name)
        if p and p.is_configured():
            return p
    return None


__all__ = [
    "MusicProvider", "MusicSpec", "GenerationResult", "MissingAPIKey",
    "get_provider", "all_providers", "preferred_provider", "PRIORITY",
]
