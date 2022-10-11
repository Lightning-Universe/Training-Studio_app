:orphan:

##################################
Run a Sweep with PyTorch Lightning
##################################

.. _optimize_with_pl:

.. join_slack::
   :align: left

----

*******************
Why Lightning HPO ?
*******************

If you're already a PyTorch Lightning user and are looking forward to doing hyper-parameter optimization.

You are in the right place and Lightning HPO is what you are looking for !

Lightning HPO provides a :class:`~lightning_hpo.components.sweep.Sweep` abstraction to coordinate complex hyper-parameters
which can be run locally or in the cloud with a simple CLI change.

----

******************
Prepare your Sweep
******************


Import a :class:`~lightning_hpo.components.sweep.Sweep` component, pass the path to your script and define your arguments in an ``app.py`` file.

For this example, download ``train.py`` and ``app.py`` files with the following commands.

.. code-block::

   mkdir example_demo && cd example_demo && mkdir scripts

   wget https://raw.githubusercontent.com/Lightning-AI/lightning-hpo/master/examples/scripts/train.py

   wget -O app.py https://raw.githubusercontent.com/Lightning-AI/lightning-hpo/master/examples/2_app_pytorch_lightning.py

In the ``app.py`` file, we configure a :class:`~lightning_hpo.components.sweep.Sweep` object to run 4 sequential experiments where the ``model.lr``, ``model.gamma``, ``data.batch_size`` and ``trainer.max_epochs`` are hyper-parameters sampled from several distributions.

.. literalinclude:: ../../../examples/2_app_pytorch_lightning.py

Under the hood, the :class:`~lightning_hpo.components.sweep.Sweep` launches one process per experiment and passed the sampled parameters to your script
e.g this would work with any argument parser such as `hydra <https://github.com/facebookresearch/hydra>`_ or `jsonargparse <https://github.com/omni-us/jsonargparse>`_.

.. code-block::

   The provided arguments are ['--model.lr=0.01715209192907918', '--model.gamma=0.6520463886841567', '--data.batch_size=32', '--trainer.max_epochs=5']

   The provided arguments are ['--model.lr=0.01889036668053488', '--model.gamma=0.7965239180957129', '--data.batch_size=32', '--trainer.max_epochs=4']

   The provided arguments are ['--model.lr=0.018730095755230075', '--model.gamma=0.5170345255250421', '--data.batch_size=64', '--trainer.max_epochs=5']


.. note:: Don't forget to pass ``framework="pytorch_lightning"`` to the ``Sweep`` component, so Lightning HPO can do more (automated logging, check-pointing, multi-node training, etc..).

----

*****************************
Run your Sweep on your script
*****************************

Now, you can optimize it locally.

.. code-block::

   python -m lightning run app app.py

or with ``--cloud`` to run it in the cloud.

.. code-block::

   python -m lightning run app app.py --cloud

You can find similar lines within the logs.

.. code-block::

   INFO: Experiment 0 finished with value: 0.2874999940395355 and parameters: {'model.lr': 0.01889036668053488, 'model.gamma': 0.7965239180957129, 'data.batch_size': 32, 'trainer.max_epochs': 4}. Best is experiment 0 with value: 0.2874999940395355.

   INFO: Experiment 1 finished with value: 0.08124999701976776 and parameters: {'model.lr': 0.01715209192907918, 'model.gamma': 0.6520463886841567, 'data.batch_size': 32, 'trainer.max_epochs': 5}. Best is experiment 0 with value: 0.2874999940395355.

   INFO: Experiment 2 finished with value: 0.11249999701976776 and parameters: {'model.lr': 0.018730095755230075, 'model.gamma': 0.5170345255250421, 'data.batch_size': 64, 'trainer.max_epochs': 5}. Best is experiment 0 with value: 0.2874999940395355

.. note:: Locally, each experiment runs in its own process, so there is overhead if your objective is quick to run.


----

**********
Next Steps
**********

.. raw:: html

   <br />
   <div class="display-card-container">
      <div class="row">

.. displayitem::
   :header: The Research Studio App
   :description: Manage Sweeps and Tools to accelerate Training.
   :col_css: col-md-6
   :button_link: ../training_studio.html
   :height: 180

.. raw:: html

   <hr class="docutils" style="margin: 50px 0 50px 0">

.. raw:: html

   <div style="display:none">
