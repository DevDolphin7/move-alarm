import os
from move_alarm import utils
import move_alarm.types as datatype

cache: datatype.Contexts | None = None


def use_context() -> datatype.Contexts:
    global cache

    if cache != None:
        return cache

    config_path = os.path.join(os.path.dirname(__file__)[:-8], "config.ini")

    cache = datatype.Contexts(
        utils.HandleAuthorisation(), utils.Configuration(config_path)
    )

    return cache
