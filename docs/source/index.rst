.. lightning documentation master file, created by
   sphinx-quickstart on Sat Sep 19 16:37:02 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

###########################
Welcome to ⚡ Lightning HPO
###########################

.. twocolumns::
   :left:
      .. image:: https://pl-flash-data.s3.amazonaws.com/assets_lightning/Lightning.gif
         :alt: Animation showing how to convert a standard training loop to a Lightning loop
   :right:
      The `open-source Lightning HPO <https://github.com/Lightning-AI/lightning-hpo>`_ gives ML Researchers and Data Scientists, the fastest & most flexible
      way to iterate on ML research ideas and deliver scalable ML systems with the performance enterprises requires at the same time.

.. join_slack::
   :align: center
   :margin: 0

----

*********************
Install Lightning HPO
*********************

.. code-block:: bash

   pip install lightning-hpo

Or read the :ref:`advanced install <install>` guide.

----

***********
Get Started
***********

.. raw:: html

   <br />
   <div class="display-card-container">
      <div class="row">

.. displayitem::
   :header: Discover what Lightning Apps can do in 5 min
   :description: Browse through mind-blowing ML Systems
   :col_css: col-md-6
   :button_link: get_started/what_app_can_do.html
   :height: 180

.. displayitem::
   :header: Fundamentals about HyperParameter Optimization (HPO)
   :description: Learn about its inner workings
   :col_css: col-md-6
   :button_link: get_started/fundamentals.html
   :height: 180

.. displayitem::
   :header: Use Lightning HPO with your own scripts
   :description: Discover PyTorch Lightning and train your first Model.
   :col_css: col-md-6
   :button_link: get_started/build_model.html
   :height: 180

.. displayitem::
   :header: The Training Studio App
   :description: Use your own App or share it with your teammates.
   :col_css: col-md-6
   :button_link: get_started/training_with_apps.html
   :height: 180

.. raw:: html

      </div>
   </div>

----

.. raw:: html

   <hr class="docutils" style="margin: 50px 0 50px 0">

.. raw:: html

   <div style="display:none">

.. toctree::
   :maxdepth: 1
   :caption: Home

   self

.. toctree::
   :maxdepth: 1
   :caption: Get Started

   installation
   workflows/sweep
   training_studio

.. toctree::
   :maxdepth: 1
   :caption: Lightning HPO: How to...

   Convert from raw Optuna <workflows/convert_from_raw_optuna>
   Optimize with PyTorch Lightning <workflows/optimize_with_pytorch_lightning>
   Configure your loggers <workflows/loggers>

.. toctree::
   :maxdepth: 1
   :caption: Training Studio: How to...

   Connect or Disconnect to a Lightning App <workflows/connect_or_disconnect>
   Run a Sweep <workflows/run_sweep>
   Run a Notebook <workflows/run_notebook>
   Show Sweeps <workflows/show_sweeps>
   Show Notebooks <workflows/show_notebooks>
   Stop or delete a Sweep <workflows/stop_or_delete_sweep>
   Stop or delete a Notebook <workflows/stop_or_delete_notebook>
   Show or download Artefacts <workflows/show_or_download_artifacts>
   Show or download Logs <workflows/show_or_download_logs>
