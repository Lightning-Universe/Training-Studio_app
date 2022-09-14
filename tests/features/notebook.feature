Feature: Start Notebook
  As an app user,
  I want to start a jupyter interactive session on a instance type of my choice,
  so that I can develop and run my model, or explore my data or artifacts.

  Scenario: Start notebook CLI
    Given I am connected to the app
     When I execute lightning run notebook
     Then I can see a notebook in the UI
      And the notebook status in the UI is running
      And I can open the notebook

  Scenario: Stop notebook CLI
    Given I am connected to the app
      And a notebook is running
     When I execute lightning stop notebook
     Then I can see a notebook in the UI
      And the notebook status in the UI is stopped

  Scenario: View notebooks CLI
    Given I am connected to the app
      And a notebook is running
     When I execute lightning show notebooks
     Then I can see a notebook in the terminal
      And the notebook status in the terminal is running
