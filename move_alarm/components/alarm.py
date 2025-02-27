import threading
import time
from datetime import datetime
from move_alarm.contexts import use_context
from move_alarm import components
import move_alarm.datatypes as datatype

lock = threading.Lock()


class Alarm:
    _sounds: datatype.Sounds = components.Sounds()
    __time: datetime = datetime.fromtimestamp(0)
    __stop_alarm: bool = False
    __lock = None

    @property
    def is_set(self) -> bool:
        alarm_threads = [
            thread for thread in threading.enumerate() if thread.name == "MoveAlarm"
        ]

        return len(alarm_threads) > 0

    @property
    def time(self) -> datetime:
        return self.__time

    @property
    def sounds(self) -> datatype.Sounds:
        return self._sounds

    def set_alarm(self, snooze: bool = False) -> datetime:
        if self.is_set and not snooze:
            return self.__time

        config = use_context().config

        interval = (
            config.snooze_duration.seconds if snooze else config.wait_duration.seconds
        )

        set_alarm = threading.Thread(target=self.thread_alarm, args=[interval])
        set_alarm.name = "MoveAlarm"
        set_alarm.start()

        self.__time = datetime.now() + config.wait_duration

        return self.__time

    def thread_alarm(self, interval) -> None:
        print(self.__stop_alarm)
        for _ in range(0, interval):
            with lock:
                if self.__stop_alarm:
                    print("Stopping early!")
                    self.__stop_alarm = False
                    return

            time.sleep(1)

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

    def remove_alarm(self) -> bool:
        print("remove called")
        for thread in threading.enumerate():
            if thread.name == "MoveAlarm":
                with lock:
                    self.__stop_alarm = True
                print(f"__stop_alarm set to {self.__stop_alarm}")
