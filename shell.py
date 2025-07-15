import random

from ssd import SSD
import random

class Shell:

    def __init__(self):
        self.ssd = SSD()

    def _ssd_reset(self):
        self.ssd.reset_ssd()

    def read(self, lba: int):
        if 0 <= lba <= 99:
            self.ssd.read(lba)
            value = self.ssd.read_output()
            print(f"[Read] LBA {lba:02d} : {value}")
        else:
            print("[Read] ERROR")

    def write(self, lba, address):
        try:
            self.ssd.write(lba, address)
            return "[Write] Done"
        except Exception:
            return "Usage: write <LBA> <VALUE>"

    def full_write(self, value):
        for lba in range(100):
            self.ssd.write(lba, value)
        print(f"[Full Write] Done")

    def fullread(self):
        for lba in range(100):
            print(self.ssd.read(lba))

    def FullWriteAndReadCompare(self):
        ssd_length = 100
        block_length = 5
        for block_idx in range(ssd_length // block_length):
            random_val = random.randint(0x00000001, 0xFFFFFFFF)
            random_val = f"{random_val:#08X}"
            remove_duplicates = set()
            for inner_idx in range(block_length):
                idx = block_idx * block_length + inner_idx
                self.ssd.write(idx, random_val)
                self.ssd.read(idx)
                result = self.ssd.read_output()
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
                self.ssd.write(lba, write_value)

            read_value = self.ssd.read(0)
            for lba in range(1, 5):
                if read_value != self.ssd.read(lba):
                    print("FAIL")
                    return
        print("PASS")
        return


    def WriteReadAging(self):
        for i in range(200):
            rand_value = random.random()
            self.ssd.write(0, rand_value)
            self.ssd.write(99, rand_value)
            if self.ssd.read(0) != self.ssd.read(99):
                print("FAIL")
                return False

        print("PASS")
        return True

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
