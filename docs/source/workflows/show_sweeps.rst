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

The Research Studio App CLI provides its own help.

.. code-block::

   lightning show sweeps --help

.. code-block::

   lightning show experiments --help

----

*******************
2. Show Experiments
*******************

To show your experiments the use the following command:

.. code-block::

   lightning show experiments

Here is the output of the command:

.. code-block::

   You are connected to the local Lightning App.
                           Experiments
   ┏━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┓
   ┃ name    ┃ progress  ┃ best_model_score ┃ sweep_name      ┃
   ┡━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━┩
   │ 062bb69 │ succeeded │ 0.68             │ thomas-d68d9d5d │
   │ 9a817ad │ succeeded │ 0.43             │ thomas-d68d9d5d │
   │ 1dccc66 │ succeeded │ 0.12             │ thomas-d68d9d5d │
   │ 06901f0 │ succeeded │ 0.68             │ thomas-d68d9d5d │
   │ 9ec7672 │ succeeded │ 0.11             │ thomas-d68d9d5d │
   │ f511bd1 │ succeeded │ 0.11             │ thomas-d68d9d5d │
   └─────────┴───────────┴──────────────────┴─────────────────┘
   Your command execution was successful.

----

**************
3. Show Sweeps
**************

To show your sweeps the use the following command:

.. code-block::

   lightning show sweeps

Here is the output of the command:

.. code-block::

   You are connected to the local Lightning App.
                                            Sweeps
   ┏━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┓
   ┃ name            ┃ status    ┃ cloud_compute ┃ total_experiments ┃ total_experiments_done ┃
   ┡━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━┩
   │ thomas-d68d9d5d │ succeeded │ cpu           │ 6                 │ 6                      │
   └─────────────────┴───────────┴───────────────┴───────────────────┴────────────────────────┘
   Your command execution was successful.

To show the details of a specific sweep use the following command:

.. code-block::

   lightning show sweeps --name=<sweep-id>

For example:

.. code-block::

   lightning show sweeps --name=thomas-d68d9d5d

Here is the output of the command:

.. code-block::

   You are connected to the local Lightning App.
                                           Sweep
   ┏━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┓
   ┃ id              ┃ status    ┃ cloud_compute ┃ total_experiments ┃ total_experiments_done ┃
   ┡━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━┩
   │ thomas-d68d9d5d │ succeeded │ cpu           │ 6                 │ 6                      │
   └─────────────────┴───────────┴───────────────┴───────────────────┴────────────────────────┘
                     Experiments monitor=(val_acc)
   ┏━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━┓
   ┃ name    ┃ progress ┃ best_model_score ┃ data.batch ┃ model.lr ┃
   ┡━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━┩
   │ 062bb69 │ 100.0    │ 0.68             │ 32         │ 0.01     │
   │ 9a817ad │ 100.0    │ 0.43             │ 32         │ 0.02     │
   │ 1dccc66 │ 100.0    │ 0.12             │ 32         │ 0.03     │
   │ 06901f0 │ 100.0    │ 0.68             │ 64         │ 0.01     │
   │ 9ec7672 │ 100.0    │ 0.11             │ 64         │ 0.02     │
   │ f511bd1 │ 100.0    │ 0.11             │ 64         │ 0.03     │
   └─────────┴──────────┴──────────────────┴────────────┴──────────┘
   Your command execution was successful.

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
   :col_css: col-md-6
   :button_link: stop_or_delete_sweep.html
   :height: 180

..
   .. displayitem::
      :header: Run a Notebook
      :description: Learn how to run a notebook locally or in the cloud
      :col_css: col-md-4
      :button_link: run_notebook.html
      :height: 180

.. displayitem::
   :header: Show or Download Artifacts
   :description: Learn how to interact with your Research Studio App artifacts
   :col_css: col-md-6
   :button_link: show_or_download_artifacts.html
   :height: 180

.. raw:: html

      </div>
   </div>
