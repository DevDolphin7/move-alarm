import os, re, io
from datetime import datetime
from collections.abc import Callable
import pytest, dotenv
from src.utils.utils import HandleAuthorisation

@pytest.fixture(scope="class", autouse=True)
def env_path(request: pytest.FixtureRequest):
    request.cls.pytest_fixture_env_path = os.path.join(os.path.dirname(__file__)[:-9], "src", ".env")

class TestHandleAuthorisation():
    
    @pytest.fixture
    def remove_env_file(self):
        def _remove_env_file(env_path: str) -> Callable[[str], None]:
            if os.path.exists(env_path):
                os.remove(env_path)
        return _remove_env_file
    
    @pytest.fixture(name="Change env file modified date to 1 day ago")
    def patch_env_file_modification_date_to_24_hours_ago(self, monkeypatch: pytest.MonkeyPatch):
        now = datetime.timestamp(datetime.now())
        yesterday = now - 86401
        monkeypatch.setattr(os.path, "getmtime", lambda _: yesterday)
        
    @pytest.fixture(name="Prevent browser opening")
    def prevent_browser_opening(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr("webbrowser.open", lambda _: None)
    
    @pytest.fixture
    def mock_input_to_terminal(self, monkeypatch: pytest.MonkeyPatch) -> Callable[[str], None]:
        def mock_stdin(value: str) -> None:
            monkeypatch.setattr('sys.stdin', io.StringIO(value))
        return mock_stdin
    
    @pytest.fixture(name="Mock API request / response")
    def mock_api_request_and_response(self, monkeypatch: pytest.MonkeyPatch) -> dict[str: str | int]:
        monkeypatch.setattr("requests.post", lambda _: {
            "access_token": "64c64660ceed813476b314f52136d9698e075622",
            "scope": "read write read+write",
            "expires_in": 86399,
            "refresh_token": "0354489231f6a874331aer4927569297c7fea4d5"})

    class TestProperties():
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

    class TestIsDotenvFileRecent():
        
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

    class TestGenerateState():
        
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

    class TestSetDotenvFile():
        
        @property
        def env_path(self):
            return self.pytest_fixture_env_path
        
        @property
        def valid_env_vars(self):
            return ["CLIENT_ID", "CLIENT_STATE", "CLIENT_TOKEN"]
        
        @pytest.fixture(autouse=True)
        def before_each(self, remove_env_file: Callable[[str], None]):
            remove_env_file(self.env_path)
        
        def test_creates_a_env_file(self):
            ha = HandleAuthorisation("user id")
            
            ha.set_dotenv_file("token")
            
            assert os.path.exists(self.env_path) == True
            
        def test_env_file_contains_correct_variables(self):
            ha = HandleAuthorisation("user id")
            
            ha.set_dotenv_file("token")
            
            env_dict = dotenv.dotenv_values(self.env_path)
            env_keys = env_dict.keys()
            
            assert len(env_keys) == len(self.valid_env_vars)
            
            for valid_env_var in self.valid_env_vars:
                assert valid_env_var in env_keys
                
        def test_env_file_values_are_user_defined(self):
            ha = HandleAuthorisation("user_bob")
            
            ha.set_dotenv_file("bobs_api_token")
            
            env_dict = dotenv.dotenv_values(self.env_path)

            assert env_dict[self.valid_env_vars[0]] == "user_bob"
            assert env_dict[self.valid_env_vars[2]] == "bobs_api_token"
            
        
        def test_doesnt_modify_env_file_if_less_than_24_hours_since_modified(self):
            with open(self.env_path, "w") as file:
                file.write("")
            
            ha = HandleAuthorisation("user id")
            
            ha.set_dotenv_file("token")
            
            env_dict = dotenv.dotenv_values(self.env_path)
            
            assert len(env_dict) == 0
        
        def test_returns_true_if_env_file_up_to_date(self):
            ha = HandleAuthorisation("user id")
            
            assert ha.set_dotenv_file("token") == True
            
        def test_client_state_is_randomly_generated_in_env_file(self):
            ha = HandleAuthorisation("user id")
            ha.set_dotenv_file("token")
            
            env_dict = dotenv.dotenv_values(self.env_path)
            state = env_dict[self.valid_env_vars[1]]
            regex_result = re.fullmatch("^[A-Z0-9]{8,12}$", state, flags=re.I)

            assert isinstance(regex_result, re.Match) == True

    class TestLoadDotEnv():
        
        @property
        def env_path(self):
            return self.pytest_fixture_env_path
        
        @pytest.fixture(autouse=True)
        def before_each(self, remove_env_file: Callable[[str], None]):
            remove_env_file(self.env_path)

        def test_if_file_is_recent_updates_state_and_oauth_with_value_from_env_file(self):
            ha = HandleAuthorisation("user id")
            ha.set_dotenv_file("token")
            
            env_dict = dotenv.dotenv_values(self.env_path)
            env_values = env_dict.values()
            
            ha.load_dotenv_file()
            
            assert ha._state in env_values
            assert ha.oauth_token in env_values
            
        @pytest.mark.usefixtures("Change env file modified date to 1 day ago")
        def test_if_file_is_old_updates_oauth_with_value_from_env_file(self):
            ha = HandleAuthorisation("user id")
            ha.set_dotenv_file("token")
            
            env_dict = dotenv.dotenv_values(self.env_path)
            env_values = env_dict.values()
            
            ha.load_dotenv_file()
            
            assert ha.oauth_token in env_values
            
        def test_returns_string_recent_on_success(self):
            ha = HandleAuthorisation("user id")
            ha.set_dotenv_file("token")
            
            assert ha.load_dotenv_file() == "recent"
            
        @pytest.mark.usefixtures("Change env file modified date to 1 day ago")
        def test_returns_string_old_if_env_file_is_not_recent(self):
            ha = HandleAuthorisation("user id")
            ha.set_dotenv_file("token")
            
            assert ha.load_dotenv_file() == "old"
                
        def test_raises_error_if_env_file_missing(self):
            ha = HandleAuthorisation("user id")
            
            with pytest.raises(FileNotFoundError):
                ha.load_dotenv_file()

    @pytest.mark.usefixtures("Prevent browser opening")
    class TestGetUserPermission():
        
        def test_opens_browser_window_and_allows_user_to_enter_oauth_code(self, mock_input_to_terminal: Callable[[str], None]):
            ha = HandleAuthorisation("user id")
            
            mock_input_to_terminal('6Wc9r2zbAcatxfjnAB63hzsOElGCtlbXmn3ZHzJh')
            
            ha.get_user_permission()
            
            assert type(ha._oauth_code) == str
            assert len(ha._oauth_code) == 40
            
            regex_result = re.fullmatch("^[A-Z0-9]{40}$", ha._oauth_code, flags=re.I)
            assert isinstance(regex_result, re.Match) == True
            
        def test_returns_true_on_success(self, mock_input_to_terminal: Callable[[str], None]):
            ha = HandleAuthorisation("user id")
            
            mock_input_to_terminal('6Wc9r2zbAcatxfjnAB63hzsOElGCtlbXmn3ZHzJh')
            assert ha.get_user_permission() == True
            
        def test_raises_error_on_invalid_oauth_code(self, mock_input_to_terminal: Callable[[str], None]):
            ha = HandleAuthorisation("user id")
            
            mock_input_to_terminal('!Wc9r2zbAcatxfjnAB63hzsOElGCtlbXmn3ZHzJh')        
            with pytest.raises(ValueError):
                ha.get_user_permission()

    @pytest.mark.usefixtures("Mock API request / response")
    class TestRequestOauthToken():
        
        def test_updates_oauth_token_property_with_access_token(self):
            ha = HandleAuthorisation("user id")
            
            ha.request_oauth_token()
            
            assert ha.oauth_token == "0354489231f6a874331aer4927569297c7fea4d5"

    @pytest.mark.skip
    class TestGetOauthToken():
        
        @property
        def env_path(self):
            return self.pytest_fixture_env_path
        
        @pytest.fixture(autouse=True)
        def before_each(self, remove_env_file: Callable[[str], None]):
            remove_env_file(self.env_path)

        def test_gets_an_oauth_token_and_updates_env_file(self):
            ha = HandleAuthorisation("user id")
            
            ha.get_oauth_token()
            
            env_dict = dotenv.dotenv_values(self.env_path)
            
            assert env_dict["CLIENT_TOKEN"] != None
    
    ### request_oauth_token
    # updates oauth_token property with access_token
    # invokes set_dotenv_file with refresh__token
    # Returns an access_token string
    
    ### get_oauth_token
    # if .env file is missing, invokes get_user_permission
    # if .env file is missing, creates valid .env file
    # if .env file is old, invokes load_dotenv_file
    # if .env file is old, invokes request_oauth_token with refresh_token
    # if .env file is recent, invokes load_dotenv_file
    # if .env file is recent, returns oauth_token
