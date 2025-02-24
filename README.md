# 🚧 App Under Construction 🏗️

```





```

# 🚨 MoveAlarm

MoveAlarm is a command-line application designed to help you stay active by reminding you to move at regular intervals. 🏃‍♂️

It reminds you by playing customizable local or online sounds at random, to keep things fresh! 🎵

Where possible, information about the sound is displayed. 🖥️

# ✨ Features

- **Alarm Reminders:** Set the script to run at log on to automatically remind you to _move_ every hour or so.
- **Interactive REPL Interface:** Engage with the application through a user-friendly command-line interface.
- **Customizable Alerts:** Set personalized reminders with custom sound notifications!
- **Unique Alerts:** You can log into [Freesound](https://freesound.org) and customise the types of sounds you'll hear from their large database!
- **Cross-Platform Support:** Compatible with Windows, macOS, and Linux systems.

# 📄 Supported File Formats

To ensure cross-platform function, MoveAlarm currently only supports wave audio files (`.wav` format).

# 📥 Installation

## 🖇️ Prerequisites

- [pip](https://pip.pypa.io/en/stable/installation/)

## ⚙️ Install

The app is available on pip:

```bash
pip install move-alarm
```

For an extra point, you can add it to your start up scripts ⭐

## 🛠️ Manual Install

### ⛓️ Prerequisites

- **[Python 3.10+](https://www.python.org/downloads/):** Ensure you have Python installed.
- **[Git](https://git-scm.com/downloads):** For cloning the repository.
- **[Poetry](https://python-poetry.org/docs/):** Manages dependencies and virtual environments.

### 🏗️ Additional Prerequisites for Linux

- Sounds are played through [`simpleaudio`](https://simpleaudio.readthedocs.io/en/latest/), which may require additional system packages. See [the installation docs](https://simpleaudio.readthedocs.io/en/latest/installation.html) for further information.
- During testing, [`pulseaudio`](https://www.freedesktop.org/wiki/Software/PulseAudio/) was used. A sound server system may be required to play the audio.

### 🪜 Steps

1. **Clone the Repository**

   ```bash
   git clone https://github.com/DevDolphin7/move-alarm.git
   cd move-alarm
   ```

2. **Install Dependencies**

   ```bash
   poetry install
   ```

# 🚀 Getting Started

After installation, launch MoveAlarm to enter the interactive [REPL](https://en.wikipedia.org/wiki/Read%E2%80%93eval%E2%80%93print_loop) environment.

## ▶️ Running the Application

To enter the [REPL](https://en.wikipedia.org/wiki/Read%E2%80%93eval%E2%80%93print_loop) environment:

```bash
move-alarm
```

Or for a manual installation:

```bash
poetry run move-alarm
```

⚙️ All commands can also be given as flags. For example, finding the help information can be done through the terminal or the [REPL](https://en.wikipedia.org/wiki/Read%E2%80%93eval%E2%80%93print_loop) environment:

```Bash
your@pc:~$ move-alarm --help
# Is the same output as:
your@pc:~$ move-alarm
MoveAlarm> help
```

## 💬 Using the REPL Interface

Once running, you'll be greeted with the MoveAlarm prompt:

```
MoveAlarm>
```

From here, you can enter various commands to control the application.

## 🔮 Commands

- **help** - View all available commands.

- **exit** - Exit the REPL.

- **start** - Begin the reminder cycle.

- **snooze** - Delay the current reminder cycle by the snooze duration.

- **stop** - Halt the reminders.

- **test** - Test the sound notifications.

  💡 This plays a sound immediately, letting you know when it should start and stop playing.

- **set** - List all the options that can be configured.

  - **set interval** - Define how often you'd like to receive reminders.

    ```
    MoveAlarm> set interval 30
    ```

    💡 This sets the reminder to alert you every 30 minutes. Whole numbers should be provided.

  - **set snooze** - Define how long to snooze the alarm on command.

    ```
    MoveAlarm> set snooze 5
    ```

    💡 This will snooze the alarm for 5 minutes on command. Whole numbers should be provided.

  - **set message** - Customize the notification message.

    ```
    MoveAlarm> set message "Time to stretch!"
    ```

    💡 This will display "Time to stretch!" at each interval.

  - **set path** - Define the path to the directory where you want sounds to be selected from (and downloaded to if using [Freesound](https://freesound.org)).

    ```
    MoveAlarm> set path path/to/your/wav_files/
    ```

  - **set freesound** - Define whether to get sounds from [Freesound](https://freesound.org) or just use local files.

    ```
    MoveAlarm> set freesound true
    ```

    💡 This will prompt you to log into [Freesound](https://freesound.org) and authorise the move-alarm app.

    ```
    MoveAlarm> set freesound false
    ```

    💡 This will only look at the local directory where you want sounds to be selected from. Any exisiting log on information will be removed, see [Data Storage](#data-storage) for more information.

  - **set theme** - Define the themes of the sounds you want to hear from [Freesound](https://freesound.org).

    ```
    MoveAlarm> set themes piano "acoustic guitar"
    ```

    💡 This will add "piano" and "acoustic guitar" to the search terms.

# 🔍 Behaviour-Driven Development (BDD)

This project employs BDD to define and test application behaviors. The primary user interactions are documented in [`App.md`](https://github.com/DevDolphin7/move-alarm/blob/main/Plan/BDD/App.md), located in the [`Plan/BDD`](https://github.com/DevDolphin7/move-alarm/blob/main/Plan/BDD/) directory. These files outline expected behaviors and serve as a reference for development and testing.

# ✅ Testing - Manual Installation

Automated tests are implemented using [`pytest`](https://docs.pytest.org/en/stable/). To execute the test suite:

```bash
poetry run pytest
```

Test files are located in the `__tests__` directory at the project's root. 🧪

Testing will not make any real API calls, instead mocking returns values for the required functions. If you have logged into freesound, your data will be still be remembered (tests produce a `.env.test` file while the live app uses a `.env` file). See [Data Storage](#data-storage).

# 🔄 Continuous Integration

MoveAlarm utilizes [GitHub Actions](https://github.com/features/actions) for continuous integration. The CI pipeline automates linting and testing for each pull request to ensure code quality before merging into the main branch. ⚡

# 📜 License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT). 📄

# Data Storage

This app only stores data locally on the device. No data is stored online.

If you choose to _use_ sounds from [Freesound](https://freesound.org), a local `.env` file will be created in the root directory of the app to store the Client ID you provide. The `.env` file will also store any refresh token recieved by the [Freesound API](https://freesound.org/docs/api/authentication.html) for future authentification requests.

If you do **not enable** [Freesound](https://freesound.org), a local `.env` _file will not be created_. If you decide to **disable** [Freesound](https://freesound.org), the `.env` _file will be removed_. This means if you change your mind, you will need to re-sign into [Freesound](https://freesound.org) when re-enabling.

To use [Freesound](https://freesound.org) with MoveAlarm, a list of valid Client IDs is checked before each request. If you wish to use [Freesound](https://freesound.org) with MoveAlarm, please get in touch to add your ID to the valid list, see [Contact](#contact).

Configuration settings are stored in a local `.ini` file in the root folder. If the file is missing or corrupt, default values will be used **and** an attempt to restore the `.ini` file will be made. As default, [Freesound](https://freesound.org) is **not enabled**.

# 📡 Contact

- [GitHub](https://github.com/DevDolphin7/move-alarm/)
- [PyPI](https://pypi.org/project/move-alarm/)
- Email: [DevDolphin7@outlook.com](mailto:devdolphin7@outlook.com)

# 🪧 Ideas for Improvement

- Check if the alarm is currently set or not
- Script to automate add to startup process (cross-platform)
- Check information on recently played sounds (number of sounds could be user defined)
- Option to have max number of files in directory (after downloading one, it removes one)
