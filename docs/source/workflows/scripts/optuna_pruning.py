import optuna
import sklearn.datasets
import sklearn.linear_model
import sklearn.model_selection


def objective(trial: optuna.Trial):
    # 1. Download the dataset and prepare the data
    iris = sklearn.datasets.load_iris()
    classes = list(set(iris.target))
    train_x, valid_x, train_y, valid_y = sklearn.model_selection.train_test_split(
        iris.data, iris.target, test_size=0.25, random_state=0
    )

    # 2: Sample alpha from the Trial
    alpha = trial.suggest_float("alpha", 1e-5, 1e-1, log=True)

    # 3: Create a SGDClassifier
    clf = sklearn.linear_model.SGDClassifier(alpha=alpha)

    # 4. Optimize for 100 steps
    for step in range(100):
        # 4.1 Fit the classifier on the training data
        clf.partial_fit(train_x, train_y, classes=classes)

        # 4.2 Report intermediate objective value.
        # If the model doesn't converge, the trial would be pruned (e.g killed)
        intermediate_value = 1.0 - clf.score(valid_x, valid_y)
        trial.report(intermediate_value, step)

        # 4.3 Manually prune the trial
        if trial.should_prune():
            raise optuna.TrialPruned()

    # 5. Return the score to be optimized
    return 1.0 - clf.score(valid_x, valid_y)


if __name__ == "__main__":
    # 6. Create an Optuna Study with a median pruner.
    # All trials below the median are pruned.
    study = optuna.create_study(pruner=optuna.pruners.MedianPruner())

    # 7. Launch 20 trials
    study.optimize(objective, n_trials=20)
