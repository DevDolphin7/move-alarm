from move_alarm import contexts


def get_auth_token():
    auth = contexts.use_context().auth
    token = auth.get_token()

    if token is None:
        raise ValueError("Unexpected error: Unable to get an access token")

    return token
