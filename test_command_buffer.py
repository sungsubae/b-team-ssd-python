import pytest
from pytest_mock import MockerFixture
from unittest.mock import call, patch, mock_open
import builtins
import os
from shell import Shell, main
from buffer import Buffer
from ssd import SSD


def test_command_buffer_flush():
    buffer = Buffer()
    buffer.make_init_buffer()
    buffer.write('W', 1, '0x00001111')
    buffer.write('W', 2, '0x22220000')
    buffer.write('W', 3, '0x00003333')
    buffer.write('W', 4, '0x44440000')
    buffer.write('W', 5, '0x00005555')

    buffer.flush()

    expected_files = {'1_empty', '2_empty', '3_empty', '4_empty', '5_empty'}
    actual_files = set(os.listdir(r"./buffer"))

    assert expected_files.issubset(actual_files)


# 1_W_20_0xABCDABCD , 2_W_20_0x12341234 , 3_E_20_1
def test_command_buffer_example_1(mocker: MockerFixture):
    shell_write_mock = mocker.patch('shell.Shell._write')
    shell_erase_mock = mocker.patch('shell.Shell._erase')

    buffer = Buffer()
    buffer.make_init_buffer()
    buffer.write('W', 20, "0xABCDABCD")
    buffer.write('W', 20, "0x12341234")
    buffer.erase(20, 1)

    expected_files = {'E_20_1', 'empty'}
    actual_files = set([fn[2:] for fn in os.listdir(r"./buffer")])

    shell_write_mock.assert_not_called()
    shell_erase_mock.assert_not_called()
    assert expected_files.issubset(actual_files)


def test_command_buffer_example_2(mocker: MockerFixture):
    shell_read_mock = mocker.patch('shell.Shell._read')

    buffer = Buffer()
    buffer.make_init_buffer()
    buffer.write('W', 50, "0xAAAABBBB")
    buffer.write('W', 20, "0xABABCCCC")
    buffer.read(50)

    expected_buffer_set_without_index = {'W_50_0xAAAABBBB', 'W_20_0xABABCCCC', 'empty'}
    actual_files = set([fn[2:] for fn in os.listdir(r"./buffer")])

    shell_read_mock.assert_not_called()

    assert expected_buffer_set_without_index == actual_files
    assert SSD().read_output().strip() == '0xAAAABBBB'


def test_command_buffer_example_3(mocker: MockerFixture):
    shell_write_mock = mocker.patch('shell.Shell._write')
    shell_erase_mock = mocker.patch('shell.Shell._erase')

    buffer = Buffer()
    buffer.make_init_buffer()
    buffer.write('W', 20, "0xABCDABCD")
    buffer.erase(10, 4)
    buffer.erase(12, 3)

    expected_buffer_set_without_index = {'W_20_0xABCDABCD', 'E_10_5', 'empty'}
    actual_files = set([fn[2:] for fn in os.listdir(r"./buffer")])

    shell_write_mock.assert_not_called()
    shell_erase_mock.assert_not_called()
    assert expected_buffer_set_without_index == actual_files
