# 音乐生成大模型 API 对比（2026 年中调研）

针对本项目工作流的选型：**EDM / 旋律我主导 / 痛点是音色与节奏 / 要整首参考 + 按段重做。**

## 总览

| 平台 | 官方 API | 对本工作流的价值 | 价格 / 门槛 | env 变量 |
|---|---|---|---|---|
| **Replicate · MusicGen** ⭐ | ✅ 官方统一 API | **最契合**：旋律条件 / 和弦条件 / 分轨(stem)生成与编辑；一把 key 多模型 | 按秒计费，便宜 | `REPLICATE_API_TOKEN` |
| **Stable Audio**（Stability AI） | ✅ 官方 API | 器乐 EDM 质感好，audio-to-audio + 局部重绘，商用清晰 | 新号 $5–25 试用额度 | `STABILITY_API_KEY` |
| **ElevenLabs Music v2** | 🟡 逐步开放（v1 已有，v2 企业先行） | 录音室级，**API 层支持段落重绘** | 自助 API 刚铺开 | `ELEVENLABS_API_KEY` |
| **Google Lyria 2** | ✅ Vertex AI GA | 48kHz 立体声，可控 BPM/乐器 | 需 GCP 工程+鉴权，偏企业 | （走 Vertex，暂未接） |
| **Suno** | ❌ 无官方 API | 整首+人声最强，做"参考 vibe" | 第三方 ~$0.02–0.15/首，**有合规风险** | `SUNO_API_BASE` + `SUNO_API_KEY` |
| **Udio** | ❌ 无官方 API | 段落重绘(inpainting)强 | 第三方，**有合规风险** | （第三方，暂未接） |

## 选型建议（优先级）

1. **Replicate（MusicGen-melody / -chord / -stem）** —— 旋律条件直接命中"旋律我主导"，
   还能出分轨，一个 key 多模型，最便宜。**第一个接。**
2. **Stable Audio** —— 官方、试用额度、EDM 器乐、能局部重绘。第二路。
3. **Suno（经第三方）** —— 只用来出"整首参考音频"找灵感；⚠️ 无官方 API、有法律风险，生产慎用。
4. **ElevenLabs / Lyria** —— 等自助 API 完全铺开 / 需要企业级时再接。

## 关键能力对照（对应你的痛点）

- **旋律条件**（"旋律我主导，AI 帮编曲"）：MusicGen-melody 能接你的旋律音频，
  剥离鼓与 bass、提取主音高，围绕你的旋律生成 → 首选 Replicate。
- **按段重做 / 段落重绘**（如只重写 buildup）：Stable Audio 的 inpainting、
  ElevenLabs/Udio 的 inpainting；MusicGen-Stem 支持逐分轨生成与编辑。
- **整首参考 vibe**：Suno 最强（人声+完整制作），但仅作灵感参考。
- **音色**：注意大模型出的是"成品音频"，不携带可换的音色工程；
  真正在 FL 里换音色仍靠 MIDI + 你的合成器（见 workflow.md §4）。

## 落地

代码"口子"已就位：见 [`../ai-music/`](../ai-music/)。
`python generate.py --list` 可查就绪状态，填 `.env` 即可启用任意一家。

## 来源

- [Suno Pricing 2026 / We Compare AI](https://www.wecompareai.com/pricing/suno)
- [Top 7 Suno API Providers 2026 / FontsArena](https://fontsarena.com/blog/top-7-suno-api-providers-for-ai-music-generation-in-2026/)
- [Stable Audio 3.0 / Stability AI](https://stability.ai/stable-audio)
- [Stable Audio 2.5 API / Pixazo](https://www.pixazo.ai/models/audio-generation/stable-audio-2-5-api)
- [Eleven Music, now available in the API / ElevenLabs](https://elevenlabs.io/blog/eleven-music-now-available-in-the-api)
- [Eleven Music docs / ElevenLabs](https://elevenlabs.io/docs/overview/capabilities/music)
- [Udio API for Developers / MusicAPI.ai](https://musicapi.ai/udio-api)
- [meta/musicgen on Replicate](https://replicate.com/meta/musicgen)
- [MusicGen-Chord / Replicate blog](https://replicate.com/blog/generate-music-from-chord-progressions-musicgen-chord)
- [Lyria on Vertex AI / Google Cloud docs](https://docs.cloud.google.com/vertex-ai/generative-ai/docs/music/overview)
- [Announcing Lyria 2 on Vertex AI / Google Cloud blog](https://cloud.google.com/blog/products/ai-machine-learning/announcing-veo-3-imagen-4-and-lyria-2-on-vertex-ai)
