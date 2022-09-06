:orphan:

############
Wandb Logger
############

.. _wandb_logger:

.. join_slack::
   :align: left

----

****************************************
1. Pass the logger argument to the Sweep
****************************************

.. code-block:: python

    from lightning_hpo import Sweep

    Sweep(..., logger="wandb")


***********************************
2. Setup your environment variables
***********************************

You can either setup the ``WANDB_ENTITY`` and ``WANDB_API_KEY`` and run the App

.. code-block::

    export WANDB_ENTITY=...
    export WANDB_API_KEY=...
    lightning run app app.py

Or pass them through the CLI.

.. code-block::

    lightning run app app.py WANDB_ENTITY=... --env WANDB_API_KEY=...

***************************
3. Check your Wandb Account
***************************

Lightning HPO automatically generate a Sweep Report and organize your runs, so everything is a single place.

.. figure:: https://pl-flash-data.s3.amazonaws.com/assets_lightning/wandb2.png
   :alt: Wandb
   :width: 100 %
