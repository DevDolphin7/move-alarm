import webbrowser, requests
import move_alarm.types as datatype


def open_browser_to_api_auth(client_id: str, state: str | None = "") -> None:
    url = (
        "https://freesound.org/apiv2/oauth2/authorize/?"
        + f"client_id={client_id}&response_type=code&state={state}"
    )
    webbrowser.open(url)


def get_api_token(url: str) -> requests.Response:
    return requests.get(url)


def search_for_sounds(
    token: str, themes: list[str] = []
) -> list[datatype.SoundResultDict]:
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
        result: datatype.SoundListResponse = response.json()
        return result["results"]

    raise ConnectionError(response.text)


def download_sound(token: str, url: str, new_path: str) -> bool:
    with requests.get(
        url, headers={"Authorization": f"Bearer {token}"}, stream=True
    ) as response:
        response.raise_for_status()

        with open(new_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

    return True
