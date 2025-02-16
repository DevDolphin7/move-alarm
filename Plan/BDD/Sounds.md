# Sounds

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

-   get_local_file
-   get_freesound_file
-   search_freesound
-   play_file

### Tests

#### get_local_file

-   required parameter str: directory path
-   searches given directory for wav files
-   randomly selects a file from the directory
-   return str: wav file path

#### get_freesound_file

-   required parameter str: directory path
-   keyword parameter list[str]: sound theme
-   invokes search_freesound with the sound theme
-   if there _are_ valid results, downloads a wav sound to the directory path
-   if there _are_ valid results, sets the wav path to the downloaded file
-   if there **are not** valid results, warns the user
-   if there **are not** valid results, sets the wav path to get_local_file return value
-   return str: wav file path

#### play_file

-   required parameter str: wav path
-   sets currently_playing to true
-   plays the sound
-   when the sound stops, sets currently_playing to false

### Properties

-   dir_path: str
-   wav_path: str
-   sound_theme: list[str]
-   currently_playing: bool

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

-   stop_playing

### Tests

#### stop_playing

-   return bool: false if no sound is playing
-   if one sound is playing, it immediately stops
-   if multiple sounds are playing, they all immediately stop
-   sets currently_playing to false
-   return bool: true if a sound was made to stop playing

### Properties

-   currently_playing

# References:

-   [Freesound](https://freesound.org)
