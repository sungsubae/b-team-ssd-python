import pytest
from pytest_mock import MockerFixture
from ssd import SSD


def test_ssd_write(mocker: MockerFixture):
    ssd = SSD()

    ssd.write(2, '0x00113456')
    contents = ssd.read_all()
    assert contents[2] == f"02 0x00113456\n"

    ssd.write(99, '0xFF34FF33')
    contents = ssd.read_all()
    assert contents[99] == f"99 0xFF34FF33\n"

    ssd.write(-1, '0x00113456')
    content = ssd.read_output()
    assert content == "ERROR"

    ssd.write(987, '0x00113456')
    contents = ssd.read_all()
    assert contents[2] == f"02 0x00113456\n"
