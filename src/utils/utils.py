from os import path
from datetime import datetime
from random import randint
from time import sleep
import threading, webbrowser, re
import dotenv, requests


class HandleAuthorisation:

    @property
    def client_id(self) -> str:
        return self.__client_id

    @client_id.setter
    def client_id(self, id: str) -> None:
        if type(id) == str:
            self.__client_id = id
        else:
            raise TypeError("client_id must be a string")

    @property
    def oauth_code(self) -> str | None:
        return self.__oauth_code

    @oauth_code.setter
    def oauth_code(self, code: str | None) -> None:
        if code != None:
            regex_result = re.fullmatch("^[A-Z0-9]{25,45}$", code, flags=re.I)
            if isinstance(regex_result, re.Match) == False:
                raise (
                    ValueError(
                        "Please enter a valid Freesound authorisation code, see https://freesound.org/docs/api/authentication.html"
                    )
                )
        self.__oauth_code = code

    def __init__(self, client_id: str = "Load from .env file") -> None:
        self.__env_path: str = path.join(path.dirname(__file__)[:-5], ".env")

        if client_id != "Load from .env file":
            self.client_id = client_id
        else:
            self.load_dotenv_file()

        self._state: str | None = None
        self.oauth_code = None
        self.oauth_token: str | None = None

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
        state = self.generate_state()

        with open(self.__env_path, "w") as file:
            file.write(
                f"CLIENT_ID={self.client_id}\n"
                + f"CLIENT_STATE={state}\n"
                + f"REFRESH_TOKEN={client_token}"
            )
        return True

    def load_dotenv_file(self) -> str:
        output = "recent" if self.is_dotenv_file_recent() else "old"

        env_dict: dict[str, str | None] = dotenv.dotenv_values(self.__env_path)

        self.client_id = str(env_dict["CLIENT_ID"])
        self._state = env_dict["CLIENT_STATE"]
        self.oauth_token = env_dict["REFRESH_TOKEN"]

        return output

    def get_user_permission(self) -> bool:
        url = f"https://freesound.org/apiv2/oauth2/authorize/?client_id={self.client_id}&response_type=code&state={self._state}"
        browser_thread = threading.Thread(target=lambda: self.open_browser(url))
        browser_thread.start()

        browser_thread.join(timeout=15.0)
        if browser_thread.is_alive():
            raise TimeoutError(
                "Opening default browser timed out, user permissions could not be granted"
            )
        sleep(1)

        self.oauth_code = input("Please enter your authorisation code: ")

        return True

    def open_browser(self, url: str) -> None:
        webbrowser.open(url)

    def request_oauth_token(self) -> str | None:
        url = (
            "https://devdolphin7.netlify.app/.netlify/functions/move-alarm?"
            + f"client_id={self.client_id}"
        )
        if self.oauth_code != None:
            url += f"&code={self.oauth_code}"
        else:
            url += f"&token={self.oauth_token}"

        token_response = requests.get(url)

        match token_response.status_code:
            case 200:
                token = token_response.json()
                self.oauth_token = token["access_token"]

                self.set_dotenv_file(token["refresh_token"])
                return self.oauth_token
            case 401 | 429:
                raise ConnectionRefusedError(token_response.text)
            case _:
                raise ConnectionError(token_response.text)

    def get_token(self) -> str | None:
        try:
            self.is_dotenv_file_recent()
        except FileNotFoundError:
            if self.get_user_permission():
                self.set_dotenv_file("None")
            else:
                return None

        self.load_dotenv_file()

        return self.request_oauth_token()
