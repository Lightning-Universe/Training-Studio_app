:orphan:

###############################
Optimize with PyTorch Lightning
###############################

.. _optimize_with_pl:

.. join_slack::
   :align: left

----

*******************************
From a PyTorch Lightning Script
*******************************

If you're already a PyTorch Lightning user, Lightning HPO works seamlessly with it.

Import a ``Sweep`` component, pass the path to your script and define your arguments in an ``app.py`` file.

.. literalinclude:: ../../../examples/2_app_pytorch_lightning.py

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

.. note:: Locally, each trial runs in its own process, so there is overhead if your objective is quick to run.
