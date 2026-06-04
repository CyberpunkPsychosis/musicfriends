# 设计文档：以 Ardour 为底座的 AI 驱动编曲软件

> 状态：设计阶段（蓝图）。本会话环境为临时容器，决策落仓库以便跨会话延续。
> 目标读者：未来的你 + 未来的 AI 会话。

---

## 1. 愿景

把开源 DAW **Ardour** 当底座，搭一层 **MCP**，让你在对话里就能驱动它编曲：
AI 在活的工程里加轨、写旋律、搭 buildup、调混音，**你盯着屏幕实时看、随时接管**。

相比之前 FL 的"文件交换"方案，这个形态更优：不是"AI 出文件→你导入"，
而是**我们操作同一个活工程**，省掉来回导入导出。FL 路线降级为可选/并行。

---

## 2. 为什么是 Ardour（选型依据）

| 特性 | 意义 |
|---|---|
| **开源（GPLv2）** | 自由改用；我们的外挂层可自由开发 |
| **会话是 XML**（`.ardour`） | AI 能直接读/写工程结构（FL 的 `.flp` 是闭源二进制，做不到） |
| **内置 Lua 脚本** | 能钻进会话内部：创建 MIDI 轨、写音符/region、加插件、画自动化 —— **编曲的关键** |
| **内置 OSC** | 网络远程控制走带与混音：play/stop、推子、mute/solo、插件参数 |
| **官方正在做 MCP** | Ardour 9.3 将自带 MCP server —— 项目本身就朝这个方向走，可借势 |

---

## 3. 关键决策：搭桥，不 fork（ADR）

- **否决：fork Ardour 的 C++ 改源码重编译。** 代价极大（C++、编译数小时、难维护），
  且绝大多数需求用现成接口就能满足。
- **采用：不动 C++，在 Ardour 现成接口上搭一层 MCP。** 三条通道分工：

| 能力 | 通道 | 现状 |
|---|---|---|
| 走带 / 混音 / 插件参数 | **OSC**（UDP 3819） | ✅ 已有社区 MCP 做了（`Ron-312`、`pyroqbit`），可复用 |
| **编曲：建轨、写音符、加 buildup、换音色** | **Lua 脚本** | ⬜ **空白 = 我们的核心价值** |
| 离线生成 / 批量改工程 | **`.ardour` XML 读写** | ⬜ 辅助手段 |

> 调研确认：现有 Ardour MCP **只覆盖 OSC 那层**（走带+混音+插件参数），
> **不能创建 MIDI 轨、不能写音符、不碰编曲**。所以"AI 编曲"是真正的空白区。

---

## 4. 部署拓扑（很重要）

```
你的 Mac（本地）                         云端（本会话）
┌─────────────────────────────┐         ┌────────────────────┐
│  Ardour (开着，你盯着改)      │         │  Claude (我)        │
│     ▲ OSC / Lua             │         │  - 写代码           │
│     │                       │         │  - 提交仓库         │
│  MCP server (本地进程)       │         │  - 单元测试无需      │
│     ▲ MCP                   │         │    Ardour 的部分    │
│     │                       │         └────────────────────┘
│  本地 Claude 客户端          │
│  (Claude Desktop / Code)    │  ← 你在这里聊天，驱动本地 Ardour
└─────────────────────────────┘
```

- **运行在你的 Mac 上**：Ardour 要声卡/显示，云容器跑不了。
- **本会话的我负责"造"，本地的 Claude 负责"用"**：我在这里把 MCP server + Lua 脚本
  写好提交；你拉到本地，配进本地 Claude 客户端，就能边聊边驱动 Ardour。
- **端到端实测在你本地做**：本会话连不到你的 Ardour；但不依赖 Ardour 的逻辑
  （OSC 消息构造、Lua 脚本生成、XML 解析）我在云端就能单元测试。

---

## 5. 计划暴露的 MCP 工具（草图）

**混音/走带（OSC，复用现有）**
`play` `stop` `locate` `set_fader(track,db)` `mute(track)` `solo(track)` `set_plugin_param`

**编曲（Lua，我们要做的核心）**
`set_tempo(bpm)` `add_midi_track(name)` `add_audio_track(name)`
`write_region(track, start, notes[])`  ← 把 MIDI 写进工程
`add_plugin(track, "Surge XT")` `set_automation(track, param, points[])`
`regenerate_section(section, spec)`  ← 只重做 buildup 等某一段
`import_audio(track, file)`  ← 接大模型产出的音频/stems

