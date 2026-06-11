# musicfriends

> 新方向：**AI 协作的 EDM 音乐制作工作流** —— 你是创意总监，AI 包掉重复的技术劳动。

原「音乐分享交友网站」代码已不再沿用，完整保留在 git 历史中：

```bash
git log --oneline              # 查看历史提交
git checkout <旧commit> -- .   # 取回旧版本的文件
```

## 文档

- **[2026-06 复检调研](docs/research-2026-06.md)** —— 最新格局（Suno v5.5 / ACE-Step 1.5 / Ardour 官方 MCP 等）、
  三条推荐路线、仓库改造清单。**选型以此为准**。
- **[对话驱动 DAW 接入指南](docs/daw-mcp-setup.md)** —— 路线 ③：REAPER / Ableton 的现成 MCP 怎么配，Ardour 现状
- [AI 协作音乐制作工作流](docs/workflow.md) —— 角色分工、模块化原则、AI↔FL 交接方式、工具链
- [音乐生成大模型 API 对比](docs/music-api-comparison.md) —— ⚠️ 2026-06 复检后部分结论已过时（MusicGen 首选、Udio 候选已作废），见上面的复检调研
- [以 Ardour 为底座的 AI 驱动编曲软件（设计）](docs/ardour-ai-daw-design.md) —— MCP 桥接架构、分阶段路线、技术风险

## 代码

- [`ai-music/`](ai-music/) —— 路线 ②（可控+可商用）的管线：
  - `generate.py` —— 统一调度各家模型（**首选 ace_step**，`--list` 看就绪状态，填 `.env` 启用）
  - `hum2midi.py` —— **灵感入口**：你的哼唱 → 可编辑 MIDI + BPM/调性
  - `regenerate.py` —— 按段重做（ACE-Step repaint 真 inpaint，`splice.py` 等功率拼接兜底）
  - `stems.py` —— 整首拆分轨（audio-separator / RoFormer 系 SOTA）
- [`ardour-ai/`](ardour-ai/) —— 符号层（与 DAW 无关，继续主用）：EDM 作曲助手、段落级模块化、
  无依赖 MIDI 写入、试听渲染 + Ardour OSC 走带/混音。
  ⚠️ Lua 编曲桥已冻结，「对话驱动 DAW」见 [docs/daw-mcp-setup.md](docs/daw-mcp-setup.md)。
