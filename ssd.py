class SSD:
    def __init__(self):
        ...

    def read_all(self):
        with open("ssd_nand.txt", 'r', encoding='utf-8') as f:
            return f.readlines()

    def read_output(self):
        with open("ssd_output.txt", 'r', encoding='utf-8') as f:
            return f.read()

    def write(self, address: int, value):
        if 0 <= address <= 99:
            contents = self.read_all()
            contents[address] = f"{address:02d} {value}\n"

            f = open("ssd_nand.txt", 'w', encoding='utf-8')
            f.writelines(contents)
            f.close()

            f = open("ssd_output.txt", 'w', encoding='utf-8')
            f.write('')
            f.close()
        else:
            f = open("ssd_output.txt", 'w', encoding='utf-8')
            f.write('ERROR')
            f.close()
