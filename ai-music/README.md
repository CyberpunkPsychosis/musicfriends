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

# 自动路由：选优先级最高且已配置 key 的专业模型（出声音优先专业模型）
python generate.py --auto --prompt "140 BPM melodic dubstep, dark to euphoric"

# 或指定一家：
python generate.py --provider replicate \
    --prompt "140 BPM melodic dubstep, dark intro to euphoric drop" \
    --bpm 140 --duration 30

# 以你自己的旋律为基础生成编曲（旋律你主导）：
python generate.py --provider replicate --prompt "..." --melody my_lead.wav
```

> **路由原则**：出"声音"优先调专业模型（`--auto` 按 `PRIORITY` 选已配置的，
> MusicGen 居首）；要**可编辑 MIDI** 仍走符号路（`../ardour-ai/`，无需 key）。

## 段落重生成（音频路的模块化）

对应你的迭代循环："改好 drop 的旋律 → 让大模型用我的旋律只重生成这一段 → 拼回原曲"。

- **能力声明**：`provider.supports_melody`（旋律条件）/ `supports_inpaint`（段落重绘），
  `--list` 会显示。MusicGen=🎹旋律条件；Stable Audio / ElevenLabs=✂️段落重绘。
- **`MusicSpec.region=(start_s, end_s)` + `melody_path` + `source_audio`**：描述"只重生成
  哪一段、以哪段旋律为条件、在哪条原曲上"。`provider.regenerate_section(spec)` 调用。
- **`splice.py`**：把"新生成的一段"等功率交叉淡化**拼回原曲**，区间外**逐样本不变**
  （已单测保证）。`replace_region_in_file(原曲, 新段, start_s, end_s, 输出)`。

> 模型调用需 key（口子就绪）；拼接器 `splice.py` 不需要 key、已测通，是"只换这一段"的保证。

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
