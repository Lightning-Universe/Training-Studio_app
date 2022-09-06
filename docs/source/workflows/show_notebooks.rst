:orphan:

##############
Show Notebooks
##############

.. _show_sweeps:

.. join_slack::
   :align: left

----

In order to view your notebooks, simply run the following command:

.. code-block::

   lightning show notebooks

Here is the output of such command above:

.. code-block::

    You are connected to the local Lightning App.
                                            Notebooks
   ┏━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
   ┃ id              ┃ name        ┃ status  ┃ desired_status ┃ cloud_compute ┃ requirements ┃
   ┡━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
   │ thomas-a130d079 │ notebook_2  │ stopped │ stopped        │ cpu           │ []           │
   │ thomas-c2dd597b │ my_notebook │ running │ running        │ cpu           │ []           │
   └─────────────────┴─────────────┴─────────┴────────────────┴───────────────┴──────────────┘
