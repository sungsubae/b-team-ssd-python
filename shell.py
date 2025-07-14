from ssd import SSD


class Shell:

    def __init__(self):
        self.ssd = SSD()

    def read(self, index: int):
        if 0 <= index <= 99:
            print(f"[Read] LBA {index:02d} : 0xAAAABBBB")
        else:
            print("[Read] ERROR")

    def full_write(self, value):
        for idx in range(100):
            self.ssd.write(idx, value)
        print(f"[Full Write] Done")

    def write(self, lba, value):
        pass

    def fullwrite(self):
        pass

    def fullread(self):
        pass

    def FullWriteAndReadCompare(self):
        pass

    def PartialLBAWrite(self):
        pass

    def WriteReadAging(self):
        pass

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
            lba = int(user_input_list[1])
            value = user_input_list[2]
            shell.write(lba, value)
        elif cmd_type == "exit":
            break
        elif cmd_type == "help":
            shell.help()
        elif cmd_type == "fullwrite":
            shell.fullwrite()
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