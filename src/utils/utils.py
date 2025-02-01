from os import path
from datetime import datetime

class HandleAuthorisation():
    
    @property
    def user_id(self) -> str:
        return self._user_id
    
    @user_id.setter
    def user_id(self, id: str) -> None:
        if type(id) == str:
            self._user_id = id
        else:
            raise TypeError("user_id must be a string")
    
    @property
    def oauth_token(self) -> str:
        return self._oauth_token
    
    @oauth_token.setter
    def oauth_token(self, token: str) -> None:
        self._oauth_token = token
    
    def __init__(self, user_id: str) -> None:
        self.user_id = user_id
        self.oauth_token = ""
        
        self.__env_path = path.join(path.dirname(__file__)[:-5], ".env")
    
    def check_dotenv_file(self) -> bool:
        try:
            modded_unix = path.getmtime(self.__env_path)
        except FileNotFoundError:
            return False
        
        env_modified_time: datetime = datetime.fromtimestamp(modded_unix)
        now: datetime = datetime.now()
        time_since_modifying = now - env_modified_time
        
        return time_since_modifying.days < 1
    
    def set_dotenv_file(self, client_id, client_token):
        with open(self.__env_path, "w") as file:
            file.write("")