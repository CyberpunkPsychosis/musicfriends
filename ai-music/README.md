# ai-music — 大模型生成「口子」

统一调度各家音乐生成大模型的薄抽象层。**换一家 = 换一个 `--provider`，其它不动。**
所有 API key 走环境变量，绝不进仓库。

## 现在就能做（不用 key）

```bash
cd ai-music
python generate.py --list      # 看哪些 provider 就绪 / 哪些待填 key
```

## 拿到 key 后

```bash
cp .env.example .env           # 填入任意一家的 key
pip install -r requirements.txt

python generate.py --provider replicate \
    --prompt "140 BPM melodic dubstep, dark intro to euphoric drop" \
    --bpm 140 --duration 30

# 以你自己的旋律为基础生成编曲（旋律你主导）：
python generate.py --provider replicate --prompt "..." --melody my_lead.wav
```

## 各家现状（2026 年中）

| provider | 官方 API | 亮点 | env |
|---|---|---|---|
| `replicate` ⭐ | ✅ | MusicGen：旋律/和弦/分轨条件，最契合本工作流 | `REPLICATE_API_TOKEN` |
| `stable_audio` | ✅ | 官方，EDM 器乐 + audio-to-audio + 局部重绘 | `STABILITY_API_KEY` |
| `elevenlabs` | 🟡 逐步开放 | 录音室级，API 支持段落重绘 | `ELEVENLABS_API_KEY` |
| `suno` | ❌ 仅第三方 | 整首+人声参考，⚠️有合规风险 | `SUNO_API_BASE` + `SUNO_API_KEY` |

> Google Lyria 2 也有官方 API，但走 Vertex AI（GCP 工程+鉴权），偏企业，暂未加适配器，需要时再加。

## 加一家新模型

1. 在 `providers/` 写个继承 `MusicProvider` 的适配器
2. 在 `providers/__init__.py` 登记一行
3. 在 `.env.example` 加上它的 env 变量

详见上层 [`docs/workflow.md`](../docs/workflow.md) 与 [`docs/music-api-comparison.md`](../docs/music-api-comparison.md)。
