"""ACE-Step 1.5 适配器 —— 自建路线（2026-06 复检后的新核心引擎）。

为什么是它（见 docs/research-2026-06.md）：
  - MIT 协议，输出可商用；2B 模型 6-8GB 显存可跑，4090 整曲 <10 秒
  - 一个引擎覆盖：text2music / cover(以你的音频为底换风格)
    / repaint(局部重绘 = 按段重做) / vocal2bgm / stems / LoRA 微调
  - 自带 REST API（uv run acestep-api，默认端口 8001），无按次计费

部署：在有显卡的机器上跑官方 REST server，把基址填进 ACESTEP_API_BASE
（如 http://127.0.0.1:8001）。没有本地卡时也可指向局域网/云上的实例。

接口已按官方 docs/en/API.md 对齐（/release_task → /query_result → /v1/audio）：
https://github.com/ace-step/ACE-Step-1.5/blob/main/docs/en/API.md
"""
from __future__ import annotations

import json
import time
from pathlib import Path

from .base import MusicProvider, MusicSpec, GenerationResult
from .config import get_key


def build_task_fields(spec: MusicSpec) -> dict:
    """MusicSpec -> /release_task 的表单字段（纯函数，便于单测）。

    任务类型路由：
      region + source_audio  -> repaint（只重绘该区间，其它不动）
      melody_path            -> cover（以你的哼唱/旋律为底，AI 围绕它编曲）
      否则                    -> text2music
    """
    fields: dict = {
        "prompt": spec.prompt,
        "audio_duration": float(spec.duration_s),
        "audio_format": "wav",
    }
    if spec.bpm:
        fields["bpm"] = int(spec.bpm)
    if spec.seed is not None:
        fields["seed"] = int(spec.seed)
    if spec.instrumental:
        # 纯器乐：空歌词 + 标签（ACE-Step 用 [instrumental] 约定）
        fields["lyrics"] = "[instrumental]"

    if spec.region and spec.source_audio:
        start_s, end_s = spec.region
        fields["task_type"] = "repaint"
        fields["repainting_start"] = float(start_s)
        fields["repainting_end"] = float(end_s)
        # repaint 的时长以原曲为准，区间只是重绘窗口
        fields.pop("audio_duration", None)
    elif spec.melody_path:
        fields["task_type"] = "cover"
        # 越低越贴原旋律；0.5 = 保留骨架、重做编曲（可按需暴露成参数）
        fields["audio_cover_strength"] = 0.5
    else:
        fields["task_type"] = "text2music"
    return fields


class AceStepProvider(MusicProvider):
    name = "ace_step"
    required_env = ("ACESTEP_API_BASE",)
    blurb = "ACE-Step 1.5：开源可商用，cover/repaint/vocal2bgm 全能（自部署）"
    supports_melody = True   # cover / vocal2bgm：吃你的哼唱/旋律去编曲
    supports_inpaint = True  # repaint：只重绘 region 区间

    poll_interval_s = 2.0
    timeout_s = 600.0

    def generate(self, spec: MusicSpec) -> GenerationResult:
        self.ensure_configured()
        try:
            import requests
        except ImportError as e:
            raise RuntimeError("缺少依赖：pip install requests") from e

        base = get_key("ACESTEP_API_BASE").rstrip("/")
        fields = build_task_fields(spec)

        # 带音频的任务走 multipart 上传；纯文本任务走 JSON
        files = {}
        if fields.get("task_type") == "repaint":
            files["src_audio"] = open(spec.source_audio, "rb")
            if spec.melody_path:  # repaint 同时给旋律参考也可以
                files["reference_audio"] = open(spec.melody_path, "rb")
        elif fields.get("task_type") == "cover":
            files["src_audio"] = open(spec.melody_path, "rb")

        try:
            if files:
                r = requests.post(f"{base}/release_task", data=fields, files=files, timeout=120)
            else:
                r = requests.post(f"{base}/release_task", json=fields, timeout=120)
        finally:
            for f in files.values():
                f.close()
        r.raise_for_status()
        task_id = r.json()["data"]["task_id"]

        result = self._wait(base, task_id, requests)
        return self._download(base, result, spec, requests)

    def _wait(self, base: str, task_id: str, requests) -> dict:
        """轮询 /query_result 直到任务完成（status: 0=排队/运行 1=成功 2=失败）。"""
        deadline = time.monotonic() + self.timeout_s
        while time.monotonic() < deadline:
            r = requests.post(f"{base}/query_result",
                              json={"task_id_list": [task_id]}, timeout=30)
            r.raise_for_status()
            entry = r.json()["data"][0]
            if entry["status"] == 1:
                items = json.loads(entry["result"])
                return items[0]
            if entry["status"] == 2:
                raise RuntimeError(f"ACE-Step 任务失败: {entry}")
            time.sleep(self.poll_interval_s)
        raise TimeoutError(f"ACE-Step 任务 {task_id} 超时（{self.timeout_s}s）")

    def _download(self, base: str, item: dict, spec: MusicSpec, requests) -> GenerationResult:
        file_url = item["file"]  # 形如 /v1/audio?path=...
        if file_url.startswith("/"):
            file_url = base + file_url
        r = requests.get(file_url, timeout=300)
        r.raise_for_status()
        out_dir = Path(spec.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / "ace_step.wav"
        out_path.write_bytes(r.content)
        return GenerationResult(self.name, spec, output_path=str(out_path), raw=item)
