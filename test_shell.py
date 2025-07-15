import pytest, pytest_mock
from pytest_mock import MockerFixture
from unittest.mock import call, patch

from shell import Shell, main


def test_read_valid_index(capsys):
    shell = Shell()
    result = shell.read(3)
    captured = capsys.readouterr()
    assert captured.out.strip() == "[Read] LBA 03 : 0x00000000"


def test_read_invalid_index(capsys):
    shell = Shell()
    result = shell.read(100)
    captured = capsys.readouterr()
    assert captured.out.strip() == "[Read] ERROR"


def test_write_command():
    shell = Shell()
    output = shell.write("write 3 0xAAAABBBB")
    assert "[Write] Done" in output
    # 내부 data 값이 올바르게 바뀌었는지 직접 체크
    assert shell.data[3] == int("0xAAAABBBB", 16)

def test_write_all_success(mocker: MockerFixture, capsys):
    value = 0xAAAABBBB
    shell = Shell()
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
    mk.write.assert_called_with("write 3 0xAAAABBBB")

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
    with patch("builtins.input", side_effect=["2_", "exit"]):
        main(mk)
    with patch("builtins.input", side_effect=["2_PartialLBAWrite", "exit"]):
        main(mk)

    assert mk.PartialLBAWrite.call_count == 2

def test_cmd_WriteReadAging(mocker:MockerFixture):
    mk = mocker.Mock(spec=Shell)
    with patch("builtins.input", side_effect=["3_", "exit"]):
        main(mk)
    with patch("builtins.input", side_effect=["3_WriteReadAging", "exit"]):
        main(mk)

    assert mk.WriteReadAging.call_count == 2

def test_fullread_call(mocker:MockerFixture):
    mk = mocker.Mock(spec=Shell)
    mk.fullread()

    mk.fullread.assert_called_once()

def test_fullread_valid(mocker:MockerFixture, capsys):
    shell = Shell()
    mock_read = mocker.patch('ssd.SSD.read')

    sideeffect = [f'LBA {i:02d} : 0xFFFFFFFF' for i in range(100)]
    mock_read.side_effect = sideeffect
    shell.fullread()
    captured = capsys.readouterr()
    assert captured.out.strip() == '''[Full Read]
LBA 00 : 0xFFFFFFFF
LBA 01 : 0xFFFFFFFF
LBA 02 : 0xFFFFFFFF
LBA 03 : 0xFFFFFFFF
LBA 04 : 0xFFFFFFFF
LBA 05 : 0xFFFFFFFF
LBA 06 : 0xFFFFFFFF
LBA 07 : 0xFFFFFFFF
LBA 08 : 0xFFFFFFFF
LBA 09 : 0xFFFFFFFF
LBA 10 : 0xFFFFFFFF
LBA 11 : 0xFFFFFFFF
LBA 12 : 0xFFFFFFFF
LBA 13 : 0xFFFFFFFF
LBA 14 : 0xFFFFFFFF
LBA 15 : 0xFFFFFFFF
LBA 16 : 0xFFFFFFFF
LBA 17 : 0xFFFFFFFF
LBA 18 : 0xFFFFFFFF
LBA 19 : 0xFFFFFFFF
LBA 20 : 0xFFFFFFFF
LBA 21 : 0xFFFFFFFF
LBA 22 : 0xFFFFFFFF
LBA 23 : 0xFFFFFFFF
LBA 24 : 0xFFFFFFFF
LBA 25 : 0xFFFFFFFF
LBA 26 : 0xFFFFFFFF
LBA 27 : 0xFFFFFFFF
LBA 28 : 0xFFFFFFFF
LBA 29 : 0xFFFFFFFF
LBA 30 : 0xFFFFFFFF
LBA 31 : 0xFFFFFFFF
LBA 32 : 0xFFFFFFFF
LBA 33 : 0xFFFFFFFF
LBA 34 : 0xFFFFFFFF
LBA 35 : 0xFFFFFFFF
LBA 36 : 0xFFFFFFFF
LBA 37 : 0xFFFFFFFF
LBA 38 : 0xFFFFFFFF
LBA 39 : 0xFFFFFFFF
LBA 40 : 0xFFFFFFFF
LBA 41 : 0xFFFFFFFF
LBA 42 : 0xFFFFFFFF
LBA 43 : 0xFFFFFFFF
LBA 44 : 0xFFFFFFFF
LBA 45 : 0xFFFFFFFF
LBA 46 : 0xFFFFFFFF
LBA 47 : 0xFFFFFFFF
LBA 48 : 0xFFFFFFFF
LBA 49 : 0xFFFFFFFF
LBA 50 : 0xFFFFFFFF
LBA 51 : 0xFFFFFFFF
LBA 52 : 0xFFFFFFFF
LBA 53 : 0xFFFFFFFF
LBA 54 : 0xFFFFFFFF
LBA 55 : 0xFFFFFFFF
LBA 56 : 0xFFFFFFFF
LBA 57 : 0xFFFFFFFF
LBA 58 : 0xFFFFFFFF
LBA 59 : 0xFFFFFFFF
LBA 60 : 0xFFFFFFFF
LBA 61 : 0xFFFFFFFF
LBA 62 : 0xFFFFFFFF
LBA 63 : 0xFFFFFFFF
LBA 64 : 0xFFFFFFFF
LBA 65 : 0xFFFFFFFF
LBA 66 : 0xFFFFFFFF
LBA 67 : 0xFFFFFFFF
LBA 68 : 0xFFFFFFFF
LBA 69 : 0xFFFFFFFF
LBA 70 : 0xFFFFFFFF
LBA 71 : 0xFFFFFFFF
LBA 72 : 0xFFFFFFFF
LBA 73 : 0xFFFFFFFF
LBA 74 : 0xFFFFFFFF
LBA 75 : 0xFFFFFFFF
LBA 76 : 0xFFFFFFFF
LBA 77 : 0xFFFFFFFF
LBA 78 : 0xFFFFFFFF
LBA 79 : 0xFFFFFFFF
LBA 80 : 0xFFFFFFFF
LBA 81 : 0xFFFFFFFF
LBA 82 : 0xFFFFFFFF
LBA 83 : 0xFFFFFFFF
LBA 84 : 0xFFFFFFFF
LBA 85 : 0xFFFFFFFF
LBA 86 : 0xFFFFFFFF
LBA 87 : 0xFFFFFFFF
LBA 88 : 0xFFFFFFFF
LBA 89 : 0xFFFFFFFF
LBA 90 : 0xFFFFFFFF
LBA 91 : 0xFFFFFFFF
LBA 92 : 0xFFFFFFFF
LBA 93 : 0xFFFFFFFF
LBA 94 : 0xFFFFFFFF
LBA 95 : 0xFFFFFFFF
LBA 96 : 0xFFFFFFFF
LBA 97 : 0xFFFFFFFF
LBA 98 : 0xFFFFFFFF
LBA 99 : 0xFFFFFFFF'''
