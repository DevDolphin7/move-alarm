import os, json
import pytest
from datetime import timedelta
from move_alarm.components.sounds import Sounds
from collections.abc import Callable
from move_alarm.types.config import Config
from move_alarm.types.sounds import SoundResult


@pytest.fixture(scope="class")
def define_wav_directory() -> str:
    return os.path.join(os.path.dirname(__file__)[:-9], "move_alarm", "assets")


@pytest.fixture(scope="class", autouse=True)
def env_path(request: pytest.FixtureRequest, define_wav_directory):
    request.cls.pytest_fixture_wav_directory = define_wav_directory


@pytest.fixture(scope="class", autouse=True)
def config(request: pytest.FixtureRequest, define_wav_directory):
    request.cls.pytest_fixture_config = Config(
        wait_duration=timedelta(minutes=60),
        snooze_duration=timedelta(minutes=5),
        reminder_text="Time to move!",
        wav_directory=define_wav_directory,
        api_enabled=True,
        sound_themes=["piano", "guitar"],
    )


class TestSounds:

    @pytest.fixture
    def mock_api_search_result(self) -> Callable[[], list[SoundResult]]:
        file_path = os.path.join(os.path.dirname(__file__), "mock_sounds_data.json")

        with open(file_path) as file:
            data = json.load(file)

        def _mock_api_search_result():
            return data

        return _mock_api_search_result

    @pytest.fixture(name="Mock HandleAuthorisation.get_token")
    def mock_handle_authorisation(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr("move_alarm.contexts.auth.get_token", lambda: "mock token")

    @pytest.fixture(name="200 mock api sound search")
    def mock_200_sound_search(
        self, monkeypatch: pytest.MonkeyPatch, mock_api_search_result
    ):
        class MockResponse:
            @property
            def status_code(self):
                return 200

            def json(self):
                return {
                    "count": 3876,
                    "previous": None,
                    "next": "https://freesound.org/apiv2/search/text/?&query=&filter=(duration:[30%20TO%20210]%20AND%20type:wav%20AND%20description:(piano%20OR%20guitar))&weights=&page=2&fields=id,url,name,description,download,license",
                    "results": mock_api_search_result(),
                }

        monkeypatch.setattr("requests.get", lambda _, headers: MockResponse())

    @pytest.fixture(name="200 mock api no results sound search")
    def mock_200_no_results_sound_search(self, monkeypatch: pytest.MonkeyPatch):
        class MockResponse:
            @property
            def status_code(self):
                return 200

            def json(self):
                return {
                    "count": 0,
                    "previous": None,
                    "next": None,
                    "results": [],
                }

        monkeypatch.setattr("requests.get", lambda _, headers: MockResponse())

    @pytest.fixture(name="500 mock api unexpected error")
    def mock_500_uexpected_error(self, monkeypatch: pytest.MonkeyPatch):
        class MockResponse:
            @property
            def status_code(self):
                return 500

            def text(self):
                return "An unknown bad thing happened..."

        monkeypatch.setattr("requests.get", lambda _, headers: MockResponse())

    class TestGetLocalFile:

        @property
        def wav_directory(self):
            return self.pytest_fixture_wav_directory

        def test_requires_directory_path_argument(self):
            sound = Sounds()
            with pytest.raises(TypeError):
                sound.get_local_file()

        def test_return_str_wav_path(self):
            sound = Sounds()

            wav_path = sound.get_local_file(self.wav_directory)

            assert isinstance(wav_path, str) == True
            assert wav_path[-4:] == ".wav"

        def test_searches_given_dir_for_wav_file(self):
            sound = Sounds()

            wav_path = sound.get_local_file(self.wav_directory)

            assert os.path.exists(wav_path)

        def test_randomly_selects_a_file_from_the_directory(self):
            sound = Sounds()

            wav_paths = []
            for _ in range(0, 10):
                wav_paths.append(sound.get_local_file(self.wav_directory))

            assert len(wav_paths) > 0
            assert len(set(wav_paths)) > 1

        def test_raises_os_error_on_invalid_path(self):
            sound = Sounds()

            # PLease update the variable if you happen to have a directory with this name...
            invalid_dir_name = "cheese91234_poppinCandyfolder__"

            with pytest.raises(FileNotFoundError):
                sound.get_local_file(invalid_dir_name)

    @pytest.mark.usefixtures("Mock HandleAuthorisation.get_token")
    class TestSearchFreesound:

        @property
        def config(self) -> Config:
            return self.pytest_fixture_config

        @pytest.mark.usefixtures("200 mock api sound search")
        def test_requires_sound_theme_argument(self):
            sound = Sounds()

            with pytest.raises(TypeError):
                sound.search_freesound()

        @pytest.mark.usefixtures("200 mock api sound search")
        def test_returns_a_sound_result(self):
            sound = Sounds()

            result = sound.search_freesound(self.config.sound_themes)

            assert isinstance(result, SoundResult) == True

        @pytest.mark.usefixtures("200 mock api sound search")
        def test_returns_a_random_sound_result_from_freesound(self):
            sound = Sounds()

            search_results = []
            for _ in range(0, 5):
                result = sound.search_freesound(self.config.sound_themes)
                search_results.append(result.id)

            assert len(search_results) > 0
            assert len(set(search_results)) > 1

        @pytest.mark.usefixtures("200 mock api no results sound search")
        def test_returns_none_on_no_sounds(self):
            sound = Sounds()

            result = sound.search_freesound(self.config.sound_themes)

            assert result == None

        @pytest.mark.usefixtures("500 mock api unexpected error")
        def test_raises_error_on_non_200_response(self):
            sound = Sounds()

            with pytest.raises(ConnectionError):
                sound.search_freesound(self.config.sound_themes)


###----------------------------------
# Methods to do:

# download_from_freesound
# play_sound
# stop_sound
