Feature: Sweeps
  As an app user,
  I want to start an experiment sweep on instance types of my choice,
  so that I can determine the best hyper-parameters for my model.

  Scenario: Start sweep from the CLI
    Given I am connected to the app
     When I execute lightning run sweep
     Then I can see a sweep in the UI
      And the sweep status in the UI is running
      And I can open the logger
     When I execute lightning show sweeps
     Then I can see a sweep in the terminal
      And the sweep status in the terminal is running

  Scenario: Stop sweep from the CLI
    Given I am connected to the app
      And a sweep is running
     When I execute lightning stop sweep
     Then I can see a sweep in the UI
      And the sweep status in the UI is stopped
     When I execute lightning show sweeps
     Then I can see a sweep in the terminal
      And the sweep status in the terminal is stopped

  Scenario: View sweeps from the CLI
    Given I am connected to the app
      And a sweep is running
     When I execute lightning show sweeps
     Then I can see a sweep in the terminal
      And the sweep status in the terminal is running
