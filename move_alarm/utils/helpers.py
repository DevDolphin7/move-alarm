from move_alarm.contexts import use_context


def get_auth_token():
    auth = use_context().auth
    token = auth.get_token()

    if token == None:
        raise ValueError("Unexpected error: Unable to get an access token")

    return token
