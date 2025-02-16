# HandleAuthorisation

> Scenario: New User Get Access Token

    Given the user hasn't logged into Freesound before
    And the user wants to access online songs
    When they start the app
    Then the app asks them if they want to log into [Freesound](https://freesound.org)
    And provides a way for them to do this
    Then the app saves their authorisation code

> Scenario: Repeat User Get Access Token

    Given the user has previously logged in to [Freesound](https://freesound.org)
    And the user wants to access online songs
    When they start the app
    Then the app does not require further authentification

# References:

-   [Freesound](https://freesound.org)
