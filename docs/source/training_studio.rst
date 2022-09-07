:orphan:

###############
Training Studio
###############

.. _training_studio:

.. twocolumns::
   :left:
      .. image:: https://pl-flash-data.s3.amazonaws.com/assets_lightning/training_app.png
         :alt: Logo of the App
   :right:
      The Training Studio App is a `Lightning App <https://github.com/Lightning-AI/lightning>`_ that enables you to quickly perform machine-learning research in collaborative ways by bringing
      all the tools you need in a single place (notebook, tensorboard, wandb, sweeps, etc...) and is runnable locally or on `lightning.ai <https://lightning.ai/>`_ platform.

.. join_slack::
   :align: center
   :margin: 0

----

**********************
User Flow - Admin User
**********************

Click on the `Lucidchart Diagram <https://lucid.app/lucidchart/9d513fd6-9410-4292-beac-29e73f1e1c34/edit?viewport_loc=-19%2C-798%2C6351%2C4441%2C0_0&invitationId=inv_d38b9a33-4915-4b7b-ab95-f73894923fbe#>`_ User Flow to understand how to use the Training Studio App.

The **Admin User** has access to the Admin View and the one who has run the App.

To launch the Lightning Training Studio App in the cloud, simply run:

.. code-block::

   git clone https://github.com/Lightning-AI/lightning-hpo
   cd lightning-hpo
   PACKAGE_LIGHTNING=1 lightning run app training_studio_app.py --cloud


Check :doc:`install guide <installation>` if you haven't done it yet.

To learn more about the codebase, request access to `recording <https://drive.google.com/file/d/1uqlV_06DkUZijCaqkCbc8arvVGdpzV_a/view>`_ by `@tchaton <https://github.com/tchaton>`_.

----

********************
User Flow - App User
********************

The **App User** has access to the App View and interacts with the Training Studio App by creating notebooks, sweeps, etc.

The **App User** isn't necessarily the **Admin User**, but it is also possible to connect to **someone else** Training Studio App.

As an **App User**, you can run **sweep**, **notebooks** and more. Keep reading to learn more.

----

*******************
Interact with Sweep
*******************

.. raw:: html

   <br />
   <div class="display-card-container">
      <div class="row">

.. displayitem::
   :header: Run a Sweep
   :description: Learn how to run a Sweep with your own python script
   :col_css: col-md-4
   :button_link: workflows/run_sweep.html
   :height: 180

.. displayitem::
   :header: Show Sweeps
   :description: Learn how to view the existing sweeps
   :col_css: col-md-4
   :button_link: workflows/show_sweeps.html
   :height: 180

.. displayitem::
   :header: Stop or delete a Sweep
   :description: Learn how to stop or delete an existing sweep
   :col_css: col-md-4
   :button_link: workflows/stop_or_delete_sweep.html
   :height: 180

.. raw:: html

      </div>
   </div>

----

**********************
Interact with Notebook
**********************

.. raw:: html

   <br />
   <div class="display-card-container">
      <div class="row">

.. displayitem::
   :header: Run a Notebook
   :description: Learn how to run a notebook locally or in the cloud
   :col_css: col-md-4
   :button_link: workflows/run_notebook.html
   :height: 180

.. displayitem::
   :header: Show Notebooks
   :description: Learn how to view the existing notebooks
   :col_css: col-md-4
   :button_link: workflows/show_notebooks.html
   :height: 180

.. displayitem::
   :header: Stop or delete a Notebook
   :description: Learn how to stop or delete an existing notebook
   :col_css: col-md-4
   :button_link: workflows/stop_or_delete_notebooks.html
   :height: 180

.. raw:: html

      </div>
   </div>

----

*************
App Utilities
*************

.. raw:: html

   <br />
   <div class="display-card-container">
      <div class="row">

.. displayitem::
   :header: Show or Download Artifacts
   :description: Learn how to interact with your Training Studio App artifacts
   :col_css: col-md-6
   :button_link: workflows/show_or_download_artifacts.html
   :height: 180

.. displayitem::
   :header: Show or Download Logs
   :description: Learn how to interact with your Training Studio App logs
   :col_css: col-md-6
   :button_link: workflows/show_or_download_logs.html
   :height: 180

.. raw:: html

      </div>
   </div>
