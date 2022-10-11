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

The Research Studio App CLI provides its own help.

.. code-block::

   lightning show logs --help

Here is the output of the command:

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

To view the logs use the following command:

.. code-block::

   lightning show logs training_studio_app

.. note:: You get logs only once the Lightning App is ready. Wait for the Open App button to be visible.

****************
3. Download logs
****************

You can simply download the logs by piping them within a ``log.txt`` file:

.. code-block::

   lightning show logs training_studio_app > logs.txt

----

**********
Next Steps
**********

.. raw:: html

   <br />
   <div class="display-card-container">
      <div class="row">

.. displayitem::
   :header: Show or Download Artifacts
   :description: Learn how to interact with your Research Studio App artifacts
   :col_css: col-md-4
   :button_link: show_or_download_artifacts.html
   :height: 180


.. displayitem::
   :header: Run a Sweep
   :description: Learn how to run a Sweep with your own python script
   :col_css: col-md-4
   :button_link: run_sweep.html
   :height: 180

.. displayitem::
   :header: Run a Notebook
   :description: Learn how to run a notebook locally or in the cloud
   :col_css: col-md-4
   :button_link: run_notebook.html
   :height: 180

.. raw:: html

      </div>
   </div>
