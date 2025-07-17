import os
import re
from pathlib import Path

class Buffer:
    def __init__(self):
        self.folder_path = Path('./buffer')
        if not self.folder_path.exists():
            self.reset()

    def get_sorted_buffer_file_list(self, reverse=False):
        return sorted(os.listdir(self.folder_path), reverse=reverse)

    def get_command_list(self):
        command_list = []
        for filename in self.get_sorted_buffer_file_list():
            if 'empty' in filename:
                break
            command_list.append(filename)
        return command_list

    def read(self, lba: int):
        file_list = self.get_sorted_buffer_file_list(reverse=True)

        for filename in file_list:
            if 'empty' in filename:
                continue
            parts = filename.split('_')
            if parts[1] == 'W' and int(parts[2]) == lba:
                return parts[-1]
            elif parts[1] == 'E' and int(parts[2]) <= lba <= int(parts[2]) + int(parts[3]) - 1:
                return '0x00000000'

        return ''

    def write(self, cmd: str, lba: int, value: str = '', size: int = 1):
        file_list = self.get_sorted_buffer_file_list()

        for file_name in file_list:
            if 'empty' not in file_name:
                continue
            if cmd == 'W':
                if self._join_write_command(lba, value):
                    return
                new_file_name = f'{file_name[0]}_{cmd}_{lba}_{value}'
            else:
                self._delete_write_command(lba, size)
                if self._join_erase_command(lba, size):
                    return True
                new_file_name = f'{file_name[0]}_{cmd}_{lba}_{size}'

            os.rename(self.folder_path/file_name, self.folder_path/new_file_name)
            return True
        return False

    def reset(self):
        try:
            self.folder_path.mkdir(parents=True, exist_ok=True)
            for filename in os.listdir(self.folder_path):
                file_path = self.folder_path/filename
                os.remove(file_path)  # 파일 삭제

            for idx in range(1, 6):
                file_path = self.folder_path/f"{idx}_empty"
                file_path.touch()
        except OSError as e:
            print(f"오류 발생: {e}")

    def _join_erase_command(self, lba: int, size: int):
        file_list = self.get_sorted_buffer_file_list()

        for file_name in file_list:
            if 'E' not in file_name:
                continue
            parts = file_name.split('_')
            buffer_lba = int(parts[2])
            buffer_size = int(parts[3])
            if buffer_lba <= lba <= buffer_lba + buffer_size or lba <= buffer_lba <= lba + size:
                start = min(buffer_lba, lba)
                end = max(buffer_lba + size - 1, lba + size - 1)
                new_size = end - start + 1
                if new_size <= 10:
                    new_file_name = f'{file_name[0]}_{parts[1]}_{start}_{new_size}'
                    os.rename(self.folder_path/file_name, self.folder_path/new_file_name)
                    return True

        return False

    def _join_write_command(self, lba: int, value: str):
        file_list = self.get_sorted_buffer_file_list()

        for idx, file_name in enumerate(file_list):
            parts = file_name.split('_')
            if parts[-1] == 'empty':
                continue
            buffer_lba = int(file_name.split('_')[2])
            if buffer_lba != lba:
                continue
            if parts[1] == 'E' and int(parts[-1]) != 1:
                continue

            last_file_name = ''

            for old_file_idx, old_file_name in enumerate(file_list):
                if old_file_idx < idx or 'empty' in old_file_name:
                    continue
                if old_file_idx == len(file_list) - 1:
                    new_file_name = f'{old_file_idx+1}_empty'
                else:
                    new_file_name = str(old_file_idx+1) + file_list[old_file_idx+1][1:]
                last_file_name = new_file_name
                os.rename(os.path.join(self.folder_path, old_file_name), os.path.join(self.folder_path, new_file_name))

            new_file_name = f'{last_file_name[0]}_W_{lba}_{value}'
            os.rename(os.path.join(self.folder_path, last_file_name), os.path.join(self.folder_path, new_file_name))
            return True

        return False

    def _delete_write_command(self, lba, size):
        file_list = self.get_sorted_buffer_file_list()

        for idx, file_name in enumerate(file_list):
            if 'W' not in file_name:
                continue
            buffer_lba = int(file_name.split('_')[2])
            if not (lba <= buffer_lba < lba + size):
                continue

            for old_file_idx, old_file_name in enumerate(file_list):
                if old_file_idx < idx or 'empty' in old_file_name:
                    continue
                if old_file_idx == len(file_list) - 1:
                    new_file_name = f'{old_file_idx + 1}_empty'
                else:
                    new_file_name = str(old_file_idx + 1) + file_list[old_file_idx + 1][1:]
                os.rename(os.path.join(self.folder_path, old_file_name), os.path.join(self.folder_path, new_file_name))
