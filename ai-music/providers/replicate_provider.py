"""Replicate · MusicGen 家族适配器 —— 对你工作流最契合的一路。

为什么是它：
  - meta/musicgen 支持「旋律条件」(melody_path)：以你的旋律为基础生成编曲
    → 正好对应「旋律我主导，AI 帮音色/编曲」
  - 同账号还能跑 musicgen-chord（和弦条件）、musicgen-stem（分轨生成/编辑）
  - 一个 REPLICATE_API_TOKEN 通多个模型，按秒计费，便宜

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
    blurb = "MusicGen：支持旋律条件/和弦条件/分轨，最契合本工作流"
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
