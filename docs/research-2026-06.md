# 调研：2026-06 复检 —— 更快更好的「灵感 + AI 协作编曲」方案

> 目的：检验本仓库现有方案（ai-music 调度层 + ardour-ai MCP）是否仍是最优路线，
> 并给出"用自己的灵感（哼唱/旋律）和 AI 一起编曲、可按段重做"的最快落地方案。
> 调研日期：2026-06-10/11，关键事实均经多源核实（来源见各节）。

---

## 一、结论先行

1. **「哼唱 → 保留旋律的完整编曲 → 按段重做 → 拆 stems/MIDI 回 DAW」这条链路，
   市面上已经有成品**（Suno v5.5 全家桶），不再需要从零自建。
2. **开源侧出现了决定性新引擎：ACE-Step 1.5**（MIT 可商用、8GB 显存可跑、
   原生支持 repaint 局部重绘 / cover / vocal-to-BGM / stems / LoRA 微调）——
   它一个模型就覆盖了我们 providers 层想拼出来的大部分能力，应取代 MusicGen 成为自建路线的核心。
3. **Ardour 自建 Lua 编曲桥这条线应当冻结**：Ardour 9.5（2026-05-21）官方 MCP 已落地
   但只面向无障碍/控制，不做编曲；而 Ableton/REAPER 的社区 MCP 已能建轨+写音符+加载乐器，
   成熟度远超我们自研进度。"AI 直接驱动 DAW"应换底座或等官方接口加深。
4. 仓库里**真正值得保留的资产**：段落级模块化（song.py）、拼接器（splice.py）、
   无依赖 MIDI 层（midi.py）、provider 路由框架——它们与新引擎正交，继续复用。
5. 文档 `music-api-comparison.md` 的选型结论已过时（MusicGen 首选、Udio 候选、Suno 仅参考），
   本文档为其修订依据。

---

## 二、关键事实更新（vs 仓库现有文档）

### 商业服务

| 服务 | 现状（2026-06） | 对本工作流的意义 |
|---|---|---|
| **Suno** | v5.5（2026-03-26）。**仍无官方 API**（所有"Suno API"都是第三方逆向，有 ToS 风险）。产品端能力完整：**Covers**（上传哼唱→保留旋律换风格出完整编曲）、**Replace Section**（框选 10-30 秒段落重写 = inpaint，Pro/Premier）、**12-stem 拆分 + MIDI/Tempo-locked WAV 导出**（Pro $10/月起）、**Suno Studio** 浏览器 GAW（Premier $24/月）。Warner 已和解（授权模型 2026 内上线），UMG/Sony 诉讼 2026-07 关键听证 | 作为**产品**用，几乎就是我们要造的东西；作为 **API** 接入仍不可行，仓库里 `suno.py` 维持"高风险第三方"定位或移除 |
| **Udio** | **出局**。UMG 和解后禁止下载（音频/stems 全部），转"围墙花园"，产出不可导出 | 从一切计划中删除 |
| **ElevenLabs Music** | **官方 API 已可用**，含 **stem separation 端点**（two_stems / six_stems，返回 ZIP） | `elevenlabs.py` 可以"转正"，是目前**唯一同时有官方 API + 段落级编辑 + stems** 的商业选项 |
| **Stable Audio** | 3.0 家族（2026-05）：Large 企业授权；**Medium/Small 开放权重**。官方无 stems。2.5 走 API/fal/Replicate，有 inpaint 端点 | 仍可作器乐素材/段落 inpaint 的第二路；`stable_audio.py` 端点需按 3.0 文档重对 |
| **Google Lyria 3** | Gemini API/Vertex 可用，最长 3 分钟，无 stems；Riffusion→ProducerAI 已被 Google 收购（2026-02） | 暂不接 |
| **Mureka** | O2/V8。支持哼唱作 motif、参考曲模式；**Premier 档可导出 MIDI+stems+WAV**；有官方 API（含 /v1/song/stem） | Suno 之外的备选，且**有官方 API**，可列为候选 provider |

### 开源/本地模型

| 模型 | 许可证/硬件 | 能力 | 判断 |
|---|---|---|---|
| **ACE-Step 1.5 / 1.5 XL**（2026-01/04） | **MIT，输出可商用**；2B 模型 6-8GB VRAM 起，A100 整曲 <2s，4090 <10s | text2music（10s–10min）、**repaint 局部重绘**、cover、extend、**vocal-to-BGM（人声/哼唱自动配伴奏）**、**stems**、audio2audio、**LoRA 微调（8 首歌、3090 上 1 小时）**；ComfyUI 原生节点、VST3、REST API | **自建路线新核心**，一个引擎替代我们 4 个 provider 想拼的能力 |
| MusicGen-melody（现首选） | 权重 **CC-BY-NC 不可商用**；30 秒级片段 | 旋律条件（chromagram，遵循度一般） | **降级为实验备份**。`music-api-comparison.md` 的"第一个接"结论作废 |
| YuE | Apache 2.0 可商用；官方建议 80GB（社区量化 6-16GB），慢 | 全曲带人声、双轨（vocal+inst）输出、ICL 参考 | 关注即可，重、停更（2025-06 后无代码更新） |
| DiffRhythm v1.2 / 2 | Apache 2.0；8GB VRAM；**全曲 ~10 秒生成** | 全曲、参考音频风格、v1.2 支持编辑/续写；无 stems | 快速出"整首参考 vibe"的免费方案 |
| Stable Audio Open / 3 Medium·Small | 开放权重 | 短素材/音效 | 素材库补充 |

