from os import path
from datetime import datetime
from random import randint
import dotenv

class HandleAuthorisation():
    
    @property
    def user_id(self) -> str:
        return self.__user_id
    
    @user_id.setter
    def user_id(self, id: str) -> None:
        if type(id) == str:
            self.__user_id = id
        else:
            raise TypeError("user_id must be a string")
    
    @property
    def oauth_token(self) -> str | None:
        return self.__oauth_token
    
    @oauth_token.setter
    def oauth_token(self, token: str) -> None:
        self.__oauth_token = token
    
    def __init__(self, user_id: str) -> None:
        self.user_id: str = user_id
        self._state: str | None = None
        self.oauth_token: str | None = None
        
        self.__env_path: str = path.join(path.dirname(__file__)[:-5], ".env")
    
    def is_dotenv_file_recent(self) -> bool:
        try:
            modded_unix = path.getmtime(self.__env_path)
        except FileNotFoundError:
            return False
        
        env_modified_time: datetime = datetime.fromtimestamp(modded_unix)
        now: datetime = datetime.now()
        time_since_modifying = now - env_modified_time
        
        return time_since_modifying.days < 1
    
    def generate_state(self) -> str:
        output: str = ""
        alphabet: list[str] = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
        
        for _ in range(0,randint(8,12)):
            random_int: int = randint(0,25)
            
            if random_int < 9:
                output += str(random_int)
            else:
                index: int = randint(0,25)
                case: int = randint(0, 1)
                if case == 0:
                    output += alphabet[index]
                else:
                    output += alphabet[index].upper()

        return output
    
    def set_dotenv_file(self, client_token: str) -> bool:
        if self.is_dotenv_file_recent() == False:
            state = self.generate_state()
            
            with open(self.__env_path, "w") as file:
                file.write(f"CLIENT_ID={self.user_id}\n" + \
                           f"CLIENT_STATE={state}\n" + \
                           f"CLIENT_TOKEN={client_token}")
        return True
    
    def load_dotenv_file(self) -> bool:
        if self.is_dotenv_file_recent() == False:
            raise OSError(f"{self.__env_path} could not be found OR is more than 24 hours old")
        
        env_dict: dict[str, str | None] = dotenv.dotenv_values(self.__env_path)
        
        self._state = env_dict["CLIENT_STATE"]
        self.oauth_token = env_dict["CLIENT_TOKEN"]
        
        return True
    
    def get_oauth_token(self):
        pass