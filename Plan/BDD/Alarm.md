# BDD: Gherkin Language

-   Given
-   When
-   Then
-   And
-   But
-   Feature
-   Rule
-   Example
-   Background
-   Scenario

# Alarm

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

# References:

-   [https://katalon.com/resources-center/blog/bdd-testing](https://katalon.com/resources-center/blog/bdd-testing)
-   [Freesound](https://freesound.org)
