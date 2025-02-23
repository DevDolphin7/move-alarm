from move_alarm.utils.oauth import HandleAuthorisation
from move_alarm.utils.config import Configuration
from move_alarm.types.contexts import Contexts

cache: Contexts | None = None


def use_context() -> Contexts:
    global cache

    if cache != None:
        return cache

    cache = Contexts(HandleAuthorisation(), Configuration())

    return cache
