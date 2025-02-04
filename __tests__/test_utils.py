import pytest, os, re
import dotenv
from src.utils.utils import HandleAuthorisation

class TestHandleAuthorisation():

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

    class TestCheckDotenvFile():
        
        @property
        def env_path(self):
            return os.path.join(os.path.dirname(__file__)[:-9], "src", ".env")
    
        @pytest.fixture(autouse=True)
        def before_each(self):
            if os.path.exists(self.env_path):
                os.remove(self.env_path)
        
        def test_returns_true_if_env_file_created_in_last_24_hours(self):
            """ If .env file is older than 1 day, returns false.
                This isn't really testable for fresh installs!"""
            ha = HandleAuthorisation("user id")
            
            with open(self.env_path, "w") as file:
                file.write("")

            assert ha.is_dotenv_file_recent() == True
            
        def test_returns_false_if_env_file_doesnt_exist(self):
            ha = HandleAuthorisation("user id")
    
            assert ha.is_dotenv_file_recent() == False

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
            return os.path.join(os.path.dirname(__file__)[:-9], "src", ".env")
        
        @property
        def valid_env_vars(self):
            return ["CLIENT_ID", "CLIENT_STATE", "CLIENT_TOKEN"]
        
        @pytest.fixture(autouse=True)
        def before_each(self):
            if os.path.exists(self.env_path):
                os.remove(self.env_path)
        
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
            return os.path.join(os.path.dirname(__file__)[:-9], "src", ".env")
        
        @pytest.fixture(autouse=True)
        def before_each(self):
            if os.path.exists(self.env_path):
                os.remove(self.env_path)

        def test_if_file_is_recent_updates_state_and_oauth_with_value_from_env_file(self):
            ha = HandleAuthorisation("user id")
            ha.set_dotenv_file("token")
            
            env_dict = dotenv.dotenv_values(self.env_path)
            env_values = env_dict.values()
            
            ha.load_dotenv_file()
            state = ha._state
            oauth = ha.oauth_token
            
            assert state in env_values
            assert oauth in env_values
            
        def test_returns_true_on_success(self):
            """Returns false if file more than 24 hours old,
            can't test for that!"""
            
            ha = HandleAuthorisation("user id")
            ha.set_dotenv_file("token")
            
            assert ha.load_dotenv_file() == True
            
        def test_raises_error_if_env_file_missing_or_not_recent(self):
            ha = HandleAuthorisation("user id")
            
            with pytest.raises(OSError):
                ha.load_dotenv_file()

    class TestGetOauthToken():
        
        @property
        def env_path(self):
            return os.path.join(os.path.dirname(__file__)[:-9], "src", ".env")
        
        @pytest.fixture(autouse=True)
        def before_each(self):
            if os.path.exists(self.env_path):
                os.remove(self.env_path)

        def test_gets_an_oauth_token_and_updates_env_file(self):
            ha = HandleAuthorisation("user id")
            
            ha.get_oauth_token()
            
            env_dict = dotenv.dotenv_values(self.env_path)
            
            assert env_dict["CLIENT_TOKEN"] != None

    ### get_oauth_token
    # gets an oauth_token and updates .env file
    # updates oauth_token property
    # returns oauth_token on success
    # returns an error message on failure
