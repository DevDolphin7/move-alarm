import os


class Configuration:
    wav_directory: str = os.path.join(os.path.dirname(__file__)[:-5], "assets")
    api_enabled: bool = False
    sound_themes: list[str] = []
