# Alarm

## Set Alarm

> Scenario: Set an alarm after computer turns on

Given the user has logged into their computer  
And the script has automatically started running  
And the desired wait duration is defined  
Then a sound should play after the wait duration

### Functions

- set_alarm

### Tests

#### `__init__`

- sets property is_set: bool to false
- sets property time: datetime | None to None

#### set_alarm

- updates property to reflect alarm is set
- waits for wait duration without halting the program
- after wait duration, plays a sound
- return datetime: actual time alarm will sound on success
- update time with set time

### Properties

- wait_duration: datetime
- alarm_set: bool
- time: datetime | None

## Snooze Alarm

> Scenario: Snooze an upcoming alarm

Given an alarm has been set  
But the user wants to delay the alarm sounding  
And the snooze duration is defined  
Then the sound should play after the wait duration and snooze duration

> Scenario: Snooze a playing alarm

Given an alarm has gone off  
And is currently playing a sound  
But the user wants to snooze the alarm  
And the snooze duration is defined  
Then the sound should stop playing  
Then the sound should play after the snooze duration

### Functions

- snooze_alarm

### Tests

#### snooze_alarm

- if sound **is not** currently playing, sound will not play until after wait duration and snooze duration
- if sound _is_ currently playing, sound stops playing
- if sound _is_ currently playing, sound starts playing immediatly after snooze duration
- return datetime: actual time alarm will sound
- update time property with new set time

### Properties

- sound_playing: bool
- snooze_duration: datetime
- wait_duration
- time

## Remove_alarm

> Scenario: The user wants to turn off the sedentry alarm

Given the user has logged into their computer  
And the script has automatically started running  
But the user doesn't want the alarm to sound  
Then the alarm is removed and will not sound

### Functions

- is_set
- remove_alarm

### Tests

#### is_set

- return bool
- returns true if the alarm _is_ waiting to play
- returns true if the alarm was snoozed and _is_ still waiting to play
- returns false if the alarm **is not** waiting to play
- returns false if the alarm is currently playing and no further alarm is set

#### remove_alarm

- if an alarm is set, removes it
- if alarm was removed, updates alarm set property
- return bool: false if no alarm is set
- return bool: true on success
- update time property to None

### Properties

- alarm_set

# Summary

## Collected Functions

- set_alarm
- is_sound_currently_playing -> could be a class property
- snooze_alarm
- is_set -> could be a class property
- remove_alarm

## Collected Properties

| name             | type               | from self | from Context | from Sounds | visible? |
| ---------------- | ------------------ | --------- | ------------ | ----------- | -------- |
| config           | `<Config>`         | context   |              |             |          |
| wait_duration    | `<datetime>`       |           | yes          |             | -        |
| sound_path       | str                |           |              | yes         | -        |
| is_set           | bool               | yes       |              |             | yes      |
| time             | `<datetime>`, None | yes       |              |             | yes      |
| is_sound_playing | bool               |           |              | yes         | -        |
| snooze_duration  | `<datetime>`       |           | yes          |             | -        |
