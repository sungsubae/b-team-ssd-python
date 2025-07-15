import argparse
import os


class SSD:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.ssd_nand = "ssd_nand.txt"
        self.ssd_output = "ssd_output.txt"

        if not os.path.exists(self.ssd_nand):
            self.reset_ssd()

    def reset_ssd(self):
        self.write_nand([f'{lba:02d} 0x00000000\n' for lba in range(100)])
        self.write_output('')

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
        if lba < 0 or lba > 99:
            self.write_output('ERROR')
            return

        lines = self.read_all()
        value = ''
        for line in lines:
            if int(line.split(' ')[0]) == lba:
                value = line.split(' ')[-1]

        self.write_output(value)

        return value

    def write(self, lba: int, value: str):
        if not (self.is_valid_address(lba) and self.is_valid_value(value)):
            self.write_output('ERROR')
            return

        contents = self.read_all()
        contents[lba] = f"{lba:02d} {value}\n"

        self.write_nand(contents)
        self.write_output('')

    def erase(self, lba: int, size: int):
        pass

    def is_valid_address(self, address: int):
        try:
            if 0 <= address <= 99:
                return True
            else:
                return False
        except Exception as e:
            return False

    def is_valid_value(self, hex_input: str):
        try:
            value = int(hex_input, 16)

            if 0 <= value <= 0xFFFFFFFF:
                return True
            else:
                return False
        except Exception as e:
            return False


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
    erase_parser.add_argument('size', type=str, help='1 <= SIZE <= 10')

    args = parser.parse_args()
    ssd = SSD()

    if args.command == 'R':
        ssd.read(args.address)
    elif args.command == 'W':
        ssd.write(args.address, args.value)
    elif args.command == 'E':
        ssd.erase(args.address, args.size)


if __name__ == "__main__":
    main()
