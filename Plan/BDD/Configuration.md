# Configuration

## Configuration file

> Scenario: A user wants to define the wait duration between alarms

Given a user has the script running on start up  
And they want to define their own length of computer time before the alarm  
Then this can be configured  
And remembered the next time they log on

> Scenario: A user wants to define the snooze duration

Given a user has an alarm set  
And they want to snooze the alarm  
Then the snooze duration can be configured  
And remembered the next time they log on

> Scenario: A user wants to define the reminder message

Given an alarm goes off to remind a user to move  
And the user defined what message to be displayed  
Then the reminder text can be configured  
And remembered the next time they log on

> Scenario: A user wants to define the storage directory for wav files

Given a user has a directory of existing wav files OR  
Given a user wants to store new sounds in a preferred directory  
And they want to use those files as the alarm sound  
Then the file directory can be configured  
And remembered the next time they log on

> Scenario: A user wants to define the types of sounds that will be played

Given a user has a preference in alarm sounds  
Then the alarm sound preference can be configured  
And remembered the next time they log on

> Scenario: A user accidently deletes or corrupts their config file

Given a user a irreparably damaged their config file  
Then default values should be used  
Then the config file should be re-made

### Functions

- set_config_file
- load_config_file
- load_default_values

### Tests

#### `__init__`

- requires property: str config_path

#### set_config_file

- creates config file at config path
- config file contains only valid properties

#### load_config_file

- required parameter str: config_path
- sets wait_duration as instance of datetime
- sets snooze_duration as instance of datetime
- sets reminder_text as str
- sets wav_directory as str
- sets api_enabled as bool
- sets sound_theme as str
- return bool: true on success
- raises FileNotFoundError on missing file
- raises ValueError on missing key
- raises ValueError on incorrect value data type

#### load_default_values

- sets wait_duration to 1 hour
- sets snooze_duration to 5 minutes
- sets reminder_text to "Time to move!"
- sets wav_directory to an example directory
- sets api_enabled to false
- sets sound_theme to piano or guitar
- invokes set_config_file

### Properties

- confir_path: str
- wait_duration: datetime
- snooze_duration: datetime
- reminder_text: str
- wav_directory: str
- api_enabled: bool
- sound_themes: list[str]

# Summary

## Collected Functions

- `__init__`
- set_config_file
- load_config_file
- load_default_values

## Collected Properties

| name            | type         | from self | from App | visible? |
| --------------- | ------------ | --------- | -------- | -------- |
| config_path     | str          |           | yes      | -        |
| wait_duration   | `<datetime>` | yes       |          | yes      |
| snooze_duration | `<datetime>` | yes       |          | yes      |
| reminder_text   | str          | yes       |          | yes      |
| wav_directory   | str          | yes       |          | yes      |
| api_enabled     | bool         | yes       |          | yes      |
| sound_theme     | list[str]    | yes       |          | yes      |
