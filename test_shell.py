import builtins

import pytest, pytest_mock
from pytest_mock import MockerFixture
from unittest.mock import call, patch, mock_open

from shell import Shell, startShell
import random


def test_read_valid_index(capsys, mocker:MockerFixture):
    mock_run = mocker.patch("shell.subprocess.run")

    mocked_file = mocker.mock_open(read_data="0x00000000")
    mocker.patch("builtins.open", mocked_file)

    shell = Shell()
    shell.read(3)
    captured = capsys.readouterr()

    mock_run.assert_called_once_with(['python', 'ssd.py', 'R', '3'], capture_output=True, text=True)

    assert captured.out.strip() == "[Read] LBA 03 : 0x00000000"


def test_read_invalid_index(capsys, mocker:MockerFixture):
    mock_run = mocker.patch("shell.subprocess.run")

    mocked_file = mocker.mock_open(read_data="ERROR")
    mocker.patch("builtins.open", mocked_file)

    shell = Shell()
    shell.read(100)
    captured = capsys.readouterr()

    mock_run.assert_called_once_with(['python', 'ssd.py', 'R', '100'], capture_output=True, text=True)

    assert captured.out.strip() == "[Read] ERROR"


def test_write(capsys, mocker :MockerFixture):
    value = "0xAAAABBBB"
    mock_write = mocker.patch('shell.Shell._write')
    shell = Shell()
    shell.write(3, value)
    captured = capsys.readouterr()
    assert captured.out.strip() == "[Write] Done"
    mock_write.assert_called_once_with(3, value)

def test_write_invalid_hex_false(mocker):
    shell = Shell()
    # is_hex_string이 False를 반환하도록 mock
    mocker.patch.object(shell, 'is_hex_string', return_value=False)
    # print를 spy로 감시
    print_spy = mocker.spy(builtins, 'print')
    shell.write(3, "INVALID")
    print_spy.assert_called_with("[Write] ERROR")

def test_write_invalid_hex_true(mocker):
    shell = Shell()
    # is_hex_string이 False를 반환하도록 mock
    mocker.patch.object(shell, 'is_hex_string', return_value=True)
    # print를 spy로 감시
    print_spy = mocker.spy(builtins, 'print')
    shell.write(3, "0xAAAABBBB")
    print_spy.assert_called_with("[Write] Done")

def test_write_error_case(mocker):
    shell = Shell()
    # 올바른 hex로 통과
    mocker.patch.object(shell, 'is_hex_string', return_value=True)
    mocker.patch('subprocess.run')
    # open mock: ssd_output.txt에 "ERROR"만 반환
    m = mock_open(read_data="ERROR")
    mocker.patch("builtins.open", m)
    print_spy = mocker.spy(builtins, 'print')
    shell.write(3, "0xAAAABBBB")
    print_spy.assert_called_with("[Write] ERROR")

def test_write_success(mocker):
    shell = Shell()
    mocker.patch.object(shell, 'is_hex_string', return_value=True)
    mocker.patch('subprocess.run')
    # open mock: ssd_output.txt에 ""(빈 문자열) 반환
    m = mock_open(read_data="")
    mocker.patch("builtins.open", m)
    print_spy = mocker.spy(builtins, 'print')
    shell.write(4, "0xAABBAABB")
    print_spy.assert_called_with("[Write] Done")

def test_full_write_success(mocker: MockerFixture):
    ssd_write_mock = mocker.patch('shell.Shell._write')
    value = hex(0xAAAABBBB)
    shell = Shell()
    full_call_list = [call(idx, value) for idx in range(100)]
    shell.full_write(value)
    ssd_write_mock.assert_has_calls(full_call_list)


def test_help_call(mocker: MockerFixture):
    mk = mocker.Mock(spec=Shell)
    mk.help()

    mk.help.assert_called_once()


