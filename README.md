# MoveAlarm

An alarm designed to remind you to be more active!

# Getting Started

## For Developers

### Pre-Requisites

The code is written in [python3.12](https://www.python.org/downloads/release/python-3123/).

Version control is handled by [git](https://git-scm.com/downloads).

Some Linux OS include Debian require `python3-dev`, `libasound2-dev`, `pulseaudio`.

For exmaple, on Debian:

> `sudo apt-get install -y python3-dev libasound2-dev pulseaudio`

Package dependencies and environments are managed by [poetry](https://python-poetry.org/docs/#installation).

> git clone https://github.com/DevDolphin7/move-alarm.git

> cd move-alarm

### Installing Dependencies

> poetry install

### Testing

> poetry run pytest **tests**/

### Running The App

For Linux / MacOS / WSL:

> poetry run python3 ./src/app.py

For Windows:

> poetry run python3 .\src\app.py
