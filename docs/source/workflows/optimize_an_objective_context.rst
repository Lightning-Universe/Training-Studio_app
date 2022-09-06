************************
1. Define your objective
************************

Imagine you want to optimize a simple function called ``objective`` inside a ``objective.py`` file.

.. literalinclude:: ../../../examples/scripts/objective.py

----

********************
2. Define your Sweep
********************

Import a ``Sweep`` component and provide the path to your script and what you want to optimize on.

.. literalinclude:: ../../../examples/1_app_agnostic.py

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

.. note:: Locally, each trial runs into its own process, so there is an overhead if your objective is quick to run.