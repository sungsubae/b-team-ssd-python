import os
import subprocess

import pytest
from ssd import SSD


@pytest.fixture
def ssd():
    ssd_ = SSD()
    ssd_.reset_ssd()
    return ssd_


@pytest.mark.parametrize(
    "test_params",
    [(-1, '0x00113456', "ERROR"),
     (-987, '0x00113456', "ERROR"),
     (2, '0x00113456', ""),
     (99, '0xFF34FF33', "")]
)
def test_ssd_write_with_params(test_params, ssd: SSD):
    lba, value, expected = test_params

    ssd.write(lba, value)
    output = ssd.read_output()

    assert output == expected


@pytest.mark.parametrize(
    "address, expected",
    [(-1, False),
     (100, False),
     ('asd', False),
     (0, True),
     (99, True)]
)
def test_ssd_write_address_validation(address, expected: bool, ssd: SSD):
    assert ssd.is_valid_address(address) is expected


@pytest.mark.parametrize(
    "value, expected",
    [('asif', False),
     ('-123', False),
     ('0xAabB1234', True),
     ('4F', True),
     ('0x01230123', True)]
)
def test_ssd_write_value_validation(value, expected: bool, ssd: SSD):
    assert ssd.is_valid_value(value) is expected


def test_read_same_with_output(ssd: SSD):
    lba = 10
    ssd.read(lba)

    with open(ssd.ssd_nand, 'r', encoding='utf-8') as file:
        nand_lines = file.readlines()
    nand_value = ''
    for nand_line in nand_lines:
        if int(nand_line.split(' ')[0]) == lba:
            nand_value = nand_line.split(' ')[-1]

    output = get_ssd_output()
    assert nand_value.strip() == output.strip()


def test_read_invalid_lba_access(ssd: SSD):
    lba = 100
    ssd.read(lba)

    output = get_ssd_output()
    assert output.strip() == "ERROR"


def get_ssd_output():
    output_file_name = 'ssd_output.txt'
    with open(output_file_name, 'r', encoding='utf-8') as file:
        ssd_output = file.readline()
    return ssd_output


def run_ssd_write_on_cli(lba: int, value: str):
    result = subprocess.run(
        ["python", "ssd.py", "W", str(lba), value],
        capture_output=True,
        text=True
    )
    return result


def run_ssd_read_on_cli(lba: int):
    result = subprocess.run(
        ["python", "ssd.py", "R", str(lba)],
        capture_output=True,
        text=True
    )
    return result


def run_ssd_erase_on_cli(lba: int, size: int):
    result = subprocess.run(
        ["python", "ssd.py", "E", str(lba), str(size)],
        capture_output=True,
        text=True
    )


def test_write_and_read_command_line():
    run_ssd_write_on_cli(3, "0x1298CDEF")
    run_ssd_read_on_cli(3)

    ssd_output = get_ssd_output()
    assert ssd_output.strip() == f"0x1298CDEF"


def test_erase_and_read_command_line(ssd):
    run_ssd_erase_on_cli(3, 1)
    run_ssd_read_on_cli(3)

    ssd_output = get_ssd_output()
    assert ssd_output.strip() == f"0x00000000"


def test_erase_oversize_error():
    run_ssd_erase_on_cli(3, 11)

    ssd_output = get_ssd_output()
    assert ssd_output.strip() == "ERROR"


def test_erase_invalid_start_lba_error():
    run_ssd_erase_on_cli(100, 3)

    ssd_output = get_ssd_output()
    assert ssd_output.strip() == "ERROR"


def test_erase_invalid_last_lba_error():
    run_ssd_erase_on_cli(98, 3)

    ssd_output = get_ssd_output()
    assert ssd_output.strip() == "ERROR"
