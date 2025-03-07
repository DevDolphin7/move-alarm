import sys
import code
import time
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
        option = args[0].strip().lower()

        if len(args) == 0 or (option != "themes" and len(args) > 2):
            self.set_help()
            return

        match option:
            case "interval":
                print("to sort interval function")

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


def main():
    App()


if __name__ == "__main__":
    App()
