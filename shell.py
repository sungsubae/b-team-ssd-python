class Shell:
    def read(self, index: int):
        if 0 <= index <= 99:
            print(f"[Read] LBA {index:02d} : 0xAAAABBBB")
        else:
            print("[Read] ERROR")
