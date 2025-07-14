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
