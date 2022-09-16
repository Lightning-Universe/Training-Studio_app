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

*****************************************************
Install Lightning HPO and Run the Training Studio App
*****************************************************

.. note:: This is only temporary as some changes are being released to PiPy

Python 3.8.x or later (3.8.x, 3.9.x, 3.10.x)

.. code-block:: bash

   git clone https://github.com/Lightning-AI/lightning-hpo && cd lightning-hpo

   pip install -r requirements.txt -r requirements/test.txt --find-links https://download.pytorch.org/whl/cpu/torch_stable.html

   cd .. && git clone -b reduce_cost https://github.com/Lightning-AI/lightning.git && cd lightning && pip install -e .

   cd ../lightning-hpo && pip install -e .


Make sure everything works fine.

.. code-block:: bash

   python -m lightning run app app.py

Here is how the Training Studio App looks like:

.. raw:: html

   <video id="background-video" autoplay loop muted controls poster="https://pl-flash-data.s3.amazonaws.com/assets_lightning/training_studio_example.PNG" width="100%">
      <source src="https://pl-flash-data.s3.amazonaws.com/assets_lightning/training_studio.mp4" type="video/mp4" width="100%">
   </video>

.. note:: On MacOS, if you face OSError: [Errno 24] Too many open files, you can increase the process limit with: **ulimit -Sn 50000**

----

***********
Get Started
***********

.. raw:: html

   <br />
   <div class="display-card-container">
      <div class="row">

.. displayitem::
   :header: The Training Studio App
   :description: Manage Sweeps and Tools to accelerate Training.
   :col_css: col-md-6
   :button_link: training_studio.html
   :height: 180

.. displayitem::
   :header: Run a Sweep with PyTorch Lightning
   :description: Discover PyTorch Lightning and train your first Model.
   :col_css: col-md-6
   :button_link: workflows/optimize_with_pytorch_lightning.html
   :height: 180

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
   training_studio

.. toctree::
   :maxdepth: 1
   :caption: Training Studio: How to...

   Run the Training Studio App <workflows/run_training_studio_app>
   Connect or Disconnect to a Lightning App <workflows/connect_or_disconnect>
   Run a Sweep <workflows/run_sweep>
   Run a Notebook <workflows/run_notebook>
   Show Sweeps <workflows/show_sweeps>
   Show Notebooks <workflows/show_notebooks>
   Stop or delete a Sweep <workflows/stop_or_delete_sweep>
   Stop or delete a Notebook <workflows/stop_or_delete_notebook>
   Show or download Artefacts <workflows/show_or_download_artifacts>
   Show or download Logs <workflows/show_or_download_logs>

.. toctree::
   :maxdepth: 1
   :caption: Lightning HPO: How to...

   Convert from raw Optuna <workflows/convert_from_raw_optuna>
   Optimize with PyTorch Lightning <workflows/optimize_with_pytorch_lightning>
   Configure your loggers <workflows/loggers>
