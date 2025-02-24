import os
from move_alarm.utils.oauth import HandleAuthorisation
from move_alarm.utils.config import Configuration
from move_alarm.types.contexts import Contexts

cache: Contexts | None = None


def use_context() -> Contexts:
    global cache

    if cache != None:
        return cache

    config_path = os.path.join(os.path.dirname(__file__)[:-8], "config.ini")

    cache = Contexts(HandleAuthorisation(), Configuration(config_path))

    return cache
