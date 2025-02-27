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
            wait_duration=timedelta(minutes=60),
            snooze_duration=timedelta(minutes=5),
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
        def long_non_threaded_io_process():
            sleep(5)

        monkeypatch.setattr(
            "time.sleep",
            lambda *args: long_non_threaded_io_process,
        )

    @pytest.fixture
    def wait_for_separate_threads(self):
        def _wait_for_separate_threads():
            while len(threading.enumerate()) > 1:
                # Used to stop 1 CPU processing at max speed on test error (python GIL)
                sleep(0.001)

        return _wait_for_separate_threads

    @pytest.fixture(name="Mock sounds.play_sound")
    def mock_sounds_play_sound(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.setattr(
            Alarm._sounds,
            "play_sound",
            lambda: print("Sound is playing!"),
        )

    @pytest.fixture(name="Mock sounds.play_sound to keep thread alive 10ms")
    def mock_sounds_play_sound_keep_thread_alive_10_ms(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        """10 ms used as a balence between keeping the thread alive and fast testing"""

        monkeypatch.setattr(
            Alarm._sounds,
            "play_sound",
            lambda: sleep(0.01),
        )

    @pytest.fixture(name="Mock sounds.play_sound to keep thread alive 1 hour")
    def mock_sounds_play_sound_keep_thread_alive_one_hour(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.setattr(
            Alarm._sounds,
            "play_sound",
            lambda: sleep(3600),
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

    @pytest.fixture(name="Mock invoking set_alarm")
    def mock_invoking_set_alarm(self, monkeypatch: pytest.MonkeyPatch):
        def keep_thread_alive():
            while True:
                # Used to stop 1 CPU processing at max speed on test error (python GIL)
                sleep(0.001)

        def _mock_invoking_set_alarm():
            set_mock_alarm = threading.Thread(target=keep_thread_alive)
            set_mock_alarm.name = "MoveAlarm"
            set_mock_alarm.start()
            set_mock_alarm.join()

        monkeypatch.setattr(Alarm, "set_alarm", _mock_invoking_set_alarm)

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
        @pytest.mark.usefixtures("Mock sounds.play_sound to keep thread alive 10ms")
        def test_updates_is_set_to_true(self, wait_for_separate_threads):
            alarm = Alarm()

            assert alarm.is_set is False

            alarm.set_alarm()
            set = alarm.is_set

            wait_for_separate_threads()

            assert set is True

        @pytest.mark.usefixtures("Mock sounds.play_sound to keep thread alive 10ms")
        def test_waits_for_interval_without_halting_program(
            self, mocker: pytest_mock.MockerFixture, wait_for_separate_threads
        ):
            mock_thread = mocker.patch("time.sleep")

            alarm = Alarm()
            alarm.set_alarm()
            alarm_was_set = alarm.is_set

            wait_for_separate_threads()

            assert alarm_was_set is True
            mock_thread.assert_called_once_with(
                self.config.wait_duration.total_seconds()
            )

        def test_after_wait_duration_invokes_sounds_play_sound(
            self, mocker: pytest_mock.MockerFixture, wait_for_separate_threads
        ):
            mock_thread = mocker.patch("time.sleep")
            mock_play_sound = mocker.patch(
                "move_alarm.components.Alarm._sounds.play_sound"
            )

            magic_mock = mocker.MagicMock()
            magic_mock.attach_mock(mock_thread, "time_sleep")
            magic_mock.attach_mock(mock_play_sound, "play_sound")

            alarm = Alarm()
            alarm.set_alarm()
            wait_for_separate_threads()

            mock_thread.assert_called_once()
            mock_play_sound.assert_called_once()

            magic_mock.assert_has_calls(
                [
                    mocker.call.time_sleep(self.config.wait_duration.total_seconds()),
                    mocker.call.play_sound(),
                ],
                any_order=False,
            )

        @pytest.mark.usefixtures("Mock time.sleep")
        @pytest.mark.usefixtures("Mock sounds.play_sound")
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
        @pytest.mark.usefixtures("Mock sounds.play_sound")
        def test_updates_time_property_with_datetime(self, wait_for_separate_threads):
            alarm = Alarm()

            assert alarm.time == datetime.fromtimestamp(0)

            expected = datetime.now() + self.config.wait_duration

            alarm.set_alarm()

            assert alarm.time is not None

            formatted_time = alarm.time.strftime("%d/%m/%Y %H:%M:%S")
            formatted_expected = expected.strftime("%d/%m/%Y %H:%M:%S")

            wait_for_separate_threads()

            assert formatted_time == formatted_expected

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
            assert delta.seconds == 300

        @pytest.mark.usefixtures("Mock Alarm.is_set to True")
        @pytest.mark.usefixtures("Mock time.sleep")
        @pytest.mark.usefixtures("Mock sounds.play_sound")
        @pytest.mark.usefixtures("Mock sounds.is_playing")
        def test_if_sound_is_playing_invokes_stop_sound(
            self, mocker: pytest_mock.MockerFixture
        ):
            mock_stop_sound = mocker.patch(
                "move_alarm.components.Alarm._sounds.stop_sound"
            )

            alarm = Alarm()
            assert alarm.sounds.is_playing is True

            alarm.snooze_alarm()

            mock_stop_sound.assert_called_once()

        @pytest.mark.usefixtures("Mock Alarm.is_set to True")
        @pytest.mark.usefixtures("Mock sounds.is_playing")
        def test_if_sound_is_playing_sound_plays_after_snooze_duration(
            self, mocker: pytest_mock.MockerFixture
        ):
            mock_thread_alarm = mocker.patch("move_alarm.components.Alarm.thread_alarm")

            alarm = Alarm()
            assert alarm.sounds.is_playing is True

            alarm.snooze_alarm()

            mock_thread_alarm.assert_called_once_with(
                self.config.snooze_duration.seconds
            )

        @pytest.mark.usefixtures("Mock Alarm.is_set to True")
        def test_returns_the_new_datetime_the_sound_will_alarm(self):
            alarm = Alarm()

            original_time = alarm.time
            snoozed_time = alarm.snooze_alarm()

            delta = snoozed_time - original_time
            assert delta.seconds == 300

        @pytest.mark.usefixtures("Mock Alarm.is_set to True")
        def test_updates_the_time_property_with_new_alarm_datetime(self):
            alarm = Alarm()

            original_time = alarm.time
            alarm.snooze_alarm()

            delta = alarm.time - original_time
            assert delta.seconds == 300

    # @pytest.mark.usefixtures("Mock Context")
    # @pytest.mark.usefixtures("Mock sounds.play_sound to keep thread alive 1 hour")
    # class TestRemoveAlarm:

    #     def test_if_an_alarm_is_set_removes_it(self, wait):
    #         alarm = Alarm()

    #         assert alarm.is_set is True

    #         alarm.remove_alarm()

    #         assert alarm.is_set is False
