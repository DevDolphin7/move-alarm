import sys
import code
import time
import re
import os
from datetime import timedelta
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

        self._started = False

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

    def push(self, line: str, *args: str | None) -> bool:
        words: list[str] = []

        for char in ['"', "'"]:
            char_check: list[str] = re.findall(f" {char}(.*?){char}", line)

            for text in char_check:
                if text.find('"') != -1 or text.find("'") != -1:
                    print("Please do not combine ' followed by \"")
                    self.set_help()
                    return False

                text = text.strip()
                words.append(text)
                line = line.replace(f" {char}{text}{char}", "")

        for count, word in enumerate(line.split(" ")):
            words.insert(count, word)

        command = words[0].strip().lower()

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
                words.pop(0)
                self.set(words)

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
        sys.exit()

    def start(self) -> None:
        self._started = True

        while self._started:
            if self.alarm.is_set == False:
                self.alarm.set_alarm()

                if self.alarm.is_set == True:
                    alarm_time = self.alarm.time.strftime("%d/%m/%Y, %H:%M:%S")
                    print(f"Alarm set for {alarm_time}")
                else:
                    print("An unexpected problem occured, the alarm is not set")
                    return

            time.sleep(1)

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
        self._started = False
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
        if len(args) < 2:
            print("'set' requires at least 2 arguments!")
            self.set_help()
            return

        option, value, *themes = map(lambda input: input.strip().lower(), args)

        if len(themes) > 0 and option != "themes":
            print(f"'set' requires a valid option and value, displaying help.")
            self.set_help()
            return

        match option:
            case "interval":
                self.set_interval(value)
            case "snooze":
                self.set_snooze(value)
            case "message":
                self.set_message(value)
            case "path":
                self.set_path(value)
            case "freesound":
                self.set_freesound(value)
            case "themes":
                self.set_themes([value, *themes])
            case _:
                print(f"Option provided for 'set' not recognised: '{option}'")
                self.set_help()

    def set_help(self):
        print(
            """
Displaying valid options for 'set'. Use as below:
set [option] [value]

[option]    [example value]
interval    30                      --> How long to wait beteen alarms in minutes: int
snooze      10                      --> How long to snooze a set alarm in minutes: int
message     "Alarm sounding!"       --> Message that will show when the alarm goes off: str
path        "/wav_files/directory/" --> Directory containing wav files for the alarm to play: str
freesound   True                    --> Enable searching the freesound API: "true", "1" or "yes"
themes      piano "acoustic guitar" --> The themes for searching freesound: space separated string
"""
        )

    def set_interval(self, minutes: str) -> None:
        mins_float = self.get_float_from_input(minutes, 0.1, 1439.0)
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

    def set_message(self, message: str) -> None:
        self.config.reminder_text = message
        self.config.set_config_file()

        print("Message set")

    def set_path(self, path: str) -> None:
        try:
            self.config.wav_directory = os.path.abspath(path)
        except ValueError as error:
            print(f"Error: {error}, '{path}' does not exist")
            return

        self.config.set_config_file()
        print("Path updated")

    def set_freesound(self, enabled: str) -> None:
        valid_enable_inputs = ["true", "1", "yes"]

        self.config.api_enabled = enabled in valid_enable_inputs
        self.config.set_config_file()

        print(f"Freesound api {'enabled' if self.config.api_enabled else 'disabled'}")

    def set_themes(self, themes: list[str]) -> None:
        safe_themes: list[str] = []

        for theme in themes:
            if re.match("^[a-z0-9 $_.+!*'(),]+$", theme, re.I):
                safe_themes.append(theme)

        self.config.sound_themes = safe_themes
        self.config.set_config_file()

        print(f"Themes updated: {self.config.sound_themes}")


def main():
    App()


if __name__ == "__main__":
    App()
