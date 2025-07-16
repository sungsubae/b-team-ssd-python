import pytest
from pytest_mock import MockerFixture
from unittest.mock import call, patch, mock_open
import builtins
import os
from shell import Shell, main
from buffer import Buffer
from ssd import SSD
import subprocess


@pytest.fixture
def shell():
    shell = Shell()
    return shell


@pytest.fixture
def ssd():
    ssd = SSD()
    ssd.reset_ssd()
    return ssd


@pytest.fixture
def output():
    from pathlib import Path
    return Path('ssd_output.txt')


def test_command_buffer_flush(shell, ssd):
    shell.write(1, '0x00001111')
    shell.write(2, '0x22220000')
    shell.write(3, '0x00003333')
    shell.write(4, '0x44440000')
    shell.write(5, '0x00005555')

    ssd.flush()
    expected_files = {'1_empty', '2_empty', '3_empty', '4_empty', '5_empty'}
    actual_files = set(os.listdir(r"./buffer"))

    assert actual_files == expected_files


# 1_W_20_0xABCDABCD , 2_W_20_0x12341234 , 3_E_20_1
def test_command_buffer_example_1(mocker: MockerFixture, shell, ssd):
    ssd_write_mock = mocker.patch('ssd.SSD._write')
    ssd_erase_mock = mocker.patch('ssd.SSD._erase')

    # command buffer 적용되면 아래 주석 해제 후 TEST
    shell.write(20, "0xABCDABCD")
    shell.write(20, "0x12341234")
    shell.erase(20, 1)

    ssd_write_mock.assert_not_called()
    ssd_erase_mock.assert_not_called()

    expected_files = {'E_20_1', 'empty'}
    actual_files = set([fn[2:] for fn in os.listdir(r"./buffer")])

    assert actual_files == expected_files



def test_command_buffer_example_2(mocker: MockerFixture, shell, ssd):
    ssd_read_mock = mocker.patch('ssd.SSD.read_all')

    shell.write(50, "0xAAAABBBB")
    shell.write(20, "0xABABCCCC")
    shell.read(50)

    expected_buffer_set_without_index = {'W_50_0xAAAABBBB', 'W_20_0xABABCCCC', 'empty'}
    actual_files = set([fn[2:] for fn in os.listdir(r"./buffer")])

    ssd_read_mock.assert_not_called()

    assert expected_buffer_set_without_index == actual_files
    assert ssd.read_output().strip() == '0xAAAABBBB'


def test_command_buffer_example_3(mocker: MockerFixture, shell, ssd):
    ssd_write_mock = mocker.patch('ssd.SSD._write')
    ssd_erase_mock = mocker.patch('ssd.SSD._erase')

    shell.write(20, "0xABCDABCD")
    shell.erase(10, 4)
    shell.erase(12, 3)

    expected_buffer_set_without_index = {'W_20_0xABCDABCD', 'E_10_5', 'empty'}
    actual_files = set([fn[2:] for fn in os.listdir(r"./buffer")])

    ssd_write_mock.assert_not_called()
    ssd_erase_mock.assert_not_called()
    assert expected_buffer_set_without_index == actual_files

def test_command_buffer_write_over_buffer_limit(shell, ssd, output):
    shell.write(1, "0x00000001")
    shell.write(2, "0x00000002")
    shell.write(3, "0x00000003")
    shell.write(4, "0x00000004")
    shell.write(5, "0x00000005")
    shell.write(6, "0x00000006")

    expected_buffer_set_without_index = {'W_6_0x00000006', 'empty'}
    actual_files = set([fn[2:] for fn in os.listdir(r"./buffer")])

    for i in range(1, 7):
        ssd.read(i)
        assert output.read_text().strip() == f"0x0000000{i}"
    assert actual_files == expected_buffer_set_without_index


def test_command_buffer_write_same_lba(mocker: MockerFixture, shell, ssd, output):
    ssd_write_mock = mocker.patch('ssd.SSD._write')

    shell.write(13, "0x00000001")
    shell.write(13, "0x00000002")
    shell.write(13, "0x00000003")
    shell.write(13, "0x00000004")
    shell.write(13, "0x00000005")
    shell.write(13, "0x00000006")

    expected_buffer_set_without_index = {'W_13_0x00000006', 'empty'}
    actual_files = set([fn[2:] for fn in os.listdir(r"./buffer")])

    ssd_write_mock.assert_not_called()
    ssd.read(13)
    assert output.read_text().strip() == f"0x00000006"
    assert actual_files == expected_buffer_set_without_index


