:orphan:

#####################
Show or download logs
#####################

.. _run_sweep:

.. join_slack::
   :align: left

----

**************************
1. Check available options
**************************

The Training Studio App CLI provides an help.

.. code-block::

   lightning show logs --hel

Here is the output of such command above:

.. code-block::

   Usage: lightning show logs [OPTIONS] [APP_NAME] [COMPONENTS]...

   Show cloud application logs. By default prints logs for all currently
   available components.

   Example uses:

         Print all application logs:

            $ lightning show logs my-application

         Print logs only from the flow (no work):

            $ lightning show logs my-application flow

         Print logs only from selected works:

            $ lightning show logs my-application root.work_a root.work_b

   Options:
   -f, --follow  Wait for new logs, to exit use CTRL+C.
   --help        Show this message and exit.


************
2. Show logs
************

You can simply view the logs as follows:

.. code-block::

   lightning show logs training_studio_app

.. code-block::


****************
3. Download logs
****************

You can simply download the logs by piping them within a ``log.txt`` file as follows:

.. code-block::

   lightning show logs training_studio_app > logs.txt
