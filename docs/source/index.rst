.. lightning documentation master file, created by
   sphinx-quickstart on Sat Sep 19 16:37:02 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

##########################
Training Studio CheatSheet
##########################

Build models ⚡ *Lightning fast*.

.. join_slack::
   :align: left

----

*****
Setup
*****

First, install Lightning & Lightning-HPO.

.. lit_tabs::
   :descriptions: Pip; Macs, Apple Silicon (M1/M2/M3); Windows
   :code_files: /install/pip.bash; /install/mac.bash; /install/windows.bash
   :tab_rows: 4
   :height: 180px

----

**************************************
Want to start a hyper-parameter sweep?
**************************************

.. lit_tabs::
   :titles: 1. Connect to the app; 2. Create a new folder & move inside; 3. Copy & paste this Lightning Trainer script to a train.py file; 4. Launch a Grid Search Sweep; 5. Launch a Grid Search Sweep on GPU; 6. Use CLI help to learn more
   :code_files: sweep/connect.bash; sweep/new_folder.bash; sweep/script.py; sweep/sweep.bash; sweep/sweep_gpu.bash; sweep/help.bash
   :highlights:
   :works:
   :enable_run: false
   :tab_rows: 5
   :height: 620px

----

**************************
Want to use your own data?
**************************

.. lit_tabs::
   :titles: 1. Connect to the app; 2. Add your own Datasets from s3; 3. Show your Datasets; 4. Use your Datasets with a Sweep
   :code_files: sweep/connect.bash; data/add.bash; data/show.bash; data/sweep.bash;
   :highlights:
   :works:
   :enable_run: false
   :tab_rows: 5

----

************************************************
What else can I do with the Training Studio App?
************************************************

.. lit_tabs::
   :titles: General Usage Information; Granular Usage Information; Show Experiments & Sweeps; Show Logs; Show & Download Artifacts
   :code_files: extra/help.bash; extra/help_module.bash; extra/experiment_and_sweep.bash; extra/logs.bash; extra/artifacts.bash
   :highlights:
   :works:
   :enable_run: false
   :tab_rows: 5

.. .. note:: This is only temporary as some changes are being released to PiPy

.. Python 3.8.x or later (3.8.x, 3.9.x, 3.10.x)

.. .. code-block:: bash

..    git clone https://github.com/Lightning-AI/lightning-hpo && cd lightning-hpo

..    pip install -e . -r requirements.txt --find-links https://download.pytorch.org/whl/cpu/torch_stable.html

.. Make sure everything works locally:

.. .. code-block:: bash

..    python -m lightning run app app.py

.. Make sure everything works in the cloud:

.. .. code-block:: bash

..    PACKAGE_LIGHTNINGpython -m lightning run app app.py --cloud

.. .. note:: On MacOS, if you face OSError: [Errno 24] Too many open files, you can increase the process limit with: **ulimit -Sn 50000**

.. ----

.. ***********
.. Get Started
.. ***********

.. .. raw:: html

..    <br />
..    <div class="display-card-container">
..       <div class="row">

.. .. displayitem::
..    :header: The Training Studio App
..    :description: Manage Sweeps and Experiments to accelerate Training.
..    :col_css: col-md-12
..    :button_link: training_studio.html
..    :height: 180

.. .. raw:: html

..    <hr class="docutils" style="margin: 50px 0 50px 0">

.. .. raw:: html

..    <div style="display:none">

.. .. toctree::
..    :maxdepth: 1
..    :caption: Home

..    self

.. .. toctree::
..    :maxdepth: 1
..    :caption: Get Started

..    installation
..    training_studio

.. .. toctree::
..    :maxdepth: 1
..    :caption: Use Training Studio to...

..    Run the Training Studio App <workflows/run_training_studio_app>
..    Connect or Disconnect to a Lightning App <workflows/connect_or_disconnect>
..    Run a Sweep or Experiment <workflows/run_sweep>
..    Show Sweeps or Experiments <workflows/show_sweeps>
..    Stop or delete a Sweep or Experiment <workflows/stop_or_delete_sweep>
..    Show or download Artifacts <workflows/show_or_download_artifacts>
..    Show or download Logs <workflows/show_or_download_logs>

..
   Run a Notebook <workflows/run_notebook>
   Show Sweeps <workflows/show_sweeps>
   Show Notebooks <workflows/show_notebooks>
   Stop or delete a Sweep <workflows/stop_or_delete_sweep>
   Stop or delete a Notebook <workflows/stop_or_delete_notebook>
   Show or download Artifacts <workflows/show_or_download_artifacts>
   Show or download Logs <workflows/show_or_download_logs>

..
   .. toctree::
      :maxdepth: 1
      :caption: Use Lightning HPO to...

      Convert from raw Optuna <workflows/convert_from_raw_optuna>
      Optimize with PyTorch Lightning <workflows/optimize_with_pytorch_lightning>
      Configure your loggers <workflows/loggers>
