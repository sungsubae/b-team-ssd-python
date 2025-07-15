import random

from ssd import SSD


class Shell:
    def __init__(self, size=128):
        self.ssd = SSD()
        self.data = [0] * size  # 내부 스토리지

    def read(self, lba: int):
        if 0 <= lba <= 99:
            self.ssd.read(lba)
            value = self.ssd.read_output()
            print(f"[Read] LBA {lba:02d} : {value}")
        else:
            print("[Read] ERROR")

    def write(self, line):
        tokens = line.strip().split()
        try:
            lba = int(tokens[1])
            value = int(tokens[2], 16) # 16진수
            self.data[lba] = value
            return "[Write] Done"
        except Exception:
            return "Usage: write <LBA> <VALUE>"

    def full_write(self, value):
        for lba in range(100):
            self.ssd.write(lba, value)
        print(f"[Full Write] Done")

    def fullread(self, idx = 100):
        print('[Full Read]')
        for lba in range(idx):
            print(self.ssd.read(lba))

    def FullWriteAndReadCompare(self):
        pass

    def PartialLBAWrite(self):
        pass

    def WriteReadAging(self):
        for i in range(200):
            rand_value = random.random()
            self.ssd.write(0, rand_value)
            self.ssd.write(99, rand_value)
            if self.ssd.read(0) != self.ssd.read(99):
                return False

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
        user_input_list = user_input.split(" ")

        cmd_type = user_input_list[0]
        invalid_cmd = False
        if cmd_type == "read":
            lba = int(user_input_list[1])
            shell.read(lba)
        elif cmd_type == "write":
            shell.write(user_input)
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
