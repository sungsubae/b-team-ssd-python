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


def test_write(capsys, mocker :MockerFixture):
    value = "0xAAAABBBB"
    # SSD.write를 모킹(patch)
    mock_write = mocker.patch('ssd.SSD.write')
    shell = Shell()    # 이 시점에 Shell 내부의 SSD 인스턴스는 이미 patch된 write를 사용
    # shell.write(7, 0xDEADBEEF)
    shell.write(3, value)
    captured = capsys.readouterr()
    assert captured.out.strip() == "[Write] Done"
    mock_write.assert_called_once_with(3, value)


def test_write_all_success(mocker: MockerFixture):
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

def test_write_read_aging_pass(capsys):
    Shell().WriteReadAging()
    captured = capsys.readouterr()
    assert captured.out.strip() == "PASS"


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
