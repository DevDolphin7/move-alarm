from utils.utils import HandleAuthorisation


def get_token():
    ha = HandleAuthorisation()

    token = ha.get_token()

    print(token)


get_token()
