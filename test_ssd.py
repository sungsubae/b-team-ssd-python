import os
import subprocess

import pytest
from ssd import SSD


def test_ssd_write_error_1():
    ssd = SSD()
    ssd.reset_ssd()
    ssd.write(-1, '0x00113456')
    output = ssd.read_output()
    assert output == "ERROR"


def test_ssd_write_error_2():
    ssd = SSD()
    ssd.reset_ssd()
    ssd.write(987, '0x00113456')
    output = ssd.read_output()
    assert output == "ERROR"


def test_ssd_write_pass_1():
    ssd = SSD()
    ssd.reset_ssd()
    ssd.write(2, '0x00113456')
    contents = ssd.read_all()
    output = ssd.read_output()
    assert contents[2] == f"02 0x00113456\n" and output == ""


def test_ssd_write_pass_2():
    ssd = SSD()
    ssd.reset_ssd()
    ssd.write(99, '0xFF34FF33')
    contents = ssd.read_all()
    output = ssd.read_output()
    assert contents[99] == f"99 0xFF34FF33\n" and output == ""


def test_ssd_write_address_validation():
    ssd = SSD()
    ssd.reset_ssd()

    assert ssd.is_valid_address(-1) is False
    assert ssd.is_valid_address(0) is True
    assert ssd.is_valid_address(99) is True
    assert ssd.is_valid_address(100) is False
    assert ssd.is_valid_address('asd') is False


def test_ssd_write_data_validation():
    ssd = SSD()
    ssd.reset_ssd()

    assert ssd.is_valid_value('ass') is False
    assert ssd.is_valid_value('-123') is False
    assert ssd.is_valid_value('0xAabB1234') is True
    assert ssd.is_valid_value('4F') is True
    assert ssd.is_valid_value('0x01230123') is True


def test_read_same_with_output():
    lba = 10
    ssd = SSD()
    ssd.reset_ssd()
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


def test_read_invalid_lba_access():
    lba = 100
    ssd = SSD()
    ssd.reset_ssd()
    ssd.read(lba)

    with open(ssd.ssd_output, 'r', encoding='utf-8') as file:
        output = file.readline()

    assert output.strip() == "ERROR"


def test_write_and_read_command_line():
    result = subprocess.run(
        ["python", "ssd.py", "W", "3", "0x1298CDEF"],
        capture_output=True,
        text=True
    )

    result = subprocess.run(
        ["python", "ssd.py", "R", "3"],
        capture_output=True,
        text=True
    )

    output = 'ssd_output.txt'
    with open(output, 'r', encoding='utf-8') as file:
        line = file.readline()
    assert  line.strip() == f"0x1298CDEF"


def test_erase_and_read_command_line():
    result = subprocess.run(
        ["python", "ssd.py", "E", "3", "3"],
        capture_output=True,
        text=True
    )

    result = subprocess.run(
        ["python", "ssd.py", "R", "3"],
        capture_output=True,
        text=True
    )

    output = 'ssd_output.txt'
    with open(output, 'r', encoding='utf-8') as file:
        line = file.readline()
    assert  line.strip() == f"0x00000000"


def test_erase_oversize_error():
    result = subprocess.run(
        ["python", "ssd.py", "E", "3", "11"],
        capture_output=True,
        text=True
    )

    output = 'ssd_output.txt'
    with open(output, 'r', encoding='utf-8') as file:
        line = file.readline()
    assert  line.strip() == "ERROR"


def test_erase_invalid_start_lba_error():
    result = subprocess.run(
        ["python", "ssd.py", "E", "100", "3"],
        capture_output=True,
        text=True
    )

    output = 'ssd_output.txt'
    with open(output, 'r', encoding='utf-8') as file:
        line = file.readline()
    assert  line.strip() == "ERROR"


def test_erase_invalid_last_lba_error():
    result = subprocess.run(
        ["python", "ssd.py", "E", "98", "3"],
        capture_output=True,
        text=True
    )

    output = 'ssd_output.txt'
    with open(output, 'r', encoding='utf-8') as file:
        line = file.readline()
    assert  line.strip() == "ERROR"