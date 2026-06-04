--[[
  ai_bridge.lua —— 在 Ardour 内部运行的命令执行端。

  作用：轮询命令队列目录，读取 MCP server 写入的 JSON 命令，用 Ardour Lua API
  执行（建轨/写音符/设速度…），把回执写回 responses/。

  ⚠️ 本脚本在云端无法测试（这里没有 Ardour）。需在你本地按 README「阶段 1」验证：
     - Ardour Lua 绑定细节以 https://manual.ardour.org/lua-scripting/class_reference/
       和 luabindings.cc 为准，个别 API 名/签名可能需按你的 Ardour 版本微调。
     - 加载方式见文件末尾。

  实现为 EditorAction：每次触发「排空一次队列」。配合一个周期触发器即可常驻轮询
  （最简单：先手动触发验证逻辑，再接周期触发）。
]]

ardour { ["type"] = "EditorAction", name = "AI Bridge: drain queue",
         license = "MIT", author = "musicfriends",
         description = "Execute queued AI commands (MCP <-> Ardour)" }

-- 队列目录：与 Python 侧 config.QUEUE_DIR 保持一致
local QUEUE = os.getenv("ARDOUR_AI_QUEUE")
              or (os.getenv("HOME") .. "/.config/ardour-ai/queue")
local REQ = QUEUE .. "/requests"
local RESP = QUEUE .. "/responses"

-- 极简 JSON（仅够本桥用）。Ardour 自带 Lua 无标准 json 库。
local function json_encode(v)
  local t = type(v)
  if t == "nil" then return "null"
  elseif t == "boolean" then return v and "true" or "false"
  elseif t == "number" then return tostring(v)
  elseif t == "string" then return '"' .. v:gsub('["\\]', '\\%0') .. '"'
  elseif t == "table" then
    local parts = {}
    for k, val in pairs(v) do
      parts[#parts + 1] = '"' .. tostring(k) .. '":' .. json_encode(val)
    end
    return "{" .. table.concat(parts, ",") .. "}"
  end
  return "null"
end

local function read_file(path)
  local f = io.open(path, "r"); if not f then return nil end
  local s = f:read("*a"); f:close(); return s
end

local function write_resp(id, ok, data, err)
  local body = json_encode({ id = id, ok = ok, data = data, error = err })
  local tmp = RESP .. "/" .. id .. ".json.tmp"
  local f = io.open(tmp, "w"); if not f then return end
  f:write(body); f:close()
  os.rename(tmp, RESP .. "/" .. id .. ".json")  -- 原子落地
end

-- 列出 requests/ 下的 *.json（用 ls，macOS/Linux 通用）
local function list_requests()
  local out = {}
  local p = io.popen('ls -1 "' .. REQ .. '" 2>/dev/null')
  if not p then return out end
  for line in p:lines() do
    if line:match("%.json$") and not line:match("%.tmp$") then
      out[#out + 1] = line
    end
  end
  p:close()
  return out
end

-- 把命令 JSON 里我们需要的字段抠出来（极简解析，不引入完整 JSON 解析器）
local function parse_field(s, key)
  return s:match('"' .. key .. '"%s*:%s*"([^"]*)"')      -- 字符串
      or s:match('"' .. key .. '"%s*:%s*([%-%d%.]+)')     -- 数字
end

-- ============ 具体操作（Ardour Lua API）============

local function op_set_tempo(args_json)
  local bpm = tonumber(parse_field(args_json, "bpm"))
  local tm = Session:tempo_map()
  -- 在 0 拍处设速度；不同版本 API 可能是 add_tempo / set_tempo，按 class ref 调整
  local pos = Temporal.timepos_t(0)
  tm:set_tempo(ARDOUR.Tempo(bpm, 4.0), pos)
  Session:save_state("")
  return { bpm = bpm }
end

local function op_add_midi_track(args_json)
  local name = parse_field(args_json, "name") or "AI MIDI"
  -- 新建 1 条 MIDI 轨
  local tl = Session:new_midi_track(
      ARDOUR.ChanCount(ARDOUR.DataType.MIDI(), 1),
      ARDOUR.ChanCount(ARDOUR.DataType.AUDIO(), 2),
      true, nil, nil, nil, 1, name,
      ARDOUR.PresentationInfo.max_order, ARDOUR.TrackMode.Normal, true)
  return { name = name, created = (tl ~= nil) }
end

local function op_add_audio_track(args_json)
  local name = parse_field(args_json, "name") or "AI Audio"
  Session:new_audio_track(1, 2, nil, 1, name,
      ARDOUR.PresentationInfo.max_order, ARDOUR.TrackMode.Normal, true)
  return { name = name }
end

-- write_notes / import_audio 含较多 region/source 细节，先占位，阶段 1 spike 落实。
local function op_write_notes(args_json)
  error("write_notes 待阶段 1 实现（region + MidiModel 写入）")
end

local function op_import_audio(args_json)
  error("import_audio 待阶段 1 实现（SourceFactory + region 导入）")
end

local DISPATCH = {
  set_tempo = op_set_tempo,
  add_midi_track = op_add_midi_track,
  add_audio_track = op_add_audio_track,
  write_notes = op_write_notes,
  import_audio = op_import_audio,
}

-- ============ 主流程：排空一次队列 ============

function factory() return function()
  os.execute('mkdir -p "' .. REQ .. '" "' .. RESP .. '"')
  for _, fname in ipairs(list_requests()) do
    local path = REQ .. "/" .. fname
    local raw = read_file(path)
    os.remove(path)
    if raw then
      local id = parse_field(raw, "id") or fname:gsub("%.json$", "")
      local op = parse_field(raw, "op")
      local handler = DISPATCH[op]
      if not handler then
        write_resp(id, false, nil, "未知操作: " .. tostring(op))
      else
        local ok, ret = pcall(handler, raw)
        if ok then write_resp(id, true, ret, nil)
        else write_resp(id, false, nil, tostring(ret)) end
      end
    end
  end
end end

--[[
  加载方式（本地）：
    1. 复制本文件到 Ardour 脚本目录，例如：
         ~/Library/Preferences/Ardour8/scripts/   (macOS, 版本号按实际)
    2. Ardour 菜单 Window ▸ Scripting，或在 Editor 的 Lua Action 槽里挂上
       "AI Bridge: drain queue"。
    3. 先手动触发一次，验证 add_midi_track / set_tempo 能跑通。
    4. 再接一个周期触发（如 Ardour 的 signal/定时，或临时用快捷键反复触发）实现常驻轮询。
       —— 周期化方案在阶段 1 与 Python 侧一起定。
]]
