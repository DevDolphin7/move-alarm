# MoveAlarm

MoveAlarm is a command-line application designed to help you stay active by reminding you to move at regular intervals.

It reminds you by playing customisable sounds at random, to keep things fresh!

## Features

- **Interactive REPL Interface:** Engage with the application through a user-friendly command-line interface.
- **Customizable Alerts:** Set personalized reminders with custom sound notifications!
- **Unique Alerts:** You can log into [Freesound](https://freesound.org) and customise the types of sounds you'll here from their large database!
- **Cross-Platform Support:** Compatible with Windows, macOS, and Linux systems.

## Installation

### Prerequisites

- [pip](https://pip.pypa.io/en/stable/installation/)

### Install

The app is available on pip:
```bash
pip install move-alarm
```

And that's all!

### Manual Install

### Prerequisites

- **[Python 3.10+](https://www.python.org/downloads/):** Ensure you have Python installed.
- **[Git](https://git-scm.com/downloads):** For cloning the repository.
- **[Poetry](https://python-poetry.org/docs/):** Manages dependencies and virtual environments.

#### Additional Prerequisistes for Linux:
- Sounds are played through [`simpleaudio`](https://simpleaudio.readthedocs.io/en/latest/), which may require additional level system packages, see [the installation docs](https://simpleaudio.readthedocs.io/en/latest/installation.html) for further information.
- During testing, [`pulseaudio`](https://www.freedesktop.org/wiki/Software/PulseAudio/) was used. A sound server system may be required to play the audio.

### Steps

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/DevDolphin7/move-alarm.git
   cd move-alarm
   ```

2. **Install Dependencies:**

   ```bash
   poetry install
   ```

## Getting Started

After installation, launch move-alarm to enter the interactive REPL environment.

### Running the Application

 ```bash
  move-alarm
  ```

### Running the Application - Manual Installation

  ```bash
  poetry run move-alarm
  ```

### Using the REPL Interface

Once running, you'll be greeted with the MoveAlarm prompt:

```
MoveAlarm>
```

From here, you can enter various commands to control the application:

- **help** - View all available commands.

  ```
  MoveAlarm> help
  ```

- **start** - Begin the reminder cycle.

  ```
  MoveAlarm> start
  ```

- **stop** - Halt the reminders.

  ```
  MoveAlarm> stop
  ```

- **test** - Test the sound notifications.

  ```
  MoveAlarm> test
  ```

  💡 This plays a sound immediately, letting you know when it should start and stop playing.

- **set** - List all the options that can be configured.

  ```
  MoveAlarm> set
  ```

- **set interval** - Define how often you'd like to receive reminders.

  ```
  MoveAlarm> set interval 30
  ```

  This sets the reminder to alert you every 30 minutes. Whole numbers should be provided.

- **set snooze** - Define how long to snooze the alarm on command.

  ```
  MoveAlarm> set snooze 5
  ```

  This will snooze the alarm for 5 minutes on command. Whole numbers should be provided.

- **set message** - Customize the notification message.

  ```
  MoveAlarm> set message "Time to stretch!"
  ```

  This will display "Time to stretch!" at each interval.

- **set path** - Define the path to the directory where you want sounds to be selected from (and downloaded to if using [Freesound](https://freesound.org)).

  ```
  MoveAlarm> set path path/to/your/wav_files/
  ```

- **set theme** - Define the themes of the sounds you want to hear from [Freesound](https://freesound.org).

  ```
  MoveAlarm> set themes piano guitar
  ```

- **exit** - Exit the REPL.

  ```
  MoveAlarm> exit
  ```

For a comprehensive list of commands and detailed usage, refer to the [`App.md`](https://github.com/DevDolphin7/move-alarm/blob/main/Plan/BDD/App.md) file in the `Plan/BDD` directory.

## Behaviour-Driven Development (BDD)

This project employs BDD to define and test application behaviors. The primary user interactions are documented in [`App.md`](https://github.com/DevDolphin7/move-alarm/blob/main/Plan/BDD/App.md), located in the [`Plan/BDD`](https://github.com/DevDolphin7/move-alarm/blob/main/Plan/BDD/) directory. The files outline expected behaviors and serves as a reference for development and testing.

## Testing - Manual Installation

Automated tests are implemented using [`pytest`](https://docs.pytest.org/en/stable/). To execute the test suite:

```bash
poetry run pytest
```

Test files are located in the `__tests__` directory at the project's root.

## Continuous Integration

Move-Alarm utilizes [GitHub Actions](https://github.com/features/actions) for continuous integration. The CI pipeline automates linting and testing for each pull request to ensure code quality before merging into the main branch.

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).

