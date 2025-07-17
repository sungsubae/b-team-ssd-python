import os
from pathlib import Path


class Buffer:
    def __init__(self):
        self.buffer_path = Path('./buffer')
        if not self.buffer_path.exists():
            self.reset()

    def _get_sorted_buffer_file_list(self, reverse=False):
        return sorted(os.listdir(self.buffer_path), reverse=reverse)

    def get_command_list(self):
        command_list = []
        for filename in self._get_sorted_buffer_file_list():
            if 'empty' in filename:
                break
            command_list.append(filename)
        return command_list

    def read(self, lba: int):
        file_list = self._get_sorted_buffer_file_list(reverse=True)

        for filename in file_list:
            if 'empty' in filename:
                continue
            idx, cmd, buffer_lba, value = filename.split('_')
            buffer_lba = int(buffer_lba)
            if cmd == 'W' and buffer_lba == lba:
                return value
            if cmd == 'E' and buffer_lba <= lba < buffer_lba + int(value):
                return '0x00000000'
        return ''

    def write(self, cmd: str, lba: int, value: str = '', size: int = 1):
        if cmd == 'W':
            return self._join_write_command(lba, value)

        if cmd == 'E':
            self._delete_write_command(lba, size)
            return self._join_erase_command(lba, size)

    def reset(self):
        try:
            self.buffer_path.mkdir(parents=True, exist_ok=True)
            for file in self.buffer_path.iterdir():
                file.unlink()

            for idx in range(1, 6):
                file_path = self.buffer_path / f"{idx}_empty"
                file_path.touch()
        except OSError as e:
            print(f"오류 발생: {e}")

    def _join_write_command(self, lba: int, value: str):
        commands = []
        for command in self.get_command_list():
            idx, cmd, buffer_lba, buffer_value = command.split('_')
            buffer_lba = int(buffer_lba)

            if cmd == 'W' and buffer_lba == lba:
                continue
            if cmd == 'E' and buffer_lba == lba and int(buffer_value) == 1:
                continue

            commands.append(f"{cmd}_{buffer_lba}_{buffer_value}")

        commands.append(f"W_{lba}_{value}")
        return self._write_buffer(commands)

    def _delete_write_command(self, lba, size):
        commands = self.get_command_list()
        commands_after_delete = []

        for command in commands:
            idx, cmd, buffer_lba, value = command.split('_')
            buffer_lba = int(buffer_lba)
            if cmd == 'W' and lba <= buffer_lba < lba + size:
                continue
            commands_after_delete.append(command)

        if len(commands_after_delete) == len(commands):
            return
        self._write_buffer(commands_after_delete)

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
        return self._write_buffer(erase_commands + write_commands)

    def _write_buffer(self, commands):
        if len(commands) > 5:
            return False

        self.reset()
        for idx, command in enumerate(commands):
            os.rename(self.buffer_path / f"{idx + 1}_empty", self.buffer_path / f"{idx + 1}_{command}")
        return True

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
