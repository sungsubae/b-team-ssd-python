import pytest
from ssd import SSD


@pytest.fixture
def reset_ssd():
    with open('ssd_nand.txt', 'w', encoding='utf-8') as f:
        for i in range(100):
            f.write(f'{i:02d} 0x00000000\n')

    with open('ssd_output.txt', 'w', encoding='utf-8') as f:
        f.write('')


def test_ssd_write(reset_ssd):
    ssd = SSD()

    ssd.write(-1, '0x00113456')
    output = ssd.read_output()
    assert output == "ERROR"

    ssd.write(2, '0x00113456')
    contents = ssd.read_all()
    output = ssd.read_output()
    assert contents[2] == f"02 0x00113456\n" and output == ""

    ssd.write(987, '0x00113456')
    output = ssd.read_output()
    assert output == "ERROR"

    ssd.write(99, '0xFF34FF33')
    contents = ssd.read_all()
    output = ssd.read_output()
    assert contents[99] == f"99 0xFF34FF33\n" and output == ""


def test_read_same_with_output(reset_ssd):
    lba = 10
    ssd = SSD()
    ssd.read(lba)

    with open(ssd.ssd_nand, 'r', encoding='utf-8') as file:
        nand_lines = file.readlines()
    nand_value = ''
    for nand_line in nand_lines:
        if int(nand_line.split(' ')[0]) == lba:
            nand_value = nand_line.split(' ')[-1]

    with open(ssd.ssd_output, 'r', encoding='utf-8') as file:
        output = file.readline()

    assert nand_value.strip() == output.strip()


def test_read_invalid_lba_access(reset_ssd):
    lba = 100
    ssd = SSD()
    ssd.read(lba)

    with open(ssd.ssd_output, 'r', encoding='utf-8') as file:
        output = file.readline()

    assert output.strip() == "ERROR"