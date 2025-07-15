import pytest, pytest_mock
from pytest_mock import MockerFixture
from unittest.mock import call, patch

from shell import Shell, main
from ssd import SSD
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


def test_full_write_success(mocker: MockerFixture):
    ssd_write_mock = mocker.patch('shell.Shell._write')
    value = hex(0xAAAABBBB)
    shell = Shell()
    shell._ssd_reset()
    full_call_list = [call(idx, value) for idx in range(100)]
    shell.full_write(value)
    ssd_write_mock.assert_has_calls(full_call_list)


def test_help_call(mocker: MockerFixture):
    mk = mocker.Mock(spec=Shell)
    mk.help()

    mk.help.assert_called_once()


def test_help_text_valid(capsys):
    shell = Shell()
    shell._ssd_reset()
    ret = shell.help()
    captured = capsys.readouterr()

    assert captured.out.strip() == '''제작자: 배성수 팀장, 연진혁, 이정은, 이찬욱, 임창근, 정구환, 이근우
명령어 사용 법 : 
1. read : read + idx
2. write : write + idx + contents
3. exit : exit
4. fullwrite : fullwrite + contents
5. fullread : fullread
6. 1_FullWriteAndReadCompare : 1_ 혹은 1_FullWriteAndReadCompare 입력
7. 2_PartialLBAWrite : 2_ 혹은 2_PartialLBAWrite 입력
8. 3_WriteReadAging : 3_ 혹은 3_WriteReadAging 입력
9. 그 외 명령어 입력 시, INVALID COMMAND 가 출력 됩니다.'''


def test_cmd_read(mocker:MockerFixture):
    mk = mocker.Mock(spec=Shell)
    with patch("builtins.input", side_effect=["read 0", "exit"]):
        main(mk)

    mk.read.assert_called_with(0)


def test_cmd_write(mocker:MockerFixture):
    mk = mocker.Mock(spec=Shell)
    with patch("builtins.input", side_effect=["write 3 0xAAAABBBB", "exit"]):
        main(mk)
    mk.write.assert_called_with(3, "0xAAAABBBB")


def test_cmd_fullwrite(mocker:MockerFixture):
    mk = mocker.Mock(spec=Shell)
    with patch("builtins.input", side_effect=["fullwrite 0xAAAABBBB", "exit"]):
        main(mk)
    mk.full_write.assert_called_with("0xAAAABBBB")


def test_cmd_fullread(mocker:MockerFixture):
    mk = mocker.Mock(spec=Shell)
    with patch("builtins.input", side_effect=["fullread", "exit"]):
        main(mk)

    mk.fullread.assert_called()


def test_cmd_FullWriteAndReadCompare(mocker:MockerFixture):
    mk = mocker.Mock(spec=Shell)
    with patch("builtins.input", side_effect=["1_", "exit"]):
        main(mk)

    with patch("builtins.input", side_effect=["1_FullWriteAndReadCompare", "exit"]):
        main(mk)

    assert mk.FullWriteAndReadCompare.call_count == 2


def test_cmd_PartialLBAWrite(mocker:MockerFixture):
    mk = mocker.Mock(spec=Shell)
    with patch("builtins.input", side_effect=["2_", "2_PartialLBAWrite", "exit"]):
        main(mk)

    assert mk.PartialLBAWrite.call_count == 2


def test_cmd_WriteReadAging(mocker:MockerFixture):
    mk = mocker.Mock(spec=Shell)
    with patch("builtins.input", side_effect=["3_", "3_WriteReadAging", "exit"]):
        main(mk)

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
            random_values.append(f'{random_val:#08X}')
            write_calls.append(call(i * block_length + j, f'{random_val:#08X}'))
            read_calls.append(call(i * block_length + j))
    shell_read_mock.side_effect = random_values
    random.seed(seed)
    shell.FullWriteAndReadCompare()
    shell_write_mock.assert_has_calls(write_calls)
    shell_read_mock.assert_has_calls(read_calls)
    assert capsys.readouterr().out.strip() == "PASS"


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
            random_values.append(f'{random_val:#08X}')
            write_calls.append(call(i * block_length + j, f'{random_val:#08X}'))
            read_calls.append(call(i * block_length + j))
    shell_read_mock.side_effect = random_values
    random.seed(seed+1)
    shell.FullWriteAndReadCompare()
    assert capsys.readouterr().out.strip() == "FAIL"


def test_full_read_call(mocker:MockerFixture):
    mk = mocker.Mock(spec=Shell)
    mk.full_read()

    mk.full_read.assert_called_once()


def test_full_read_valid(mocker:MockerFixture, capsys):
    shell = Shell()

    shell.full_read()
    captured = capsys.readouterr()
    assert captured.out.strip() == '[Full Read]\n' + '\n'.join([f"LBA {i:02d} : 0x00000000" for i in range(100)])


def test_write_read_aging_calls_write_400_times(mocker: MockerFixture):
    shell = Shell()
    mk = mocker.Mock(spec=SSD)

    shell.ssd = mk
    shell.WriteReadAging()

    assert mk.write.call_count == 400


def test_write_read_aging_calls_read_400_times(mocker: MockerFixture):
    shell = Shell()
    mk = mocker.Mock(spec=SSD)

    shell.ssd = mk
    shell.WriteReadAging()

    assert mk.read.call_count == 400


def test_write_read_aging_return_true():
    assert Shell().WriteReadAging() == True


def test_PartialLBAWrite(mocker: MockerFixture):
    mock_write = mocker.patch('shell.Shell._write')
    mock_read = mocker.patch('shell.Shell._read')
    mock_read.return_value = hex(1)

    shell = Shell()
    shell.PartialLBAWrite(repeat=1, seed=42)
    write_calls = []
    random.seed(42)
    write_value = hex(random.randint(0x00000000, 0xFFFFFFFF))
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
    mock_read.return_value = hex(1)


    shell = Shell()
    shell.PartialLBAWrite(repeat=1, seed=42)
    captured = capsys.readouterr()
    assert captured.out.strip() == "PASS"

    mock_read.side_effect = [hex(1), hex(1), hex(2), hex(1), hex(1)]
    shell.PartialLBAWrite(repeat=1, seed=42)
    captured = capsys.readouterr()
    assert captured.out.strip() == "FAIL"


