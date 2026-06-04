"""OSC 客户端单测：用本地 UDP server 真收消息，验证地址与参数构造正确。

这部分不需要 Ardour —— 我们自己起一个 OSC 服务端把消息收下来核对。
"""
import threading
import time

import pytest
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer

from ardour_ai.osc_client import ArdourOSC


@pytest.fixture
def osc_capture():
    received = []
    disp = Dispatcher()
    disp.set_default_handler(lambda addr, *args: received.append((addr, args)))
    server = BlockingOSCUDPServer(("127.0.0.1", 0), disp)
    port = server.server_address[1]
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    client = ArdourOSC(host="127.0.0.1", port=port)
    yield client, received
    server.shutdown()


def _wait(received, n, timeout=2.0):
    end = time.time() + timeout
    while time.time() < end and len(received) < n:
        time.sleep(0.01)


def test_transport_messages(osc_capture):
    client, received = osc_capture
    client.play()
    client.stop()
    _wait(received, 2)
    addrs = [a for a, _ in received]
    assert "/transport_play" in addrs
    assert "/transport_stop" in addrs


def test_gain_message(osc_capture):
    client, received = osc_capture
    client.set_gain(3, -6.0)
    _wait(received, 1)
    addr, args = received[0]
    assert addr == "/strip/gain"
    assert args[0] == 3
    assert abs(args[1] - (-6.0)) < 1e-6


def test_mute_solo_messages(osc_capture):
    client, received = osc_capture
    client.set_mute(2, True)
    client.set_solo(5, False)
    _wait(received, 2)
    by_addr = {a: args for a, args in received}
    assert by_addr["/strip/mute"] == (2, 1)
    assert by_addr["/strip/solo"] == (5, 0)
