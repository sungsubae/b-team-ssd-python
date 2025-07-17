import builtins
import sys
from pytest_mock import MockerFixture
from unittest.mock import call, patch, mock_open

import shell
from shell import Shell, start_shell
import random


def test_read_valid_index(capsys, mocker: MockerFixture):
    mock_run = mocker.patch("shell.subprocess.run")

    mocked_file = mocker.mock_open(read_data="0x00000000")
    mocker.patch("builtins.open", mocked_file)

    shell = Shell()
    shell.read(3)
    captured = capsys.readouterr()

    mock_run.assert_called_once_with(['python', 'ssd.py', 'R', '3'], capture_output=True, text=True)

    assert captured.out.strip() == "[Read] LBA 03 : 0x00000000"


def test_read_invalid_index(capsys, mocker: MockerFixture):
    mock_run = mocker.patch("shell.subprocess.run")

    mocked_file = mocker.mock_open(read_data="ERROR")
    mocker.patch("builtins.open", mocked_file)

    shell = Shell()
    shell.read(100)
    captured = capsys.readouterr()

    mock_run.assert_called_once_with(['python', 'ssd.py', 'R', '100'], capture_output=True, text=True)

    assert captured.out.strip() == "[Read] ERROR"


def test_write(capsys, mocker: MockerFixture):
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
    shell.help()
    captured = capsys.readouterr()

    assert captured.out.strip() == '''제작자: 배성수 팀장, 연진혁, 이정은, 이찬욱, 임창근, 정구환, 이근우
명령어 사용 법 : 
 1. read: read [LBA]
 2. write: write [LBA] [VALUE]
 3. erase: erase [LBA] [SIZE]
 4. erase_range: erase_range [ST_LBA] [EN_LBA]
 5. fullwrite: fullwrite [VALUE]
 6. fullread: fullread
 7. flush: flush
 8. 1_FullWriteAndReadCompare: 1_ 혹은 1_FullWriteAndReadCompare 입력
 9. 2_PartialLBAWrite: 2_ 혹은 2_PartialLBAWrite 입력
10. 3_WriteReadAging: 3_ 혹은 3_WriteReadAging 입력
11. 4_EraseAndWriteAging: 4_ 혹은 4_EraseAndWriteAging 입력
12. exit: exit
그 외 명령어 입력 시, INVALID COMMAND 가 출력 됩니다.'''


def test_cmd_read(mocker: MockerFixture):
    mk = mocker.Mock(spec=Shell)
    with patch("builtins.input", side_effect=["read 0", "exit"]):
        start_shell(mk)

    mk.read.assert_called_with(0)


def test_cmd_write(mocker: MockerFixture):
    mk = mocker.Mock(spec=Shell)
    with patch("builtins.input", side_effect=["write 3 0xAAAABBBB", "exit"]):
        start_shell(mk)
    mk.write.assert_called_with(3, "0xAAAABBBB")


def test_cmd_fullwrite(mocker: MockerFixture):
    mk = mocker.Mock(spec=Shell)
    with patch("builtins.input", side_effect=["fullwrite 0xAAAABBBB", "exit"]):
        start_shell(mk)
    mk.full_write.assert_called_with("0xAAAABBBB")


def test_cmd_full_write_and_read_compare(mocker: MockerFixture):
    mk = mocker.Mock(spec=Shell)
    with patch("builtins.input", side_effect=["1_", "exit"]):
        start_shell(mk)

    with patch("builtins.input", side_effect=["1_FullWriteAndReadCompare", "exit"]):
        start_shell(mk)

    assert mk.full_write_and_read_compare.call_count == 2


def test_cmd_partial_lba_write(mocker: MockerFixture):
    mk = mocker.Mock(spec=Shell)
    with patch("builtins.input", side_effect=["2_", "2_PartialLBAWrite", "exit"]):
        start_shell(mk)

    assert mk.partial_lba_write.call_count == 2


def test_cmd_write_read_aging(mocker: MockerFixture):
    mk = mocker.Mock(spec=Shell)
    with patch("builtins.input", side_effect=["3_", "3_WriteReadAging", "exit"]):
        start_shell(mk)

    assert mk.write_read_aging.call_count == 2


