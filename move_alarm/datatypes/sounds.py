from dataclasses import dataclass
from typing import TypedDict


class Sounds:
    @property
    def is_playing(self) -> bool:
        return False

    def play_sound(self) -> None:
        pass

    def stop_sound(self) -> bool:
        return False


@dataclass
class SoundResult:
    id: int
    url: str
    name: str
    description: str
    download: str
    license: str


class SoundResultDict(TypedDict):
    id: int
    url: str
    name: str
    description: str
    download: str
    license: str


class SoundListResponse(TypedDict):
    count: int
    previous: str | None
    next: str | None
    results: list[SoundResultDict]
