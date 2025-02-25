from dataclasses import dataclass
import move_alarm.types as datatype


@dataclass
class Contexts:
    auth: datatype.OauthObject
    config: datatype.Config
