"""环境变量 / .env 读取。所有 API key 的唯一入口。"""
from __future__ import annotations

import os
from pathlib import Path

_loaded = False


def _load_dotenv_once() -> None:
    """若同级有 .env，自动加载（python-dotenv 可选，没装就手动解析）。"""
    global _loaded
    if _loaded:
        return
    _loaded = True
    env_path = Path(__file__).resolve().parent.parent / ".env"
    if not env_path.exists():
        return
    try:
        from dotenv import load_dotenv  # type: ignore
        load_dotenv(env_path)
        return
    except ImportError:
        pass
    # 极简手动解析，避免硬依赖
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


def get_key(name: str) -> str | None:
    _load_dotenv_once()
    val = os.environ.get(name)
    return val if val else None


def has_keys(names: tuple[str, ...]) -> bool:
    return all(get_key(n) for n in names)


def missing_keys(names: tuple[str, ...]) -> list[str]:
    return [n for n in names if not get_key(n)]
