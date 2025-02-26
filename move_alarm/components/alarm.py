import threading
import time
from datetime import datetime
from move_alarm.contexts import use_context
from move_alarm import components
import move_alarm.datatypes as datatype


class Alarm:
    _sounds: datatype.Sounds = components.Sounds()
    __is_set: bool = False
    __time: datetime = datetime.fromtimestamp(0)

    @property
    def is_set(self) -> bool:
        return self.__is_set

    @property
    def time(self) -> datetime:
        return self.__time

    @property
    def sounds(self) -> datatype.Sounds:
        return self._sounds

    def set_alarm(self, snooze: bool = False) -> datetime:
        config = use_context().config

        interval = (
            config.snooze_duration.seconds if snooze else config.wait_duration.seconds
        )

        set_alarm = threading.Thread(target=self.thread_alarm, args=[interval])
        set_alarm.name = "MoveAlarm"
        set_alarm.start()

        self.__is_set = True
        self.__time = datetime.now() + config.wait_duration

        return self.__time

    def thread_alarm(self, interval) -> None:
        time.sleep(interval)

        self.sounds.play_sound()

    def snooze_alarm(self) -> datetime:
        if not self.is_set:
            raise datatype.AlarmNotSetError(
                "Please set the alarm first using .set_alarm()"
            )

        config = use_context().config

        if self.sounds.is_playing is False:
            self.__time = self.__time + config.snooze_duration
        else:
            self.sounds.stop_sound()
            self.set_alarm(snooze=True)

        return self.time
