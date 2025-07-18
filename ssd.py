import argparse
import os
from buffer import Buffer

MIN_VALUE = 0
MAX_VALUE = 0xFFFFFFFF
MIN_VALUE_STR = "0x00000000"
MAX_VALUE_STR = "0xFFFFFFFF"
MIN_LBA = 0
MAX_LBA = 99
MIN_SIZE = 1
MAX_SIZE = 10


class SSD:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.ssd_nand = "ssd_nand.txt"
        self.ssd_output = "ssd_output.txt"
        self.buffer = Buffer()

        if not os.path.exists(self.ssd_nand):
            self.reset_ssd()

    def reset_ssd(self):
        self.write_nand([f'{lba:02d} {MIN_VALUE_STR}\n' for lba in range(100)])
        self.write_output('')
        self.buffer.reset()

    def read_all(self):
        with open(self.ssd_nand, 'r', encoding='utf-8') as f:
            return f.readlines()

    def read_output(self):
        with open(self.ssd_output, 'r', encoding='utf-8') as f:
            return f.read()

    def write_output(self, value: str):
        with open(self.ssd_output, 'w', encoding='utf-8') as f:
            f.write(value)

    def write_nand(self, lines: list[str]):
        with open(self.ssd_nand, 'w', encoding='utf-8') as f:
            f.writelines(lines)

    def read(self, lba: int):
        if not self.is_valid_lba(lba):
            self.write_output('ERROR')
            return

        value = self.buffer.read(lba)
        if not value:
            contents = self.read_all()
            value = contents[lba].split(' ')[-1]

        self.write_output(value)
        return

    def write(self, lba: int, value: str):
        if not (self.is_valid_lba(lba) and self.is_valid_value(value)):
            self.write_output('ERROR')
            return

        value = f"0x{int(value, 16):08X}"

        if not self.buffer.write('W', lba, value):
            self.flush()
            self.buffer.write('W', lba, value)
        self.write_output('')

    def _write(self, lba: int, value: str):
        contents = self.read_all()
        contents[lba] = f"{lba:02d} {value}\n"

        self.write_nand(contents)
        self.write_output('')

    def flush(self):
        command_list = self.buffer.get_command_list()
        self.do_commmands(command_list)
        self.buffer.reset()

    def do_commmands(self, command_list):
        for command in command_list:
            idx, cmd, lba, value = command.split('_')
            if cmd == 'W':
                self._write(int(lba), value)
            else:
                self._erase(int(lba), int(value))

    def erase(self, lba: int, size: int):
        if not (self.is_valid_lba(lba) and self.is_valid_size(size) and self.is_valid_lba(lba + size - 1)):
            self.write_output('ERROR')
            return

        if not self.buffer.write('E', lba, size=size):
            self.flush()
            self.buffer.write('E', lba, size=size)

        self.write_output('')

    def _erase(self, lba: int, size: int):
        contents = self.read_all()
        for idx in range(lba, lba + size):
            contents[idx] = f"{idx:02d} {MIN_VALUE_STR}\n"

        self.write_nand(contents)

    def is_valid_lba(self, lba: int):
        try:
            return MIN_LBA <= lba <= MAX_LBA
        except TypeError:
            return False

    def is_valid_value(self, hex_input: str):
        try:
            value = int(hex_input, 16)
            return MIN_VALUE <= value <= MAX_VALUE
        except ValueError:
            return False

    def is_valid_size(self, size):
        return isinstance(size, int) and MIN_SIZE <= size <= MAX_SIZE


def main():
    parser = argparse.ArgumentParser(description="SSD Read/Write")
    subparsers = parser.add_subparsers(dest='command', required=True)

    read_parser = subparsers.add_parser('R', help='Read from SSD')
    read_parser.add_argument('address', type=int, help='LBA address to read (0~99)')

    # Write 명령
    write_parser = subparsers.add_parser('W', help='Write to SSD')
    write_parser.add_argument('address', type=int, help='LBA address to write (0~99)')
    write_parser.add_argument('value', type=str, help='Hex value to write (e.g., 0x1234ABCD)')

    erase_parser = subparsers.add_parser('E', help='Erase to SSD')
    erase_parser.add_argument('address', type=int, help='LBA address to write (0~99)')
    erase_parser.add_argument('size', type=int, help='1 <= SIZE <= 10')

    subparsers.add_parser('F', help='Flush buffer')

    args = parser.parse_args()
    ssd = SSD()

    if args.command == 'R':
        ssd.read(args.address)
    elif args.command == 'W':
        ssd.write(args.address, args.value)
    elif args.command == 'E':
        ssd.erase(args.address, args.size)
    elif args.command == 'F':
        ssd.flush()


if __name__ == "__main__":
    main()
