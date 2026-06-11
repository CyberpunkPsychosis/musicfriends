"""Replicate · MusicGen 家族适配器 —— ⚠️ 2026-06 复检后降级为实验项。

降级原因（docs/research-2026-06.md）：
  - MusicGen 权重为 CC-BY-NC，**输出不可商用**
  - 只能出 30 秒级片段、32kHz，旋律遵循度一般
  - 同等能力已被 ACE-Step 1.5（MIT 可商用、整曲、repaint）覆盖 → 优先用 ace_step
保留价值：旋律条件的对照实验、无本地显卡且只想快速试听时的兜底。

docs: https://replicate.com/meta/musicgen
"""
from __future__ import annotations

from pathlib import Path

from .base import MusicProvider, MusicSpec, GenerationResult
from .config import get_key

# 可按需替换为带版本号的具体模型；不带版本会用最新版
MODEL = "meta/musicgen"


class ReplicateProvider(MusicProvider):
    name = "replicate"
    required_env = ("REPLICATE_API_TOKEN",)
    blurb = "MusicGen：旋律条件（⚠️输出不可商用，已降级为实验项，优先用 ace_step）"
    supports_melody = True   # MusicGen-melody：吃你的旋律去编曲

    def generate(self, spec: MusicSpec) -> GenerationResult:
        self.ensure_configured()
        try:
            import replicate  # pip install replicate
        except ImportError as e:
            raise RuntimeError("缺少依赖：pip install replicate") from e

        client = replicate.Client(api_token=get_key("REPLICATE_API_TOKEN"))

        prompt = spec.prompt
        if spec.bpm:
            prompt += f", {spec.bpm} BPM"
        if spec.genre:
            prompt += f", {spec.genre}"

        model_input: dict = {
            "prompt": prompt,
            "duration": spec.duration_s,
            "output_format": "wav",
        }
        if spec.seed is not None:
            model_input["seed"] = spec.seed
        # 「旋律条件」：把你的旋律喂进去，AI 围绕它编曲
        if spec.melody_path:
            model_input["input_audio"] = open(spec.melody_path, "rb")
            model_input["continuation"] = False
            model_input["model_version"] = "stereo-melody-large"

        output = client.run(MODEL, input=model_input)

        # output 可能是 URL 或文件对象，统一落地
        out_dir = Path(spec.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "replicate_musicgen.wav"
        try:
            data = output.read() if hasattr(output, "read") else None
            if data:
                out_path.write_bytes(data)
                return GenerationResult(self.name, spec, output_path=str(out_path))
        except Exception:
            pass
        return GenerationResult(self.name, spec, url=str(output), raw={"output": str(output)})
