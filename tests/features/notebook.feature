Feature: Notebook
  As an app user,
  I want to start a jupyter interactive session on a instance type of my choice,
  so that I can develop and run my model, or explore my data or artifacts.

  Scenario: Start notebook CLI
    Given I am connected to the app
     When I execute lightning run notebook
     Then I can see a notebook in the UI
      And I can open the notebook
