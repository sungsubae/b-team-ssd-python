from abc import ABC, abstractmethod

from shell import Shell


# Command 인터페이스
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
            print("Usage: write <LBA> <VALUE>")
            return
        try:
            lba = int(args[0])
            value = args[1]
            shell.write(lba, value)
        except Exception:
            print("Usage: write <LBA> <VALUE>")

class FullWriteCommand(Command):
    def execute(self, shell, *args):
        if len(args) != 1:
            print("Usage: fullwrite <VALUE>")
            return
        shell.full_write(args[0])

class FullReadCommand(Command):
    def execute(self, shell, *args):
        shell.fullread()

class FullWriteAndReadCompareCommand(Command):
    def execute(self, shell, *args):
        shell.FullWriteAndReadCompare()

class PartialLBAWriteCommand(Command):
    def execute(self, shell, *args):
        shell.PartialLBAWrite()

class WriteReadAgingCommand(Command):
    def execute(self, shell, *args):
        shell.WriteReadAging()

class EraseAndWriteAging(Command):
    def execute(self, shell, *args):
        shell.erase_and_write_aging()

class HelpCommand(Command):
    def execute(self, shell, *args):
        shell.help()

class ExitCommand(Command):
    def execute(self, shell, *args):
        exit()


COMMANDS = {
    "read": ReadCommand(),
    "write": WriteCommand(),
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

def command_main(shell: Shell):
    while True:
        user_input = input("Shell> ")
        user_input_list = user_input.strip().split()
        if not user_input_list:
            print("INVALID COMMAND")
            continue

        cmd_type = user_input_list[0].lower()

        args = user_input_list[1:]

        command = COMMANDS.get(cmd_type)
        if command:
            command.execute(shell, *args)
        else:
            print("INVALID COMMAND")

if __name__ == "__main__":
    shell = Shell()
    command_main(shell)