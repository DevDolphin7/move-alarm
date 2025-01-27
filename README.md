# MoveAlarm

An alarm designed to remind you to be more active!

# Getting Started

## For Developers

### Pre-Requisites

The code is written in [python3.12](https://www.python.org/downloads/release/python-3123/).

Version control is handled by [git](https://git-scm.com/downloads).

Package dependencies and environments are managed by [poetry](https://python-poetry.org/docs/#installation).

```CLI
git clone https://github.com/DevDolphin7/move-alarm.git
```

```CLI
cd move-alarm
```

### Installing Dependencies

```CLI
poetry install
```

### Testing

```CLI
poetry run pytest
```

> 💡 All tests are stored in `__tests__` in the project root folder.

### Running The App

For Linux / MacOS / WSL:

```CLI
poetry run python3 ./src/app.py
```

For Windows:

```CLI
poetry run python3 .\src\app.py
```
