import os, json
import requests
import pytest, pytest_mock
from datetime import timedelta
from move_alarm.components.sounds import Sounds
from collections.abc import Callable
from move_alarm.types.config import Config
from move_alarm.types.contexts import Contexts
from move_alarm.types.sounds import SoundResult


@pytest.fixture(scope="class")
def define_wav_directory() -> str:
    return os.path.join(os.path.dirname(__file__)[:-9], "move_alarm", "assets")


@pytest.fixture(scope="class")
def define_new_sound_path(define_wav_directory) -> str:
    return os.path.join(define_wav_directory, "mock_sound.wav")


@pytest.fixture(scope="class", autouse=True)
def env_path(request: pytest.FixtureRequest, define_wav_directory):
    request.cls.pytest_fixture_wav_directory = define_wav_directory


@pytest.fixture(scope="class", autouse=True)
def new_sound_path(request: pytest.FixtureRequest):
    request.cls.pytest_fixture_new_sound_path = os.path.join(
        os.path.dirname(__file__), "..", "move_alarm", "assets", "mock_sound.wav"
    )


class TestSounds:

    @property
    def mock_config(self) -> Config:
        return Config(
            wait_duration=timedelta(minutes=60),
            snooze_duration=timedelta(minutes=5),
            reminder_text="Time to move!",
            wav_directory=define_wav_directory,
            api_enabled=True,
            sound_themes=["piano", "guitar"],
        )

    @pytest.fixture(name="Mock Context")
    def mock_context(self, monkeypatch: pytest.MonkeyPatch):
        class MockAuth:
            def get_token(self):
                return "mock token"

        mock_contexts = Contexts(MockAuth(), self.mock_config)

        monkeypatch.setattr(
            "move_alarm.components.sounds.use_context", lambda: mock_contexts
        )

    @pytest.fixture
    def mock_api_search_result(self) -> Callable[[], list[SoundResult]]:
        file_path = os.path.join(os.path.dirname(__file__), "mock_sounds_data.json")

        with open(file_path) as file:
            data = json.load(file)

        def _mock_api_search_result():
            return data

        return _mock_api_search_result

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

    @pytest.fixture(name="200 mock api sound download")
    def mock_200_sound_download(self, monkeypatch: pytest.MonkeyPatch):
        class MockResponse:
            def raise_for_status(self):
                return None

            def iter_content(chunk_size=1):
                return []

        class MockWith:
            def __enter__(self):
                return MockResponse()

            def __exit__(self, type, value, traceback):
                return True

        monkeypatch.setattr("requests.get", lambda _, headers, stream: MockWith())

    @pytest.fixture(name="500 mock api sound download error")
    def mock_500_sound_download_error(self, monkeypatch: pytest.MonkeyPatch):
        class MockWith:
            def __enter__(self):
                raise requests.exceptions.HTTPError("Mock download issue")

            def __exit__(self, type, value, traceback):
                return True

        monkeypatch.setattr("requests.get", lambda _, headers, stream: MockWith())

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

    @pytest.mark.usefixtures("Mock Context")
    class TestSearchFreesound:

        @property
        def config(self) -> Config:
            return TestSounds.mock_config.fget(self)

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

    @pytest.mark.usefixtures("Mock Context")
    class TestDownloadFromFreesound:

        @pytest.mark.usefixtures("200 mock api sound download")
        def test_requires_url_argument(self):
            sound = Sounds()

            with pytest.raises(TypeError):
                sound.download_from_freesound()

        @pytest.mark.usefixtures("200 mock api sound download")
        def test_requires_directory_path_argument(self):
            sound = Sounds()

            with pytest.raises(TypeError):
                sound.download_from_freesound("url")

        @pytest.mark.usefixtures("200 mock api sound download")
        def test_downloads_song_from_freesound(self, define_new_sound_path):
            sound = Sounds()

            new_file = sound.download_from_freesound("url", define_new_sound_path)

            assert os.path.exists(new_file) == True

        @pytest.mark.usefixtures("500 mock api sound download error")
        def test_raises_error_on_connection_issue(self, define_new_sound_path):
            sound = Sounds()

            with pytest.raises(requests.exceptions.HTTPError):
                sound.download_from_freesound("url", define_new_sound_path)

        @pytest.mark.usefixtures("200 mock api sound download")
        def test_returns_str_wav_file_path(self, define_new_sound_path):
            sound = Sounds()

            new_file_path = sound.download_from_freesound("url", define_new_sound_path)

            assert isinstance(new_file_path, str) == True

    @pytest.mark.usefixtures("Mock Context")
    class TestGetFreesound:

        @property
        def config(self) -> Config:
            return TestSounds.mock_config.fget(self)

        def test_invokes_search_freesound_with_the_sound_themes_from_config(
            self, mocker: pytest_mock.MockerFixture
        ):
            mock_search_freesound = mocker.patch(
                "move_alarm.components.sounds.Sounds.search_freesound"
            )

            sound = Sounds()
            sound.get_freesound()

            mock_search_freesound.assert_called_once_with(self.config.sound_themes)


###----------------------------------
# Methods to do:

# get_freesound
# get_sound
# play_sound
# stop_sound
