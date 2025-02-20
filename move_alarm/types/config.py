from dataclasses import dataclass
from datetime import timedelta


@dataclass
class Config:
    wait_duration: timedelta
    snooze_duration: timedelta
    reminder_text: str
    wav_directory: str
    api_enabled: str
    sound_themes: list[str]
