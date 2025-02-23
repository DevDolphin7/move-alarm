import os, random
import simpleaudio as sa  # type: ignore
from move_alarm.contexts import use_context
from move_alarm import utils
import move_alarm.types as datatype


class Sounds:

    @property
    def is_playing(self) -> bool:
        return self.__is_playing

    @is_playing.setter
    def is_playing(self, boolean: bool) -> None:
        if isinstance(boolean, bool):
            self.__is_playing = boolean

    def __init__(self):
        self.is_playing = False

    def get_local_file(self, dir_path: str) -> str:
        files = [
            file
            for file in os.listdir(dir_path)
            if os.path.isfile(os.path.join(dir_path, file)) and file[-4:] == ".wav"
        ]

        index = random.randint(0, len(files) - 1)

        return os.path.join(dir_path, files[index])

    def search_freesound(self, themes: list[str]) -> datatype.SoundResult | None:
        token = utils.get_auth_token()

        sounds = utils.search_for_sounds(token, themes=themes)

        if len(sounds) == 0:
            return None

        index = random.randint(0, len(sounds) - 1)
        sound = sounds[index]

        id = int(sound["id"])
        url = str(sound["url"])
        name = str(sound["name"])
        description = str(sound["description"])
        download = str(sound["download"])
        license = str(sound["license"])

        return datatype.SoundResult(id, url, name, description, download, license)

    def download_from_freesound(self, url: str, new_path: str) -> str:
        token = utils.get_auth_token()

        utils.download_sound(token, url, new_path)

        if os.path.exists(new_path):
            return new_path
        raise FileNotFoundError(
            f"Sound file should exist but could not be found: {new_path}"
        )

    def get_freesound(self) -> str | None:
        config = use_context().config

        search_result = self.search_freesound(config.sound_themes)

        if isinstance(search_result, datatype.SoundResult):
            new_path = os.path.join(config.wav_directory, search_result.name)

            return self.download_from_freesound(search_result.download, new_path)

        return None

    def get_sound(self) -> str:
        config = use_context().config

        if config.api_enabled:
            sound = self.get_freesound()
            if sound != None:
                return sound
            print(f"Info: Freesound returned no results for {config.sound_themes}")

        return self.get_local_file(config.wav_directory)

    def play_sound(self) -> None:
        sound_path = self.get_sound()

        self.is_playing = True

        wave_obj = sa.WaveObject.from_wave_file(sound_path)
        play_obj = wave_obj.play()
        play_obj.wait_done()

        self.stop_sound()

    def stop_sound(self) -> None:
        return False
