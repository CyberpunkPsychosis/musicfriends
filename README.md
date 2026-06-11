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
- [AI 协作音乐制作工作流](docs/workflow.md) —— 角色分工、模块化原则、AI↔FL 交接方式、工具链
- [音乐生成大模型 API 对比](docs/music-api-comparison.md) —— ⚠️ 2026-06 复检后部分结论已过时（MusicGen 首选、Udio 候选已作废），见上面的复检调研
- [以 Ardour 为底座的 AI 驱动编曲软件（设计）](docs/ardour-ai-daw-design.md) —— MCP 桥接架构、分阶段路线、技术风险

## 代码

- [`ai-music/`](ai-music/) —— 大模型生成「口子」：统一调度各家 API，key 走环境变量。
  `python generate.py --list` 看就绪状态，填 `.env` 即可启用。
- [`ardour-ai/`](ardour-ai/) —— AI 驱动 Ardour 的 MCP server（阶段 1）：混音/走带走 OSC，
  编曲走 Lua 命令队列。不依赖 Ardour 的逻辑已 `pytest` 测通（11 passed）。
