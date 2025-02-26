from dataclasses import dataclass
import move_alarm.datatypes as datatype


@dataclass
class Contexts:
    auth: datatype.OauthObject
    config: datatype.Config
