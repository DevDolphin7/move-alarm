# Sounds

## `__init__`

> Scenario: The user wants to get sounds from [Freesound](https://freesound.org)

Given the user has the [Freesound](https://freesound.org) api enabled  
And they have previously logged into [Freesound](https://freesound.org)  
And the alarm is about to sound  
Then authorisation is handled without the users knowledge  
And a sound is downloaded

### Functions

None

### Tests

None

### Properties

- auth - this is handled by a context

## Play a Sound

> Scenario: Play a sound

Given a user **has not** logged in to [Freesound](https://freesound.org)  
And wants a sound to remind them to move  
Then play a sound

> Scenario: Play user defined sounds

Given a user **has not** logged in to [Freesound](https://freesound.org)  
And wants a sound to remind them to move  
Feature the user can add thier own sound files  
Then play one of the files given by the user

> Scenario: Play a sound from [Freesound](https://freesound.org)

Given a user _has_ logged in to [Freesound](https://freesound.org)  
And wants a sound to remind them to move  
Then play a sound from [Freesound](https://freesound.org)

> Scenario: Play a user defined sound from [Freesound](https://freesound.org)

Given a user _has_ logged in to [Freesound](https://freesound.org)  
And wants a sound to remind them to move  
Feature the user can define the type of sounds they want to hear  
Then play a user defined sound from [Freesound](https://freesound.org)

> Scenario: User defined search on [Freesound](https://freesound.org) returns no results

Given a user _has_ logged in to [Freesound](https://freesound.org)  
And has defined the type of sound they want to hear  
But there are no matching search results  
Then warn the user that their search terms yielded no results  
Then play a sound

### Functions

- get_local_file
- search_freesound
- download_from_freesound
- get_freesound
- get_sound
- play_sound

### Tests

#### get_local_file

- required parameter str: directory path
- searches given directory for wav files
- randomly selects a file from the directory
- return str: wav file path

#### search_freesound

- required parameter list[str]: themes
- searches for sound results from [Freesound](https://freesound.org)
- returns a random sound result on success
- returns None on failure

#### download_from_freesound

- required parameter str: directory path
- downloads song from freesound
- raises error on connection issue
- return str: wav file path

#### get_freesound

- invokes `search_freesound` with the sound themes from config
- if there _is_ a valid search result, invokes `download_from_fressound`
- if there _is_ a valid result, returns the wav path to the downloaded file
- if there **is not** a valid search result, returns None

#### get_sound

- if `api_enabled` is **false**, invokes `get_local_file`
- if `api_enabled` is _true_, invokes `get_freesound`
- if `get_freesound` returns None, warns user
- if `get_freesound` returns None, invokes `get_local_file`
- returns str wav path

#### play_sound

- invokes `get_sound`
- sets currently_playing to true
- plays the sound
- when the sound stops, invokes `stop_sound`

### Properties

- wav_directory: str
- wav_path: str
- sound_theme: list[str]
- selected_sound: `<sound result>`
- currently_playing: bool
- api_enabled

## Stop Playing a Sound

> Scenario: Stop playing a sound

Given a user has started playing a sound  
And the user provided a stop command during the playback  
Then the sound should stop playing immediately

> Scenario: Stop playing multiple sounds

Given multiple sounds are currently playing  
And the user provided a stop command during the playback  
Then all sounds should stop playing immediately

### Functions

- stop_sound

### Tests

#### stop_sound

- return bool: false if no sound is playing
- if one sound is playing, it immediately stops
- if multiple sounds are playing, they all immediately stop
- sets currently_playing to false
- return bool: true if a sound was made to stop playing

### Properties

- currently_playing

# Summary

## Collected Functions

- get_local_file
- download_from_freesound
- search_freesound
- play_sound
- stop_sound

## Collected Properties

| name           | type                  | from self | from Contexts | visible? |
| -------------- | --------------------- | --------- | ------------- | -------- |
| contexts       | `Contexts`            | context   |               |          |
| auth           | `HandleAuthorisation` |           | yes           |          |
| wav_directory  | str                   |           | yes           | -        |
| wav_path       | str                   | yes       |               |          |
| sound_theme    | list[str]             |           | yes           | -        |
| selected_sound | `<sound result>`      | yes       |               | yes      |
| is_playing     | bool                  | yes       |               | yes      |
| api_enabled    | bool                  |           | yes           |          |

# References

- [Freesound](https://freesound.org)
- [Freesound `<Sound Result>`](https://freesound.org/docs/api/resources_apiv2.html#response-sound-list)
