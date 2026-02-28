import pytest
from tf03.reader import parse_frame, TF03Visualizer


def make_frame(distance, strength):
    # distance 0-65535, strength 0-65535
    dist_L = distance & 0xFF
    dist_H = (distance >> 8) & 0xFF
    str_L = strength & 0xFF
    str_H = (strength >> 8) & 0xFF
    reserved1 = 0
    reserved2 = 0
    total = 0x59 + 0x59 + dist_L + dist_H + str_L + str_H + reserved1 + reserved2
    checksum = total & 0xFF
    return bytes([dist_L, dist_H, str_L, str_H, reserved1, reserved2, checksum])


def test_parse_frame_valid():
    frame = make_frame(1234, 567)
    dist, strength = parse_frame(frame)
    assert dist == 1234
    assert strength == 567


def test_parse_frame_invalid_length():
    with pytest.raises(ValueError):
        parse_frame(b'\x00')


def test_parse_frame_bad_checksum():
    frame = make_frame(100, 200)
    bad = bytearray(frame)
    bad[-1] = (bad[-1] + 1) & 0xFF
    with pytest.raises(ValueError):
        parse_frame(bytes(bad))
