class SSD:
    def __init__(self):
        ...

    def write(self, address: int, value):
        f = open("ssd_nand.txt", 'r', encoding='utf-8')
        contents = f.readlines()
        f.close()

        contents[address] = f"{address:02d} {value}\n"
        f = open("ssd_nand.txt", 'w', encoding='utf-8')
        f.writelines(contents)
        f.close()

        f = open("ssd_output.txt", 'w', encoding='utf-8')
        f.write('')
        f.close()

        return contents

