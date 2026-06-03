"""统一的音乐生成 provider 抽象。

设计目标：换一家大模型 = 换一个 --provider 参数，其它不动。
所有 API key 走环境变量，绝不写进代码（见 config.py / .env.example）。
"""
from __future__ import annotations

import abc
from dataclasses import dataclass, field
from typing import Optional


class MissingAPIKey(RuntimeError):
    """某 provider 需要的环境变量没设置时抛出，带清晰的指引。"""


@dataclass
class MusicSpec:
    """一次生成请求的统一描述。各 provider 自己挑用得上的字段。"""
    prompt: str                              # 文本描述，如 "140 BPM melodic dubstep, dark to euphoric"
    duration_s: int = 30                     # 时长（秒）
    bpm: Optional[int] = None                # 速度
    genre: Optional[str] = None              # 风格标签
    melody_path: Optional[str] = None        # 你的旋律音频/MIDI —— 用于「旋律条件」生成（你主导旋律）
    chords: Optional[str] = None             # 和弦进行，如 "Am F C G" —— 用于「和弦条件」生成
    instrumental: bool = True                # EDM 默认纯器乐
    seed: Optional[int] = None
    output_dir: str = "output"


@dataclass
class GenerationResult:
    provider: str
    spec: MusicSpec
    output_path: Optional[str] = None        # 落地的音频文件
    url: Optional[str] = None                # 或远端 URL
    raw: dict = field(default_factory=dict)  # provider 原始返回，便于调试

    def __str__(self) -> str:
        where = self.output_path or self.url or "(无输出)"
        return f"[{self.provider}] -> {where}"


class MusicProvider(abc.ABC):
    """所有大模型适配器的基类。"""

    name: str = "base"
    #: 这个 provider 需要的环境变量名（缺一不可）
    required_env: tuple[str, ...] = ()
    #: 一句话能力描述，--list 时显示
    blurb: str = ""

    @abc.abstractmethod
    def generate(self, spec: MusicSpec) -> GenerationResult:
        ...

    # --- 下面是通用逻辑，子类一般不用改 ---

    def is_configured(self) -> bool:
        from .config import has_keys
        return has_keys(self.required_env)

    def ensure_configured(self) -> None:
        from .config import missing_keys
        missing = missing_keys(self.required_env)
        if missing:
            raise MissingAPIKey(
                f"provider「{self.name}」缺少环境变量: {', '.join(missing)}。\n"
                f"  → 在 ai-music/.env 里填上（参考 .env.example），或 export 到环境。\n"
                f"  → key 还没有也没关系，其它已配置的 provider 仍可用：python generate.py --list"
            )