### 灵感输入（哼唱 → 系统）

- **哼唱→MIDI**：Spotify **Basic Pitch**（Apache-2.0，事实标准）+ **NeuralNote**（免费 VST3/AU 插件，DAW 内直接用）；多乐器转录前沿是 YourMT3+。FL 用户也可用 Samplab（复音转 MIDI，$7.99/月）。
- **哼唱→直接出编曲**：Suno Covers（最佳体验）/ Mureka motif / ACE-Step vocal-to-BGM（开源）。
- **BPM/调性检测**：librosa 即可（~10 行），ACE-Step 1.5 自带音频理解（BPM/调性/拍号提取）。
- **MIDI 伴奏生成**（给你的旋律配和声/伴奏，纯符号、可编辑）：
  **Anticipatory Music Transformer**（开源，"给定旋律生成伴奏"最对口）、**MIDI-GPT**（AAAI 2025，多轨可控）、
  **Hookpad Aria**（$14.99/月，旋律↔和声互生，可导 MIDI）、Scaler 3 / Lemonaide（已被 BeatStars 收购）。

### Stems 分离（不要自建）

- 官方 Demucs 已归档（2025-01）。SOTA 是 **BS/Mel-Band RoFormer 家族**（MVSEP 榜：vocals SDR ~11.3-11.9 vs Demucs ~8.2）。
- 本地免费跑 SOTA：**UVR5-UI**（v1.8.4，2026-04）或 **MSST-WebUI**；Python 侧用 `audio-separator`（活跃维护）。
- DAW 内置已成标配：FL Studio 21.2+ 内置分轨，FL 2026 beta 有一键 "Remix a song"；Ableton 12.3 / Logic 11.2 同。
- API：Music.AI 8-stem $0.07/min；fal/Replicate 跑 Demucs ~$0.03/曲。

### DAW × AI 集成

| DAW | 现状 | 判断 |
|---|---|---|
| **Ardour** | **9.5（2026-05-21）官方 MCP 落地，但实验性、面向无障碍**（本地 LLM 控制），不写音符不编曲；最新 9.7（2026-06-05） | 我们设计文档预判的"官方 MCP"兑现了，但接口深度不够。**自研 Lua write_notes 收益/成本比已变差** |
| **Ableton Live** | 社区 MCP 最成熟：**ahujasid/ableton-mcp** 2.6k★ 活跃，能建轨、**写 MIDI 音符**、浏览器加载乐器/效果、编排视图；Producer Pal（M4L 内嵌 MCP）获 Anthropic 提名；Live 12 自带哼唱转 MIDI + stems 分离 | "对话驱动 DAW"想立刻可用，**这是事实上的最佳底座**（代价：Standard $439） |
| **REAPER** | ReaScript API 全开放，MCP 项目 40+：TwelveTake-Studios/reaper-mcp（153 工具，2026-06 仍发版）、bonfire-audio（58 工具，建轨/写 MIDI/FX/渲染） | 便宜（$60）+ 可完全脚本化，自建路线的务实底座 |
| **FL Studio** | 官方仅 stems 分离 + AI 母带；**脚本 API 不能写钢琴卷帘**，社区 MCP 全是"虚拟 MIDI 控制器"hack 且已停更 | "AI 直接操作 FL"仍不可行，维持文件交接（MIDI/stems），与 workflow.md §5 结论一致 |

### 音色与母带（痛点 A 的补充弹药）

- **ACE Studio 2.0**（2025-12）：**MIDI → 真人级乐器演奏**（18+ 免版税 AI 乐器）+ 140+ 声库，约 $16.58/月起——"MIDI 不带音色"的最短补丁。
- **Kits.AI**（2026-01 被 Splice 收购）：哼唱→萨克斯/吉他/贝斯等 tone transfer。**Neutone Morpho**（$99 买断）实时音色变形。
- 母带：仓库提过的 **matchering** 仍可用但停更（2022 后无 release）；商业侧 Ozone 12 / LANDR；免费在线 BandLab Mastering。

---

## 三、推荐方案：三层并行，按需取用

> 共同原则不变（workflow.md）：你主导旋律与审美，AI 包技术劳动；一切模块化、按段重做。

### 路线 ①「最快出活」：Suno 当成品引擎，仓库做"进出加工"
```
手机录哼唱 → Suno Covers（保留你的旋律出完整编曲）
  → 不满意的段落用 Replace Section 局部重做
  → 12-stem + MIDI 导出 → FL 精修（你的音色、自动化）
仓库的角色：MIDI 后处理（song.py 段落工具）、stems 清理（串音是已知问题）、母带（matchering）
```
- 成本：Pro $10/月（要 Studio 则 Premier $24/月）。注意：无官方 API，**别试图程序化接入**；
  商用条款随 Warner 协议在变，发行前确认当期条款。

