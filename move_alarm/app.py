import sys
import code
from move_alarm.contexts import use_context
from move_alarm import components
import move_alarm.datatypes as datatype


class App(code.InteractiveConsole):

    @property
    def config(self) -> datatype.Config:
        return self._config

    def __init__(self) -> None:
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
        command = line.strip().lower()

        match command:
            case "help":
                self.help()
                return False
            case c if c == "exit" or c == "quit":
                self.exit()
                return False
            case "start":
                self.start()
                return False
            case "snooze":
                self.snooze()
                return False
            case "stop":
                self.stop()
                return False
            case _:
                return super().push(line)

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

    def stop(self) -> None:
        print(self.alarm.remove_alarm())


def main():
    App()


if __name__ == "__main__":
    App()
