import os, random
import simpleaudio as sa  # type: ignore
from move_alarm.contexts import auth, config
from move_alarm.utils.api_calls import search_for_sounds, download_sound
from move_alarm.types.sounds import SoundResult


class Sounds:
    def get_local_file(self, dir_path: str) -> str:
        files = [
            file
            for file in os.listdir(dir_path)
            if os.path.isfile(os.path.join(dir_path, file)) and file[-4:] == ".wav"
        ]

        index = random.randint(0, len(files) - 1)

        return os.path.join(dir_path, files[index])

    def search_freesound(self, themes: list[str]) -> SoundResult | None:
        token = auth.get_token()
        if token == None:
            raise ValueError("Unexpected error: Unable to get an access token")

        sounds = search_for_sounds(token, themes=themes)

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

        return SoundResult(id, url, name, description, download, license)

    def download_from_freesound(self, url: str, new_path: str) -> str:
        token = auth.get_token()

        download_sound(token, url, new_path)

        if os.path.exists(new_path):
            return new_path
        raise FileNotFoundError(
            f"Sound file should exist but could not be found: {new_path}"
        )

    def get_freesound(self) -> str | None:
        print(config.sound_themes)
        self.search_freesound(config.sound_themes)


def how_to_play_a_wav(path) -> None:
    wave_obj = sa.WaveObject.from_wave_file(path)

    play_obj = wave_obj.play()
    play_obj.wait_done()
