from typing import TypedDict


class SoundResult(TypedDict):
    id: int
    url: str
    name: str
    description: str
    geotag: str
    created: str
    license: str
    type: str
    channels: int
    filesize: int
    bitrate: int
    bitdepth: int
    duration: int
    samplerate: str
    pack: str
    download: str
    bookmark: str
    previews: object
    images: object
    num_downloads: int
    avg_rating: int
    num_ratings: int
    rate: str
    comments: str
    num_comments: int
    comment: str
    similar_sounds: str
    analysis: object
    analysis_stats: str
    analysis_frames: str
    ac_analysis: object
