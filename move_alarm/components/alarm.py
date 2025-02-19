import os
import simpleaudio as sa  # type: ignore


class Alarm:
    def test(self) -> None:
        print("hello!")


def how_to_play_a_wav() -> None:
    wave_obj = sa.WaveObject.from_wave_file(
        os.path.join(os.path.dirname(__file__), "..", "assets", "fresh-pop-alert.wav")
    )

    play_obj = wave_obj.play()
    play_obj.wait_done()
