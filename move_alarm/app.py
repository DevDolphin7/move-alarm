import sys
from code import InteractiveConsole
from move_alarm.contexts import use_context
import move_alarm.datatypes as datatype


class App:

    @property
    def config(self) -> datatype.Config:
        return self._config

    def __init__(self) -> None:
        self._config = use_context().config

        sys.ps1 = "MoveAlarm> "
        sys.ps2 = "MoveAlarm... "
        self._console = InteractiveConsole(locals={"config": self.config})

        self._console.interact("Welcome to Move Alarm!", "Goodbye")


def main():
    App()


if __name__ == "__main__":
    App()
