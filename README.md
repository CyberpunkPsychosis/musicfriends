# musicfriends

> 新方向：**AI 协作的 EDM 音乐制作工作流** —— 你是创意总监，AI 包掉重复的技术劳动。

原「音乐分享交友网站」代码已不再沿用，完整保留在 git 历史中：

```bash
git log --oneline              # 查看历史提交
git checkout <旧commit> -- .   # 取回旧版本的文件
```

## 文档

- [AI 协作音乐制作工作流](docs/workflow.md) —— 角色分工、模块化原则、AI↔FL 交接方式、工具链
- [音乐生成大模型 API 对比](docs/music-api-comparison.md) —— 各家 API 现状、选型建议、来源

## 代码

- [`ai-music/`](ai-music/) —— 大模型生成「口子」：统一调度各家 API，key 走环境变量。
  `python generate.py --list` 看就绪状态，填 `.env` 即可启用。
