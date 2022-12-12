.. lightning documentation master file, created by
   sphinx-quickstart on Sat Sep 19 16:37:02 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

#####################################
PyTorch Lightning Training Studio App
#####################################

Build models ⚡ *Lightning fast*.

.. join_slack::
   :align: left

----

*****
Setup
*****

.. lit_tabs::
   :descriptions: 1. Install the Training Studio; 2. Duplicate the Training Studio on your own account; 3. Connect to the App Training Studio
   :code_files: /setup/pip.bash; /setup/duplicate.bash; /setup/connect.bash; example/show_experiment_and_sweep.bash
   :tab_rows: 4
   :height: 290px

----

***************
Run an example
***************

Run a Lightning Trainer script in the cloud.

.. lit_tabs::
   :titles: 1. Lightning Trainer Example; 2. Prepare locally; 2. Launch an experiment; 3. Launch a Grid Search; 4. Show experiment & Sweeps; 5. Show logs; 6. Show & Download Artifacts; 7. Use your own data; 8. Stop & Delete Experiments or Sweep; 9 Getting Help;
   :code_files: example/script.py; example/prepare.bash; example/experiment.bash; example/sweep.bash; example/show_experiment_and_sweep.bash; example/logs.bash; example/artifacts.bash; example/data.bash; example/stop_delete.bash; example/help.bash
   :highlights:
   :works:
   :enable_run: false
   :tab_rows: 3
   :height: 540px

----

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
