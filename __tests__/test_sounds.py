import os, json
import requests
import pytest, pytest_mock
from datetime import timedelta
from move_alarm.components.sounds import Sounds
from collections.abc import Callable
import move_alarm.types as datatype


class TestSounds:

    @property
    def wav_directory(self) -> str:
        try:
            return self._wav_directory
        except:
            self._wav_directory = os.path.join(
                os.path.dirname(__file__)[:-9], "move_alarm", "assets"
            )
            return self._wav_directory

    @property
    def new_sound_path(self) -> str:
        return os.path.join(self.wav_directory, "mock_sound.wav")

    @property
    def mock_config(self) -> datatype.Config:
        return datatype.Config(
            wait_duration=timedelta(minutes=60),
            snooze_duration=timedelta(minutes=5),
            reminder_text="Time to move!",
            wav_directory=self.wav_directory,
            api_enabled=True,
            sound_themes=["piano", "guitar"],
        )

    @pytest.fixture(name="Mock Context")
    def mock_context(self, monkeypatch: pytest.MonkeyPatch):
        class MockAuth:
            def get_token(self):
                return "mock token"

        mock_contexts = datatype.Contexts(MockAuth(), self.mock_config)

        monkeypatch.setattr(
            "move_alarm.components.sounds.use_context", lambda: mock_contexts
        )

        monkeypatch.setattr(
            "move_alarm.utils.helpers.use_context", lambda: mock_contexts
        )

    @pytest.fixture(name="Mock Context api_enabled false")
    def mock_context_api_diabled(self, monkeypatch: pytest.MonkeyPatch):
        class MockAuth:
            def get_token(self):
                return "mock token"

        mock_config_copy = self.mock_config
        mock_config_copy.api_enabled = False

        mock_contexts = datatype.Contexts(MockAuth(), mock_config_copy)

        monkeypatch.setattr(
            "move_alarm.components.sounds.use_context", lambda: mock_contexts
        )

        monkeypatch.setattr(
            "move_alarm.utils.helpers.use_context", lambda: mock_contexts
        )

    @pytest.fixture(name="Remove mock_sounds.wav file", autouse=True)
    def remove_mock_sounds_file(self):
        if os.path.exists(self.new_sound_path):
            os.remove(self.new_sound_path)

    @pytest.fixture
    def mock_api_search_result(self) -> Callable[[], list[datatype.SoundResult]]:
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

        monkeypatch.setattr("requests.get", lambda *args, **kwargs: MockResponse())

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

        monkeypatch.setattr("requests.get", lambda *args, **kwargs: MockResponse())

    @pytest.fixture(name="500 mock api unexpected error")
    def mock_500_uexpected_error(self, monkeypatch: pytest.MonkeyPatch):
        class MockResponse:
            @property
            def status_code(self):
                return 500

            def text(self):
                return "An unknown bad thing happened..."

        monkeypatch.setattr("requests.get", lambda *args, **kwargs: MockResponse())

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

            def __exit__(self, *args):
                return True

        monkeypatch.setattr("requests.get", lambda *args, **kwargs: MockWith())

    @pytest.fixture(name="500 mock api sound download error")
    def mock_500_sound_download_error(self, monkeypatch: pytest.MonkeyPatch):
        class MockWith:
            def __enter__(self):
                raise requests.exceptions.HTTPError("Mock download issue")

            def __exit__(self, *args):
                return True

        monkeypatch.setattr("requests.get", lambda *args, **kwargs: MockWith())

    @pytest.fixture(name="Mock search_freesound")
    def replace_search_for_sounds(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr(
            "move_alarm.components.sounds.Sounds.search_freesound",
            lambda *args, **kwargs: datatype.SoundResult(
                1, "", self.new_sound_path, "", "", ""
            ),
        )

    @pytest.fixture
    def define_mock_play_object(self):
        class MockPlayObject:
            def wait_done(self):
                return None

            def stop(self):
                print("stop was invoked from MockPlayObject!")
                return None

        return MockPlayObject

    @pytest.fixture(name="Mock WaveObject")
    def replace_from_wave_file(
        self, monkeypatch: pytest.MonkeyPatch, define_mock_play_object
    ):
        class MockWaveObject:
            def play(self):
                print("play was invoked from MockWaveObject!")
                return define_mock_play_object()

        self.mock_wave_object = MockWaveObject()

        monkeypatch.setattr(
            "move_alarm.components.sounds.sa.WaveObject.from_wave_file",
            lambda *args, **kwargs: self.mock_wave_object,
        )

    @pytest.fixture(name="Mock stop_sound")
    def replace_stop_sound(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr(
            "move_alarm.components.sounds.Sounds.stop_sound",
            lambda *args, **kwargs: None,
        )

    @pytest.fixture
    def mock_invoke_play_sound_times(
        self, monkeypatch: pytest.MonkeyPatch, define_mock_play_object
    ):
        def replace_play_sound(invocations: int, sounds_self: Sounds) -> None:
            def update_play_objs(*args, **kwargs):
                for _ in range(0, invocations):
                    sounds_self._play_objects.append(define_mock_play_object())

            monkeypatch.setattr(
                "move_alarm.components.sounds.Sounds.play_sound", update_play_objs
            )

            sounds_self.play_sound()

        return replace_play_sound

    class TestGetLocalFile:

        @property
        def wav_directory(self):
            try:
                return self._wav_directory
            except:
                self._wav_directory = TestSounds.wav_directory.fget(self)
                return self._wav_directory

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

            assert os.path.exists(wav_path) == True

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
        def wav_directory(self) -> str:
            try:
                return self._wav_directory
            except:
                self._wav_directory = TestSounds.wav_directory.fget(self)
                return self._wav_directory

        @property
        def config(self) -> datatype.Config:
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

            assert isinstance(result, datatype.SoundResult) == True

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
    @pytest.mark.usefixtures("Remove mock_sounds.wav file")
    class TestDownloadFromFreesound:

        @property
        def new_sound_path(self) -> str:
            wav_directory = TestSounds.wav_directory.fget(self)
            return os.path.join(wav_directory, "mock_sound.wav")

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
        def test_downloads_song_from_freesound(self):
            sound = Sounds()

            new_file = sound.download_from_freesound("url", self.new_sound_path)

            assert os.path.exists(new_file) == True

        @pytest.mark.usefixtures("500 mock api sound download error")
        def test_raises_error_on_connection_issue(self):
            sound = Sounds()

            with pytest.raises(requests.exceptions.HTTPError):
                sound.download_from_freesound("url", self.new_sound_path)

        @pytest.mark.usefixtures("200 mock api sound download")
        def test_returns_str_wav_file_path(self):
            sound = Sounds()

            new_file_path = sound.download_from_freesound("url", self.new_sound_path)

            assert isinstance(new_file_path, str) == True

    @pytest.mark.usefixtures("Mock Context")
    @pytest.mark.usefixtures("Remove mock_sounds.wav file")
    class TestGetFreesound:

        @property
        def wav_directory(self) -> str:
            try:
                return self._wav_directory
            except:
                self._wav_directory = TestSounds.wav_directory.fget(self)
                return self._wav_directory

        @property
        def config(self) -> datatype.Config:
            return TestSounds.mock_config.fget(self)

        @property
        def new_sound_path(self) -> str:
            return os.path.join(self.wav_directory, "mock_sound.wav")

        @pytest.mark.usefixtures("200 mock api sound download")
        def test_invokes_search_freesound_with_the_sound_themes_from_config(
            self, mocker: pytest_mock.MockerFixture
        ):
            mock_search_freesound = mocker.patch(
                "move_alarm.components.sounds.Sounds.search_freesound"
            )

            sound = Sounds()
            sound.get_freesound()

            mock_search_freesound.assert_called_once_with(self.config.sound_themes)

        @pytest.mark.usefixtures("200 mock api sound search")
        def test_if_valid_search_result_invokes_download_from_freesound(
            self, mocker: pytest_mock.MockerFixture
        ):
            mock_download_from_freesound = mocker.patch(
                "move_alarm.components.sounds.Sounds.download_from_freesound"
            )

            sound = Sounds()
            sound.get_freesound()

            mock_download_from_freesound.assert_called_once()

        @pytest.mark.usefixtures("Mock search_freesound")
        @pytest.mark.usefixtures("200 mock api sound download")
        def test_if_sound_downloaded_ok_return_wav_file_path(self):
            sound = Sounds()

            assert os.path.exists(self.new_sound_path) == False

            wav_path = sound.get_freesound()

            assert wav_path == self.new_sound_path
            assert os.path.exists(wav_path) == True

        @pytest.mark.usefixtures("200 mock api no results sound search")
        def test_if_no_search_result_returns_none(self):
            sound = Sounds()

            wav_path = sound.get_freesound()

            assert wav_path == None

    @pytest.mark.usefixtures("Remove mock_sounds.wav file")
    class TestGetSound:

        @property
        def wav_directory(self) -> str:
            try:
                return self._wav_directory
            except:
                self._wav_directory = TestSounds.wav_directory.fget(self)
                return self._wav_directory

        @property
        def config(self) -> datatype.Config:
            return TestSounds.mock_config.fget(self)

        @property
        def new_sound_path(self) -> str:
            return os.path.join(self.wav_directory, "mock_sound.wav")

        @pytest.mark.usefixtures("Mock Context api_enabled false")
        def test_if_api_is_not_enabled_invokes_get_local_file(
            self, mocker: pytest_mock.MockerFixture
        ):
            mock_get_local_file = mocker.patch(
                "move_alarm.components.sounds.Sounds.get_local_file"
            )

            sound = Sounds()
            sound.get_sound()

            mock_get_local_file.assert_called_once_with(self.wav_directory)

        @pytest.mark.usefixtures("Mock Context")
        def test_api_is_enabled_invokes_get_freesound(
            self, mocker: pytest_mock.MockerFixture
        ):
            mock_get_freesound = mocker.patch(
                "move_alarm.components.sounds.Sounds.get_freesound"
            )

            sound = Sounds()
            sound.get_sound()

            mock_get_freesound.assert_called_once()

        @pytest.mark.usefixtures("Mock Context")
        @pytest.mark.usefixtures("Mock search_freesound")
        @pytest.mark.usefixtures("200 mock api sound download")
        def test_if_returns_wav_path(self):
            sound = Sounds()

            sound_path = sound.get_sound()

            assert sound_path == self.new_sound_path

        @pytest.mark.usefixtures("Mock Context")
        @pytest.mark.usefixtures("200 mock api no results sound search")
        def test_if_get_freesound_fails_then_warns_user_and_invoke_get_local_file(
            self, mocker: pytest_mock.MockerFixture
        ):
            mock_print = mocker.patch("move_alarm.components.sounds.print")

            mock_get_local_file = mocker.patch(
                "move_alarm.components.sounds.Sounds.get_local_file",
                return_value=self.new_sound_path,
            )

            sound = Sounds()
            sound_path = sound.get_sound()

            assert isinstance(sound_path, str) == True
            assert os.path.exists(os.path.dirname(sound_path)) == True
            mock_print.assert_called_once()
            mock_get_local_file.assert_called_once()

    @pytest.mark.usefixtures("Mock Context api_enabled false")
    @pytest.mark.usefixtures("Mock WaveObject")
    class TestPlaySound:

        @pytest.mark.usefixtures("Mock stop_sound")
        def test_invokes_get_sound(self, mocker: pytest_mock.MockerFixture):
            mock_get_sound = mocker.patch(
                "move_alarm.components.sounds.Sounds.get_sound",
            )

            sound = Sounds()
            sound.play_sound()

            mock_get_sound.assert_called_once()

        @pytest.mark.usefixtures("Mock stop_sound")
        def test_sets_is_playing_property_to_true(self):
            sound = Sounds()
            sound.play_sound()

            assert sound.is_playing == True

        @pytest.mark.usefixtures("Mock stop_sound")
        def test_plays_the_sound(self, capfd: pytest.CaptureFixture):
            sound = Sounds()
            sound.play_sound()

            out, err = capfd.readouterr()

            assert out == "play was invoked from MockWaveObject!\n"

        def test_when_the_sound_stops_invokes_stop_sound(
            self, mocker: pytest_mock.MockerFixture
        ):
            sound = Sounds()

            mock_stop_sound = mocker.patch(
                "move_alarm.components.sounds.Sounds.stop_sound",
            )

            sound.play_sound()

            mock_stop_sound.assert_called_once()

    class TestStopSound:

        def test_return_bool_false_if_no_sound_is_playing(self):
            sound = Sounds()

            a_sound_was_stopped = sound.stop_sound()

            assert a_sound_was_stopped == False

        def test_if_one_sound_is_playing_it_stops_immediately(
            self, capfd: pytest.CaptureFixture, mock_invoke_play_sound_times
        ):
            sound = Sounds()
            mock_invoke_play_sound_times(1, sound)

            sound.stop_sound()

            out, err = capfd.readouterr()

            assert out == "stop was invoked from MockPlayObject!\n"

        def test_if_multiple_sounds_are_playing_they_all_stop(
            self, capfd: pytest.CaptureFixture, mock_invoke_play_sound_times
        ):
            sound = Sounds()
            mock_invoke_play_sound_times(3, sound)

            assert len(sound._play_objects) == 3

            sound.stop_sound()

            out, err = capfd.readouterr()

            assert out == 3 * "stop was invoked from MockPlayObject!\n"
            assert len(sound._play_objects) == 0

        def test_stop_sound_sets_is_playing_to_false(
            self, mock_invoke_play_sound_times
        ):
            sound = Sounds()
            mock_invoke_play_sound_times(2, sound)

            assert sound.is_playing == True

            sound.stop_sound()

            assert sound.is_playing == False

        def test_returns_true_if_any_sound_was_stopped_playing(
            self, mock_invoke_play_sound_times
        ):
            sound = Sounds()
            mock_invoke_play_sound_times(1, sound)

            a_sound_was_stopped = sound.stop_sound()

            assert a_sound_was_stopped == True

        def test_a_specific_sound_can_be_stopped(self, mock_invoke_play_sound_times):
            sound = Sounds()
            mock_invoke_play_sound_times(4, sound)
            specific_sound = sound._play_objects[2]

            assert len(set(sound._play_objects)) == 4
            assert specific_sound in sound._play_objects

            sound.stop_sound(specific_sound)

            assert len(sound._play_objects) == 3
            assert specific_sound not in sound._play_objects


###----------------------------------
# Methods to do:

# stop_sound
