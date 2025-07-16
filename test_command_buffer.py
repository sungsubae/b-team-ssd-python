import pytest
from pytest_mock import MockerFixture
import os


def write_buffer(index: int, command: str):
    """
    index에 해당하는 buffer를 작성한다.
    :param index: 1~5
    :param command: ex) R_10, W_10_0x12345678
    """
    buffer_path = r'.\buffer'
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
    # 나중에 Flush로 대체
    for i in range(1, 6):
        write_buffer(i, 'empty')


def test_command_buffer_flush(capsys, mocker: MockerFixture, init_buffer):
    buffer_path = r'.\buffer'

    # write_buffer(1, 'R_10')
    # write_buffer(2, 'W_10_0x12341234')
    # do flush here

    expected_files = {'1_empty', '2_empty', '3_empty', '4_empty', '5_empty'}
    actual_files = set(os.listdir(buffer_path))

    assert expected_files.issubset(actual_files)

