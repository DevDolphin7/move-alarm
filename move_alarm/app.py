import sys
import code
import time
import re
from datetime import timedelta
from move_alarm.contexts import use_context
from move_alarm import components
import move_alarm.datatypes as datatype


class App(code.InteractiveConsole):

    @property
    def config(self) -> datatype.Config:
        return self._config

    def __init__(self) -> None:
        # self.__command_history = []

        self._config = use_context().config
        self.variables = {"config": self.config}

        self.alarm = components.Alarm()

        sys.ps1 = "MoveAlarm > "
        sys.ps2 = "MoveAlarm... "

        super().__init__(locals=self.variables)

        self.interact(
            banner="""
Welcome to Move Alarm!

Type 'help' then '↩ enter' if you're not sure where to start, or visit:
https://github.com/DevDolphin7/move-alarm

license: MIT
""",
            exitmsg="Goodbye :)",
        )

    def push(self, line: str) -> bool:
        quotation_check = re.match('(.*?)"(.*?)"', line)

        try:
            instructions = quotation_check.groups()
            lines = instructions[0].strip().split(" ")
            lines.append(instructions[1])
        except AttributeError:
            lines = line.split(" ")

        command = lines[0].strip().lower()

        # self.__command_history.append(command)

        match command:
            case "":
                pass

            case "help":
                self.help()

            case c if c == "exit" or c == "quit":
                self.exit()

            case "start":
                self.start()

            case "snooze":
                self.snooze()

            case "stop":
                self.stop()

            case "test":
                self.test()

            case "set":
                lines.pop(0)
                self.set(lines)

            # case c if c == "^[[A":
            #     print(self.__command_history[0])

            case invalid:
                print(f"Command not found: {invalid}")

        return False

    def help(self) -> None:
        print(
            """This
              is
              multi-line"""
        )

    def exit(self) -> None:
        print("Goodbye :)")
        self.push("exit()")

    def start(self) -> None:
        time = self.alarm.set_alarm().strftime("%d/%m/%Y, %H:%M:%S")

        if self.alarm.is_set == True:
            print(f"Alarm set for {time}")
        else:
            print("An unexpected problem occured, the alarm is not set")

    def snooze(self) -> None:
        try:
            time = self.alarm.snooze_alarm().strftime("%d/%m/%Y, %H:%M:%S")
        except datatype.AlarmNotSetError:
            print("Please use 'start' to begin an alarm before you try to snooze it!")
            return

        print(
            f"Alarm snoozed for {int(self.config.snooze_duration.total_seconds() / 60)} minutes, it will now sound at {time}"
        )

    def stop(self, timeout=2) -> None:
        self.alarm.remove_alarm()

        loop_range = int(timeout / 0.05)

        for i in range(0, loop_range):
            time.sleep(0.05)
            if self.alarm.is_set == False:
                return

        print("An unexpected problem occured, the alarm is not set")

    def test(self) -> None:
        print("Playing a sound now...")
        self.alarm.sounds.play_sound()
        print("Sound should have stopped!")

    def set(self, args: list[str]) -> None:
        if len(args) == 0 or len(args) > 2:
            print("set requires 1 or 2 arguments!")
            self.set_help()
            return

        option = args[0].strip().lower()

        if len(args) == 1 and option != "themes":
            print("Invalid number of arguments!")
            self.set_help()
            return

        match option:
            case "interval":
                self.set_interval(args[1])
            case "snooze":
                self.set_snooze(args[1])
            case "message":
                self.set_message(args[1])
            case "path":
                self.set_path(args[1])

    def set_help(self):
        print(
            """
Displaying valid options for set. Use as below:
set [option] [value]

[option]    [example value]
interval    30                      --> How long to wait beteen alarms in minutes: int
snooze      10                      --> How long to snooze a set alarm in minutes: int
message     "Alarm sounding!"       --> Message to show when alarm goes off: str
path        "/wav_files/directory/" --> Directory containing wav files for alarm to play: str
freesound   True                    --> Enables searching the freesound API: bool
themes      piano "acoustic guitar" --> The themes for searching freesound: space separated string
"""
        )

    def set_interval(self, minutes: str) -> None:
        mins_float = self.get_float_from_input(minutes, 1.0, 1439.0)
        if mins_float == -1.0:
            return

        self.config.wait_duration = timedelta(minutes=mins_float)
        self.config.set_config_file()

        print(f"Any alarm set from now on will wait {mins_float} minutes")

    def set_snooze(self, minutes: str) -> None:
        wait_duration = float(self.config.wait_duration.total_seconds() / 60)

        mins_float = self.get_float_from_input(minutes, 1.0, wait_duration - 1.0)
        if mins_float == -1.0:
            return

        self.config.snooze_duration = timedelta(minutes=mins_float)
        self.config.set_config_file()

        print(f"Any alarm from now on will snooze for {mins_float} minutes")

    def set_message(self, message: str) -> None:
        self.config.reminder_text = message
        self.config.set_config_file()

        print("Message set")

    def set_path(self, path: str) -> None:
        try:
            self.config.wav_directory = path
            self.config.set_config_file()
        except ValueError as error:
            print(f"Error: {error}, '{path}' does not exist")
            return

        print("Path updated")

    def get_float_from_input(self, input, min_value, max_value) -> float:
        try:
            mins_float = float(input)
            if mins_float < min_value or mins_float > max_value:
                raise ValueError()
        except ValueError:
            print(
                f"Please enter a number {min_value} - {max_value}, or enter 'set' to see the help page"
            )
            return -1.0

        return mins_float


def main():
    App()


if __name__ == "__main__":
    App()
