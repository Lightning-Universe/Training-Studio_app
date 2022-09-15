:orphan:

######################
Stop or delete a Sweep
######################

.. _stop_sweep:

.. join_slack::
   :align: left

----

************
Stop a Sweep
************

To stop a sweep use the following commnand:

.. code-block::

   lightning stop sweep --name=<sweep-name>

For example:

.. code-block::

   lightning stop sweep --name=thomas-0f615232

Here is the output of the command:

.. code-block::

   You are connected to the local Lightning App.
   Stopped the sweep `thomas-0f615232`
   Your command execution was successful

----

**************
Delete a Sweep
**************

To delete a sweep use the following command:

.. code-block::

   lightning delete sweep --name=<sweep-name>

For example:

.. code-block::

   lightning delete sweep --name=thomas-0f615232

----

**********
Next Steps
**********

.. raw:: html

   <br />
   <div class="display-card-container">
      <div class="row">

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

.. displayitem::
   :header: Show or Download Logs
   :description: Learn how to interact with your Training Studio App logs
   :col_css: col-md-4
   :button_link: show_or_download_logs.html
   :height: 180

.. raw:: html

      </div>
   </div>
