:orphan:

#######################
Convert from raw Optuna
#######################

.. _convert_from_raw_optuna:

.. join_slack::
   :align: left

----

************************
1. Your Optuna Objective
************************

We are going to convert `Optuna Efficient Optimization Algorithms <https://optuna.readthedocs.io/en/stable/tutorial/10_key_features/003_efficient_optimization_algorithms.html#sphx-glr-tutorial-10-key-features-003-efficient-optimization-algorithms-py>`_ into a Lightning App.

This Optuna example optimizes the value (for example: learning-rate) of a ``SGDClassifier`` from ``sklearn`` trained over the `Iris Dataset <https://archive.ics.uci.edu/ml/datasets/iris>`_.

The example below is going to be re-organized as a Lightning App.

.. literalinclude:: scripts/optuna_pruning.py

----

***************************
2. Convert to Lightning HPO
***************************

Import ``Sweep`` and ``Objective`` components and move your Optuna code within the objective method of your custom Objective.

Add Imports
^^^^^^^^^^^

.. literalinclude:: ../../../examples/3_app_sklearn.py
   :lines: 1-9

Implement the CustomObjective
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To customize an ``Objective``, you need to override the ``objective`` and pass all your hyper-parameters.

The core difference from the previous scripts are:

- ``self.monitor``: This is used to automatically populate metrics with your selected logger
- ``self.reports``: Lightning HPO automatically takes care of pruning the trials, simply register the step based reports.
- ``self.best_model_score``: Lightning HPO expects you to register the best mode score of your model in the ``Objective`` state.

.. literalinclude:: ../../../examples/3_app_sklearn.py
   :lines: 12-36

Configure your Sweep
^^^^^^^^^^^^^^^^^^^^

Finally, you can define your ``Sweep`` and pass it an ``OptunaAlgorithm``

.. literalinclude:: ../../../examples/3_app_sklearn.py
   :lines: 39-

----

**************************
3. Optimize your objective
**************************

Now, you can optimize it locally.

.. code-block::

   python -m lightning run app examples/1_app_agnostic.py

or with ``--cloud`` to run it in the cloud.

.. code-block::

   python -m lightning run app examples/1_app_agnostic.py --cloud

.. note:: Locally, each trial runs in its own process, so there is overhead if your objective is quick to run.