def test_full_write_and_read_compare_success(mocker: MockerFixture, capsys):
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
    shell.full_write_and_read_compare()
    captured = capsys.readouterr()
    assert captured.out.strip() == "PASS"
    shell_write_mock.assert_has_calls(write_calls)
    shell_read_mock.assert_has_calls(read_calls)


def test_full_write_and_read_compare_fail(mocker: MockerFixture, capsys):
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

    shell.full_write_and_read_compare()
    captured = capsys.readouterr()
    assert captured.out.strip() == "FAIL"


def test_full_read_call(mocker: MockerFixture):
    '''
    cmd에서 fullread 입력 시,
    fullread 함수가 정상적으로 호출되는지 확인하는 테스트 입니다.
    '''
    mk = mocker.Mock(spec=Shell)
    with patch("builtins.input", side_effect=["fullread", "exit"]):
        start_shell(mk)

    mk.full_read.assert_called_once()


def test_full_read_valid(mocker: MockerFixture, capsys):
    '''
    fullread 호출 시,
    _read 함수를 100회 정상 호출 하는지 확인하고,
    _read 함수의 return 값을 제외한 나머지 부분이 정상적으로 출력되는지 확인하는 테스트 입니다.
    '''
    mk_full_read = mocker.patch('shell.Shell._read')
    mk_full_read.return_value = '0x00000000'

    with patch("builtins.input", side_effect=["fullread", "exit"]):
        start_shell(Shell())

    captured = capsys.readouterr()
    assert mk_full_read.call_count == 100
    assert captured.out.strip() == '[Full Read]\n' + '\n'.join([f"LBA {i:02d} : 0x00000000" for i in range(100)])


def test_write_read_aging_calls_write_read_400_times(mocker: MockerFixture, capsys):
    mock_write = mocker.patch('shell.Shell._write')
    mock_read = mocker.patch('shell.Shell._read')
    mock_read.return_value = '0x00000001'
    shell = Shell()

    shell.write_read_aging()
    captured = capsys.readouterr()
    assert captured.out.strip() == "PASS"
    assert mock_write.call_count == 400
    assert mock_read.call_count == 400


def test_partial_lba_write(mocker: MockerFixture):
    mock_write = mocker.patch('shell.Shell._write')
    mock_read = mocker.patch('shell.Shell._read')
    mock_read.return_value = '0x00000001'

    shell = Shell()
    shell.partial_lba_write(repeat=1, seed=42)
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


def test_partial_lba_write_pass_and_fail(mocker: MockerFixture, capsys):
    mock_read = mocker.patch('shell.Shell._read')
    mock_read.return_value = '0x00000001'

    shell = Shell()
    shell.partial_lba_write(repeat=1, seed=42)
    captured = capsys.readouterr()
    assert captured.out.strip() == "PASS"

    mock_read.side_effect = ['0x00000001', '0x00000001', '0x00000002', '0x00000001', '0x00000001']
    shell.partial_lba_write(repeat=1, seed=42)
    captured = capsys.readouterr()
    assert  captured.out.strip()  == "FAIL"



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

def test_erase_and_write_aging(mocker):
    shell = Shell()
    # erase_range, _write 메서드를 mock
    erase_range_mock = mocker.patch.object(shell, '_erase_range')
    write_mock = mocker.patch.object(shell, '_write')
    shell.erase_and_write_aging(loop=1)

    assert erase_range_mock.call_count == 50
    assert write_mock.call_count == 98

    first_en = min(0 + 2, 99)
    erase_range_mock.assert_any_call(0, first_en)
    called_args_list = [call.args for call in write_mock.call_args_list[:2]]
    assert all(isinstance(args[0], int) for args in called_args_list)
    assert all(isinstance(args[1], str) and args[1].startswith("0x") for args in called_args_list)

    for lba in range(49):
        st = lba * 2
        en = min(st + 2, 99)
        w1_args = write_mock.call_args_list[lba * 2].args
        w2_args = write_mock.call_args_list[lba * 2 + 1].args
        assert w1_args[0] == en
        assert w2_args[0] == en
        assert w1_args[1].startswith("0x") and w2_args[1].startswith("0x")


