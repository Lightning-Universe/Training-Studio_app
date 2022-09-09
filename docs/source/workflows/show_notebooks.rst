:orphan:

##############
Show Notebooks
##############

.. _show_sweeps:

.. join_slack::
   :align: left

----

In order to view your notebooks, use this command:

.. code-block::

   lightning show notebooks

Here is the output of the command:

.. code-block::

    You are connected to the local Lightning App.
                                            Notebooks
   ┏━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
   ┃ id              ┃ name        ┃ status  ┃ desired_status ┃ cloud_compute ┃ requirements ┃
   ┡━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
   │ thomas-a130d079 │ notebook_2  │ stopped │ stopped        │ cpu           │ []           │
   │ thomas-c2dd597b │ my_notebook │ running │ running        │ cpu           │ []           │
   └─────────────────┴─────────────┴─────────┴────────────────┴───────────────┴──────────────┘

----

**********
Next Steps
**********

.. raw:: html

   <br />
   <div class="display-card-container">
      <div class="row">

.. displayitem::
   :header: Stop or delete a Notebook
   :description: Learn how to stop or delete an existing notebook
   :col_css: col-md-4
   :button_link: stop_or_delete_notebook.html
   :height: 180

.. displayitem::
   :header: Run a Sweep
   :description: Learn how to run a Sweep with your own python script
   :col_css: col-md-4
   :button_link: run_sweep.html
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
