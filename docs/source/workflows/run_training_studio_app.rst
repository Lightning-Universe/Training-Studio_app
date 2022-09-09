:orphan:

###########################
Run the Training Studio App
###########################

.. _run_the_training_studio_app:

.. join_slack::
   :align: left

----

*************************
1. Setup your environment
*************************

In order to run the Training Studio App, you need to complete the :doc:`installation guide <../installation>`.

----

**********************
2. Run the App locally
**********************

Once you are setup, you can run the App locally from the **lightning-hpo** directory as follows:

.. code-block::

    lightning run app training_studio_app.py

If you want to enable the `Weights And Biases Logger <https://wandb.ai/>`_, follow the following :doc:`guide <loggers/wandb>`.

----

***************************
3. Run the App in the cloud
***************************

.. note:: This is only temporary as some changes are being released to PiPy

First, you would need to install the **lightning** in editable mode on the lightning ``small_fixes`` branch.

.. code-block::

   git clone https://github.com/Lightning-AI/lightning
   git checkout small_fixes
   pip install -e .

Secondly, you would need to set the **PACKAGE_LIGHTNING=1** environment variable to package the ``small_fixes`` branch in the cloud.

.. code-block::

   PACKAGE_LIGHTNING=1 lightning run app training_studio_app.py --cloud

If you see the following lines in your terminal, this means everything should work as expected !

.. code-block::

   Your Lightning App is starting. This won't take long.
   The Lightning UI has successfully been downloaded!
   INFO: Packaged Lightning with your application.

----

**********
Next Steps
**********

.. raw:: html

   <br />
   <div class="display-card-container">
      <div class="row">

.. displayitem::
   :header: Run a Sweep
   :description: Learn how to run a Sweep with your own python script
   :col_css: col-md-4
   :button_link: run_sweep.html
   :height: 180

.. displayitem::
   :header: Show Sweeps
   :description: Learn how to view the existing sweeps
   :col_css: col-md-4
   :button_link: show_sweeps.html
   :height: 180

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
   :header: Show Notebooks
   :description: Learn how to view the existing notebooks
   :col_css: col-md-4
   :button_link: show_notebooks.html
   :height: 180

.. displayitem::
   :header: Stop or delete a Notebook
   :description: Learn how to stop or delete an existing notebook
   :col_css: col-md-4
   :button_link: stop_or_delete_notebook.html
   :height: 180

.. displayitem::
   :header: Show or Download Artifacts
   :description: Learn how to interact with your Training Studio App artifacts
   :col_css: col-md-6
   :button_link: show_or_download_artifacts.html
   :height: 180

.. displayitem::
   :header: Show or Download Logs
   :description: Learn how to interact with your Training Studio App logs
   :col_css: col-md-6
   :button_link: show_or_download_logs.html
   :height: 180

.. raw:: html

      </div>
   </div>
