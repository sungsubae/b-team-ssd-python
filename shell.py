
class Shell:
    def __init__(self, size=128):
        self.data = [0] * size  # 내부 스토리지

    def ssd_write(self, line):
        return 0