def test_help_text_valid(capsys):
    shell = Shell()
    ret = shell.help()
    captured = capsys.readouterr()

    assert captured.out.strip() == '''제작자: 배성수 팀장, 연진혁, 이정은, 이찬욱, 임창근, 정구환, 이근우
명령어 사용 법 : 
 1. read: read [LBA]
 2. write: write [LBA] [VALUE]
 3. erase: erase [LBA] [SIZE]
 4. erase_range: erase_range [ST_LBA] [EN_LBA]
 5. fullwrite: fullwrite [VALUE]
 6. fullread: fullread
 7. 1_FullWriteAndReadCompare: 1_ 혹은 1_FullWriteAndReadCompare 입력
 8. 2_PartialLBAWrite: 2_ 혹은 2_PartialLBAWrite 입력
 9. 3_WriteReadAging: 3_ 혹은 3_WriteReadAging 입력
10. 4_EraseAndWriteAging: 4_ 혹은 4_EraseAndWriteAging 입력
11. exit: exit
그 외 명령어 입력 시, INVALID COMMAND 가 출력 됩니다.'''


def test_cmd_read(mocker:MockerFixture):
    mk = mocker.Mock(spec=Shell)
    with patch("builtins.input", side_effect=["read 0", "exit"]):
        startShell(mk)

    mk.read.assert_called_with(0)


def test_cmd_write(mocker:MockerFixture):
    mk = mocker.Mock(spec=Shell)
    with patch("builtins.input", side_effect=["write 3 0xAAAABBBB", "exit"]):
        startShell(mk)
    mk.write.assert_called_with(3, "0xAAAABBBB")


def test_cmd_fullwrite(mocker:MockerFixture):
    mk = mocker.Mock(spec=Shell)
    with patch("builtins.input", side_effect=["fullwrite 0xAAAABBBB", "exit"]):
        startShell(mk)
    mk.full_write.assert_called_with("0xAAAABBBB")


def test_cmd_FullWriteAndReadCompare(mocker:MockerFixture):
    mk = mocker.Mock(spec=Shell)
    with patch("builtins.input", side_effect=["1_", "exit"]):
        startShell(mk)

    with patch("builtins.input", side_effect=["1_FullWriteAndReadCompare", "exit"]):
        startShell(mk)

    assert mk.FullWriteAndReadCompare.call_count == 2


def test_cmd_PartialLBAWrite(mocker:MockerFixture):
    mk = mocker.Mock(spec=Shell)
    with patch("builtins.input", side_effect=["2_", "2_PartialLBAWrite", "exit"]):
        startShell(mk)

    assert mk.PartialLBAWrite.call_count == 2


def test_cmd_WriteReadAging(mocker:MockerFixture):
    mk = mocker.Mock(spec=Shell)
    with patch("builtins.input", side_effect=["3_", "3_WriteReadAging", "exit"]):
        startShell(mk)

    assert mk.WriteReadAging.call_count == 2


