import os, re, io
from datetime import datetime
from collections.abc import Callable
import pytest, pytest_mock, dotenv
from src.utils.utils import HandleAuthorisation


@pytest.fixture(scope="class")
def define_env_path():
    return os.path.join(os.path.dirname(__file__)[:-9], "src", ".env.test")


@pytest.fixture(scope="class", autouse=True)
def env_path(request: pytest.FixtureRequest, define_env_path):
    request.cls.pytest_fixture_env_path = define_env_path


@pytest.fixture(autouse=True, name="Set env path")
def before_all(monkeypatch: pytest.MonkeyPatch, define_env_path):
    monkeypatch.setattr("os.path.join", lambda *args: define_env_path)


@pytest.fixture(scope="class", autouse=True)
def valid_env_vars(request: pytest.FixtureRequest):
    request.cls.pytest_fixture_valid_env_vars = [
        "CLIENT_ID",
        "CLIENT_STATE",
        "REFRESH_TOKEN",
    ]


@pytest.mark.usefixtures(name="Set env path")
class TestHandleAuthorisation:

    @pytest.fixture
    def remove_env_file(self) -> Callable[[str], None]:
        def _remove_env_file(env_path: str) -> None:
            if os.path.exists(env_path):
                os.remove(env_path)

        return _remove_env_file

    @pytest.fixture
    def create_mock_env_file(self) -> Callable[[str], None]:
        def _create_mock_env_file(env_vars, env_path):
            for valid_env_var in env_vars:
                with open(env_path, "a") as file:
                    file.write(f"{valid_env_var}=mock_data\n")

        return _create_mock_env_file

    @pytest.fixture(name="Change env file modified date to 1 day ago")
    def patch_env_file_modification_date_to_24_hours_ago(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        now = datetime.timestamp(datetime.now())
        yesterday = now - 86401
        monkeypatch.setattr(os.path, "getmtime", lambda _: yesterday)

    @pytest.fixture(name="Prevent browser opening")
    def prevent_browser_opening(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("webbrowser.open", lambda _: None)

    @pytest.fixture
    def mock_input_to_terminal(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> Callable[[str], None]:
        def mock_stdin(value: str) -> None:
            monkeypatch.setattr("sys.stdin", io.StringIO(value))

        return mock_stdin

    @pytest.fixture(name="200 mock API request / response")
    def mock_200_api_request_and_response(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        class MockResponse:
            @property
            def status_code(self):
                return 200

            def json(self):
                return {
                    "access_token": "64c64660ceed813476b314f52136d9698e075622",
                    "scope": "read write read+write",
                    "expires_in": 86399,
                    "refresh_token": "0354489231f6a874331aer4927569297c7fea4d5",
                }

        monkeypatch.setattr("requests.get", lambda _: MockResponse())

    @pytest.fixture(name="401 mock API request / response")
    def mock_401_api_request_and_response(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        class MockResponse:
            @property
            def status_code(self):
                return 401

            def text(self):
                return "The credentials you provided are invalid."

        monkeypatch.setattr("requests.get", lambda _: MockResponse())

    @pytest.fixture(name="404 mock API request / response")
    def mock_404_api_request_and_response(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        class MockResponse:
            @property
            def status_code(self):
                return 404

            def text(self):
                return "The information that the request is trying to access does not exist."

        monkeypatch.setattr("requests.get", lambda _: MockResponse())

    @pytest.fixture(name="429 mock API request / response")
    def mock_429_api_request_and_response(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        class MockResponse:
            @property
            def status_code(self):
                return 429

            def text(self):
                return (
                    "The request was throttled because of exceeding request limit rates"
                )

        monkeypatch.setattr("requests.get", lambda _: MockResponse())

    @pytest.fixture(name="Unknown bad mock API request / response")
    def mock_4xx_5xx_api_request_and_response(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        class MockResponse:
            @property
            def status_code(self):
                return 500

            def text(self):
                return "An unknown bad thing happened..."

        monkeypatch.setattr("requests.get", lambda _: MockResponse())

    class TestProperties:
        @property
        def env_path(self):
            return self.pytest_fixture_env_path

        @property
        def valid_env_vars(self):
            return self.pytest_fixture_valid_env_vars

        @pytest.fixture(autouse=True)
        def before_each(
            self,
            remove_env_file,
            create_mock_env_file,
        ):
            remove_env_file(self.env_path)
            create_mock_env_file(self.valid_env_vars, self.env_path)

        def test_has_property_client_id(self):
            ha = HandleAuthorisation("")
            assert isinstance(ha.client_id, str)

        def test_has_property_oauth_code(self):
            ha = HandleAuthorisation("")
            assert isinstance(ha.oauth_code, (str, type(None)))

        def test_invoking_with_string_sets_client_id(self):
            ha = HandleAuthorisation("client id")
            assert ha.client_id == "client id"

        def test_invoking_with_other_data_types_raises_error(self):
            with pytest.raises(TypeError):
                HandleAuthorisation(True)

        def test_invoking_with_no_arguments_loads_client_id_from_env_file(
            self, create_mock_env_file
        ):
            create_mock_env_file(self.valid_env_vars, self.env_path)

            ha = HandleAuthorisation()
            assert ha.client_id == "mock_data"

    class TestIsDotenvFileRecent:

        @property
        def env_path(self):
            return self.pytest_fixture_env_path

        @pytest.fixture(autouse=True)
        def before_each(self, remove_env_file):
            remove_env_file(self.env_path)

        def test_returns_true_if_env_file_created_in_last_24_hours(self):
            ha = HandleAuthorisation("client id")

            with open(self.env_path, "w") as file:
                file.write("")

            assert ha.is_dotenv_file_recent() == True

        @pytest.mark.usefixtures("Change env file modified date to 1 day ago")
        def test_returns_false_if_env_file_more_than_24_hours_old(self):
            ha = HandleAuthorisation("client id")

            with open(self.env_path, "w") as file:
                file.write("")

            assert ha.is_dotenv_file_recent() == False

        def test_raises_error_if_env_file_not_found(self):
            ha = HandleAuthorisation("client id")

            with pytest.raises(FileNotFoundError):
                ha.is_dotenv_file_recent()

    class TestGenerateState:

        def test_returns_a_string(self):
            ha = HandleAuthorisation("client id")

            state = ha.generate_state()

            assert type(state) == str

        def test_state_length_is_8_to_12_characters(self):
            ha = HandleAuthorisation("client id")

            state = ha.generate_state()

            assert len(state) >= 8
            assert len(state) <= 12

        def test_state_only_contains_upper_case_lower_case_or_numbers(self):
            ha = HandleAuthorisation("client id")

            state = ha.generate_state()

            regex_result = re.fullmatch("^[A-Z0-9]{8,12}$", state, flags=re.I)

            assert isinstance(regex_result, re.Match) == True

        def test_state_is_different_on_repeat_calls(self):
            ha = HandleAuthorisation("client id")

            state_one = ha.generate_state()
            state_two = ha.generate_state()

            assert state_one != state_two

    class TestSetDotenvFile:

        @property
        def env_path(self):
            return self.pytest_fixture_env_path

        @property
        def valid_env_vars(self):
            return self.pytest_fixture_valid_env_vars

        @pytest.fixture(autouse=True)
        def before_each(self, remove_env_file):
            remove_env_file(self.env_path)

        def test_creates_an_env_file(self):
            ha = HandleAuthorisation("client id")
            ha.oauth_code = "mockcodemockcodemockcodemockcode"

            ha.set_dotenv_file("token")

            assert os.path.exists(self.env_path) == True

        def test_env_file_contains_correct_variables(self):
            ha = HandleAuthorisation("client id")
            ha.oauth_code = "mockcodemockcodemockcodemockcode"

            ha.set_dotenv_file("token")

            env_dict = dotenv.dotenv_values(self.env_path)
            env_keys = env_dict.keys()

            assert len(env_keys) == len(self.valid_env_vars)

            for valid_env_var in self.valid_env_vars:
                assert valid_env_var in env_keys

        def test_env_file_values_are_user_defined(self):
            ha = HandleAuthorisation("client_bob")
            ha.oauth_code = "mockcodemockcodemockcodemockcode"

            ha.set_dotenv_file("bobs_api_token")

            env_dict = dotenv.dotenv_values(self.env_path)

            assert env_dict[self.valid_env_vars[0]] == "client_bob"
            assert env_dict[self.valid_env_vars[2]] == "bobs_api_token"

        def test_returns_true_if_env_file_up_to_date(self):
            ha = HandleAuthorisation("client id")
            ha.oauth_code = "mockcodemockcodemockcodemockcode"

            assert ha.set_dotenv_file("token") == True

        def test_client_state_is_randomly_generated_in_env_file(self):
            ha = HandleAuthorisation("client id")
            ha.oauth_code = "mockcodemockcodemockcodemockcode"
            ha.set_dotenv_file("token")

            env_dict = dotenv.dotenv_values(self.env_path)
            state = env_dict[self.valid_env_vars[1]]
            regex_result = re.fullmatch("^[A-Z0-9]{8,12}$", state, flags=re.I)

            assert isinstance(regex_result, re.Match) == True

    class TestLoadDotenvFile:

        @property
        def env_path(self):
            return self.pytest_fixture_env_path

        @property
        def valid_env_vars(self):
            return self.pytest_fixture_valid_env_vars

        @pytest.fixture(autouse=True)
        def before_each(
            self,
            remove_env_file,
            create_mock_env_file,
        ):
            remove_env_file(self.env_path)
            create_mock_env_file(self.valid_env_vars, self.env_path)

        def test_if_file_is_recent_updates_id_and_state_and_oauth_with_value_from_env_file(
            self,
        ):
            ha = HandleAuthorisation("client id")
            ha.oauth_code = "mockcodemockcodemockcodemockcode"

            env_dict = dotenv.dotenv_values(self.env_path)
            env_values = env_dict.values()

            ha.load_dotenv_file()

            assert ha.client_id in env_values
            assert ha._state in env_values
            assert ha.oauth_token in env_values

        @pytest.mark.usefixtures("Change env file modified date to 1 day ago")
        def test_if_file_is_old_updates_id_and_oauth_with_value_from_env_file(self):
            ha = HandleAuthorisation("client id")
            ha.oauth_code = "mockcodemockcodemockcodemockcode"

            env_dict = dotenv.dotenv_values(self.env_path)
            env_values = env_dict.values()

            ha.load_dotenv_file()

            assert ha.client_id in env_values
            assert ha.oauth_token in env_values

        def test_returns_string_recent_on_success(self):
            ha = HandleAuthorisation("client id")
            ha.oauth_code = "mockcodemockcodemockcodemockcode"

            assert ha.load_dotenv_file() == "recent"

        @pytest.mark.usefixtures("Change env file modified date to 1 day ago")
        def test_returns_string_old_if_env_file_is_not_recent(self):
            ha = HandleAuthorisation("client id")
            ha.oauth_code = "mockcodemockcodemockcodemockcode"

            assert ha.load_dotenv_file() == "old"

        def test_raises_error_if_env_file_missing(self, remove_env_file):
            remove_env_file(self.env_path)

            ha = HandleAuthorisation("client id")

            with pytest.raises(FileNotFoundError):
                ha.load_dotenv_file()

    @pytest.mark.usefixtures("Prevent browser opening")
    class TestGetUserPermission:

        def test_opens_browser_window_and_allows_user_to_enter_oauth_code(
            self, mock_input_to_terminal
        ):
            ha = HandleAuthorisation("client id")

            mock_input_to_terminal("6Wc9r2zbAcatxfjnAB63hzsOElGCtlbXmn3ZHzJh")

            ha.get_user_permission()

            assert type(ha.oauth_code) == str
            assert len(ha.oauth_code) == 40

            regex_result = re.fullmatch("^[A-Z0-9]{40}$", ha.oauth_code, flags=re.I)
            assert isinstance(regex_result, re.Match) == True

        def test_returns_true_on_success(self, mock_input_to_terminal):
            ha = HandleAuthorisation("client id")

            mock_input_to_terminal("6Wc9r2zbAcatxfjnAB63hzsOElGCtlbXmn3ZHzJh")
            assert ha.get_user_permission() == True

        def test_raises_error_on_invalid_oauth_code(self, mock_input_to_terminal):
            ha = HandleAuthorisation("client id")

            mock_input_to_terminal("!Wc9r2zbAcatxfjnAB63hzsOElGCtlbXmn3ZHzJh")
            with pytest.raises(ValueError):
                ha.get_user_permission()

    class TestRequestOauthToken:

        @property
        def env_path(self):
            return self.pytest_fixture_env_path

        @property
        def valid_env_vars(self):
            return self.pytest_fixture_valid_env_vars

        @pytest.mark.usefixtures("200 mock API request / response")
        def test_updates_oauth_token_property_with_access_token(self):
            ha = HandleAuthorisation("client id")
            ha.oauth_code = "mockcodemockcodemockcodemockcode"

            ha.request_oauth_token()

            assert ha.oauth_token == "64c64660ceed813476b314f52136d9698e075622"

        @pytest.mark.usefixtures("200 mock API request / response")
        def test_updates_env_file_with_refresh_token(self):
            ha = HandleAuthorisation("client id")
            ha.oauth_code = "mockcodemockcodemockcodemockcode"

            ha.request_oauth_token()

            env_dict = dotenv.dotenv_values(self.env_path)

            assert (
                env_dict[self.valid_env_vars[2]]
                == "0354489231f6a874331aer4927569297c7fea4d5"
            )

        @pytest.mark.usefixtures("200 mock API request / response")
        def test_returns_an_access_token(self):
            ha = HandleAuthorisation("client id")
            ha.oauth_code = "mockcodemockcodemockcodemockcode"

            assert (
                ha.request_oauth_token() == "64c64660ceed813476b314f52136d9698e075622"
            )

        @pytest.mark.usefixtures("401 mock API request / response")
        def test_401_status_raises_connection_refused_error(self):
            ha = HandleAuthorisation("client id")
            ha.oauth_code = "mockcodemockcodemockcodemockcode"

            with pytest.raises(ConnectionRefusedError):
                ha.request_oauth_token()

        @pytest.mark.usefixtures("404 mock API request / response")
        def test_404_status_raises_connection_error(self):
            ha = HandleAuthorisation("client id")
            ha.oauth_code = "mockcodemockcodemockcodemockcode"

            with pytest.raises(ConnectionError):
                ha.request_oauth_token()

        @pytest.mark.usefixtures("429 mock API request / response")
        def test_429_status_raises_connection_refused_error(self):
            ha = HandleAuthorisation("client id")
            ha.oauth_code = "mockcodemockcodemockcodemockcode"

            with pytest.raises(ConnectionRefusedError):
                ha.request_oauth_token()

        @pytest.mark.usefixtures("Unknown bad mock API request / response")
        def test_4xx_5xx_status_raises_connection_refused_error(self):
            ha = HandleAuthorisation("client id")
            ha.oauth_code = "mockcodemockcodemockcodemockcode"

            with pytest.raises(ConnectionError):
                ha.request_oauth_token()

    @pytest.mark.usefixtures("Prevent browser opening")
    class TestGetToken:

        @property
        def env_path(self):
            return self.pytest_fixture_env_path

        @property
        def valid_env_vars(self):
            return self.pytest_fixture_valid_env_vars

        @pytest.fixture(autouse=True)
        def before_each(self, remove_env_file):
            remove_env_file(self.env_path)

        @pytest.mark.usefixtures("200 mock API request / response")
        def test_if_env_file_missing_invokes_get_user_permission(
            self, mocker: pytest_mock.MockerFixture
        ):
            ha = HandleAuthorisation("client id")

            mock_get_user_permission = mocker.patch(
                "src.utils.utils.HandleAuthorisation.get_user_permission"
            )

            ha.get_token()

            mock_get_user_permission.assert_called_once()

        @pytest.mark.usefixtures("200 mock API request / response")
        def test_if_env_file_missing_creates_valid_env_file(
            self, mock_input_to_terminal
        ):
            ha = HandleAuthorisation("client id")

            mock_input_to_terminal("6Wc9r2zbAcatxfjnAB63hzsOElGCtlbXmn3ZHzJh")
            ha.get_token()

            env_dict = dotenv.dotenv_values(self.env_path)
            env_keys = env_dict.keys()

            assert len(env_keys) == len(self.valid_env_vars)

            for valid_env_var in self.valid_env_vars:
                assert valid_env_var in env_keys

        @pytest.mark.usefixtures("200 mock API request / response")
        def test_invokes_load_dotenv_file(
            self, mocker: pytest_mock.MockerFixture, create_mock_env_file
        ):
            create_mock_env_file(self.valid_env_vars, self.env_path)

            ha = HandleAuthorisation()

            mock_load_dotenv_file = mocker.patch(
                "src.utils.utils.HandleAuthorisation.load_dotenv_file"
            )

            ha.get_token()

            mock_load_dotenv_file.assert_called_once()

        @pytest.mark.usefixtures("200 mock API request / response")
        def test_invokes_request_oauth_token(
            self, mocker: pytest_mock.MockerFixture, create_mock_env_file
        ):
            create_mock_env_file(self.valid_env_vars, self.env_path)

            ha = HandleAuthorisation()

            mock_request_oauth_token = mocker.patch(
                "src.utils.utils.HandleAuthorisation.request_oauth_token"
            )

            ha.get_token()

            mock_request_oauth_token.assert_called_once()

        @pytest.mark.usefixtures("200 mock API request / response")
        def test_returns_oauth_token(self, create_mock_env_file):
            create_mock_env_file(self.valid_env_vars, self.env_path)
            ha = HandleAuthorisation()

            token = ha.get_token()

            assert token == "64c64660ceed813476b314f52136d9698e075622"

        @pytest.mark.usefixtures("200 mock API request / response")
        def test_for_repeat_user_refresh_token_is_used(self, create_mock_env_file):
            create_mock_env_file(self.valid_env_vars, self.env_path)
            ha = HandleAuthorisation()

            token = ha.get_token()

            assert token == "64c64660ceed813476b314f52136d9698e075622"
            assert ha.oauth_code == None
