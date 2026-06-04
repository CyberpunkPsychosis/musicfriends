"""无依赖的标准 MIDI(SMF) 写入器：把我们的 Note 模型写成 .mid。

为什么独立做、不用第三方库：零依赖、完全可控，且和命令层共用同一个 Note 模型
（拍为单位）。产出的 .mid 文件 FL 和 Ardour 都能直接拖入。

时间单位：Note.start / Note.length 以「拍(beat = 四分音符)」计；写出时按 PPQ 转 tick。
鼓轨用 channel 9（GM 打击乐通道）。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .commands import Note

PPQ = 480  # ticks per quarter note


@dataclass
class MidiTrack:
    name: str
    notes: list[Note] = field(default_factory=list)
    channel: int = 0          # 0-15；鼓轨用 9
    program: int | None = None  # GM 音色号(0-127)，None=不发 Program Change


# ---------- 低层编码 ----------

def _vlq(n: int) -> bytes:
    """可变长度量(variable-length quantity)，用于 delta-time。"""
    if n < 0:
        raise ValueError("VLQ 不能为负")
    out = bytearray([n & 0x7F])
    n >>= 7
    while n:
        out.insert(0, (n & 0x7F) | 0x80)
        n >>= 7
    return bytes(out)


def _chunk(tag: bytes, data: bytes) -> bytes:
    return tag + len(data).to_bytes(4, "big") + data


def _meta(kind: int, data: bytes) -> bytes:
    return b"\xFF" + bytes([kind]) + _vlq(len(data)) + data


def _events_to_track(events: list[tuple[int, bytes]]) -> bytes:
    """events: (absolute_tick, raw_event_bytes)。排序后做 delta 编码。"""
    events.sort(key=lambda e: e[0])
    out = bytearray()
    last = 0
    for tick, ev in events:
        out += _vlq(tick - last) + ev
        last = tick
    out += _vlq(0) + b"\xFF\x2F\x00"  # End of Track
    return _chunk(b"MTrk", bytes(out))


# ---------- 公开 API ----------

def write_smf(path: str | Path, tracks: list[MidiTrack], bpm: float,
              numerator: int = 4, denominator: int = 4, ppq: int = PPQ) -> Path:
    """写出一个 format-1 多轨 SMF。轨 0 为速度/拍号(conductor)，其后每轨一个乐器。"""
    path = Path(path)

    # --- conductor 轨：tempo + time signature ---
    micros = int(round(60_000_000 / bpm))
    dd = max(0, (denominator).bit_length() - 1)  # denominator=4 -> dd=2
    conductor = [
        (0, _meta(0x51, micros.to_bytes(3, "big"))),          # set tempo
        (0, _meta(0x58, bytes([numerator, dd, 24, 8]))),      # time signature
        (0, _meta(0x03, b"Conductor")),                       # track name
    ]

    chunks = [_events_to_track(conductor)]

    # --- 乐器轨 ---
    for tr in tracks:
        ch = tr.channel & 0x0F
        evs: list[tuple[int, bytes]] = [(0, _meta(0x03, tr.name.encode("utf-8")))]
        if tr.program is not None:
            evs.append((0, bytes([0xC0 | ch, tr.program & 0x7F])))
        for n in tr.notes:
            on_tick = int(round(n.start * ppq))
            off_tick = int(round((n.start + n.length) * ppq))
            evs.append((on_tick, bytes([0x90 | ch, n.pitch & 0x7F, n.velocity & 0x7F])))
            # note off 用 note-on velocity 0；同 tick 时排在 note-on 前避免粘连
            evs.append((off_tick, bytes([0x90 | ch, n.pitch & 0x7F, 0])))
        chunks.append(_events_to_track(evs))

    header = _chunk(b"MThd", (1).to_bytes(2, "big")          # format 1
                    + (len(chunks)).to_bytes(2, "big")        # ntracks
                    + ppq.to_bytes(2, "big"))                 # division
    path.write_bytes(header + b"".join(chunks))
    return path