def test_buffer_write_and_read():
    buffer = Buffer()
    buffer.reset()

    buffer.write('E', 5, size=5)
    assert buffer.read(5) == '0x00000000'
    buffer.write('W', 5, '0x00000011')
    assert buffer.read(5) == '0x00000011'


def get_empty_buffer_cnt(file_list):
    empty_cnt = 0

    for file_name in file_list:
        if 'empty' in file_name:
            empty_cnt += 1

    return empty_cnt


def test_buffer_write_join_command():
    buffer = Buffer()
    buffer.reset()

    buffer.write('E', 5, size=5)
    buffer.write('E', 7, size=5)
    buffer.write('E', 9, size=5)

    file_list = os.listdir(Buffer().folder_path)

    assert get_empty_buffer_cnt(file_list) == len(file_list) - 1


def test_buffer_write_not_join_erase_command():
    buffer = Buffer()
    buffer.reset()

    buffer.write('E', 5, size=5)
    buffer.write('E', 10, size=6)

    file_list = os.listdir(Buffer().folder_path)

    assert get_empty_buffer_cnt(file_list) == len(file_list) - 2

def test_write_with_same_lba():
    buffer = Buffer()
    buffer.reset()

    buffer.write('W', 5, value='0x00000001')
    buffer.write('W', 6, value='0x00000001')
    buffer.write('W', 7, value='0x00000001')
    buffer.write('W', 5, value='0x00000002')
    buffer.write('W', 6, value='0x00000002')
    buffer.write('W', 7, value='0x00000002')

    file_list = os.listdir(Buffer().folder_path)

    assert get_empty_buffer_cnt(file_list) == len(file_list) - 3


def test_buffer_erase_merge_1():
    ssd = SSD()
    ssd.reset_ssd()

    buffer = Buffer()
    buffer.reset()

    commands = [["python", "ssd.py", "E", "11", "6"],
                ["python", "ssd.py", "E", "12", "6"],
                ["python", "ssd.py", "E", "13", "6"],
                ["python", "ssd.py", "E", "14", "6"],
                ["python", "ssd.py", "E", "15", "6"]]

    for command in commands:
        subprocess.run(
            command,
            capture_output=True,
            text=True
        )

    expected_buffer_set_without_index = {'E_11_10', 'empty'}
    actual_files = set([fn[2:] for fn in os.listdir(r"./buffer")])
    assert actual_files == expected_buffer_set_without_index


def test_buffer_erase_merge_2():
    ssd = SSD()
    ssd.reset_ssd()

    buffer = Buffer()
    buffer.reset()

    commands = [["python", "ssd.py", "E", "11", "3"],
                ["python", "ssd.py", "E", "18", "3"],
                ["python", "ssd.py", "E", "14", "4"]]

    for command in commands:
        subprocess.run(
            command,
            capture_output=True,
            text=True
        )

    expected_buffer_set_without_index = {'E_11_10', 'empty'}
    actual_files = set([fn[2:] for fn in os.listdir(r"./buffer")])
    assert actual_files == expected_buffer_set_without_index


def test_buffer_erase_merge_3():
    ssd = SSD()
    ssd.reset_ssd()

    buffer = Buffer()
    buffer.reset()

    commands = [["python", "ssd.py", "E", "0", "3"],
                ["python", "ssd.py", "E", "12", "3"],
                ["python", "ssd.py", "E", "6", "3"],
                ["python", "ssd.py", "E", "3", "3"],
                ["python", "ssd.py", "E", "9", "3"]]

    for command in commands:
        subprocess.run(
            command,
            capture_output=True,
            text=True
        )

    # 아래 조건을 만족시키며 두 개로 Merge 되어야 한다.
    # A + B = 15, A, B <= 10 를 만족하는 자연수
    # E_0_A, E_A_B
    expected_buffer_set_without_index = {'E_0_A', 'E_A_B'}
    actual_files = [fn[2:] for fn in os.listdir(r"./buffer") if "empty" not in fn]
    actual_files.sort()

    A = int(actual_files[0][-1:])
    B = int(actual_files[1][-1:])

    assert A + B == 15
    assert A <= 10 and B <= 10
    assert len(expected_buffer_set_without_index) == 2
