from pytest_mock import MockerFixture

from shell import Shell
import pytest, pytest_mock

def test_read_valid_index(capsys):
    shell = Shell()
    result = shell.read(3)
    captured = capsys.readouterr()
    assert captured.out.strip() == "[Read] LBA 03 : 0xAAAABBBB"

def test_read_invalid_index(capsys):
    shell = Shell()
    result = shell.read(100)
    captured = capsys.readouterr()
    assert captured.out.strip() == "[Read] ERROR"

def test_help_call(mocker:MockerFixture):
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