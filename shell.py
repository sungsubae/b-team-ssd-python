class Shell:
    def __init__(self, size=128):
        self.data = [0] * size  # 내부 스토리지
  
    def read(self, index: int):
        if 0 <= index <= 99:
            print(f"[Read] LBA {index:02d} : 0xAAAABBBB")
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