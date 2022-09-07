:orphan:

##################
Tensorboard Logger
##################

.. _tensorboard_logger:

.. join_slack::
   :align: left

----

Simply add ``logger=tensorboard`` to the ``Sweep`` component.

.. code-block:: python

   from lightning_hpo import Sweep

   Sweep(..., logger="tensorboard")

And Lightning HPO handles the rest:

.. figure:: https://pl-flash-data.s3.amazonaws.com/assets_lightning/tensorboard_sweep.png
   :alt: Tensorboard Logger 1
   :width: 100 %

.. figure:: https://pl-flash-data.s3.amazonaws.com/assets_lightning/tensorboard_sweep_2.png
   :alt: Tensorboard Logger 2
   :width: 100 %
