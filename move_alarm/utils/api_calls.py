import webbrowser, requests, random
from move_alarm.types.sounds import SoundListResponse, SoundResultDict


def open_browser_to_api_auth(client_id: str, state: str | None = "") -> None:
    url = (
        "https://freesound.org/apiv2/oauth2/authorize/?"
        + f"client_id={client_id}&response_type=code&state={state}"
    )
    webbrowser.open(url)


def get_api_token(url: str) -> requests.Response:
    return requests.get(url)


def search_for_sounds(token: str, themes: list[str] = []) -> list[SoundResultDict]:
    url: str = (
        "https://freesound.org/apiv2/search/text/?"
        + "filter=(duration:[30%20TO%20210]%20AND%20type:wav)"
    )

    if len(themes) > 0:
        url = url[:-1] + "%20AND%20description:("

        url += "%20OR%20".join([theme for theme in themes]) + "))"

    url += "&fields=id,url,name,description,download,license"

    response = requests.get(url, headers={"Authorization": f"Bearer {token}"})

    if response.status_code == 200:
        result: SoundListResponse = response.json()
        return result["results"]

    raise ConnectionError(response.text)
