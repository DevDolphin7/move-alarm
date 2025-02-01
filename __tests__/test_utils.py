import pytest, os
import dotenv
from src.utils.utils import HandleAuthorisation

class TestHandleAuthorisation():

    class TestProperties():
        def test_has_property_user_id(self):
            ha = HandleAuthorisation("")
            assert isinstance(ha.user_id, str)
            
        def test_has_property_oauth_token(self):
            ha = HandleAuthorisation("")
            assert isinstance(ha.oauth_token, str)
    
        def test_invoking_with_string_sets_user_id(self):
            ha = HandleAuthorisation("user id")
            assert ha.user_id == "user id"
            
        def test_invoking_with_other_data_types_raises_error(self):
            with pytest.raises(TypeError):
                ha = HandleAuthorisation(True)

    class TestCheckDotenvFile():
        
        @property
        def env_path(self):
            return os.path.join(os.path.dirname(__file__)[:-9], ".", "src", ".env")
    
        def test_returns_true_if_env_file_created_in_last_24_hours(self):
            """ If .env file is older than 1 day, returns false.
                This isn't really testable for fresh installs!"""
            ha = HandleAuthorisation("user id")
            
            with open(self.env_path, "w") as file:
                file.write("")

            assert ha.check_dotenv_file() == True
            
        def test_returns_false_if_env_file_doesnt_exist(self):
            ha = HandleAuthorisation("user id")
            
            os.remove(self.env_path)
    
            assert ha.check_dotenv_file() == False

    class TestSetDotenvFile():
        
        @property
        def env_path(self):
            return os.path.join(os.path.dirname(__file__)[:-9], ".", "src", ".env")
        
        @property
        def valid_env_vars(self):
            return ["CLIENT_ID", "CLIENT_STATE", "CLIENT_TOKEN"]
        
        def test_creates_a_env_file(self):
            ha = HandleAuthorisation("user id")
            
            if os.path.exists(self.env_path):
                os.remove(self.env_path)
                
            ha.set_dotenv_file("id", "token")
            
            assert os.path.exists(self.env_path) == True
            
        def test_env_file_contains_correct_variables(self):
            ha = HandleAuthorisation("user id")
            
            ha.set_dotenv_file("id", "token")
            
            for valid_env_var in self.valid_env_vars:
                pass###################
                
            actual_values = dotenv.dotenv_values(self.env_path)
                
    ### set_dotenv_file
    # creates .env file
    # .env file contains CLIENT_ID, CLIENT_STATE and CLIENT_TOKEN
    # Doesn't modify an existing .env file that was modified within 24 hours
    # returns true if .env file modified within last 24 hours
    # returns false on error
    
    ### get_oauth_token
    # gets an oauth_token and updates .env file
    # updates oauth_token property
    # returns oauth_token on success
    # returns an error message on failure
