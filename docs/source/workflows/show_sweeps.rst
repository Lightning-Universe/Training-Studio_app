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
   usage: sweeps [-h] [--sweep_id SWEEP_ID]

   optional arguments:
   -h, --help           show this help message and exit
   --sweep_id SWEEP_ID  Provide the `sweep_id` to be showed.

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
   ┃ id              ┃ status    ┃ framework       ┃ cloud_compute ┃ n_trials ┃ n_trials_done ┃
   ┡━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━┩
   │ thomas-85982a9b │ succeeded │ pytorch_lightn… │ cpu           │ 10       │ 10            │
   │ thomas-1dbfed8a │ failed    │ pytorch_lightn… │ cpu           │ 10       │ 0             │
   │ thomas-b4a4b274 │ failed    │ pytorch_lightn… │ cpu           │ 10       │ 0             │
   │ thomas-f5fee22a │ running   │ pytorch_lightn… │ cpu           │ 10       │ 5             │
   └─────────────────┴───────────┴─────────────────┴───────────────┴──────────┴───────────────┘

To show the details of a specific sweep use the following command:

.. code-block::

   lightning show sweeps --sweep_id=<sweep-id>

For example:

.. code-block::

   lightning show sweeps --sweep_id=thomas-f5fee22a

Here is the output of the command:

.. code-block::

   You are connected to the local Lightning App.
                                             Sweep
   ┏━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━┓
   ┃ id              ┃ status  ┃ framework         ┃ cloud_compute ┃ n_trials ┃ n_trials_done ┃
   ┡━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━┩
   │ thomas-f5fee22a │ running │ pytorch_lightning │ cpu           │ 10       │ 5             │
   └─────────────────┴─────────┴───────────────────┴───────────────┴──────────┴───────────────┘
                                             Trials
   ┏━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┓
   ┃ id ┃ status    ┃ best_model_score ┃ params                                        ┃ monitor ┃
   ┡━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━┩
   │ 0  │ succeeded │ 0.05             │ {'model.lr': 0.02647, 'data.batch_size': 4.0} │ val_acc │
   │ 1  │ succeeded │ 0.15             │ {'model.lr': 0.0588, 'data.batch_size': 4.0}  │ val_acc │
   │ 2  │ succeeded │ 0.15             │ {'model.lr': 0.06855, 'data.batch_size': 4.0} │ val_acc │
   │ 3  │ succeeded │ 0.12             │ {'model.lr': 0.07618, 'data.batch_size': 8.0} │ val_acc │
   │ 4  │ succeeded │ 0.15             │ {'model.lr': 0.05112, 'data.batch_size': 4.0} │ val_acc │
   │ 5  │ pending   │ None             │ {'model.lr': 0.09735, 'data.batch_size': 4.0} │ None    │
   └────┴───────────┴──────────────────┴───────────────────────────────────────────────┴─────────┘
