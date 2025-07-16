import os


class Buffer:
    def __init__(self):
        self.folder_path = './buffer'
        if not os.path.exists(self.folder_path):
            self.make_init_buffer()

    def read(self, lba: int):
        result = ''

        for filename in os.listdir(self.folder_path):
            if 'empty' in filename:
                continue
            parts = filename.split('_')
            if int(parts[2]) == lba:
                if parts[1] == 'W':
                    result = parts[-1]
                elif parts[1] == 'E':
                    result = '0x0x00000000'

        return result

    def write(self, cmd: str, lba: int, value: str = '', size: int = 1):
        file_list = os.listdir(self.folder_path)
        for idx in range(1, 6):
            buffer_name = str(idx) + '_empty'
            if buffer_name not in file_list:
                continue
            if cmd == 'W':
                new_file_name = str(idx) + '_' + cmd + '_' + str(lba) + '_' + value
            else:
                new_file_name = str(idx) + '_' + cmd + '_' + str(lba) + '_' + str(size)

            os.rename(os.path.join(self.folder_path, buffer_name), os.path.join(self.folder_path, new_file_name))
            return

    def erase(self, lba: int, size: int):
        pass

    def flush(self):
        pass

    def make_init_buffer(self):
        try:
            os.makedirs(self.folder_path, exist_ok=True)
            for filename in os.listdir(self.folder_path):
                file_path = os.path.join(self.folder_path, filename)
                os.remove(file_path)  # 파일 삭제

            for idx in range(1, 6):
                file_path = os.path.join(self.folder_path, str(idx) + "_empty")
                with open(file_path, 'w') as f:
                    pass
        except OSError as e:
            print(f"오류 발생: {e}")
