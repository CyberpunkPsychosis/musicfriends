"""Stable Audio (Stability AI) 适配器 —— 官方 API，EDM 器乐质感好。

能力：text-to-audio、audio-to-audio、局部重绘(inpainting)、商用授权清晰。
新账号有 $5–25 试用额度。

docs: https://platform.stability.ai/  （生成接口的确切路径/模型 id 以官方文档为准）
TODO(接 key 后核对): endpoint 路径、字段名、返回格式按当时文档微调。
"""
from __future__ import annotations

from pathlib import Path

from .base import MusicProvider, MusicSpec, GenerationResult
from .config import get_key

# 以官方文档为准；这里给出占位，接 key 时核对一次即可
API_URL = "https://api.stability.ai/v2beta/audio/stable-audio-2/text-to-audio"


class StableAudioProvider(MusicProvider):
    name = "stable_audio"
    required_env = ("STABILITY_API_KEY",)
    blurb = "Stable Audio：官方 API，器乐 EDM + audio-to-audio + 局部重绘"

    def generate(self, spec: MusicSpec) -> GenerationResult:
        self.ensure_configured()
        try:
            import requests  # pip install requests
        except ImportError as e:
            raise RuntimeError("缺少依赖：pip install requests") from e

        prompt = spec.prompt
        if spec.bpm:
            prompt += f", {spec.bpm} BPM"

        headers = {
            "authorization": f"Bearer {get_key('STABILITY_API_KEY')}",
            "accept": "audio/*",
        }
        data = {
            "prompt": prompt,
            "duration": spec.duration_s,
            "output_format": "wav",
        }
        if spec.seed is not None:
            data["seed"] = spec.seed

        resp = requests.post(API_URL, headers=headers, files={"none": ""}, data=data, timeout=300)
        resp.raise_for_status()

        out_dir = Path(spec.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "stable_audio.wav"
        out_path.write_bytes(resp.content)
        return GenerationResult(self.name, spec, output_path=str(out_path))
