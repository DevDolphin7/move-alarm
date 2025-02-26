from dataclasses import dataclass
from datetime import timedelta


@dataclass
class Config:
    wait_duration: timedelta
    snooze_duration: timedelta
    reminder_text: str
    wav_directory: str
    api_enabled: bool
    sound_themes: list[str]


class IniFormattedAlarm(dict[str, int | str]):
    interval: int
    snooze: int
    message: str


class IniFormattedSounds(dict[str, str | bool | list[str]]):
    path: str
    freesound: bool
    themes: list[str]


class IniFormattedConfig(dict[str, IniFormattedAlarm | IniFormattedSounds]):
    Alarm: IniFormattedAlarm
    Sounds: IniFormattedSounds
