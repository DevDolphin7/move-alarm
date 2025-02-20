from dataclasses import dataclass


@dataclass
class SoundResult:
    id: int
    url: str
    name: str
    description: str
    download: str
    license: str


@dataclass
class SoundListResponse:
    count: int
    previous: str | None
    next: str | None
    results: list[SoundResult]
