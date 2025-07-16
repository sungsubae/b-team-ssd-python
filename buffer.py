import os
import re


class Buffer:
    def __init__(self):
        self.folder_path = './buffer'
        if not os.path.exists(self.folder_path):
            self.make_init_buffer()

    def _extract_leading_number(self, filename: str):
        match = re.match(r'^(\d+)_', filename)
        if match:
            return int(match.group(1))
        return float('inf')

    def read(self, lba: int):
        file_list = os.listdir(self.folder_path)
        file_list.sort(key=self._extract_leading_number, reverse=True)

        for filename in file_list:
            if 'empty' in filename:
                continue
            parts = filename.split('_')
            if int(parts[2]) == lba:
                if parts[1] == 'W':
                    return parts[-1]
                elif parts[1] == 'E':
                    return '0x00000000'

        return ''

    def write(self, cmd: str, lba: int, value: str = '', size: int = 1):
        file_list = os.listdir(self.folder_path)
        file_list.sort(key=self._extract_leading_number)

        for file_name in file_list:
            if 'empty' not in file_name:
                continue
            if cmd == 'W':
                new_file_name = f'{file_name[0]}_{cmd}_{lba}_{value}'
            else:
                new_file_name = f'{file_name[0]}_{cmd}_{lba}_{size}'

            os.rename(os.path.join(self.folder_path, file_name), os.path.join(self.folder_path, new_file_name))
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
