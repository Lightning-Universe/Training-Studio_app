:orphan:

###########
Show Sweeps
###########

.. _show_sweeps:

.. join_slack::
   :align: left

----

**************************
1. Check available options
**************************

The Training Studio App CLI provides its own help.

.. code-block::

   lightning show sweeps --help

Here is the output of the command:

.. code-block::

   You are connected to the local Lightning App.
   usage: sweeps [-h] [--name NAME]

   optional arguments:
   -h, --help   show this help message and exit
   --name NAME  Provide the `name` to be showed.

----

**************
2. Show Sweeps
**************

To show your sweeps the use the following command:

.. code-block::

   lightning show sweeps

Here is the output of the command:

.. code-block::

   ┏━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━┓
   ┃ name            ┃ status    ┃ framework       ┃ cloud_compute ┃ n_trials ┃ n_trials_done ┃
   ┡━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━┩
   │ thomas-85982a9b │ succeeded │ pytorch_lightn… │ cpu           │ 10       │ 10            │
   │ thomas-1dbfed8a │ failed    │ pytorch_lightn… │ cpu           │ 10       │ 0             │
   │ thomas-b4a4b274 │ failed    │ pytorch_lightn… │ cpu           │ 10       │ 0             │
   │ thomas-5660535a │ succeeded │ pytorch_lightn… │ cpu-medium    │ 3        │ 3             │
   └─────────────────┴───────────┴─────────────────┴───────────────┴──────────┴───────────────┘

To show the details of a specific sweep use the following command:

.. code-block::

   lightning show sweeps --name=<sweep-id>

For example:

.. code-block::

   lightning show sweeps --name=thomas-f5fee22a

Here is the output of the command:

.. code-block::

   You are connected to the local Lightning App.
                                             Sweep
   ┏━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━┓
   ┃ name            ┃ status  ┃ framework         ┃ cloud_compute ┃ n_trials ┃ n_trials_done ┃
   ┡━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━┩
   │ thomas-5660535a │ succeeded │ pytorch_lightn… │ cpu-medium    │ 3        │ 3             │
   └─────────────────┴─────────┴───────────────────┴───────────────┴──────────┴───────────────┘
                              Trials monitor=(val_acc)
   ┏━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┓
   ┃ name ┃ status    ┃ best_model_score ┃ model.lr ┃ model.gamma ┃ data.batch_size ┃
   ┡━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
   │ 0    │ succeeded │ 0.11             │ 0.09119  │ 0.76141     │ 64              │
   │ 1    │ succeeded │ 0.12             │ 0.04976  │ 0.74855     │ 32              │
   │ 2    │ succeeded │ 0.11             │ 0.03404  │ 0.58845     │ 64              │
   └──────┴───────────┴──────────────────┴──────────┴─────────────┴─────────────────┘

----

**********
Next Steps
**********

.. raw:: html

   <br />
   <div class="display-card-container">
      <div class="row">

.. displayitem::
   :header: Stop or delete a Sweep
   :description: Learn how to stop or delete an existing sweep
   :col_css: col-md-4
   :button_link: stop_or_delete_sweep.html
   :height: 180

.. displayitem::
   :header: Run a Notebook
   :description: Learn how to run a notebook locally or in the cloud
   :col_css: col-md-4
   :button_link: run_notebook.html
   :height: 180

.. displayitem::
   :header: Show or Download Artifacts
   :description: Learn how to interact with your Training Studio App artifacts
   :col_css: col-md-4
   :button_link: show_or_download_artifacts.html
   :height: 180

.. raw:: html

      </div>
   </div>
