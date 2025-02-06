from os import path
from datetime import datetime
from random import randint
from time import sleep
import threading, webbrowser, re
import dotenv, requests


class HandleAuthorisation:

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
        modded_unix = path.getmtime(self.__env_path)
        env_modified_time: datetime = datetime.fromtimestamp(modded_unix)
        now: datetime = datetime.now()
        time_since_modifying = now - env_modified_time

        return time_since_modifying.days < 1

    def generate_state(self) -> str:
        output: str = ""
        alphabet: list[str] = [
            "a",
            "b",
            "c",
            "d",
            "e",
            "f",
            "g",
            "h",
            "i",
            "j",
            "k",
            "l",
            "m",
            "n",
            "o",
            "p",
            "q",
            "r",
            "s",
            "t",
            "u",
            "v",
            "w",
            "x",
            "y",
            "z",
        ]

        for _ in range(0, randint(8, 12)):
            random_int: int = randint(0, 25)

            if random_int < 9:
                output += str(random_int)
            else:
                index: int = randint(0, 25)
                case: int = randint(0, 1)
                if case == 0:
                    output += alphabet[index]
                else:
                    output += alphabet[index].upper()

        return output

    def set_dotenv_file(self, client_token: str) -> bool:
        try:
            recent_env_file = self.is_dotenv_file_recent()
        except FileNotFoundError:
            recent_env_file = False

        if recent_env_file == False:
            state = self.generate_state()

            with open(self.__env_path, "w") as file:
                file.write(
                    f"CLIENT_ID={self.user_id}\n"
                    + f"CLIENT_STATE={state}\n"
                    + f"CLIENT_TOKEN={client_token}"
                )
        return True

    def load_dotenv_file(self) -> bool:
        output = "recent" if self.is_dotenv_file_recent() else "old"

        env_dict: dict[str, str | None] = dotenv.dotenv_values(self.__env_path)

        self._state = env_dict["CLIENT_STATE"]
        self.oauth_token = env_dict["CLIENT_TOKEN"]

        return output

    def get_user_permission(self) -> bool:
        url = f"https://freesound.org/apiv2/oauth2/authorize/?client_id={self.user_id}&response_type=code&state={self._state}"
        browser_thread = threading.Thread(target=lambda: self.open_browser(url))
        browser_thread.start()

        browser_thread.join(timeout=15.0)
        if browser_thread.is_alive():
            raise TimeoutError(
                "Opening default browser timed out, user permissions could not be granted"
            )
        sleep(1)

        self._oauth_code = input("Please enter your authorisation code: ")

        regex_result = re.fullmatch("^[A-Z0-9]{40}$", self._oauth_code, flags=re.I)
        if isinstance(regex_result, re.Match) == False:
            raise (
                ValueError(
                    "Please enter a valid Freesound authorisation code, see https://freesound.org/docs/api/authentication.html"
                )
            )

        return True

    def open_browser(self, url: str) -> None:
        webbrowser.open(url)

    def request_oauth_token(self) -> str:
        token_response = requests.post(
            "https://freesound.org/apiv2/oauth2/access_token/",
            data={
                "client_id": self.user_id,
                "client_secret": "self.__client_secret",
                "grant_type": "authorization_code",
                "code": self._oauth_code,
            },
        )

        token = token_response.json()
        self.oauth_token = token["access_token"]
