import argparse


class SSD:
    def __init__(self, ssd_nand=None, ssd_output=None):
        self.ssd_nand = ssd_nand if ssd_output is not None else "ssd_nand.txt"
        self.ssd_output = ssd_output if ssd_output is not None else "ssd_output.txt"

    def read_all(self):
        with open(self.ssd_nand, 'r', encoding='utf-8') as f:
            return f.readlines()

    def read_output(self):
        with open(self.ssd_output, 'r', encoding='utf-8') as f:
            return f.read()

    def read(self, lba: int):
        if lba < 0 or lba > 99:
            with open(self.ssd_output, 'w', encoding='utf-8') as file:
                file.write('ERROR')
            return

        lines = self.read_all()
        value = ''
        for line in lines:
            if int(line.split(' ')[0]) == lba:
                value = line.split(' ')[-1]

        with open(self.ssd_output, 'w', encoding='utf-8') as file:
            file.write(value)

        return value

    def write(self, address: int, value):
        if 0 <= address <= 99:
            contents = self.read_all()
            contents[address] = f"{address:02d} {value}\n"

            f = open(self.ssd_nand, 'w', encoding='utf-8')
            f.writelines(contents)
            f.close()

            f = open(self.ssd_output, 'w', encoding='utf-8')
            f.write('')
            f.close()
        else:
            f = open(self.ssd_output, 'w', encoding='utf-8')
            f.write('ERROR')
            f.close()

def main():
    parser = argparse.ArgumentParser(description="SSD Read/Write")
    subparsers = parser.add_subparsers(dest='command', required=True)

    read_parser = subparsers.add_parser('R', help='Read from SSD')
    read_parser.add_argument('address', type=int, help='LBA address to read (0~99)')

    # Write 명령
    write_parser = subparsers.add_parser('W', help='Write to SSD')
    write_parser.add_argument('address', type=int, help='LBA address to write (0~99)')
    write_parser.add_argument('value', type=str, help='Hex value to write (e.g., 0x1234ABCD)')

    args = parser.parse_args()
    ssd = SSD()

    if args.command == 'R':
        ssd.read(args.address)
    elif args.command == 'W':
        ssd.write(args.address, args.value)

if __name__ == "__main__":
    main()