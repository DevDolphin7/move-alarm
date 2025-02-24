import configparser, datetime, os
import move_alarm.types as datatype


class Configuration:

    @property
    def config_path(self) -> str:
        return self.__config_path

    @config_path.setter
    def config_path(self, path: str) -> None:
        if isinstance(path, str):
            self.__config_path = path
        else:
            raise TypeError("Configuration must be initialised with a string.")

    @property
    def wait_duration(self) -> datetime.timedelta:
        return self.__wait_duration

    @wait_duration.setter
    def wait_duration(self, duration: datetime.timedelta) -> None:
        if isinstance(duration, datetime.timedelta):
            self.__wait_duration = duration
        else:
            raise TypeError("datetime.timedelta required for wait_duration")

    @property
    def snooze_duration(self) -> datetime.timedelta:
        return self.__snooze_duration

    @snooze_duration.setter
    def snooze_duration(self, duration: datetime.timedelta) -> None:
        if isinstance(duration, datetime.timedelta):
            self.__snooze_duration = duration
        else:
            raise TypeError("datetime.timedelta required for snooze_duration")

    @property
    def reminder_text(self) -> str:
        return self.__reminder_text

    @reminder_text.setter
    def reminder_text(self, message: str) -> None:
        if isinstance(message, str):
            self.__reminder_text = message
        else:
            raise TypeError("str required for reminder_text")

    @property
    def wav_directory(self) -> str:
        return self.__wav_directory

    @wav_directory.setter
    def wav_directory(self, dir: str) -> None:
        if isinstance(dir, str) and os.path.exists(dir):
            self.__wav_directory = dir
        else:
            raise ValueError(
                "A string representing an existing directory required for wav_directory"
            )

    @property
    def api_enabled(self) -> bool:
        return self.__api_enabled

    @api_enabled.setter
    def api_enabled(self, value: bool) -> None:
        if isinstance(value, bool):
            self.__api_enabled = value
        else:
            raise TypeError("bool required for api_enabled")

    @property
    def sound_themes(self) -> list[str]:
        return self.__sound_themes

    @sound_themes.setter
    def sound_themes(self, themes: list[str]) -> None:
        if isinstance(themes, list):
            self.__sound_themes = [theme for theme in themes if isinstance(theme, str)]
        else:
            raise TypeError("list[str] required for sound_themes")

    def __init__(self, config_path: str):
        self.config_path = config_path

        try:
            self.load_config_file()
        except Exception as error:
            print(f"Warning: {Warning(error)}\nUsing default values...")
            self.use_default_values()
            self.set_config_file()

    def use_default_values(self) -> None:
        self.wait_duration = datetime.timedelta(minutes=60)
        self.snooze_duration = datetime.timedelta(minutes=5)
        self.reminder_text = "Time to stretch!"
        self.wav_directory = os.path.abspath(
            os.path.join(os.path.dirname(__file__)[:-5], "assets")
        )
        self.api_enabled = False
        self.sound_themes = ["funk"]

    def define_data_to_save(self) -> datatype.IniFormattedConfig:
        return {
            "Alarm": datatype.IniFormattedAlarm(
                interval=int(self.wait_duration.total_seconds()),
                snooze=int(self.snooze_duration.total_seconds()),
                message=self.reminder_text,
            ),
            "Sounds": datatype.IniFormattedSounds(
                path=self.wav_directory,
                freesound=self.api_enabled,
                themes=self.sound_themes,
            ),
        }

    def set_config_file(self) -> bool:
        data = self.define_data_to_save()

        parser = configparser.ConfigParser()
        parser.read_dict(data)

        with open(self.config_path, "w") as file:
            parser.write(file)

        return True

    def load_config_file(self) -> bool:
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(self.config_path)

        config_parser = configparser.ConfigParser()
        config_parser.read(self.config_path)

        self.wait_duration = datetime.timedelta(
            seconds=config_parser.getint("Alarm", "interval")
        )
        self.snooze_duration = datetime.timedelta(
            seconds=config_parser.getint("Alarm", "snooze")
        )
        self.reminder_text = config_parser.get("Alarm", "message")
        self.wav_directory = config_parser.get("Sounds", "path")
        self.api_enabled = config_parser.getboolean("Sounds", "freesound")
        self.sound_themes = list(config_parser.get("Sounds", "themes"))

        return True
