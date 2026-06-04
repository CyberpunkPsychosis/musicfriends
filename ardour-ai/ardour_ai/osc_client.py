"""Ardour OSC 客户端 —— 走带与混音的实时控制。

OSC 地址依据 Ardour 官方手册：
  https://manual.ardour.org/using-control-surfaces/controlling-ardour-with-osc/
Ardour 里 strip 的编号 ssid 从 1 开始。不同版本个别地址可能微调，以本地实测为准。

注意：OSC 是「发了就走」的 UDP，本类不保证 Ardour 真的收到/执行；
真正的回执验证留待本地连上 Ardour 时做。
"""
from __future__ import annotations

from pythonosc.udp_client import SimpleUDPClient

from . import config


class ArdourOSC:
    def __init__(self, host: str | None = None, port: int | None = None):
        self.host = host or config.ARDOUR_OSC_HOST
        self.port = port or config.ARDOUR_OSC_PORT
        self._client = SimpleUDPClient(self.host, self.port)

    def _send(self, address: str, *args) -> None:
        self._client.send_message(address, list(args) if args else [])

    # --- 走带 ---
    def play(self) -> None:
        self._send("/transport_play")

    def stop(self) -> None:
        self._send("/transport_stop")

    def locate(self, seconds: float, roll: bool = False) -> None:
        """跳到指定秒数。Ardour /locate 接收采样数，这里按 48k 估算（仅定位用）。"""
        samples = int(seconds * 48000)
        self._send("/locate", samples, 1 if roll else 0)

    def rewind(self) -> None:
        self._send("/goto_start")

    # --- 混音（strip = 轨，ssid 从 1 开始）---
    def set_gain(self, strip: int, db: float) -> None:
        """设轨道增益（dB）。"""
        self._send("/strip/gain", int(strip), float(db))

    def set_mute(self, strip: int, on: bool) -> None:
        self._send("/strip/mute", int(strip), 1 if on else 0)

    def set_solo(self, strip: int, on: bool) -> None:
        self._send("/strip/solo", int(strip), 1 if on else 0)
