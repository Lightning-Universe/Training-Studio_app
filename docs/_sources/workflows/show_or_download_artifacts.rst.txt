:orphan:

##########################
Show or download artifacts
##########################

.. _show_and_download_artifacts:

.. join_slack::
   :align: left

----

******************
Show the artifacts
******************

1. Check available options for show
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The Training Studio App CLI provides its own help.

Here is the command to learn more:

.. code-block::

   lightning show artifacts --help

----

2. Show artifacts
^^^^^^^^^^^^^^^^^

To show all artifacts use the following command:

.. code-block::

   lightning show artifacts

.. code-block::

   📂 /thomas-d4fd7d7c/
   📂 /thomas-d4fd7d7c/29f40d6/
      /thomas-d4fd7d7c/29f40d6/config.yaml
      /thomas-d4fd7d7c/29f40d6/events.out.tfevents.1665501311.thomass-MacBook-Pro.local.52388.0
      /thomas-d4fd7d7c/29f40d6/hparams.yaml
   📂 /thomas-d4fd7d7c/29f40d6/checkpoints/
      /thomas-d4fd7d7c/29f40d6/checkpoints/epoch=0-step=20.ckpt
   📂 /thomas-d4fd7d7c/379c91d/
      /thomas-d4fd7d7c/379c91d/config.yaml
      /thomas-d4fd7d7c/379c91d/events.out.tfevents.1665501311.thomass-MacBook-Pro.local.52392.0
      /thomas-d4fd7d7c/379c91d/hparams.yaml
   📂 /thomas-d4fd7d7c/379c91d/checkpoints/
      /thomas-d4fd7d7c/379c91d/checkpoints/epoch=0-step=20.ckpt
   📂 /thomas-d4fd7d7c/4de6450/
      /thomas-d4fd7d7c/4de6450/events.out.tfevents.1665501312.thomass-MacBook-Pro.local.52389.0
   📂 /thomas-d4fd7d7c/740910d/
      /thomas-d4fd7d7c/740910d/config.yaml
      /thomas-d4fd7d7c/740910d/events.out.tfevents.1665501312.thomass-MacBook-Pro.local.52390.0
      /thomas-d4fd7d7c/740910d/hparams.yaml
   📂 /thomas-d4fd7d7c/740910d/checkpoints/
      /thomas-d4fd7d7c/740910d/checkpoints/epoch=0-step=20.ckpt
   📂 /thomas-d4fd7d7c/d0293aa/
      /thomas-d4fd7d7c/d0293aa/config.yaml
      /thomas-d4fd7d7c/d0293aa/events.out.tfevents.1665501312.thomass-MacBook-Pro.local.52393.0
      /thomas-d4fd7d7c/d0293aa/hparams.yaml
   📂 /thomas-d4fd7d7c/d0293aa/checkpoints/
      /thomas-d4fd7d7c/d0293aa/checkpoints/epoch=0-step=20.ckpt
   📂 /thomas-d4fd7d7c/f1a0cb6/
      /thomas-d4fd7d7c/f1a0cb6/config.yaml
      /thomas-d4fd7d7c/f1a0cb6/events.out.tfevents.1665501312.thomass-MacBook-Pro.local.52391.0
      /thomas-d4fd7d7c/f1a0cb6/hparams.yaml
   📂 /thomas-d4fd7d7c/f1a0cb6/checkpoints/
      /thomas-d4fd7d7c/f1a0cb6/checkpoints/epoch=0-step=20.ckpt
   📂 /uploaded_files/
   📂 /uploaded_files/file_server/
      /uploaded_files/file_server/thomas-d4fd7d7c


2. Show artifacts with filtering
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To filter the artifacts shown use the following command:

.. code-block::

   lightning show artifacts --names 29f40d6

.. code-block::

   📂 /thomas-d4fd7d7c/
   📂 /thomas-d4fd7d7c/29f40d6/
      /thomas-d4fd7d7c/29f40d6/config.yaml
      /thomas-d4fd7d7c/29f40d6/events.out.tfevents.1665501311.thomass-MacBook-Pro.local.52388.0
      /thomas-d4fd7d7c/29f40d6/hparams.yaml
   📂 /thomas-d4fd7d7c/29f40d6/checkpoints/
      /thomas-d4fd7d7c/29f40d6/checkpoints/epoch=0-step=20.ckpt
   Your command execution was successful.

******************
Download artifacts
******************

1. Check available options for download
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block::

   lightning download artifacts --help

2. Download artifacts
^^^^^^^^^^^^^^^^^^^^^

To download artifacts for experiment ``29f40d6``, use the following command:

.. code-block::

   lightning download artifacts --names 29f40d6 --output_dir=./output_artifacts

----

**********
Next Steps
**********

.. raw:: html

   <br />
   <div class="display-card-container">
      <div class="row">

.. displayitem::
   :header: Show or Download Logs
   :description: Learn how to interact with your Training Studio App logs
   :col_css: col-md-6
   :button_link: show_or_download_logs.html
   :height: 180

.. displayitem::
   :header: Run a Sweep
   :description: Learn how to run a Sweep with your own python script
   :col_css: col-md-6
   :button_link: run_sweep.html
   :height: 180

..
   .. displayitem::
      :header: Run a Notebook
      :description: Learn how to run a notebook locally or in the cloud
      :col_css: col-md-4
      :button_link: run_notebook.html
      :height: 180

.. raw:: html

      </div>
   </div>
