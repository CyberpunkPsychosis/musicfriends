# 对话驱动 DAW（路线 ③）：用现成 MCP 生态，不再自研 Ardour 桥

> 背景见 [research-2026-06.md](research-2026-06.md) §二「DAW × AI 集成」。
> 结论：Ableton / REAPER 的社区 MCP 已能建轨、**写 MIDI 音符**、加载乐器；
> Ardour 官方 MCP（9.5+）只做无障碍控制不做编曲。自研 Lua write_notes 冻结，换底座。

## 体验是什么样

你开着 DAW + 本地 Claude（Desktop 或 Claude Code），对话即操作：

> "建一条 Bass 轨，写一段 140 BPM melodic dubstep 的低音线，加载一个合成贝斯" —— AI 当场在工程里做完，你看着改。

仓库里 `ai-music/`（音频生成）和 `ardour-ai/` 的符号层（MIDI 生成）继续作为
素材来源：AI 先在对话里产出 MIDI/音频文件，再经 DAW 的 MCP 导入工程。

## 选项 A：REAPER（推荐起步，$60 个人授权）

ReaScript API 全开放（建轨/写 MIDI/FX/渲染都有官方接口），社区 MCP 最务实。

1. 装 [REAPER](https://www.reaper.fm/)（60 天全功能试用，个人授权 $60）。
2. 二选一装 MCP server（都在活跃维护，2026-06 核实）：
   - [TwelveTake-Studios/reaper-mcp](https://github.com/TwelveTake-Studios/reaper-mcp) —— 153 工具，含 takes/FX，发版最勤
   - [bonfire-audio/reaper-mcp](https://github.com/bonfire-audio/reaper-mcp) —— 58 工具，走 python-reapy，含渲染/stems/响度分析
3. 按各自 README 配进 Claude Desktop / Claude Code 的 MCP 配置。
4. 冒烟：对话里说"新建工程，速度 140，加一条 MIDI 轨写 C 小调和弦"——
   能在 REAPER 里看到结果即通。

## 选项 B：Ableton Live（体验最好，Standard $439）

社区 MCP 事实标准 + Live 12 自带哼唱转 MIDI（Convert Melody）与 stems 分离（12.3+，Suite），
正好把灵感输入也包了。

1. 装 [Ableton Live 12](https://www.ableton.com/)（Standard 起；Suite 才有内置分轨）。
2. 装 [ahujasid/ableton-mcp](https://github.com/ahujasid/ableton-mcp)（2.6k★，活跃）：
   一个 Remote Script 进 Live + 一个 MCP server 进 Claude 配置，README 一步步照做。
   能建轨/写音符/从浏览器加载乐器与效果/控制 Session 和 Arrangement。
   - 备选：[Producer Pal](https://producer-pal.org)（Max for Live 内嵌 MCP，免装 Python）。
3. 冒烟同上。

## Ardour 怎么办（现状保留）

- **OSC 走带/混音继续可用**：`ardour-ai/server.py` 的 transport/gain/mute/solo 工具已测通，
  按 [`../ardour-ai/README.md`](../ardour-ai/README.md) 开 OSC 即可。
- **Lua 编曲桥（write_notes / import_audio）冻结**：不再投入自研。
  跟踪 Ardour 官方 MCP（9.5 起内置，实验性）的接口加深，够用时直接换官方。
- 符号层（compose/song/midi/render/arrangement）与 DAW 无关，**全部继续用**。

## FL Studio 用户注意

FL 的脚本接口写不了钢琴卷帘，"AI 直接操作 FL"仍不可行（2026-06 复检确认）。
FL 维持文件交接：`hum2midi.py` / 符号层出 `.mid`、`ai-music` 出 `.wav`，拖进 FL 精修。

## 与仓库管线的衔接

```
灵感:  哼唱.wav ──hum2midi.py──► melody.mid ─┐
                                            ├─► DAW MCP 导入工程（REAPER/Ableton）
生成:  ai-music generate/regenerate ──.wav ──┤      或拖进 FL（文件交接）
       符号层 make_demo/make_song ──.mid ────┘
按段重做: regenerate.py --section drop（ACE-Step repaint + splice 兜底）
分轨:    stems.py（audio-separator / BS-RoFormer）
```
