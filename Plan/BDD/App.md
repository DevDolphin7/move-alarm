# App

## `__init__`

> Scenario: The user has just launched the app

Given the user has just launched the app  
Then the configuration file is loaded  
Then the user has access to the move-alarm [REPL](https://en.wikipedia.org/wiki/Read%E2%80%93eval%E2%80%93print_loop) environment

### Functions

- `__init__`

### Tests

- the config file is loaded on initialisation
- the user is warned if a config file has to be made from default values
- the user has access to the MoveAlarm [REPL](https://en.wikipedia.org/wiki/Read%E2%80%93eval%E2%80%93print_loop) environment

### Properties

- config_path: str

## Help

> Scenario: The user wants to learn the available commands

Given the user is new  
And they type the help command  
Feature or they type the help flag  
Then a list of avilable commands and what they do is displayed

### Functions

- help

### Tests

- optional parameter str: command
- the help command invokes help
- the help flag invokes help
- if a command _is_ specified, information on that command is shown
- if a command **is not** specified, a list of all the commands is shown

### Properties

- command: str

## Exit

> Scenario: The user wants to learn the available commands

Given the user has launched the [REPL](https://en.wikipedia.org/wiki/Read%E2%80%93eval%E2%80%93print_loop) environment  
And they type the exit command  
Then the user exits the [REPL](https://en.wikipedia.org/wiki/Read%E2%80%93eval%E2%80%93print_loop) environment

### Functions

- exit

### Tests

- the REPL is no longer active on exit

### Properties

None

## Start

> Scenario: The user wants to manually start the alarm

Given the user has not set up the script to automatically start  
And they want it to start  
Then the alarm is set  
Then notification of success is provided to the user

### Functions

- start

### Tests

- invokes set_alarm with `<Config>`
- user is notified of success
- user is notified of failure

### Properties

- config: `<Config>`

## Snooze

> Scenario: The user wants to snooze the alarm

Given the user knows an alarm is sounding or will sound soon
And the user wants it to sound in an additional few minutes time
Then the alarm can be delayed
Then notification of success is provided to the user

### Functions

- snooze

### Tests

- invokes snooze_alarm with `<Config>`
- user is notified of success
- user is notified of failure

### Properties

- config: `<Config>`

## Stop

> Scenario: The user wants to stop the alarm going off in the future

Given an alarm is set  
And the user wants to stop the alarm  
Then the alarm is removed  
Then positive feedback is provided to the user

> Scenario: The user wants to stop an alarm that is currently sounding

Given an alarm is currently playing a sound  
And the user wants to stop the alarm  
Then the sound stops playing  
Then positive feedback is provided to the user

### Functions

- stop

### Tests

- if sound _is_ currently playing, invokes stop_sound
- if sound _is_ currently playing, invokes remove_alarm
- if sound **is not** currently playing, invokes remove_alarm
- user is notified of success
- user is notified of failure

### Properties

None!

## Test

> Scenario: The user wants to test the sound is playing properly

Given the user has installed the package  
And the user wants to check the sound will play after the wait duration  
Then a sound should play immediately  
And the user should be provided helpful information

### Functions

- test

### Tests

- notifies the user of further help available on [move-alarm](https://github.com/DevDolphin7/move-alarm)
- notifies the user it will now try to play a sound
- invokes play_sound
- notifies the user the sound should be playing
- notifies the user when the sound should have stopped

### Properties

- test_wav_path: str

## Configure (Set)

> Scenario: The user wants to know what they can configure

Given the user is new  
And would like to know what they can configure  
Then a list of all valid configuration properties should be displayed  
And their current values and what they do

> Scenario: The user wants to define the wait duration

Given the user wants to get up more or less frequently from the computer  
And would like to define the wait duration  
Then they should be able to configure the app to do so  
And this should be remembered after computer reboot

> Scenario: The user wants to define the snooze duration

Given the user would like to define the snooze duration  
Then they should be able to configure the app to do so  
And this should be remembered after computer reboot

> Scenario: The user wants to define the message that appears when an alarm goes off

Given the user would like to define a personalised alarm message
Then they should be able to configure the app to do so  
And this should be remembered after computer reboot

> Scenario: The user wants to define a directory containing their wav files

Given the user would like to define their own sound files  
Then they should be able to configure the app to do so  
And this should be remembered after computer reboot

> Scenario: The user only wants to play local files (no [Freesound](https://freesound.org))

Given the user does not want to download songs from the internet
Then they should be able to configure the app to do so  
And this should be remembered after computer reboot

> Scenario: The user wants to start using sounds from [Freesound](https://freesound.org)

Given the user has just enabled the [Freesound](https://freesound.org) api feature  
Then they are able to log into their [Freesound](https://freesound.org) account  
And this should be remembered after computer reboot

> Scenario: The user wants to define their own sound themes from [Freesound](https://freesound.org)

Given the user would like to define their own sound themes  
Then they should be able to configure the app to do so  
And this should be remembered after computer reboot

### Functions

- config
- format_str_to_datetime
- check_url_banned_chars

### Tests

#### config

- on no argument, notifies the user of the valid arguments
- on invalid argument, notifies the user of the valid arguments
- updates wait_duration with datetime
- updates snooze_duration with datetime
- notifies the user on invalid duration with correct example
- Updates reminder_text with str
- updates wav_directory with str
- notifies user if wav_directory does not exist
- updates api_enabled with bool
- notifies user if invalid input given with correct example
- updates sound_themes with a list of strings
- notifies user is url banned characters are used with example themes
- invokes set_config_file with `<Config>`

#### format_str_to_datetime

- required parameter str: minutes
- returns a datetime of minutes
- raises ValueError on failure

#### check_url_banned_chars

- required parameter str: theme
- return str: theme if str _is_ ok for a url
- raise ValueError if str **is not** ok for a url

### Properties

- args: list[str]
- wait_duration
- snooze_duration
- reminder_text
- wav_directory
- api_enabled
- sound_themes
- minutes_str: str
- theme: str
- url_regex: re.Pattern

# Summary

## Collected Functions

- `__init__`
- help
- exit
- start
- snooze
- stop
- test
- config
- format_str_to_datetime
- check_url_banned_chars

## Collected Properties

| name            | type         | from self | from Config | visible? |
| --------------- | ------------ | --------- | ----------- | -------- |
| config_path     | str          | yes       |             | -        |
| command         | str          | yes       |             | -        |
| config          | `<Config>`   | context   |             | -        |
| test_wav_path   | str          | yes       |             | -        |
| args            | list[str]    | yes       |             | -        |
| wait_duration   | `<datetime>` |           | context     | -        |
| snooze_duration | `<datetime>` |           | context     | -        |
| reminder_text   | str          |           | context     | -        |
| wav_directory   | str          |           | context     | -        |
| api_enabled     | bool         |           | context     | -        |
| sound_themes    | list[str]    |           | context     | -        |
| minutes_str     | str          | yes       |             | -        |
| theme           | str          | yes       |             | -        |
| url_regex       | re.Pattern   | yes       |             | -        |

# References

- [REPL](https://en.wikipedia.org/wiki/Read%E2%80%93eval%E2%80%93print_loop)
- [move-alarm](https://github.com/DevDolphin7/move-alarm)
- [Freesound](https://freesound.org)
