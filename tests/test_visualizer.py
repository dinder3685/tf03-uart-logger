import io
import pytest
from tf03.reader import TF03Visualizer, make_frame

class DummySerial:
    def __init__(self, data=b''):
        self._buf = io.BytesIO(data)
        self.in_waiting = len(data)
    def read(self, size=1):
        b = self._buf.read(size)
        self.in_waiting = len(self._buf.getvalue()) - self._buf.tell()
        return b
    def close(self):
        pass


def test_visualizer_read(monkeypatch, tmp_path):
    # prepare a buffer with two valid frames preceded by headers
    frame1 = make_frame(10, 20)
    frame2 = make_frame(30, 40)
    data = b'\x59\x59' + frame1 + b'\x59\x59' + frame2
    dummy = DummySerial(data)
    monkeypatch.setattr('serial.Serial', lambda port, baud, timeout: dummy)
    # Skip matplotlib initialization in test
    monkeypatch.setattr(TF03Visualizer, '_init_plot', lambda self: None)
    vis = TF03Visualizer(port='COMX')
    count = vis.read_sensor()
    assert count == 2
    assert vis.distances[-1] == 30
    assert vis.strengths[-1] == 40
