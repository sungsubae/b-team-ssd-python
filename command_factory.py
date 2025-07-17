from command_shell import (
    ReadCommand, WriteCommand, EraseCommand, EraseRangeCommand,
    FullWriteCommand, FullReadCommand, FlushCommand,
    FullWriteAndReadCompareCommand, PartialLBAWriteCommand,
    WriteReadAgingCommand, EraseAndWriteAging,
    HelpCommand, ExitCommand
)


class CommandFactory:
    def __init__(self):
        # 명령 문자열 ↔ Command 클래스 매핑
        self.command_map = {
            "read": ReadCommand,
            "write": WriteCommand,
            "erase": EraseCommand,
            "erase_range": EraseRangeCommand,
            "fullwrite": FullWriteCommand,
            "fullread": FullReadCommand,
            "flush": FlushCommand,
            "1_": FullWriteAndReadCompareCommand,
            "1_fullwriteandreadcompare": FullWriteAndReadCompareCommand,
            "2_": PartialLBAWriteCommand,
            "2_partiallbawrite": PartialLBAWriteCommand,
            "3_": WriteReadAgingCommand,
            "3_writereadaging": WriteReadAgingCommand,
            "4_": EraseAndWriteAging,
            "4_eraseandwriteaging": EraseAndWriteAging,
            "help": HelpCommand,
            "exit": ExitCommand,
        }

    def create(self, cmd_type: str):
        if cmd_type in self.command_map:
            return self.command_map[cmd_type]()
        return None
