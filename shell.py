import random
import subprocess
from functools import wraps

from command_factory import CommandFactory
from logger import Logger
from command_shell import COMMANDS
import sys


def log_and_print(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        method_name = func.__name__
        class_name = self.__class__.__name__
        location = f"{class_name}.{method_name}()"
        msg = result if isinstance(result, str) else str(result)
        for msg in self.msg:
            self.logger.print(msg.strip(), location=location)
            print(msg.strip())
        self.msg.clear()
        return result
    return wrapper


class Shell:
    MIN_INDEX = 0
    MAX_INDEX = 100  # 99번까지

    def __init__(self):
        self.logger = Logger()
        self.msg = []

    @log_and_print
    def read(self, lba: int):
        line = self._read(lba)

        if line == "ERROR":
            self.msg.append("[Read] ERROR")
        else:
            self.msg.append(f"[Read] LBA {lba:02d} : {line}")

        return self.msg

    def _read(self, lba):
        subprocess.run(
            ["python", "ssd.py", "R", str(lba)],
            capture_output=True,
            text=True
        )
        output = 'ssd_output.txt'
        with open(output, 'r', encoding='utf-8') as file:
            line = file.readline().strip()
        return line

    def is_hex_string(self, s):
        try:
            int(s, 16)
            return True
        except ValueError:
            return False

    @log_and_print
    def write(self, lba, value):
        try:
            if not (0 <= lba < self.MAX_INDEX):
                self.msg.append("[Write] ERROR")
                return
            if not self.is_hex_string(value):
                self.msg.append("[Write] ERROR")
                return self.msg

            output_msg = self._write(lba, value)
            if output_msg == "ERROR":
                self.msg.append("[Write] ERROR")
            else:
                self.msg.append("[Write] Done")
        except Exception:
            self.msg.append("Usage: write <LBA> <VALUE>")

        return self.msg

    @log_and_print
    def _write(self, lba, value):
        try:
            subprocess.run(
                ["python", "ssd.py", "W", str(lba), value],
                capture_output=True,
                text=True
            )
            with open("ssd_output.txt", "r", encoding="utf-8") as f:
                output_msg = f.read().strip()
            return output_msg
        except Exception:
            self.msg.append("Usage: write <LBA> <VALUE>")

        return self.msg

    def _erase(self, lba, size):
        subprocess.run(
            ["python", "ssd.py", "E", str(lba), str(size)],
            capture_output=True,
            text=True
        )
        output = 'ssd_output.txt'
        with open(output, 'r', encoding='utf-8') as file:
            line = file.readline().strip()
        return line == "ERROR"

    @log_and_print
    def erase(self, lba, size):
        if (lba < self.MIN_INDEX or lba >= self.MAX_INDEX):
            self.msg.append("[Erase] ERROR")
            return self.msg
        if size <= self.MIN_INDEX or size > self.MAX_INDEX:
            self.msg.append("[Erase] ERROR")
            return self.msg
        if lba + size > self.MAX_INDEX:
            self.msg.append("[Erase] ERROR")
            return self.msg

        for start in range(lba, lba + size, 10):
            end = min(lba + size - start, 10)
            self._erase(start, end)

        self.msg.append("[Erase] Done")

        return self.msg

    @log_and_print
    def erase_range(self, start_lba, end_lba):
        result = "[Erase Range] " + self._erase_range(start_lba, end_lba)
        self.msg.append(result)
        return self.msg

    def _erase_range(self, start_lba, end_lba):
        if not (self.MIN_INDEX <= start_lba <= end_lba < self.MAX_INDEX):
            return "ERROR"
        for start in range(start_lba, end_lba + 1, 10):
            end = min(end_lba + 1 - start, 10)
            self._erase(start, end)
        return "Done"

    @log_and_print
    def full_write(self, value):
        for lba in range(self.MAX_INDEX):
            self._write(lba, value)

        self.msg.append("[Full Write] Done")

        return self.msg

    @log_and_print
    def full_read(self):
        self.msg.append("[Full Read]")
        for lba in range(self.MAX_INDEX):
            self.msg.append(f'LBA {lba:02d} : {self._read(lba)}')

        return self.msg

    @log_and_print
    def flush(self):
        subprocess.run(
            ["python", "ssd.py", "F"],
            capture_output=True,
            text=True
        )
        self.msg.append("[Flush]")
        return self.msg

    @log_and_print
    def full_write_and_read_compare(self):
        ssd_length = self.MAX_INDEX
        block_length = 5
        before_random_val = "0x00000000"
        random_val = "0x00000000"
        for block_idx in range(ssd_length // block_length):
            while before_random_val == random_val:
                random_val = random.randint(0X00000001, 0XFFFFFFFF)
                random_val = f"{random_val:#010x}"
            before_random_val = random_val
            remove_duplicates = set()
            for inner_idx in range(block_length):
                idx = block_idx * block_length + inner_idx
                self._write(idx, random_val)
                result = self._read(idx).strip()
                remove_duplicates.add(result)
            if len(remove_duplicates) == 1 and random_val in remove_duplicates:
                continue
            self.msg.append("FAIL")
            return self.msg
        self.msg.append("PASS")
        return self.msg

    @log_and_print
    def partial_lba_write(self, repeat=30, seed=42):
        random.seed(seed)
        for _ in range(repeat):
            random_val = random.randint(0x00000000, 0xFFFFFFFF)
            write_value = f"{random_val:#010x}"
            for lba in [4, 0, 3, 1, 2]:
                self._write(lba, write_value)

            read_value = self._read(0)
            for lba in range(1, 5):
                if read_value != self._read(lba):
                    self.msg.append("FAIL")
                    return self.msg

        self.msg.append("PASS")
        return self.msg

    @log_and_print
    def write_read_aging(self):
        for _ in range(200):
            random_val = random.randint(0x00000000, 0xFFFFFFFF)
            write_value = f"{random_val:#010x}"
            self._write(0, write_value)
            self._write(99, write_value)
            if self._read(0).strip() != self._read(99).strip():
                self.msg.append("FAIL")
                return self.msg

        self.msg.append("PASS")
        return self.msg

    @log_and_print
    def erase_and_write_aging(self, loop=30):
        try:
            for cnt in range(loop):
                for i in range(50):
                    st = i * 2
                    en = st + 2
                    self._erase_range(st, min(en, 99))
                    # 마지막 LBA에 "서로 다른" 랜덤 값 2번 write
                    if en <= 99:
                        rand_val1 = random.randint(0x00000000, 0xFFFFFFFF)
                        rand_val1 = f"{rand_val1:#010x}"
                        rand_val2 = rand_val1
                        # rand_val2가 rand_val1과 다를 때까지 뽑기
                        while rand_val2 == rand_val1:
                            rand_val2 = random.randint(0x00000000, 0xFFFFFFFF)
                            rand_val2 = f"{rand_val2:#010x}"
                        self._write(en, rand_val1)
                        self._write(en, rand_val2)
            self.msg.append("[EraseAndWriteAging] Done")
            return self.msg
        except Exception as e:
            self.msg.append(f"[EraseAndWriteAging] FAIL: {e}")
            return self.msg

    @log_and_print
    def help(self):
        message = '''제작자: 배성수 팀장, 연진혁, 이정은, 이찬욱, 임창근, 정구환, 이근우
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
        self.msg.append(message)
        return self.msg


def check_invalid(user_input_list):
    if not user_input_list:
        return True

    cmd_type = user_input_list[0]
    if cmd_type not in ['read', 'write', 'erase', 'erase_range', 'exit', 'help', 'fullwrite', 'fullread', 'flush', '1_', '1_FullWriteAndReadCompare', '2_', '2_PartialLBAWrite', '3_', '3_WriteReadAging', '4_', '4_EraseAndWriteAging']:
        return True

    try:
        if cmd_type == "read" or cmd_type == "write":
            lba = int(user_input_list[1])
            if cmd_type == "write":
                user_input_list[2]
                if not (0 <= lba < 100):
                    return True
        if cmd_type == "erase" or cmd_type == "erase_range":
            int(user_input_list[1])
            int(user_input_list[2])
        if cmd_type == "fullwrite":
            user_input_list[1]
    except (IndexError, ValueError):
        return True

    return False


def start_runner(shell: Shell, file_path):
    def test_run_and_pass_check(func):
        ret = func()
        if ret == "FAIL":
            print(f'{ret}!')
            return False
        print(ret)
        return True

    try:
        with open(file_path, encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.rstrip("\n")  # 줄 끝 개행 문자 제거
                if line == '1_' or line == '1_FullWriteAndReadCompare':
                    print('1_FullWriteAndReadCompare  ___   Run...', end='', flush=True)
                    if not test_run_and_pass_check(shell.full_write_and_read_compare):
                        break
                elif line == '2_' or line == '2_PartialLBAWrite':
                    print('2_PartialLBAWrite          ___   Run...', end='', flush=True)
                    if not test_run_and_pass_check(shell.partial_lba_write):
                        break
                elif line == '3_' or line == '3_WriteReadAging':
                    print('3_WriteReadAging           ___   Run...', end='', flush=True)
                    if not test_run_and_pass_check(shell.write_read_aging):
                        break
                elif line == '4_' or line == '4_EraseAndWriteAging':
                    print('4_EraseAndWriteAging       ___   Run...', end='', flush=True)
                    if not test_run_and_pass_check(shell.erase_and_write_aging):
                        break
                else:
                    print('INVALID COMMAND')
                    break
    except Exception:
        print('INVALID COMMAND')


def find_command(cmd_type):
    if cmd_type in COMMANDS:
        return COMMANDS[cmd_type]
    return None


def start_factory_shell(shell: Shell):
    factory = CommandFactory()
    while True:
        user_input = input("Shell> ")
        user_input_list = user_input.strip().split()
        if not user_input_list:
            print("INVALID COMMAND")
            continue

        cmd_type = user_input_list[0].lower()
        args = user_input_list[1:]

        command = factory.create(cmd_type)
        if command:
            command.execute(shell, *args)
        else:
            print("INVALID COMMAND")


def factory_main():
    shell = Shell()
    if len(sys.argv) == 1:
        start_factory_shell(shell)
    elif len(sys.argv) == 2:
        start_runner(shell, sys.argv[1])
    else:
        print("INVALID COMMAND")
        return 1


if __name__ == "__main__":
    # sys.exit(main())
    sys.exit(factory_main())
