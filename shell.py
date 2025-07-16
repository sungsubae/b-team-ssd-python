import random
import subprocess

from logger import Logger
import sys

class Shell:
    MIN_INDEX = 0
    MAX_INDEX = 100  # 99번까지

    def __init__(self):
        self.logger = Logger()

    def read(self, lba: int):
        line = self._read(lba)

        if  line == f"ERROR":
            self.logger.print("[Read] ERROR")
            print("[Read] ERROR")
        else:
            self.logger.print(f"[Read] LBA {lba:02d} : {line}")
            print(f"[Read] LBA {lba:02d} : {line}")

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

    def write(self, lba, value):
        try:
            if not self.is_hex_string(value):
                self.logger.print("[Write] ERROR")
                print("[Write] ERROR")
                return

            output_msg = self._write(lba, value)

            if output_msg == "ERROR":
                print("[Write] ERROR")
            else:
                print("[Write] Done")
        except Exception:
            self.logger.print(f"Usage: write <LBA> <VALUE>")
            print(f"Usage: write <LBA> <VALUE>")

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
            self.logger.print(f"Usage: write <LBA> <VALUE>")
            print(f"Usage: write <LBA> <VALUE>")

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

    def erase(self, lba, size):
        if (lba < self.MIN_INDEX or lba >= self.MAX_INDEX):
            self.logger.print("[Erase] ERROR")
            print("[Erase] ERROR")
            return
        if size <= self.MIN_INDEX or size > self.MAX_INDEX:
            self.logger.print("[Erase] ERROR")
            print("[Erase] ERROR")
            return
        if lba + size > self.MAX_INDEX:
            self.logger.print("[Erase] ERROR")
            print("[Erase] ERROR")
            return

        for start in range(lba, lba + size, 10):
            end = min(lba + size - start, 10)
            self._erase(start, end)
        self.logger.print("[Erase] Done")
        print("[Erase] Done")


    def erase_range(self, start_lba, end_lba):
        if not (self.MIN_INDEX <= start_lba
                and start_lba <= end_lba
                and end_lba < self.MAX_INDEX):
            self.logger.print("[Erase Range] ERROR")
            print("[Erase Range] ERROR")
            return
        for start in range(start_lba, end_lba + 1, 10):
            end = min(end_lba + 1 - start, 10)
            self._erase(start, end)
        print("[Erase Range] Done")


    def full_write(self, value):
        for lba in range(self.MAX_INDEX):
            self._write(lba, value)
        self.logger.print(f"[Full Write] Done")
        print(f"[Full Write] Done")

    def full_read(self):
        self.logger.print("[Full Read]")
        print("[Full Read]")
        for lba in range(self.MAX_INDEX):
            self.logger.print(f'LBA {lba:02d} : {self._read(lba)}')
            print(f'LBA {lba:02d} : {self._read(lba)}')

    def FullWriteAndReadCompare(self):
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
            return "FAIL"
        return "PASS"


    def PartialLBAWrite(self, repeat=30, seed=42):
        random.seed(seed)
        for _ in range(repeat):
            random_val = random.randint(0x00000000, 0xFFFFFFFF)
            write_value = f"{random_val:#010x}"
            for lba in [4, 0, 3, 1, 2]:
                self._write(lba, write_value)

            read_value = self._read(0)
            for lba in range(1, 5):
                if read_value != self._read(lba):
                    return "FAIL"
        return "PASS"


    def WriteReadAging(self):
        for _ in range(200):
            random_val = random.randint(0x00000000, 0xFFFFFFFF)
            write_value = f"{random_val:#010x}"
            self._write(0, write_value)
            self._write(99, write_value)
            if self._read(0).strip() != self._read(99).strip():
                return "FAIL"
        return "PASS"

    def erase_range(self, line):
        # 파라미터 파싱 (예: "erase_range 0 2")
        tokens = line.strip().split()
        st_lba = int(tokens[1])
        en_lba = int(tokens[2])

        # 해당 구간을 0x00000000으로 초기화
        for lba in range(st_lba, en_lba + 1):
            init_val = "0x00000000"
            self.write(lba, init_val)

        print(f"[EraseRange] Done ({st_lba}~{en_lba})")

    def erase_and_write_aging(self, loop=30):
        for cnt in range(loop):
            for i in range(50):
                st = i * 2
                en = st + 2
                self.erase_range(f"erase_range {st} {min(en, 99)}")
                # 마지막 LBA에 "서로 다른" 랜덤 값 2번 write
                if en <= 99:
                    rand_val1 = random.randint(0x00000000, 0xFFFFFFFF)
                    rand_val1 = f"{rand_val1:#010x}"
                    rand_val2 = rand_val1
                    # rand_val2가 rand_val1과 다를 때까지 뽑기
                    while rand_val2 == rand_val1:
                        rand_val2 = random.randint(0x00000000, 0xFFFFFFFF)
                        rand_val2 = f"{rand_val2:#010x}"
                    self.write(en, rand_val1)
                    self.write(en, rand_val2)
                    print(f"{en} 번 난수로 변경 ")

        print("[EraseAndWriteAging] Done")

    def help(self):
        message = '''제작자: 배성수 팀장, 연진혁, 이정은, 이찬욱, 임창근, 정구환, 이근우
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
        print(message)
        self.logger.print(message)


def checkInvalid(user_input_list):
    if not user_input_list:
        return True

    cmd_type = user_input_list[0]
    if cmd_type not in ['read', 'write', 'erase', 'erase_range', 'exit', 'help', 'fullwrite', 'fullread', '1_', '1_FullWriteAndReadCompare', '2_', '2_PartialLBAWrite', '3_', '3_WriteReadAging', '4_', '4_EraseAndWriteAging']:
        return True

    try:
        if cmd_type == "read" or cmd_type == "write":
            lba = int(user_input_list[1])
            if cmd_type == "write":
                user_input_list[2]
                if not (0 <= lba < 100):
                    return True
        if cmd_type == "fullwrite":
            user_input_list[1]
    except (IndexError, ValueError):
        return True

    return False

def startShell(shell: Shell):
    logger = Logger()

    def loggingAndPrinting(ret:str):
        logger.print(ret)
        print(ret)

    while True:
        user_input = input("Shell> ")
        user_input_list = user_input.strip().split()

        if checkInvalid(user_input_list):
            print("INVALID COMMAND")
            continue

        cmd_type = user_input_list[0]
        if cmd_type == "read":
            lba = int(user_input_list[1])
            shell.read(lba)
        elif cmd_type == "write":
            lba = int(user_input_list[1])
            address = user_input_list[2]
            shell.write(lba, address)
        elif cmd_type == "erase":
            start_lba = int(user_input_list[1])
            size = int(user_input_list[2])
            shell.erase(start_lba, size)
        elif cmd_type == "erase_range":
            start_lba = int(user_input_list[1])
            end_lba = int(user_input_list[2])
            shell.erase_range(start_lba, end_lba)
        elif cmd_type == "exit":
            break
        elif cmd_type == "help":
            shell.help()
        elif cmd_type == "fullwrite":
            value = user_input_list[1]
            shell.full_write(value)
        elif cmd_type == "fullread":
            shell.full_read()
        elif cmd_type == "1_" or cmd_type == "1_FullWriteAndReadCompare":
            loggingAndPrinting(shell.FullWriteAndReadCompare())
        elif cmd_type == "2_" or cmd_type == "2_PartialLBAWrite":
            loggingAndPrinting(shell.PartialLBAWrite())
        elif cmd_type == "3_" or cmd_type == "3_WriteReadAging":
            loggingAndPrinting(shell.WriteReadAging())
        else:
            continue



def startRunner(shell: Shell, file_path):
    with open(file_path, encoding="utf-8") as f:
        for raw_line in f:
            line = raw_line.rstrip("\n")  # 줄 끝 개행 문자 제거
            if line == '1_' or line == '1_FullWriteAndReadCompare':
                print('1_FullWriteAndReadCompare  ___   Run...', end='', flush=True)
                shell.FullWriteAndReadCompare()
            elif line == '2_' or line == '2_PartialLBAWrite':
                print('2_PartialLBAWrite          ___   Run...', end='', flush=True)
                shell.PartialLBAWrite()
            elif line == '3_' or line == '3_WriteReadAging':
                print('3_WriteReadAging           ___   Run...', end='', flush=True)
                shell.WriteReadAging()
            elif line == '4_' or line == '4_EraseAndWriteAging':
                print('4_EraseAndWriteAging       ___   Run...', end='', flush=True)
                # shell.FullWriteAndReadCompare()
            else:
                continue


def main():
    shell = Shell()
    if len(sys.argv) == 1:
        startShell(shell)
    elif len(sys.argv) == 2:
        startRunner(shell, sys.argv[1])
    else:
        print("INVALID COMMAND")
        return 1


if __name__ == "__main__":
    sys.exit(main())
