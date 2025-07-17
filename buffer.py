import os
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
                    return True
                new_file_name = f'{file_name[0]}_{cmd}_{lba}_{value}'
            else:
                self._delete_write_command(lba, size)
                self._join_erase_command(lba, size)
                return True

            os.rename(self.folder_path / file_name, self.folder_path / new_file_name)
            return True
        return False

    def reset(self):
        try:
            self.folder_path.mkdir(parents=True, exist_ok=True)
            for filename in os.listdir(self.folder_path):
                file_path = self.folder_path / filename
                os.remove(file_path)  # 파일 삭제

            for idx in range(1, 6):
                file_path = self.folder_path/f"{idx}_empty"
                file_path.touch()
        except OSError as e:
            print(f"오류 발생: {e}")

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
                os.rename(self.folder_path / old_file_name, self.folder_path / new_file_name)

            new_file_name = f'{last_file_name[0]}_W_{lba}_{value}'
            os.rename(self.folder_path / last_file_name, self.folder_path / new_file_name)
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
                os.rename(self.folder_path / old_file_name, self.folder_path / new_file_name)

    def _getElementsAfterIndex(self, file_list, s_idx):
        for idx, file_name in enumerate(file_list):
            if idx < s_idx:
                continue
            if 'empty' not in file_name:
                return idx, file_name
        return None, None

    def _merge_intervals(self, intervals: list):
        intervals.sort(key=lambda x: x[0])
        merged = []

        for interval in intervals:
            if not merged or merged[-1][1] < interval[0]:
                merged.append(interval)
            else:
                merged[-1][1] = max(merged[-1][1], interval[1])

        return merged

    def _join_erase_command(self, lba: int, size: int):
        erase_intervals = [[lba, lba + size]]
        erase_intervals = self._get_erase_intervals(erase_intervals)
        merged_intervals = self._merge_intervals(erase_intervals)
        erase_commands = self._get_erase_commands(merged_intervals)

        write_commands = self._get_write_commands()
        self._write_buffer(erase_commands + write_commands)

    def _write_buffer(self, commands):
        self.reset()
        for idx, command in enumerate(commands):
            os.rename(self.folder_path / f"{idx + 1}_empty", self.folder_path / f"{idx + 1}_{command}")

    def _get_erase_commands(self, merged_intervals):
        erase_commands = []
        for interval in merged_intervals:
            lba = interval[0]
            size = interval[1] - interval[0]

            while size > 10:
                erase_commands.append(f'E_{lba}_10')
                lba += 10
                size -= 10
            erase_commands.append(f'E_{lba}_{size}')
        return erase_commands

    def _get_erase_intervals(self, erase_intervals):
        for command in self.get_command_list():
            idx, cmd, lba, value = command.split('_')
            if cmd != 'E':
                continue
            lba = int(lba)
            size = int(value)
            erase_intervals.append([lba, lba + size])
        return erase_intervals

    def _get_write_commands(self):
        write_commands = []
        for command in self.get_command_list():
            idx, cmd, lba, value = command.split('_')
            if cmd == 'W':
                write_commands.append(f'{cmd}_{lba}_{value}')
        return write_commands
