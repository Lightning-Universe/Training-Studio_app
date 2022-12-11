import optuna
from lightning import LightningApp
from sklearn import datasets
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import train_test_split

from lightning_training_studio import Objective, Sweep
from lightning_training_studio.algorithm.optuna import OptunaAlgorithm
from lightning_training_studio.distributions.distributions import LogUniform


class MyObjective(Objective):
    def objective(self, alpha: float):

        iris = datasets.load_iris()
        classes = list(set(iris.target))
        train_x, valid_x, train_y, valid_y = train_test_split(
            iris.data,
            iris.target,
            test_size=0.25,
            random_state=0,
        )

        clf = SGDClassifier(alpha=alpha)

        self.monitor = "accuracy"

        for step in range(100):
            clf.partial_fit(train_x, train_y, classes=classes)
            intermediate_value = clf.score(valid_x, valid_y)

            # WARNING: Assign to reports,
            # so the state is instantly sent to the flow.
            self.reports = self.reports + [[intermediate_value, step]]

        self.best_model_score = clf.score(valid_x, valid_y)


app = LightningApp(
    Sweep(
        objective_cls=MyObjective,
        total_experiments=20,
        parallel_experiments=1,
        algorithm=OptunaAlgorithm(
            optuna.create_study(
                pruner=optuna.pruners.MedianPruner(),
                direction="maximize",
            )
        ),
        distributions={"alpha": LogUniform(1e-5, 1e-1)},
    )
)