**与已有仓库件衔接**
- `ai-music/`（大模型口子）→ 先出 MIDI/音频 → 经 `write_region`/`import_audio` 进工程
- `docs/workflow.md`（角色分工/模块化）→ 这套工具按"段×轨"粒度，正好支持按段重做

---

## 6. 技术风险点（需在阶段 1 先验证）⚠️

**最大未知：MCP server 如何触发 Ardour 内的 Lua。**
OSC 默认不能跑任意 Lua。候选机制（阶段 1 做技术验证 spike）：
1. **常驻 Lua 脚本 + 命令队列**：Ardour 里跑一个轮询脚本，读 MCP server 写入的命令文件/队列。
   （Ardour Lua 绑定是沙盒，能否开 socket 待验证，文件队列最稳。）
2. **借力 Ardour 9.3 官方 MCP**：若官方 MCP 暴露了更深的接口，直接扩展它。
3. **离线 XML 批改**：结构性批量改直接写 `.ardour`，再让 Ardour 重载。

其它风险：
- **Lua API 无完整文档**：以 `luabindings.cc` + 官方 Class Reference 为准，需边做边查。
- **实时性不是目标**：我们做的是编曲/结构编辑，不是采样级实时演奏。
- **License**：MCP 是独立进程走网络协议，非衍生作品，干净。仅当向 Ardour 主仓库
  上游贡献代码时才涉及其 AI 政策。

---

## 7. 分阶段路线

- **阶段 0 · 验证链路**（几乎零开发）
  本地装 Ardour → 开 OSC（Preferences ▸ Control Surfaces ▸ OSC，端口 3819）→
  跑现有 OSC-MCP → 在本地 Claude 里说"播放/调推子"，确认链路通。
- **阶段 1 · Lua 编曲层 + IPC 验证**（核心）
  先做 §6 的 spike 定下 Lua 触发机制；再实现 `add_midi_track` / `write_region` / `set_tempo`。
- **阶段 2 · 接大模型口子**
  `ai-music/` 出 MIDI → 直接 `write_region` 进 Ardour；出音频/stems → `import_audio`。

> **MIDI 基础层（已完成，云端可验证）**：`ardour-ai/ardour_ai/midi.py`（无依赖 SMF 写入）
> + `compose.py`（EDM 鼓/和弦/bass 助手）。产出标准 `.mid`，FL/Ardour 都能拖入，
> 已用 mido 回读测通。这层是下面「离线 `.ardour` 生成器」的素材基础。
>
> **关于离线 `.ardour` 生成器（修正预期）**：`.ardour` 是复杂且版本强绑定的 XML，
> 云端只能验证「XML 合法」，无法验证「Ardour 能打开」。**正确做法是模板法**——
> 由你在本地保存一个最简 Ardour 工程，把 `.ardour` 作为模板，我们用脚本往里
> 塞轨道并引用上面生成的 SMF 文件。该步待你能本地 open-test 时再做，避免硬猜 schema。
- **阶段 3 · 远程协作/网页**
  接 Ardour 新出的 web 控制面 + 远程协作，对接你"网页媒介"的想法。

---

## 8. 待办 / 待确认

- [ ] 阶段 0：本地装 Ardour（macOS 版，ardour.org）并跑通现有 OSC-MCP
- [ ] 阶段 1 spike：定下 Lua 触发机制（命令队列 vs 官方 9.3 MCP）
- [ ] 评估 Ardour 9.3 官方 MCP 的接口深度，决定"扩展它"还是"自建"
- [ ] 本地 Claude 客户端选型：Claude Desktop vs Claude Code（都支持 MCP）

---

## 参考

- [Ardour Lua Scripting 手册](https://manual.ardour.org/lua-scripting/) ·
  [Lua Class Reference](https://manual.ardour.org/lua-scripting/class_reference/)
- [Ardour OSC 控制手册](https://manual.ardour.org/using-control-surfaces/controlling-ardour-with-osc/)
- 现有 MCP：[Ron-312/ardour-mcp](https://github.com/Ron-312/ardour-mcp) ·
  [pyroqbit/ardour-mcp](https://github.com/pyroqbit/ardour-mcp)
- [Ardour：web 控制面与远程协作](https://discourse.ardour.org/t/new-web-based-control-surface-and-remote-collaboration-for-ardour/113241)
