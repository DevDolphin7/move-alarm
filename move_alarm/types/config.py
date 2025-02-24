from dataclasses import dataclass
from datetime import timedelta
from typing import TypedDict


@dataclass
class Config:
    wait_duration: timedelta
    snooze_duration: timedelta
    reminder_text: str
    wav_directory: str
    api_enabled: str
    sound_themes: list[str]


class IniFormattedAlarm(TypedDict):
    wait_duration: timedelta
    snooze_duration: timedelta
    reminder_text: str


class IniFormattedSounds(TypedDict):
    wav_directory: str
    api_enabled: str
    sound_themes: list[str]


class IniFormattedConfig(TypedDict):
    Alarm = IniFormattedAlarm
    Sounds = IniFormattedSounds
