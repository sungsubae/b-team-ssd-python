import pytest, pytest_mock
from pytest_mock import MockerFixture
from unittest.mock import call, patch

from shell import Shell, main
from ssd import SSD
import random


def test_read_valid_index(capsys):
    shell = Shell()
    shell._ssd_reset()
    shell.read(3)
    captured = capsys.readouterr()
    assert captured.out.strip() == "[Read] LBA 03 : 0x00000000"


def test_read_invalid_index(capsys):
    shell = Shell()
    shell._ssd_reset()
    shell.read(100)
    captured = capsys.readouterr()
    assert captured.out.strip() == "[Read] ERROR"


def test_write(mocker :MockerFixture):
    value = "0xAAAABBBB"
    # SSD.write를 모킹(patch)
    mock_write = mocker.patch('ssd.SSD.write')
    shell = Shell()    # 이 시점에 Shell 내부의 SSD 인스턴스는 이미 patch된 write를 사용
    # shell.write(7, 0xDEADBEEF)
    result = shell.write(3, value)
    assert "[Write] Done" in result
    mock_write.assert_called_once_with(3, value)


def test_write_all_success(mocker: MockerFixture, capsys):
    value = 0xAAAABBBB
    shell = Shell()
    shell._ssd_reset()
    ssd_write_mock = mocker.patch('ssd.SSD.write')
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
    ssd = mocker.Mock(spec=SSD)
    shell = Shell()
    shell.ssd = ssd
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
    ssd.read_output.side_effect = random_values
    random.seed(seed)
    shell.FullWriteAndReadCompare()
    ssd.write.assert_has_calls(write_calls)
    ssd.read.assert_has_calls(read_calls)
    assert capsys.readouterr().out == "PASS\n"

def test_full_write_and_read_compare_fail(mocker:MockerFixture, capsys):
    seed = 42
    ssd = mocker.Mock(spec=SSD)
    shell = Shell()
    shell.ssd = ssd
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
    ssd.read_output.side_effect = random_values
    shell.FullWriteAndReadCompare()

    assert capsys.readouterr().out == "FAIL\n"

def test_fullread_call(mocker:MockerFixture):
    mk = mocker.Mock(spec=Shell)
    mk.fullread()

    mk.fullread.assert_called_once()


def test_fullread_valid(mocker:MockerFixture, capsys):
    shell = Shell()
    shell._ssd_reset()

    shell.fullread()
    captured = capsys.readouterr()
    assert captured.out.strip() == '''[Full Read]
LBA 00 : 0x00000000
LBA 01 : 0x00000000
LBA 02 : 0x00000000
LBA 03 : 0x00000000
LBA 04 : 0x00000000
LBA 05 : 0x00000000
LBA 06 : 0x00000000
LBA 07 : 0x00000000
LBA 08 : 0x00000000
LBA 09 : 0x00000000
LBA 10 : 0x00000000
LBA 11 : 0x00000000
LBA 12 : 0x00000000
LBA 13 : 0x00000000
LBA 14 : 0x00000000
LBA 15 : 0x00000000
LBA 16 : 0x00000000
LBA 17 : 0x00000000
LBA 18 : 0x00000000
LBA 19 : 0x00000000
LBA 20 : 0x00000000
LBA 21 : 0x00000000
LBA 22 : 0x00000000
LBA 23 : 0x00000000
LBA 24 : 0x00000000
LBA 25 : 0x00000000
LBA 26 : 0x00000000
LBA 27 : 0x00000000
LBA 28 : 0x00000000
LBA 29 : 0x00000000
LBA 30 : 0x00000000
LBA 31 : 0x00000000
LBA 32 : 0x00000000
LBA 33 : 0x00000000
LBA 34 : 0x00000000
LBA 35 : 0x00000000
LBA 36 : 0x00000000
LBA 37 : 0x00000000
LBA 38 : 0x00000000
LBA 39 : 0x00000000
LBA 40 : 0x00000000
LBA 41 : 0x00000000
LBA 42 : 0x00000000
LBA 43 : 0x00000000
LBA 44 : 0x00000000
LBA 45 : 0x00000000
LBA 46 : 0x00000000
LBA 47 : 0x00000000
LBA 48 : 0x00000000
LBA 49 : 0x00000000
LBA 50 : 0x00000000
LBA 51 : 0x00000000
LBA 52 : 0x00000000
LBA 53 : 0x00000000
LBA 54 : 0x00000000
LBA 55 : 0x00000000
LBA 56 : 0x00000000
LBA 57 : 0x00000000
LBA 58 : 0x00000000
LBA 59 : 0x00000000
LBA 60 : 0x00000000
LBA 61 : 0x00000000
LBA 62 : 0x00000000
LBA 63 : 0x00000000
LBA 64 : 0x00000000
LBA 65 : 0x00000000
LBA 66 : 0x00000000
LBA 67 : 0x00000000
LBA 68 : 0x00000000
LBA 69 : 0x00000000
LBA 70 : 0x00000000
LBA 71 : 0x00000000
LBA 72 : 0x00000000
LBA 73 : 0x00000000
LBA 74 : 0x00000000
LBA 75 : 0x00000000
LBA 76 : 0x00000000
LBA 77 : 0x00000000
LBA 78 : 0x00000000
LBA 79 : 0x00000000
LBA 80 : 0x00000000
LBA 81 : 0x00000000
LBA 82 : 0x00000000
LBA 83 : 0x00000000
LBA 84 : 0x00000000
LBA 85 : 0x00000000
LBA 86 : 0x00000000
LBA 87 : 0x00000000
LBA 88 : 0x00000000
LBA 89 : 0x00000000
LBA 90 : 0x00000000
LBA 91 : 0x00000000
LBA 92 : 0x00000000
LBA 93 : 0x00000000
LBA 94 : 0x00000000
LBA 95 : 0x00000000
LBA 96 : 0x00000000
LBA 97 : 0x00000000
LBA 98 : 0x00000000
LBA 99 : 0x00000000'''

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
    import random
    shell = Shell()
    shell.ssd = mocker.Mock(spec=SSD)

    shell.PartialLBAWrite(repeat=1, seed=42)
    write_calls = []
    random.seed(42)
    write_value = hex(random.randint(0x00000000, 0xFFFFFFFF))
    for lba in [4, 0, 3, 1, 2]:
        write_calls.append(call(lba, write_value))
    shell.ssd.write.assert_has_calls(write_calls)

    read_calls = []
    for lba in range(5):
        read_calls.append(call(lba))
    shell.ssd.read.assert_has_calls(read_calls)

def test_PartialLBAWrite_pass(capsys):
    Shell().PartialLBAWrite()
    captured = capsys.readouterr()
    assert captured.out.strip() == "PASS"

