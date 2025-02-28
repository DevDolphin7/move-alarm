import os
import threading
from time import sleep
from datetime import datetime, timedelta
import pytest, pytest_mock
from move_alarm.components.alarm import Alarm
import move_alarm.datatypes as datatype


class TestAlarm:

    @property
    def wav_directory(self) -> str:
        try:
            return self._wav_directory
        except:
            self._wav_directory = os.path.join(
                os.path.dirname(__file__)[:-9], "move_alarm", "assets"
            )
            return self._wav_directory

    @property
    def mock_config(self) -> datatype.Config:
        return datatype.Config(
            wait_duration=timedelta(minutes=3),
            snooze_duration=timedelta(minutes=2),
            reminder_text="Time to move!",
            wav_directory=self.wav_directory,
            api_enabled=True,
            sound_themes=["piano", "guitar"],
        )

    @pytest.fixture(name="Mock Context")
    def mock_context(self, monkeypatch: pytest.MonkeyPatch):
        class MockAuth:
            def get_token(self):
                return "mock token"

        mock_contexts = datatype.Contexts(MockAuth(), self.mock_config)

        monkeypatch.setattr(
            "move_alarm.components.alarm.use_context", lambda: mock_contexts
        )

    @pytest.fixture(name="Mock time.sleep")
    def mock_time_sleep(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr(
            "time.sleep",
            lambda *args: None,
        )

    @pytest.fixture
    def wait_for_separate_threads(self):
        def _wait_for_separate_threads():
            while len(threading.enumerate()) > 1:
                # Used to stop 1 CPU processing at max speed on test error (python GIL)
                sleep(0.001)

        return _wait_for_separate_threads

    @pytest.fixture(name="Mock sounds.play_sound to keep thread alive 1ms")
    def mock_sounds_play_sound_keep_thread_alive_1_ms(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        """1 ms used as a balence between keeping the thread alive and fast testing"""

        monkeypatch.setattr(
            Alarm._sounds,
            "play_sound",
            lambda: sleep(0.001),
        )

    @pytest.fixture(name="Mock sounds.is_playing")
    def mock_sounds_is_playing(self, monkeypatch: pytest.MonkeyPatch):
        class MockPlayObject:
            def stop(self):
                return

        monkeypatch.setattr(
            Alarm._sounds,
            "_play_objects",
            [MockPlayObject()],
        )

    @pytest.fixture(name="Mock Alarm.is_set to True")
    def mock_alarm_is_set(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr(Alarm, "is_set", True)

    @pytest.fixture(name="Mock invoking threading.Thread")
    def mock_threading_thread(self, monkeypatch: pytest.MonkeyPatch):
        def _mock_threading_thread(self):
            thread = threading.Thread()
            thread.name = "MoveAlarm"
            thread.start()

        monkeypatch.setattr(
            "threading.Thread", lambda *args, **kwargs: _mock_threading_thread
        )

    @pytest.fixture
    def mock_set_alarm(self, monkeypatch: pytest.MonkeyPatch):
        def mock_alarm_thread(alarm_self: Alarm):
            alarm_self._time = datetime.now() + self.mock_config.wait_duration

            thread = threading.Thread(target=alarm_self.thread_alarm, args=[5])
            thread.name = "MoveAlarm"
            thread.start()

        monkeypatch.setattr(
            Alarm,
            "set_alarm",
            mock_alarm_thread,
        )

        monkeypatch.setattr(
            "time.sleep",
            lambda *args: sleep(0.001),
        )

        return lambda alarm: alarm.set_alarm()

    @pytest.fixture
    def mock_remove_alarm(self, monkeypatch: pytest.MonkeyPatch):
        def mock_remove_thread(alarm_self: Alarm):
            if alarm_self.sounds.is_playing:
                return alarm_self.sounds.stop_sound()

            for thread in threading.enumerate():
                if thread.name == "MoveAlarm":
                    with alarm_self._lock:
                        alarm_self._stop_alarm = True

        monkeypatch.setattr(
            Alarm,
            "remove_alarm",
            mock_remove_thread,
        )

        return lambda alarm: alarm.remove_alarm()

    @pytest.fixture
    def mock_snooze_alarm(self, monkeypatch: pytest.MonkeyPatch):
        def mock_snooze(alarm_self: Alarm):
            alarm_self._time = alarm_self._time + self.mock_config.snooze_duration

        monkeypatch.setattr(
            Alarm,
            "snooze_alarm",
            mock_snooze,
        )

        return lambda alarm: alarm.snooze_alarm()

    @pytest.mark.usefixtures("Mock Context")
    class TestInitiation:
        def test_sets_is_set_to_false_on_initialisation(self):
            alarm = Alarm()

            assert alarm.is_set is False

        def test_creates_sounds_instance_on_initialisation(self):
            alarm = Alarm()

            assert isinstance(alarm.sounds, datatype.Sounds) is True

        def test_sets_alarm_time_to_unix_0_on_initialisation(self):
            alarm = Alarm()

            assert isinstance(alarm.time, datetime) is True
            assert alarm.time == datetime.fromtimestamp(0)

    @pytest.mark.usefixtures("Mock Context")
    class TestIsSet:
        def test_returns_true_if_sound_is_waiting_to_be_played(
            self, mock_set_alarm, mock_remove_alarm, wait_for_separate_threads
        ):
            alarm = Alarm()

            assert alarm.is_set is False

            mock_set_alarm(alarm)
            was_set = alarm.is_set

            mock_remove_alarm(alarm)
            wait_for_separate_threads()

            assert was_set is True
            assert alarm.is_set is False

        def test_returns_true_if_alarm_snoozed_and_still_waiting_to_play(
            self,
            mock_set_alarm,
            mock_snooze_alarm,
            mock_remove_alarm,
            wait_for_separate_threads,
        ):
            alarm = Alarm()

            assert alarm.is_set is False

            mock_set_alarm(alarm)

            mock_snooze_alarm(alarm)
            set_after_snooze = alarm.is_set

            mock_remove_alarm(alarm)
            wait_for_separate_threads()

            assert set_after_snooze is True
            assert alarm.is_set is False

        @pytest.mark.usefixtures("Mock sounds.play_sound to keep thread alive 1ms")
        def test_returns_true_if_alarm_is_currently_playing(
            self,
            monkeypatch: pytest.MonkeyPatch,
            mock_set_alarm,
            wait_for_separate_threads,
        ):
            monkeypatch.setattr(
                Alarm._sounds,
                "_play_objects",
                [None],
            )

            alarm = Alarm()

            mock_set_alarm(alarm)
            was_set = alarm.is_set

            wait_for_separate_threads()

            assert alarm.sounds.is_playing is True
            assert was_set is True

        def test_returns_false_if_no_alarm_is_waiting_or_currently_playing(
            self, mock_set_alarm, mock_remove_alarm, wait_for_separate_threads
        ):
            alarm = Alarm()

            assert alarm.is_set is False

            mock_set_alarm(alarm)
            was_set = alarm.is_set
            mock_remove_alarm(alarm)
            wait_for_separate_threads()

            assert was_set is True
            assert alarm.is_set is False

    @pytest.mark.usefixtures("Mock Context")
    class TestSetAlarm:

        @property
        def wav_directory(self) -> str:
            try:
                return self._wav_directory
            except:
                self._wav_directory = TestAlarm.wav_directory.fget(self)
                return self._wav_directory

        @property
        def config(self) -> datatype.Config:
            return TestAlarm.mock_config.fget(self)

        @pytest.mark.usefixtures("Mock time.sleep")
        @pytest.mark.usefixtures("Mock sounds.play_sound to keep thread alive 1ms")
        def test_updates_is_set_to_true(self, wait_for_separate_threads):
            alarm = Alarm()

            assert alarm.is_set is False

            alarm.set_alarm()
            was_set = alarm.is_set

            wait_for_separate_threads()

            assert was_set is True

        @pytest.mark.usefixtures("Mock sounds.play_sound to keep thread alive 1ms")
        def test_waits_for_interval_without_halting_program(
            self, mocker: pytest_mock.MockerFixture, wait_for_separate_threads
        ):
            mock_time_sleep = mocker.patch("time.sleep")

            magic_mock = mocker.MagicMock()
            magic_mock.attach_mock(mock_time_sleep, "time_sleep")

            alarm = Alarm()
            alarm.set_alarm()
            was_set = alarm.is_set

            wait_for_separate_threads()

            assert was_set is True

            expected_calls = [
                mocker.call.time_sleep(1)
                for _ in range(0, self.config.wait_duration.seconds)
            ]
            magic_mock.assert_has_calls(expected_calls)

        def test_after_wait_duration_invokes_sounds_play_sound(
            self, mocker: pytest_mock.MockerFixture, wait_for_separate_threads
        ):
            mock_time_sleep = mocker.patch("time.sleep")
            mock_play_sound = mocker.patch(
                "move_alarm.components.Alarm._sounds.play_sound"
            )

            magic_mock = mocker.MagicMock()
            magic_mock.attach_mock(mock_time_sleep, "time_sleep")
            magic_mock.attach_mock(mock_play_sound, "play_sound")

            alarm = Alarm()
            alarm.set_alarm()
            wait_for_separate_threads()

            mock_time_sleep.assert_called()
            mock_play_sound.assert_called_once()

            expected_time_sleep_calls = [
                mocker.call.time_sleep(1)
                for _ in range(0, self.config.wait_duration.seconds)
            ]

            magic_mock.assert_has_calls(
                [
                    *expected_time_sleep_calls,
                    mocker.call.play_sound(),
                ],
                any_order=False,
            )

        @pytest.mark.usefixtures("Mock time.sleep")
        @pytest.mark.usefixtures("Mock sounds.play_sound to keep thread alive 1ms")
        def test_returns_datetime_of_when_the_alarm_will_sound(
            self, wait_for_separate_threads
        ):
            alarm = Alarm()
            expected = datetime.now() + self.config.wait_duration

            alarm_time = alarm.set_alarm()
            wait_for_separate_threads()

            assert isinstance(alarm_time, datetime) is True

            formatted_output = alarm_time.strftime("%d/%m/%Y %H:%M:%S")
            formatted_expected = expected.strftime("%d/%m/%Y %H:%M:%S")

            assert formatted_output == formatted_expected

        @pytest.mark.usefixtures("Mock time.sleep")
        @pytest.mark.usefixtures("Mock sounds.play_sound to keep thread alive 1ms")
        def test_updates_time_property_with_datetime(self, wait_for_separate_threads):
            alarm = Alarm()

            assert alarm.time == datetime.fromtimestamp(0)

            expected = datetime.now() + self.config.wait_duration

            alarm.set_alarm()
            wait_for_separate_threads()

            formatted_time = alarm.time.strftime("%d/%m/%Y %H:%M:%S")
            formatted_expected = expected.strftime("%d/%m/%Y %H:%M:%S")

            assert formatted_time == formatted_expected

        @pytest.mark.usefixtures("Mock time.sleep")
        @pytest.mark.usefixtures("Mock sounds.play_sound to keep thread alive 1ms")
        def test_if_alarm_is_already_set_only_returns_current_set_time(
            self, wait_for_separate_threads
        ):
            alarm = Alarm()

            expected = alarm.set_alarm()
            second_call = alarm.set_alarm()

            wait_for_separate_threads()

            assert second_call == expected

    @pytest.mark.usefixtures("Mock Context")
    class TestSnoozeAlarm:

        @property
        def wav_directory(self) -> str:
            try:
                return self._wav_directory
            except:
                self._wav_directory = TestAlarm.wav_directory.fget(self)
                return self._wav_directory

        @property
        def config(self) -> datatype.Config:
            return TestAlarm.mock_config.fget(self)

        def test_if_alarm_is_not_set_raise_alarm_not_set_error(self):
            alarm = Alarm()

            assert alarm.is_set is False

            with pytest.raises(datatype.AlarmNotSetError):
                alarm.snooze_alarm()

        @pytest.mark.usefixtures("Mock Alarm.is_set to True")
        def test_if_sound_not_playing_play_sound_not_invoked_until_wait_and_snooze_duration(
            self,
        ):
            alarm = Alarm()

            assert alarm.sounds.is_playing is False

            non_snoozed_time = alarm.time
            alarm.snooze_alarm()
            snoozed_time = alarm.time

            delta = snoozed_time - non_snoozed_time
            assert delta.seconds == self.config.snooze_duration.seconds

        @pytest.mark.usefixtures("Mock Alarm.is_set to True")
        @pytest.mark.usefixtures("Mock time.sleep")
        @pytest.mark.usefixtures("Mock sounds.play_sound to keep thread alive 1ms")
        @pytest.mark.usefixtures("Mock sounds.is_playing")
        def test_if_sound_is_playing_invokes_stop_sound(
            self, mocker: pytest_mock.MockerFixture, wait_for_separate_threads
        ):
            mock_stop_sound = mocker.patch(
                "move_alarm.components.Alarm._sounds.stop_sound"
            )

            alarm = Alarm()
            was_playing = alarm.sounds.is_playing

            alarm.snooze_alarm()

            wait_for_separate_threads()

            assert was_playing is True
            mock_stop_sound.assert_called_once()

        @pytest.mark.usefixtures("Mock Alarm.is_set to True")
        @pytest.mark.usefixtures("Mock sounds.is_playing")
        def test_if_sound_is_playing_sound_plays_after_snooze_duration(
            self, mocker: pytest_mock.MockerFixture, wait_for_separate_threads
        ):
            mock_thread_alarm = mocker.patch("move_alarm.components.Alarm.thread_alarm")

            alarm = Alarm()
            was_playing = alarm.sounds.is_playing

            alarm.snooze_alarm()
            wait_for_separate_threads()

            assert was_playing is True

            mock_thread_alarm.assert_called_once_with(
                self.config.snooze_duration.seconds
            )

        @pytest.mark.usefixtures("Mock Alarm.is_set to True")
        def test_returns_the_new_datetime_the_sound_will_alarm(self):
            alarm = Alarm()

            assert alarm.is_set is True
            assert alarm.sounds.is_playing is False

            original_time = alarm.time
            snoozed_time = alarm.snooze_alarm()

            delta = snoozed_time - original_time
            assert delta.seconds == self.config.snooze_duration.seconds

        @pytest.mark.usefixtures("Mock Alarm.is_set to True")
        def test_updates_the_time_property_with_new_alarm_datetime(self):
            alarm = Alarm()

            assert alarm.is_set is True
            assert alarm.sounds.is_playing is False

            original_time = alarm.time
            alarm.snooze_alarm()

            delta = alarm.time - original_time
            assert delta.seconds == self.config.snooze_duration.seconds

    @pytest.mark.usefixtures("Mock Context")
    class TestRemoveAlarm:

        @property
        def wav_directory(self) -> str:
            try:
                return self._wav_directory
            except:
                self._wav_directory = TestAlarm.wav_directory.fget(self)
                return self._wav_directory

        @property
        def config(self) -> datatype.Config:
            return TestAlarm.mock_config.fget(self)

        def test_if_an_alarm_is_set_removes_it_and_updates_is_set_property(
            self, mock_set_alarm, wait_for_separate_threads
        ):
            alarm = Alarm()
            mock_set_alarm(alarm)

            assert alarm.is_set is True
            assert alarm._stop_alarm is False

            alarm.remove_alarm()
            thread_to_be_stopped = alarm._stop_alarm

            wait_for_separate_threads()

            assert thread_to_be_stopped is True
            assert alarm._stop_alarm is False
            assert alarm.is_set is False

        def test_return_bool_false_if_no_alarm_is_set(self):
            alarm = Alarm()

            alarm_removed = alarm.remove_alarm()

            assert alarm_removed is False

        def test_return_bool_tru_if_an_alarm_was_removed(
            self, mock_set_alarm, wait_for_separate_threads
        ):
            alarm = Alarm()
            mock_set_alarm(alarm)

            alarm_removed = alarm.remove_alarm()

            wait_for_separate_threads()

            assert alarm_removed is True

        def test_if_alarm_removed_updates_time_property_to_unix_0(
            self, mock_set_alarm, wait_for_separate_threads
        ):
            alarm = Alarm()

            expected_set_time = datetime.now() + self.config.wait_duration
            expected_removed_time = datetime.fromtimestamp(0)

            mock_set_alarm(alarm)

            set_time = alarm.time

            alarm.remove_alarm()

            wait_for_separate_threads()

            str_expected_set_time = expected_set_time.strftime("%d/%m/%Y %H:%M:%S")
            str_set_time = set_time.strftime("%d/%m/%Y %H:%M:%S")
            str_expected_removed = expected_removed_time.strftime("%d/%m/%Y %H:%M:%S")
            str_removed = alarm.time.strftime("%d/%m/%Y %H:%M:%S")

            assert str_set_time == str_expected_set_time
            assert str_removed == str_expected_removed

        def test_if_an_alarm_was_removed_informs_the_user(
            self,
            mock_set_alarm,
            wait_for_separate_threads,
            capfd: pytest.CaptureFixture,
        ):
            alarm = Alarm()
            mock_set_alarm(alarm)

            alarm.remove_alarm()

            wait_for_separate_threads()

            out, err = capfd.readouterr()

            assert out == "Alarm removed\n"

        @pytest.mark.usefixtures("Mock sounds.is_playing")
        def test_if_a_sounds_is_currently_playing_invokes_stop_sound_and_returns_result(
            self, mocker: pytest_mock.MockerFixture, wait_for_separate_threads
        ):
            mock_stop_sound = mocker.patch(
                "move_alarm.components.Alarm._sounds.stop_sound",
                return_value="Result from stop_sound()",
            )

            alarm = Alarm()

            assert alarm.sounds.is_playing is True

            sounding_alarm_removed = alarm.remove_alarm()

            wait_for_separate_threads()

            mock_stop_sound.assert_called_once()
            assert sounding_alarm_removed == "Result from stop_sound()"
