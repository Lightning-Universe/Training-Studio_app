:orphan:

#######################
StreamLit HiPlot Logger
#######################

.. _streamlit_logger:

.. join_slack::
   :align: left

----

Simply add ``logger=streamlit`` to the ``Sweep`` component.

.. code-block:: python

   from lightning_training_studio import Sweep

   Sweep(..., logger="streamlit")

And Lightning HPO handles the rest:

.. figure:: https://pl-flash-data.s3.amazonaws.com/assets_lightning/lightning_training_studio_optimizer.png
   :alt: StreamLit HiPlot
   :width: 100 %
