import pytest
from pytest_mock import MockerFixture
from ssd import SSD


@pytest.fixture
def reset_ssd():
    with open('ssd_nand.txt', 'w', encoding='utf-8') as f:
        for i in range(100):
            f.write(f'{i:02d} 0x00000000\n')

    with open('ssd_output.txt', 'w', encoding='utf-8') as f:
        f.write('')


def test_ssd_write_error_1(reset_ssd):
    ssd = SSD()
    ssd.write(-1, '0x00113456')
    output = ssd.read_output()
    assert output == "ERROR"


def test_ssd_write_error_2(reset_ssd):
    ssd = SSD()
    ssd.write(987, '0x00113456')
    output = ssd.read_output()
    assert output == "ERROR"


def test_ssd_write_2(reset_ssd):
    ssd = SSD()
    ssd.write(2, '0x00113456')
    contents = ssd.read_all()
    output = ssd.read_output()
    assert contents[2] == f"02 0x00113456\n" and output == ""


def test_ssd_write_4(reset_ssd):
    ssd = SSD()
    ssd.write(99, '0xFF34FF33')
    contents = ssd.read_all()
    output = ssd.read_output()
    assert contents[99] == f"99 0xFF34FF33\n" and output == ""
