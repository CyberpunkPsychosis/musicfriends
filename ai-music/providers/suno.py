"""Suno 适配器 —— 整首+人声最强，仅用来出「参考 vibe」。

⚠️ 重要：Suno 没有官方开发者 API。只能走第三方包装服务（sunoapi.org / GoAPI /
apiframe / EvoLink 等），按首计费（~$0.02–0.15），且存在合规/法律风险。
生产环境慎用；个人找灵感、出参考音频时可用。

通过环境变量同时指定「服务商基址」和「key」，避免把任何一家写死：
  SUNO_API_BASE  例如 https://api.sunoapi.org
  SUNO_API_KEY
TODO(接 key 后核对): 不同第三方的路径/字段不一致，按你选的那家文档对齐。
"""
from __future__ import annotations

import time
from pathlib import Path

from .base import MusicProvider, MusicSpec, GenerationResult
from .config import get_key


class SunoProvider(MusicProvider):
    name = "suno"
    required_env = ("SUNO_API_BASE", "SUNO_API_KEY")
    blurb = "Suno（第三方包装）：整首+人声参考，⚠️无官方API、有合规风险"

    def generate(self, spec: MusicSpec) -> GenerationResult:
        self.ensure_configured()
        try:
            import requests
        except ImportError as e:
            raise RuntimeError("缺少依赖：pip install requests") from e

        base = get_key("SUNO_API_BASE").rstrip("/")
        headers = {"Authorization": f"Bearer {get_key('SUNO_API_KEY')}"}
        payload = {
            "prompt": spec.prompt,
            "make_instrumental": spec.instrumental,
            "wait_audio": False,
        }
        # 提交任务（路径示意，按所选服务商文档调整）
        r = requests.post(f"{base}/api/generate", json=payload, headers=headers, timeout=60)
        r.raise_for_status()
        job = r.json()

        return GenerationResult(
            self.name, spec,
            url=str(job.get("audio_url") or ""),
            raw=job,
        )
