from dataclasses import dataclass
from move_alarm.utils.oauth import HandleAuthorisation
from move_alarm.utils.config import Configuration


@dataclass
class Contexts:
    auth: HandleAuthorisation
    config: Configuration
