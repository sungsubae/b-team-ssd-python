class Shell:
    def read(self, index: int):
        if 0 <= index <= 99:
            print(f"[Read] LBA {index:02d} : 0xAAAABBBB")
        else:
            print("[Read] ERROR")

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
        pass


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
