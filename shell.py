import random
import subprocess
import random

class Shell:
    MIN_INDEX = 0
    MAX_INDEX = 100 # 99번까지

    def read(self, lba: int):
        line = self._read(lba)

        if  line == f"ERROR":
            print("[Read] ERROR")
        else:
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
                print("[Write] ERROR")
                return
            self._write(lba, value)
        except Exception:
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
            if output_msg == "ERROR":
                print("[Write] ERROR")
            else:
                print("[Write] Done")
        except Exception:
            print(f"Usage: write <LBA> <VALUE>")

    def full_write(self, value):
        for lba in range(self.MAX_INDEX):
            self._write(lba, value)
        print(f"[Full Write] Done")

    def full_read(self):
        print('[Full Read]')
        for lba in range(self.MAX_INDEX):
            print(f'LBA {lba:02d} : {self._read(lba)}')

    def FullWriteAndReadCompare(self):
        ssd_length = self.MAX_INDEX
        block_length = 5
        for block_idx in range(ssd_length // block_length):
            random_val = random.randint(0x00000001, 0xFFFFFFFF)
            random_val = f"{random_val:#08X}"
            remove_duplicates = set()
            for inner_idx in range(block_length):
                idx = block_idx * block_length + inner_idx
                self._write(idx, random_val)
                result = self._read(idx).strip()
                remove_duplicates.add(result)
            if len(remove_duplicates) == 1 and random_val in remove_duplicates:
                continue
            print("FAIL")
            return
        print("PASS")


    def PartialLBAWrite(self, repeat=30, seed=42):
        random.seed(seed)
        for _ in range(repeat):
            write_value = hex(random.randint(0x00000000, 0xFFFFFFFF))
            for lba in [4, 0, 3, 1, 2]:
                self._write(lba, write_value)

            read_value = self._read(0)
            for lba in range(1, 5):
                if read_value != self._read(lba):
                    print("FAIL")
                    return
        print("PASS")
        return


    def WriteReadAging(self):
        for _ in range(200):
            random_val = random.randint(0x00000000, 0xFFFFFFFF)
            write_value = f"{random_val:#08X}"
            self._write(0, write_value)
            self._write(99, write_value)
            if self._read(0).strip() != self._read(99).strip():
                print("FAIL")
                return
        print("PASS")
        return

    def help(self):
        print('제작자: 배성수 팀장, 연진혁, 이정은, 이찬욱, 임창근, 정구환, 이근우')
        print('명령어 사용 법 : ')
        print('1. read : read + idx')
        print('2. write : write + idx + contents')
        print('3. exit : exit')
        print('4. fullwrite : fullwrite + contents')
        print('5. fullread : fullread')
        print("6. 1_FullWriteAndReadCompare : 1_ 혹은 1_FullWriteAndReadCompare 입력")
        print("7. 2_PartialLBAWrite : 2_ 혹은 2_PartialLBAWrite 입력")
        print("8. 3_WriteReadAging : 3_ 혹은 3_WriteReadAging 입력")
        print("9. 그 외 명령어 입력 시, INVALID COMMAND 가 출력 됩니다.")

def main(shell: Shell):
    while True:
        user_input = input("Shell> ")
        user_input_list = user_input.strip().split()
        if not user_input_list:
            print ("INVALID COMMAND")
            continue

        cmd_type = user_input_list[0]

        invalid_cmd = False
        if cmd_type == "read":
            lba = int(user_input_list[1])
            shell.read(lba)
        elif cmd_type == "write":
            if len(user_input_list) != 3:
                print("Usage: write <LBA> <VALUE>")
                continue
            lba = int(user_input_list[1])
            address = user_input_list[2]
            if not (0 <= lba < 100):
                print ("[Write] ERROR: LBA out of range (0~99)")
                return
            shell.write(lba, address)
        elif cmd_type == "exit":
            break
        elif cmd_type == "help":
            shell.help()
        elif cmd_type == "fullwrite":
            value = user_input_list[1]
            shell.full_write(value)
        elif cmd_type == "fullread":
            shell.fullread()
        elif cmd_type == "1_" or cmd_type == "1_FullWriteAndReadCompare":
            shell.FullWriteAndReadCompare()
        elif cmd_type == "2_" or cmd_type == "2_PartialLBAWrite":
            shell.PartialLBAWrite()
        elif cmd_type == "3_" or cmd_type == "3_WriteReadAging":
            shell.WriteReadAging()
        else:
            invalid_cmd = True

        if invalid_cmd:
            print("INVALID COMMAND")

if __name__ == "__main__":
    shell = Shell()
    main(shell)
