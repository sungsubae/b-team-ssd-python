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

def test_read_same_with_output():
    nand = 'ssd_nand.txt'
    output = 'ssd_output.txt'
    lba = 10
    ssd = SSD(nand, output)
    ssd.read(lba)

    with open(nand, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    value = ''
    for line in lines:
        if int(line.split(' ')[0]) == lba:
            value = line.split(' ')[-1]

    with open(output, 'r', encoding='utf-8') as file:
        line = file.readline()

    assert value.strip() == line.strip()
