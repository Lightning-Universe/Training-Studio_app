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

.. figure:: https://user-images.githubusercontent.com/12861981/188265489-e025cbb5-92a1-479f-a49a-cd66a9bd946c.png
   :alt: Tensorboard Logger 1
   :width: 100 %

.. figure:: https://user-images.githubusercontent.com/12861981/188265485-66596fc6-d624-4b5f-9c7f-702f4329ae39.png
   :alt: Tensorboard Logger 2
   :width: 100 %
