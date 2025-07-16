import pytest
from pytest_mock import MockerFixture
from unittest.mock import call, patch, mock_open
import builtins
import os
from shell import Shell, main

buffer_path = r'.\buffer'


def write_buffer(index: int, command: str):
    """
    index에 해당하는 buffer를 작성한다.
    :param index: 1~5
    :param command: ex) R_10, W_10_0x12345678
    """
    if not os.path.exists(buffer_path):
        os.makedirs(buffer_path)

    for filename in os.listdir(buffer_path):
        if filename.startswith(f'{index}_'):
            file_path = os.path.join(buffer_path, filename)
            os.remove(file_path)

    with open(os.path.join(buffer_path, f"{index}_{command}"), 'w') as f:
        pass


@pytest.fixture
def init_buffer():
    for i in range(1, 6):
        write_buffer(i, 'empty')


def test_command_buffer_flush(capsys, mocker: MockerFixture, init_buffer):
    # write_buffer(1, 'R_10')
    # write_buffer(2, 'W_10_0x12341234')
    # do flush here

    expected_files = {'1_empty', '2_empty', '3_empty', '4_empty', '5_empty'}
    actual_files = set(os.listdir(buffer_path))

    assert expected_files.issubset(actual_files)


# 1_W_20_0xABCDABCD , 2_W_20_0x12341234 , 3_E_20_1
def test_command_buffer_example_1(mocker: MockerFixture, init_buffer):
    shell_write_mock = mocker.patch('shell.Shell._write')
    shell_erase_mock = mocker.patch('shell.Shell._erase')

    shell = Shell()
    # command buffer 적용되면 아래 주석 해제 후 TEST
    # shell.write(20, "0xABCDABCD")
    # shell.write(20, "0x12341234")
    # shell.erase(20, 1)

    shell_write_mock.assert_not_called()
    shell_erase_mock.assert_not_called()

    expected_files = {'1_E_20_1', '2_empty', '3_empty', '4_empty', '5_empty'}
    actual_files = set(os.listdir(buffer_path))

    assert expected_files.issubset(actual_files)
