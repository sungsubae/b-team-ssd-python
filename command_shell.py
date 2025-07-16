from abc import ABC, abstractmethod

from shell import Shell

class Command(ABC):
    @abstractmethod
    def execute(self, shell, *args):
        pass

class ReadCommand(Command):
    def execute(self, shell, *args):
        if len(args) != 1:
            print("Usage: read <LBA>")
            return
        try:
            lba = int(args[0])
            shell.read(lba)
        except Exception:
            print("Usage: read <LBA>")

class WriteCommand(Command):
    def execute(self, shell, *args):
        if len(args) != 2:
            print("[Write] ERROR")
            return
        try:
            lba = int(args[0])
            value = args[1]
            shell.write(lba, value)
        except Exception:
            print("[Write] ERROR")

class EraseCommand(Command):
    def execute(self, shell, *args):
        if len(args) != 2:
            print("[Erase] ERROR")
            return
        try:
            lba = int(args[0])
            size = int(args[1])
            shell.erase(lba, size)
        except Exception:
            print("[Erase] ERROR")

class EraseRangeCommand(Command):
    def execute(self, shell, *args):
        if len(args) != 2:
            print("[EraseRange] ERROR")
            return
        try:
            start_lba = int(args[0])
            end_lba = int(args[1])
            shell.erase_range(start_lba, end_lba)
        except Exception:
            print("[EraseRange] ERROR")

class FullWriteCommand(Command):
    def execute(self, shell, *args):
        if len(args) != 1:
            print("Usage: fullwrite <VALUE>")
            return
        shell.full_write(args[0])

class FullReadCommand(Command):
    def execute(self, shell, *args):
        shell.full_read()

class FullWriteAndReadCompareCommand(Command):
    def execute(self, shell, *args):
        shell.logging_and_printing(shell.full_write_and_read_compare())

class PartialLBAWriteCommand(Command):
    def execute(self, shell, *args):
        shell.logging_and_printing(shell.partial_lba_write())

class WriteReadAgingCommand(Command):
    def execute(self, shell, *args):
        shell.logging_and_printing(shell.write_read_aging())

class EraseAndWriteAging(Command):
    def execute(self, shell, *args):
        shell.logging_and_printing(shell.erase_and_write_aging())

class HelpCommand(Command):
    def execute(self, shell, *args):
        shell.help()

class ExitCommand(Command):
    def execute(self, shell, *args):
        exit()


COMMANDS = {
    "read": ReadCommand(),
    "write": WriteCommand(),
    "erase": EraseCommand(),
    "erase_range": EraseRangeCommand(),
    "fullwrite": FullWriteCommand(),
    "fullread": FullReadCommand(),
    "1_": FullWriteAndReadCompareCommand(),
    "1_fullwriteandreadcompare": FullWriteAndReadCompareCommand(),
    "2_": PartialLBAWriteCommand(),
    "2_partiallbawrite": PartialLBAWriteCommand(),
    "3_": WriteReadAgingCommand(),
    "3_writereadaging": WriteReadAgingCommand(),
    "4_": EraseAndWriteAging(),
    "4_EraseAndWriteAging": EraseAndWriteAging(),
    "help": HelpCommand(),
    "exit": ExitCommand(),
}

def find_command(cmd_type):
    if cmd_type in COMMANDS:
        return COMMANDS[cmd_type]
    return None

def command_main(shell: Shell):
    while True:
        user_input = input("Shell> ")
        user_input_list = user_input.strip().split()
        if not user_input_list:
            print("INVALID COMMAND")
            continue

        cmd_type = user_input_list[0].lower()
        args = user_input_list[1:]

        command = find_command(cmd_type)
        if command:
            command.execute(shell, *args)
        else:
            print("INVALID COMMAND")

if __name__ == "__main__":
    shell = Shell()
    command_main(shell)