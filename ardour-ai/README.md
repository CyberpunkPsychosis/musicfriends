# ardour-ai — AI 驱动 Ardour 的 MCP server

设计文档见 [`../docs/ardour-ai-daw-design.md`](../docs/ardour-ai-daw-design.md)。
本目录是**阶段 1** 的代码：在你 Mac 上跑的 MCP server，让你在对话里驱动 Ardour。

```
混音 / 走带  ──OSC(UDP 3819)──►  Ardour
编曲(建轨/写音符/设速度) ──命令队列──►  Ardour 内 lua/ai_bridge.lua
```

## 已实现 & 状态

| 工具 | 通道 | 云端可测? | 状态 |
|---|---|---|---|
| `transport_play/stop` `locate` | OSC | ✅ | 完成（OSC 消息已单测） |
| `set_track_gain/mute/solo` | OSC | ✅ | 完成（已单测） |
| `set_tempo` `add_midi_track` `add_audio_track` | Lua 桥 | 🟡 | Python 侧完成+单测；Lua 侧待本地验证 |
| `write_notes` `import_audio` | Lua 桥 | 🟡 | Python 侧完成；Lua 侧占位，阶段 1 spike 落实 |

> 本仓库在云端开发，**没有 Ardour**。不依赖 Ardour 的逻辑（OSC 构造、命令队列 IPC、
> 序列化、Note 校验）已用 `pytest` 真测通过（11 passed）。Lua 在 Ardour 内执行那段
> 必须在你本地验证 —— 见下。

## 本地跑起来（macOS）

```bash
cd ardour-ai
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest -q                      # 确认 11 passed
python server.py               # 启动 MCP server (stdio)
```

### 让 Ardour 接上

1. **装 Ardour**（macOS 版，[ardour.org](https://ardour.org)）。
2. **开 OSC**：Preferences ▸ Control Surfaces ▸ 勾选 **OSC**，端口 **3819**。
   → 这步通了，`transport_play` / `set_track_gain` 等就能用。
3. **挂 Lua 桥**：把 `lua/ai_bridge.lua` 复制到 Ardour 脚本目录
   （`~/Library/Preferences/Ardour<版本>/scripts/`），在 Window ▸ Scripting 里挂上
   "AI Bridge: drain queue"。先手动触发一次，验证 `add_midi_track` / `set_tempo`。
   → 这步通了，编曲类工具就能用。（周期轮询方案在阶段 1 与 Python 侧一起定。）

### 配进本地 Claude 客户端

把本 server 加进 Claude Desktop / Claude Code 的 MCP 配置（示例，Claude Desktop）：

```json
{
  "mcpServers": {
    "ardour-ai": {
      "command": "/path/to/ardour-ai/.venv/bin/python",
      "args": ["/path/to/ardour-ai/server.py"]
    }
  }
}
```

配好后，你在本地 Claude 里说「新建一条叫 Lead 的 MIDI 轨，速度设 140」，
就会经 MCP → 本 server → Ardour 执行。

## 作曲 → MIDI（云端已完成，今天就能用）

不依赖 Ardour 也不依赖任何 key：把高层描述变成真实 `.mid`，FL / Ardour 都能拖入。

```bash
python make_demo.py --style house --bars 8 --render
python make_demo.py --style future_bass --melody --seed 7 --render
# 风格: melodic(默认) / house / future_bass / dubstep
# 产出按轨分文件(模块化) + buildup + full；--render 出 full.wav 试听
```

- `ardour_ai/midi.py` —— 无依赖 SMF 写入器（Note → .mid），用 mido 回读验证
- `ardour_ai/compose.py` —— EDM 助手 + **风格库**（house/future_bass/dubstep/melodic）：
  风格各带 BPM/鼓型/bass 型/走向；`build_arrangement()` 统一组装。
  **旋律默认不生成，留给你**；`--melody` 出一版「引子」（音阶加权游走，seed 可复现）。
- `ardour_ai/render.py` —— MIDI → WAV 试听合成，让「生成 → 听 → 迭代」闭环。
  `python -m ardour_ai.render any.mid` 可渲染任意 .mid。注：试听音质，成品音色仍在
  FL/Ardour 用你的音色做。
- `ardour_ai/song.py` —— **段落级模块化**：整首 = intro/buildup/drop/break/… 一串段落；
  `regenerate_section()` **只重做某一段，其它段逐字节不变**，并单独导出那段以便替换。
  `make_song.py --regen buildup --seed 999` / MCP 工具 `regenerate_section`。
- `ardour_ai/arrangement.py` —— 把**音符 JSON 落地**成 MIDI/试听（无需 key）。
  对话中的 Claude（我）直接产出音符 → 这里变成 .mid / .wav / 进 Ardour。
  **不需要 Anthropic API**：驱动 MCP 的就是 Claude，不必让 server 反过来调 Claude。
  对应 MCP 工具 `save_arrangement`。JSON→轨道 的解析已单测。

> 两条「AI 生成」通路：
> **符号**（我在对话里产出音符 → `arrangement`/`write_notes` → MIDI / 进 Ardour）——无需 key；
> **音频**（`../ai-music/` 大模型如 MusicGen → stem → 进 Ardour `import_audio`）——需各家 key。

> 同一个 `Note` 模型既能 `write_smf` 成文件，也能经 `write_notes` MCP 工具进 Ardour。
> 这层是未来离线 `.ardour` 工程生成器要引用的素材基础。

## 阶段 1 待办（本地）

- [ ] 验证 OSC：开 Ardour OSC 后，工具能控制走带/推子
- [ ] 验证 Lua 桥：手动触发 `ai_bridge.lua`，跑通 `add_midi_track` / `set_tempo`
- [ ] 落实 `write_notes`（region + MidiModel）与 `import_audio`（SourceFactory）
- [ ] 定周期轮询方案，让 Lua 桥常驻自动执行
