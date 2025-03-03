import os
import io
from datetime import timedelta
import pytest
from move_alarm.app import App
from move_alarm import utils
import move_alarm.datatypes as datatype


class TestApp:

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
    def mock_config(self) -> datatype.Config:
        return datatype.Config(
            wait_duration=timedelta(minutes=3),
            snooze_duration=timedelta(minutes=2),
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

        monkeypatch.setattr("move_alarm.app.use_context", lambda: mock_contexts)

    @pytest.fixture(name="Prevent set_config_file initiation call creating a new file")
    def prevent_set_config_file(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr(
            utils.Configuration,
            "set_config_file",
            lambda *args, **kwargs: None,
        )

    @pytest.fixture
    def mock_input_to_terminal(self, monkeypatch: pytest.MonkeyPatch):
        def mock_stdin(value: str) -> None:
            monkeypatch.setattr("sys.stdin", io.StringIO(value))

        return mock_stdin

    @pytest.fixture(name="prevent REPL welcome and exit message")
    def prevent_repl_welcome_and_exit_message(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr(
            "move_alarm.app.InteractiveConsole.interact", lambda *args: None
        )

    @pytest.mark.usefixtures("prevent REPL welcome and exit message")
    class TestInitialisation:

        @property
        def wav_directory(self) -> str:
            try:
                return self._wav_directory
            except:
                self._wav_directory = TestApp.wav_directory.fget(self)
                return self._wav_directory

        @property
        def config(self) -> datatype.Config:
            return TestApp.mock_config.fget(self)

        @pytest.mark.usefixtures("Mock Context")
        def test_config_file_loaded_on_initialisation(self, mock_input_to_terminal):
            print("test1")
            app = App()

            mock_input_to_terminal("exit()")

            assert isinstance(app.config, datatype.Config) is True

            app_config_attributes = dir(app.config)
            for key in [attr for attr in dir(self.config) if attr[:2] != "__"]:
                assert key in app_config_attributes
                assert type(getattr(self.config, key)) == type(getattr(app.config, key))

        @pytest.mark.usefixtures(
            "Prevent set_config_file initiation call creating a new file"
        )
        def test_user_is_warned_if_config_has_to_load_from_defaults(
            self, mock_input_to_terminal, capfd: pytest.CaptureFixture
        ):
            App()

            mock_input_to_terminal("exit()")

            out, err = capfd.readouterr()

            config_path = os.path.join(
                os.path.dirname(__file__)[:-9], "move_alarm", "config.ini"
            )

            assert out == f"File not found: {config_path}\nUsing default values...\n"

        @pytest.mark.skip
        def test_user_has_access_to_the_repl_environment(self, mock_input_to_terminal):
            app = App()

            mock_input_to_terminal("")
