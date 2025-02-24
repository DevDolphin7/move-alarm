import os, configparser, datetime
import pytest, pytest_mock
from move_alarm.utils.config import Configuration
import move_alarm.types as datatype


class TestConfig:

    @property
    def config_path(self) -> str:
        try:
            return self._config_path
        except:
            self._config_path = os.path.join(
                os.path.dirname(__file__)[:-9], "move_alarm", "test_config.ini"
            )
            return self._config_path

    @pytest.fixture(autouse=True)
    def before_each(self):
        if os.path.exists(self.config_path):
            os.remove(self.config_path)

    @pytest.fixture
    def create_mock_config_file(self):
        config_path = self.config_path

        def _create_mock_config_file(data):
            parser = configparser.ConfigParser()
            parser.read_dict(data)

            with open(config_path, "w") as file:
                parser.write(file)

        return _create_mock_config_file

    @pytest.fixture(name="Create good mock config file")
    def create_mock_good_config_file(self, create_mock_config_file):
        good_data = {
            "Alarm": datatype.IniFormattedAlarm(
                interval=3600,
                snooze=300,
                message="Time to move!",
            ),
            "Sounds": datatype.IniFormattedSounds(
                path=os.path.dirname(__file__),
                freesound=False,
                themes=["piano", "guitar"],
            ),
        }

        create_mock_config_file(good_data)

    @pytest.fixture(name="Create missing key mock config file")
    def create_mock_missing_key_config_file(self, create_mock_config_file):
        tampered_data = {
            "Alarm": datatype.IniFormattedAlarm(
                interval=3600,
                snooze=300,
                message="Time to move!",
            ),
            "Sounds": datatype.IniFormattedSounds(
                path=os.path.dirname(__file__),
                freesound=False,
            ),
        }

        create_mock_config_file(tampered_data)

    @pytest.fixture(name="Create bad value type mock config file")
    def create_mock_bad_value_type_config_file(self, create_mock_config_file):
        tampered_data = {
            "Alarm": datatype.IniFormattedAlarm(
                interval=3600,
                snooze="three hundred",
                message="Time to move!",
            ),
            "Sounds": datatype.IniFormattedSounds(
                path=os.path.dirname(__file__),
                freesound=False,
                themes=["piano"],
            ),
        }

        create_mock_config_file(tampered_data)

    @pytest.fixture(name="Prevent set_config_file initiation call creating a new file")
    def prevent_set_config_file(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr(
            "move_alarm.utils.config.Configuration.set_config_file",
            lambda *args, **kwargs: None,
        )

    class TestInitialisation:
        @property
        def config_path(self) -> str:
            return TestConfig.config_path.fget(self)

        def test_requires_str_config_path_on_initialisation(self):
            with pytest.raises(TypeError):
                Configuration()

        def test_raises_type_error_on_non_str_argument(self):
            with pytest.raises(TypeError):
                Configuration(True)

        def test_invokes_load_config_file_on_initiation(
            self, mocker: pytest_mock.MockerFixture
        ):
            mock_load_config_file = mocker.patch(
                "move_alarm.utils.config.Configuration.load_config_file"
            )

            Configuration(self.config_path)

            mock_load_config_file.assert_called_once()

        @pytest.mark.usefixtures("Create missing key mock config file")
        def test_warns_user_on_loading_error(self, capfd: pytest.CaptureFixture):
            Configuration(self.config_path)

            out, err = capfd.readouterr()

            assert (
                out
                == "Warning: No option 'themes' in section: 'Sounds'\nUsing default values...\n"
            )

        @pytest.mark.usefixtures("Create missing key mock config file")
        @pytest.mark.usefixtures(
            "Prevent set_config_file initiation call creating a new file"
        )
        def test_invokes_use_default_values_on_loading_error(
            self, mocker: pytest_mock.MockerFixture
        ):

            mock_use_default_values = mocker.patch(
                "move_alarm.utils.config.Configuration.use_default_values",
            )

            Configuration(self.config_path)

            mock_use_default_values.assert_called()

        def test_invokes_set_config_file_on_loading_error(
            self, mocker: pytest_mock.MockerFixture
        ):
            mock_set_config_file = mocker.patch(
                "move_alarm.utils.config.Configuration.set_config_file"
            )

            config = Configuration(self.config_path)

            mock_set_config_file.assert_called_once()

    class TestSetConfigFile:
        @property
        def config_path(self) -> str:
            return TestConfig.config_path.fget(self)

        def test_creates_a_config_file_at_config_path(self):
            assert os.path.exists(self.config_path) == False

            config = Configuration(self.config_path)
            config.set_config_file()

            assert os.path.exists(self.config_path) == True

        def test_config_file_contains_only_valid_properties(self):
            config = Configuration(self.config_path)

            config.set_config_file()

            output = configparser.ConfigParser()
            output.read(self.config_path)

            wait_duration = datetime.timedelta(
                seconds=output.getint("Alarm", "interval")
            )
            snooze_duration = datetime.timedelta(
                seconds=output.getint("Alarm", "snooze")
            )
            reminder_text = output.get("Alarm", "message")
            wav_directory = output.get("Sounds", "path")
            api_enabled = output.getboolean("Sounds", "freesound")
            sound_themes = list(output.get("Sounds", "themes"))

            for var in [wait_duration, snooze_duration]:
                assert isinstance(var, datetime.timedelta) == True

            for var in [reminder_text, wav_directory]:
                assert isinstance(var, str) == True

            assert isinstance(api_enabled, bool) == True
            assert isinstance(sound_themes, list) == True

            assert len(sound_themes) > 0
            for theme in sound_themes:
                assert isinstance(theme, str) == True

        def test_returns_true_on_success(self):
            config = Configuration(self.config_path)

            output = config.set_config_file()

            assert output == True

    class TestLoadConfig:

        @property
        def config_path(self) -> str:
            return TestConfig.config_path.fget(self)

        @pytest.mark.usefixtures("Create good mock config file")
        def test_sets_all_valid_variables_to_valid_data_types(self):

            config = Configuration(self.config_path)

            config.load_config_file()

            assert isinstance(config.wait_duration, datetime.timedelta) == True
            assert isinstance(config.snooze_duration, datetime.timedelta) == True
            assert isinstance(config.reminder_text, str) == True
            assert isinstance(config.wav_directory, str) == True
            assert isinstance(config.api_enabled, bool) == True
            assert isinstance(config.sound_themes, list) == True

        @pytest.mark.usefixtures("Create good mock config file")
        def test_returns_true_on_success(self):
            config = Configuration(self.config_path)

            output = config.load_config_file()

            assert output == True

        @pytest.mark.usefixtures(
            "Prevent set_config_file initiation call creating a new file"
        )
        def test_raises_file_not_found_on_missing_file(self):
            config = Configuration(self.config_path)

            with pytest.raises(FileNotFoundError):
                config.load_config_file()

        @pytest.mark.usefixtures("Create missing key mock config file")
        @pytest.mark.usefixtures(
            "Prevent set_config_file initiation call creating a new file"
        )
        def test_raises_value_error_on_missing_key(self):
            config = Configuration(self.config_path)

            with pytest.raises(configparser.NoOptionError):
                config.load_config_file()

        @pytest.mark.usefixtures("Create bad value type mock config file")
        @pytest.mark.usefixtures(
            "Prevent set_config_file initiation call creating a new file"
        )
        def test_raises_type_error_on_incorrect_value_types(self):
            config = Configuration(self.config_path)

            with pytest.raises(ValueError):
                config.load_config_file()

    class TestUseDefaultValues:
        @property
        def config_path(self) -> str:
            return TestConfig.config_path.fget(self)

        def test_sets_appropriate_default_values(self):
            config = Configuration(self.config_path)

            config.use_default_values()

            assert config.wait_duration == datetime.timedelta(hours=1)
            assert config.snooze_duration == datetime.timedelta(minutes=5)
            assert config.reminder_text == "Time to stretch!"
            assert config.wav_directory == os.path.join(
                os.path.dirname(__file__)[:-9], "move_alarm", "assets"
            )
            assert config.api_enabled == False
            assert config.sound_themes == ["funk"]
