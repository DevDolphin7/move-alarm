import threading
import time
from datetime import datetime
from move_alarm.contexts import use_context
from move_alarm import components
import move_alarm.datatypes as datatype


class Alarm:
    _sounds: datatype.Sounds = components.Sounds()
    _stop_alarm: bool = False
    _time: datetime = datetime.fromtimestamp(0)
    _lock = threading.Lock()

    @property
    def is_set(self) -> bool:
        alarm_threads = [
            thread for thread in threading.enumerate() if thread.name == "MoveAlarm"
        ]

        return len(alarm_threads) > 0

    @property
    def time(self) -> datetime:
        return self._time

    @property
    def sounds(self) -> datatype.Sounds:
        return self._sounds

    def set_alarm(self, snooze: bool = False) -> datetime:
        if self.is_set and not snooze:
            return self._time

        config = use_context().config

        interval = (
            config.snooze_duration.seconds if snooze else config.wait_duration.seconds
        )

        set_alarm = threading.Thread(target=self.thread_alarm, args=[interval])
        set_alarm.name = "MoveAlarm"
        set_alarm.start()

        self._time = datetime.now() + config.wait_duration

        return self._time

    def thread_alarm(self, interval) -> None:
        for _ in range(0, interval):
            with self._lock:
                if self._stop_alarm:
                    self._stop_alarm = False
                    self._time = datetime.fromtimestamp(0)
                    print("Alarm removed")
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
            self._time = self._time + config.snooze_duration
        else:
            self.sounds.stop_sound()
            self.set_alarm(snooze=True)

        return self.time

    def remove_alarm(self) -> bool:
        if self.sounds.is_playing:
            return self.sounds.stop_sound()

        for thread in threading.enumerate():
            if thread.name == "MoveAlarm":
                with self._lock:
                    self._stop_alarm = True
                    return True
        return False