### 路线 ②「可控 + 可商用」：ACE-Step 1.5 为核心的自建管线（本仓库主线）
```
你哼唱/弹一段 → Basic Pitch 转 MIDI（灵感进系统，可编辑）
  → 符号层（已有 compose.py/song.py）铺结构骨架，或 Anticipatory/MIDI-GPT 配伴奏
  → ACE-Step 1.5：vocal2bgm / audio2audio 出整体音频；某段不满意 → repaint 只重绘该段
  → 自家 splice.py 等功率拼接兜底（已生产级）
  → 需要分轨 → ACE-Step stems 或 BS-RoFormer（audio-separator）
  → FL 精修 + matchering 母带
```
- 全链路开源可商用、无订阅；8GB 显存即可，无卡时用 fal/Replicate 的托管端点。
- 这是仓库代码改造的主方向（见第四节）。

### 路线 ③「对话驱动 DAW」：换底座，不再自研 Ardour Lua 桥
- 想立刻体验：**Ableton + ahujasid/ableton-mcp**（能写音符、加载乐器）。
- 预算优先：**REAPER + TwelveTake/bonfire 的 reaper-mcp**。
- Ardour：保留 OSC 走带/混音（已可用），**冻结 write_notes/import_audio 自研**，
  跟踪官方 MCP（9.5+）接口加深后再评估。
- FL 维持"文件交接"，不变。

---

## 四、仓库改造清单（按优先级）

**P0（方向性）**
1. `providers/` 重排：新增 **ace_step.py**（本地 REST / fal 端点双模式，能力声明
   melody=✅(audio2audio/vocal2bgm)、inpaint=✅(repaint)、stems=✅）；置为最高优先级。
2. **elevenlabs.py 转正**：对齐官方 API（compose + stems 端点），列第二优先。
3. **replicate_provider.py（MusicGen）降级**为实验项并标注"输出不可商用"；
   `suno.py` 标注"仅手动产品流，不走 API"或删除。
4. 灵感输入管道：新增 `ai-music/hum2midi.py`（basic-pitch 封装）+ BPM/调性检测（librosa），
   打通"哼唱 → MIDI → 符号层/旋律条件"。

**P1（补强）**
5. `regenerate.py` 对接 ACE-Step repaint（region 参数真正生效，splice.py 作兜底而非唯一手段）。
6. stems：加 `audio-separator` 薄封装（BS-RoFormer 权重），供"只重编某一轨"场景。
7. `ardour-ai/`：冻结 Lua 阶段 1 的 write_notes/import_audio 开发，README 标注现状与替代（路线 ③）。

**P2（文档）**
8. 重写 `docs/music-api-comparison.md`（以本文档为准）；workflow.md §6 工具链表更新
   （加 ACE-Step、Basic Pitch/NeuralNote、audio-separator、ACE Studio；matchering 标注停更但可用）。

---

## 五、主要来源

- Suno：https://suno.com/blog/v5-5 · https://suno.com/blog/covers · https://help.suno.com/en/articles/6141441 · https://help.suno.com/en/articles/3271873
- ACE-Step 1.5：https://github.com/ace-step/ACE-Step-1.5 · https://huggingface.co/ACE-Step · https://docs.comfy.org/tutorials/audio/ace-step/ace-step-v1-5
- Udio 围墙花园：https://help.udio.com/en/articles/12683565 · https://www.musicbusinessworldwide.com/universal-music-settles-udio-lawsuit-strikes-deal-for-licensed-ai-music-platform/
- ElevenLabs stems API：https://elevenlabs.io/docs/api-reference/music/separate-stems
- Stable Audio 3.0：https://stability.ai/stable-audio
- Lyria 3：https://deepmind.google/models/lyria/
- Basic Pitch / NeuralNote：https://github.com/spotify/basic-pitch · https://github.com/DamRsn/NeuralNote
- Anticipatory Music Transformer：https://github.com/jthickstun/anticipation ；MIDI-GPT：https://github.com/Metacreation-Lab/MIDI-GPT
- 分离 SOTA：https://github.com/ZFTurbo/Music-Source-Separation-Training · https://mvsep.com/quality_checker/multisong_leaderboard · https://github.com/Eddycrack864/UVR5-UI （官方 Demucs 已归档：https://github.com/facebookresearch/demucs ）
- Ardour 9.5 官方 MCP（实验性）：https://alternativeto.net/news/2026/5/ardour-9-5-adds-pianoroll-chord-editing-midi-workflow-boosts-and-mcp-server/ · https://ardour.org/whatsnew.html
- Ableton MCP：https://github.com/ahujasid/ableton-mcp ；REAPER MCP：https://github.com/TwelveTake-Studios/reaper-mcp · https://github.com/bonfire-audio/reaper-mcp
- ACE Studio 2.0：https://acestudio.ai/blog/ace-studio-2-released/ ；Kits.AI×Splice：https://www.musicbusinessworldwide.com/splice-acquires-ai-powered-voice-production-platform-kits-ai/
