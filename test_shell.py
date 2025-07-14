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
    with patch("builtins.input", side_effect=["fullwrite", "exit"]):
        main(mk)

    mk.full_write.assert_called()

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