def test_runner_call(mocker: MockerFixture):
    '''
    cmd 창에서 명령에 입력 시,
    정상적으로 runner 호출 되는지 확인하는 test 입니다.
    '''
    mk_startrunner = mocker.patch('shell.start_runner')
    mk_startrunner.side_effect = None

    test_args = ['shell.py', r'.\path\to\shell_script.txt']
    with mk_startrunner.patch.object(sys, 'argv', test_args):
        shell.main()

    mk_startrunner.assert_called_once()


def _mock_runner_invalid_input(file_path):
    '''
    아래 test_runner_incorrect_path 를 수행하기 위한
    mock.patch 함수입니다.
    '''
    try:
        with open(file_path, encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.rstrip("\n")  # 줄 끝 개행 문자 제거
                if line == '1_' or line == '1_FullWriteAndReadCompare':
                    print('1_PASS', end='', flush=True)
                elif line == '2_' or line == '2_PartialLBAWrite':
                    print('2_PASS', end='', flush=True)
                elif line == '3_' or line == '3_WriteReadAging':
                    print('3_PASS', end='', flush=True)
                elif line == '4_' or line == '4_EraseAndWriteAging':
                    print('4_PASS', end='', flush=True)
                else:
                    continue
    except:
        print('INVALID COMMAND')


def test_runner_incorrect_path(mocker: MockerFixture, capsys):
    '''
    runner 실행 시, 파일 경로가 잘 못 입력 되었을 때, 확인 하는 테스트 입니다.
    바로 위에서 정의한 _mock_runner_invalid_input 를 사용하여 test 하였고,
    test PASS 후, 함수 개선 결과를 real 함수에 반영 완료 했습니다.
    '''
    mk_startrunner = mocker.patch('shell.start_runner')
    mk_startrunner.side_effect = _mock_runner_invalid_input

    incorrect_path = r'./incorrect_path.txt'
    mk_startrunner(incorrect_path)
    captured = capsys.readouterr().out
    mk_startrunner.assert_called_once()
    assert captured.strip() == "INVALID COMMAND"

    correct_path = r'.\path\to\shell_script.txt'
    mk_startrunner(correct_path)
    captured = capsys.readouterr().out
    assert captured.strip() == "1_PASS2_PASS3_PASS4_PASS"

def test_runner_fail(mocker:MockerFixture, capsys):
    '''
    runner 진행 간, test_script fail 발생 시,
    FAIL! 정상 출력 여부 및 break 동작 여부 확인 test 입니다.
    '''
    def do_test(expect):
        shell.start_runner(Shell(), r'.\path\to\shell_script.txt')
        captured = capsys.readouterr().out
        assert captured.strip() == expect

    mk_test_1 = mocker.patch('shell.Shell.full_write_and_read_compare')
    mk_test_2 = mocker.patch('shell.Shell.partial_lba_write')
    mk_test_3 = mocker.patch('shell.Shell.write_read_aging')
    mk_test_4 = mocker.patch('shell.Shell.erase_and_write_aging')

    mk_test_1.side_effect = ['FAIL', 'PASS', 'PASS', 'PASS', 'PASS']
    mk_test_2.side_effect = ['FAIL', 'PASS', 'PASS', 'PASS']
    mk_test_3.side_effect = ['FAIL', 'PASS', 'PASS']
    mk_test_4.side_effect = ['FAIL', 'PASS']

    expect = '''1_FullWriteAndReadCompare  ___   Run...FAIL!'''
    do_test(expect)

    expect = '''1_FullWriteAndReadCompare  ___   Run...PASS
2_PartialLBAWrite          ___   Run...FAIL!'''
    do_test(expect)

    expect = '''1_FullWriteAndReadCompare  ___   Run...PASS
2_PartialLBAWrite          ___   Run...PASS
3_WriteReadAging           ___   Run...FAIL!'''
    do_test(expect)

    expect = '''1_FullWriteAndReadCompare  ___   Run...PASS
2_PartialLBAWrite          ___   Run...PASS
3_WriteReadAging           ___   Run...PASS
4_EraseAndWriteAging       ___   Run...FAIL!'''
    do_test(expect)

    expect = '''1_FullWriteAndReadCompare  ___   Run...PASS
2_PartialLBAWrite          ___   Run...PASS
3_WriteReadAging           ___   Run...PASS
4_EraseAndWriteAging       ___   Run...PASS'''
    do_test(expect)