def test_full_write_and_read_compare_success(mocker:MockerFixture, capsys):
    seed = 42
    shell_write_mock = mocker.patch('shell.Shell._write')
    shell_read_mock = mocker.patch('shell.Shell._read')
    shell = Shell()
    ssd_length = 100
    block_length = 5
    random_values = []
    write_calls = []
    read_calls = []
    random.seed(seed)
    for i in range(ssd_length // block_length):
        random_val = random.randint(0x00000001, 0xFFFFFFFF)
        for j in range(block_length):
            random_values.append(f'{random_val:#010x}')
            write_calls.append(call(i * block_length + j, f'{random_val:#010x}'))
            read_calls.append(call(i * block_length + j))
    shell_read_mock.side_effect = random_values
    random.seed(seed)
    assert shell.FullWriteAndReadCompare() == "PASS"
    shell_write_mock.assert_has_calls(write_calls)
    shell_read_mock.assert_has_calls(read_calls)
    # assert capsys.readouterr().out.strip() == "PASS"


def test_full_write_and_read_compare_fail(mocker:MockerFixture, capsys):
    seed = 42
    shell_write_mock = mocker.patch('shell.Shell._write')
    shell_read_mock = mocker.patch('shell.Shell._read')
    shell = Shell()
    ssd_length = 100
    block_length = 5
    random_values = []
    write_calls = []
    read_calls = []
    random.seed(seed)
    for i in range(ssd_length // block_length):
        random_val = random.randint(0x00000001, 0xFFFFFFFF)
        for j in range(block_length):
            random_values.append(f'{random_val:#010x}')
            write_calls.append(call(i * block_length + j, f'{random_val:#010x}'))
            read_calls.append(call(i * block_length + j))
    shell_read_mock.side_effect = random_values
    random.seed(seed+1)
    assert shell.FullWriteAndReadCompare() == 'FAIL'
    # assert capsys.readouterr().out.strip() == "FAIL"


def test_full_read_call(mocker:MockerFixture):
    mk = mocker.Mock(spec=Shell)
    mk.full_read()

    mk.full_read.assert_called_once()


def test_full_read_valid(mocker:MockerFixture, capsys):
    mk_full_read = mocker.patch('shell.Shell._read')
    mk_full_read.return_value = '0x00000000'
    shell = Shell()
    shell.full_read()
    captured = capsys.readouterr()
    assert captured.out.strip() == '[Full Read]\n' + '\n'.join([f"LBA {i:02d} : 0x00000000" for i in range(100)])


def test_write_read_aging_calls_write_read_400_times(mocker: MockerFixture):
    mock_write = mocker.patch('shell.Shell._write')
    mock_read = mocker.patch('shell.Shell._read')
    mock_read.return_value = '0x00000001'
    shell = Shell()

    shell.WriteReadAging()
    assert mock_write.call_count == 400
    assert mock_read.call_count == 400


def test_write_read_aging_pass(mocker: MockerFixture, capsys):
    mock_write = mocker.patch('shell.Shell._write')
    mock_read = mocker.patch('shell.Shell._read')
    mock_read.return_value = '0x00000001'
    shell = Shell()

    shell.WriteReadAging()
    captured = capsys.readouterr()
    assert captured.out.strip() == "PASS"


def test_PartialLBAWrite(mocker: MockerFixture):
    mock_write = mocker.patch('shell.Shell._write')
    mock_read = mocker.patch('shell.Shell._read')
    mock_read.return_value = '0x00000001'

    shell = Shell()
    shell.PartialLBAWrite(repeat=1, seed=42)
    write_calls = []
    random.seed(42)
    random_val = random.randint(0x00000000, 0xFFFFFFFF)
    write_value = f"{random_val:#010x}"
    for lba in [4, 0, 3, 1, 2]:
        write_calls.append(call(lba, write_value))
    mock_write.assert_has_calls(write_calls)

    read_calls = []
    for lba in range(5):
        read_calls.append(call(lba))
    mock_read.assert_has_calls(read_calls)


def test_PartialLBAWrite_pass_and_fail(mocker: MockerFixture, capsys):
    mock_write = mocker.patch('shell.Shell._write')
    mock_read = mocker.patch('shell.Shell._read')
    mock_read.return_value = '0x00000001'

    shell = Shell()
    assert shell.PartialLBAWrite(repeat=1, seed=42) == "PASS"
    # shell.PartialLBAWrite(repeat=1, seed=42)
    # captured = capsys.readouterr()
    # assert captured.out.strip() == "PASS"

    mock_read.side_effect = ['0x00000001', '0x00000001', '0x00000002', '0x00000001', '0x00000001']
    assert shell.PartialLBAWrite(repeat=1, seed=42) == "FAIL"
    # shell.PartialLBAWrite(repeat=1, seed=42)
    # captured = capsys.readouterr()
    # assert captured.out.strip() == "FAIL"


def test_erase(mocker: MockerFixture, capsys):
    mock_erase = mocker.patch('shell.Shell._erase')
    shell = Shell()
    lba = 0
    size = 99
    shell.erase(lba, size)
    captured = capsys.readouterr().out
    calls = [call(start, min(lba + size - start, 10)) for start in range(lba, lba + size, 10)]
    mock_erase.assert_has_calls(calls)
    assert captured.strip() == "[Erase] Done"


def test_erase_range(mocker: MockerFixture, capsys):
    mock_erase_range = mocker.patch('shell.Shell._erase')
    shell = Shell()
    start_lba = 0
    end_lba = 98
    shell.erase_range(start_lba, end_lba)
    captured = capsys.readouterr().out
    calls = [call(start, min(end_lba + 1 - start, 10)) for start in range(start_lba, end_lba + 1, 10)]
    mock_erase_range.assert_has_calls(calls)
    assert captured.strip() == "[Erase Range] Done"