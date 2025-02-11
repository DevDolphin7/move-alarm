import os, re, io
from datetime import datetime
from collections.abc import Callable
import pytest, pytest_mock, dotenv
from src.utils.utils import HandleAuthorisation


@pytest.fixture(scope="class", autouse=True)
def env_path(request: pytest.FixtureRequest):
    request.cls.pytest_fixture_env_path = os.path.join(
        os.path.dirname(__file__)[:-9], "src", ".env"
    )


@pytest.fixture(scope="class", autouse=True)
def valid_env_vars(request: pytest.FixtureRequest):
    request.cls.pytest_fixture_valid_env_vars = [
        "CLIENT_ID",
        "CLIENT_CODE",
        "CLIENT_STATE",
        "CLIENT_TOKEN",
    ]


class TestHandleAuthorisation:

    @pytest.fixture
    def remove_env_file(self):
        def _remove_env_file(env_path: str) -> Callable[[str], None]:
            if os.path.exists(env_path):
                os.remove(env_path)

        return _remove_env_file

    @pytest.fixture(name="Change env file modified date to 1 day ago")
    def patch_env_file_modification_date_to_24_hours_ago(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        now = datetime.timestamp(datetime.now())
        yesterday = now - 86401
        monkeypatch.setattr(os.path, "getmtime", lambda _: yesterday)

    @pytest.fixture(name="Prevent browser opening")
    def prevent_browser_opening(self, monkeypatch: pytest.MonkeyPatch):
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
    ) -> dict[str : str | int]:
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

        monkeypatch.setattr("requests.post", lambda _, data: MockResponse())

    @pytest.fixture(name="401 mock API request / response")
    def mock_401_api_request_and_response(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> dict[str : str | int]:
        class MockResponse:
            @property
            def status_code(self):
                return 401

            def text(self):
                return "The credentials you provided are invalid."

        monkeypatch.setattr("requests.post", lambda _, data: MockResponse())

    @pytest.fixture(name="404 mock API request / response")
    def mock_404_api_request_and_response(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> dict[str : str | int]:
        class MockResponse:
            @property
            def status_code(self):
                return 404

            def text(self):
                return "The information that the request is trying to access does not exist."

        monkeypatch.setattr("requests.post", lambda _, data: MockResponse())

    @pytest.fixture(name="429 mock API request / response")
    def mock_429_api_request_and_response(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> dict[str : str | int]:
        class MockResponse:
            @property
            def status_code(self):
                return 429

            def text(self):
                return (
                    "The request was throttled because of exceeding request limit rates"
                )

        monkeypatch.setattr("requests.post", lambda _, data: MockResponse())

    @pytest.fixture(name="Unknown bad mock API request / response")
    def mock_4xx_5xx_api_request_and_response(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> dict[str : str | int]:
        class MockResponse:
            @property
            def status_code(self):
                return 500

            def text(self):
                return "An unknown bad thing happened..."

        monkeypatch.setattr("requests.post", lambda _, data: MockResponse())

    class TestProperties:
        def test_has_property_user_id(self):
            ha = HandleAuthorisation("")
            assert isinstance(ha.user_id, str)

        def test_has_property_oauth_token(self):
            ha = HandleAuthorisation("")
            assert isinstance(ha.oauth_token, (str, type(None)))

        def test_invoking_with_string_sets_user_id(self):
            ha = HandleAuthorisation("user id")
            assert ha.user_id == "user id"

        def test_invoking_with_other_data_types_raises_error(self):
            with pytest.raises(TypeError):
                HandleAuthorisation(True)

    class TestIsDotenvFileRecent:

        @property
        def env_path(self):
            return self.pytest_fixture_env_path

        @pytest.fixture(autouse=True)
        def before_each(self, remove_env_file: Callable[[str], None]):
            remove_env_file(self.env_path)

        def test_returns_true_if_env_file_created_in_last_24_hours(self):
            ha = HandleAuthorisation("user id")

            with open(self.env_path, "w") as file:
                file.write("")

            assert ha.is_dotenv_file_recent() == True

        @pytest.mark.usefixtures("Change env file modified date to 1 day ago")
        def test_returns_false_if_env_file_more_than_24_hours_old(self):
            ha = HandleAuthorisation("user id")

            with open(self.env_path, "w") as file:
                file.write("")

            assert ha.is_dotenv_file_recent() == False

        def test_raises_error_if_env_file_not_found(self):
            ha = HandleAuthorisation("user id")

            with pytest.raises(FileNotFoundError):
                ha.is_dotenv_file_recent()

    class TestGenerateState:

        def test_returns_a_string(self):
            ha = HandleAuthorisation("user id")

            state = ha.generate_state()

            assert type(state) == str

        def test_state_length_is_8_to_12_characters(self):
            ha = HandleAuthorisation("user id")

            state = ha.generate_state()

            assert len(state) >= 8
            assert len(state) <= 12

        def test_state_only_contains_upper_case_lower_case_or_numbers(self):
            ha = HandleAuthorisation("user id")

            state = ha.generate_state()

            regex_result = re.fullmatch("^[A-Z0-9]{8,12}$", state, flags=re.I)

            assert isinstance(regex_result, re.Match) == True

        def test_state_is_different_on_repeat_calls(self):
            ha = HandleAuthorisation("user id")

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
        def before_each(self, remove_env_file: Callable[[str], None]):
            remove_env_file(self.env_path)

        def test_creates_a_env_file(self):
            ha = HandleAuthorisation("user id")
            ha._oauth_code = "mock code"

            ha.set_dotenv_file("token")

            assert os.path.exists(self.env_path) == True

        def test_env_file_contains_correct_variables(self):
            ha = HandleAuthorisation("user id")
            ha._oauth_code = "mock code"

            ha.set_dotenv_file("token")

            env_dict = dotenv.dotenv_values(self.env_path)
            env_keys = env_dict.keys()

            assert len(env_keys) == len(self.valid_env_vars)

            for valid_env_var in self.valid_env_vars:
                assert valid_env_var in env_keys

        def test_env_file_values_are_user_defined(self):
            ha = HandleAuthorisation("user_bob")
            ha._oauth_code = "mock code"

            ha.set_dotenv_file("bobs_api_token")

            env_dict = dotenv.dotenv_values(self.env_path)

            assert env_dict[self.valid_env_vars[0]] == "user_bob"
            assert env_dict[self.valid_env_vars[3]] == "bobs_api_token"

        def test_doesnt_modify_env_file_if_less_than_24_hours_since_modified(self):
            with open(self.env_path, "w") as file:
                file.write("")

            ha = HandleAuthorisation("user id")

            ha.set_dotenv_file("token")

            env_dict = dotenv.dotenv_values(self.env_path)

            assert len(env_dict) == 0

        def test_returns_true_if_env_file_up_to_date(self):
            ha = HandleAuthorisation("user id")
            ha._oauth_code = "mock code"

            assert ha.set_dotenv_file("token") == True

        def test_client_state_is_randomly_generated_in_env_file(self):
            ha = HandleAuthorisation("user id")
            ha._oauth_code = "mock code"
            ha.set_dotenv_file("token")

            env_dict = dotenv.dotenv_values(self.env_path)
            state = env_dict[self.valid_env_vars[2]]
            regex_result = re.fullmatch("^[A-Z0-9]{8,12}$", state, flags=re.I)

            assert isinstance(regex_result, re.Match) == True

    class TestLoadDotenvFile:

        @property
        def env_path(self):
            return self.pytest_fixture_env_path

        @pytest.fixture(autouse=True)
        def before_each(self, remove_env_file: Callable[[str], None]):
            remove_env_file(self.env_path)

        def test_if_file_is_recent_updates_state_and_oauth_with_value_from_env_file(
            self,
        ):
            ha = HandleAuthorisation("user id")
            ha._oauth_code = "mock code"
            ha.set_dotenv_file("token")

            env_dict = dotenv.dotenv_values(self.env_path)
            env_values = env_dict.values()

            ha.load_dotenv_file()

            assert ha._state in env_values
            assert ha.oauth_token in env_values

        @pytest.mark.usefixtures("Change env file modified date to 1 day ago")
        def test_if_file_is_old_updates_oauth_with_value_from_env_file(self):
            ha = HandleAuthorisation("user id")
            ha._oauth_code = "mock code"
            ha.set_dotenv_file("token")

            env_dict = dotenv.dotenv_values(self.env_path)
            env_values = env_dict.values()

            ha.load_dotenv_file()

            assert ha.oauth_token in env_values

        def test_returns_string_recent_on_success(self):
            ha = HandleAuthorisation("user id")
            ha._oauth_code = "mock code"
            ha.set_dotenv_file("token")

            assert ha.load_dotenv_file() == "recent"

        @pytest.mark.usefixtures("Change env file modified date to 1 day ago")
        def test_returns_string_old_if_env_file_is_not_recent(self):
            ha = HandleAuthorisation("user id")
            ha._oauth_code = "mock code"
            ha.set_dotenv_file("token")

            assert ha.load_dotenv_file() == "old"

        def test_raises_error_if_env_file_missing(self):
            ha = HandleAuthorisation("user id")

            with pytest.raises(FileNotFoundError):
                ha.load_dotenv_file()

    @pytest.mark.usefixtures("Prevent browser opening")
    class TestGetUserPermission:

        def test_opens_browser_window_and_allows_user_to_enter_oauth_code(
            self, mock_input_to_terminal: Callable[[str], None]
        ):
            ha = HandleAuthorisation("user id")

            mock_input_to_terminal("6Wc9r2zbAcatxfjnAB63hzsOElGCtlbXmn3ZHzJh")

            ha.get_user_permission()

            assert type(ha._oauth_code) == str
            assert len(ha._oauth_code) == 40

            regex_result = re.fullmatch("^[A-Z0-9]{40}$", ha._oauth_code, flags=re.I)
            assert isinstance(regex_result, re.Match) == True

        def test_returns_true_on_success(
            self, mock_input_to_terminal: Callable[[str], None]
        ):
            ha = HandleAuthorisation("user id")

            mock_input_to_terminal("6Wc9r2zbAcatxfjnAB63hzsOElGCtlbXmn3ZHzJh")
            assert ha.get_user_permission() == True

        def test_raises_error_on_invalid_oauth_code(
            self, mock_input_to_terminal: Callable[[str], None]
        ):
            ha = HandleAuthorisation("user id")

            mock_input_to_terminal("!Wc9r2zbAcatxfjnAB63hzsOElGCtlbXmn3ZHzJh")
            with pytest.raises(ValueError):
                ha.get_user_permission()

    class TestRequestOauthToken:

        @property
        def env_path(self):
            return self.pytest_fixture_env_path

        @pytest.mark.usefixtures("200 mock API request / response")
        def test_updates_oauth_token_property_with_access_token(self):
            ha = HandleAuthorisation("user id")
            ha._oauth_code = "mock code"

            ha.request_oauth_token()

            assert ha.oauth_token == "64c64660ceed813476b314f52136d9698e075622"

        @pytest.mark.usefixtures("200 mock API request / response")
        def test_updates_env_file_with_refresh_token(self):
            ha = HandleAuthorisation("user id")
            ha._oauth_code = "mock code"

            ha.request_oauth_token()

            env_dict = dotenv.dotenv_values(self.env_path)

            assert (
                env_dict["CLIENT_TOKEN"] == "0354489231f6a874331aer4927569297c7fea4d5"
            )

        @pytest.mark.usefixtures("200 mock API request / response")
        def test_returns_an_access_token(self):
            ha = HandleAuthorisation("user id")
            ha._oauth_code = "mock code"

            assert (
                ha.request_oauth_token() == "64c64660ceed813476b314f52136d9698e075622"
            )

        @pytest.mark.usefixtures("401 mock API request / response")
        def test_401_status_raises_connection_refused_error(self):
            ha = HandleAuthorisation("user id")
            ha._oauth_code = "mock code"

            with pytest.raises(ConnectionRefusedError):
                ha.request_oauth_token()

        @pytest.mark.usefixtures("404 mock API request / response")
        def test_404_status_raises_connection_error(self):
            ha = HandleAuthorisation("user id")
            ha._oauth_code = "mock code"

            with pytest.raises(ConnectionError):
                ha.request_oauth_token()

        @pytest.mark.usefixtures("429 mock API request / response")
        def test_429_status_raises_connection_refused_error(self):
            ha = HandleAuthorisation("user id")
            ha._oauth_code = "mock code"

            with pytest.raises(ConnectionRefusedError):
                ha.request_oauth_token()

        @pytest.mark.usefixtures("Unknown bad mock API request / response")
        def test_4xx_5xx_status_raises_connection_refused_error(self):
            ha = HandleAuthorisation("user id")
            ha._oauth_code = "mock code"

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
        def before_each(self, remove_env_file: Callable[[str], None]):
            remove_env_file(self.env_path)

        @pytest.mark.usefixtures("200 mock API request / response")
        def test_if_env_file_missing_invokes_get_user_permission(
            self, mocker: pytest_mock.MockerFixture
        ):
            ha = HandleAuthorisation("user id")
            ha._oauth_code = "None"

            mock_get_user_permission = mocker.patch(
                "src.utils.utils.HandleAuthorisation.get_user_permission"
            )

            ha.get_token()

            mock_get_user_permission.assert_called_once()

        @pytest.mark.usefixtures("200 mock API request / response")
        def test_if_env_file_missing_creates_valid_env_file(
            self, mock_input_to_terminal: Callable[[str], None]
        ):
            ha = HandleAuthorisation("user id")

            mock_input_to_terminal("6Wc9r2zbAcatxfjnAB63hzsOElGCtlbXmn3ZHzJh")
            ha.get_token()

            env_dict = dotenv.dotenv_values(self.env_path)
            env_keys = env_dict.keys()

            assert len(env_keys) == len(self.valid_env_vars)

            for valid_env_var in self.valid_env_vars:
                assert valid_env_var in env_keys

        @pytest.mark.usefixtures("200 mock API request / response")
        def test_invokes_load_dotenv_file(self, mocker: pytest_mock.MockerFixture):
            ha = HandleAuthorisation("user id")
            ha._oauth_code = "mock code"
            ha.set_dotenv_file("token")

            mock_load_dotenv_file = mocker.patch(
                "src.utils.utils.HandleAuthorisation.load_dotenv_file"
            )

            ha.get_token()

            mock_load_dotenv_file.assert_called_once()

        @pytest.mark.usefixtures("200 mock API request / response")
        def test_invokes_request_oauth_token(self, mocker: pytest_mock.MockerFixture):
            ha = HandleAuthorisation("user id")
            ha._oauth_code = "mock code"
            ha.set_dotenv_file("token")

            mock_request_oauth_token = mocker.patch(
                "src.utils.utils.HandleAuthorisation.request_oauth_token"
            )

            ha.get_token()

            mock_request_oauth_token.assert_called_once()

        @pytest.mark.usefixtures("200 mock API request / response")
        def test_returns_oauth_token(self):
            ha = HandleAuthorisation("user id")
            ha._oauth_code = "mock code"
            ha.set_dotenv_file("token")

            token = ha.get_token()

            assert token == "64c64660ceed813476b314f52136d9698e075622"
        
        def test_github_action(self):
            assert 1 == 0
