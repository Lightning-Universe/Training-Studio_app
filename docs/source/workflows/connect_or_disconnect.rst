:orphan:

##########################
Connect to a Lightning App
##########################

The `Lightning App framework <https://github.com/Lightning-AI/lightning>`_ provides a mechanism
to easily expose command-line interfaces and connect to an application
to easily download and utilize the CLI.

.. _connect_app:

.. join_slack::
   :align: left

----

*******************
The Connect Command
*******************

Once a Lightning App is running locally or in the cloud, your can simply connect to it as follows:

.. code-block::

   lightning connect {CLOUD_APP_NAME} --yes

.. code-block::

   lightning connect localhost --yes

   Storing `delete_sweep` under {HOME}/.lightning/lightning_connection/commands/delete_sweep.py
   You can review all the downloaded commands under {HOME}/.lightning/lightning_connection/commands folder.

   Storing `run_sweep` under {HOME}/.lightning/lightning_connection/commands/run_sweep.py
   You can review all the downloaded commands under {HOME}/.lightning/lightning_connection/commands folder.

   Storing `show_sweeps` under {HOME}/.lightning/lightning_connection/commands/show_sweeps.py
   You can review all the downloaded commands under {HOME}/.lightning/lightning_connection/commands folder.

   Storing `stop_sweep` under {HOME}/.lightning/lightning_connection/commands/stop_sweep.py
   You can review all the downloaded commands under {HOME}/.lightning/lightning_connection/commands folder.

   Storing `run_notebook` under {HOME}/.lightning/lightning_connection/commands/run_notebook.py
   You can review all the downloaded commands under {HOME}/.lightning/lightning_connection/commands folder.

   Storing `stop_notebook` under {HOME}/.lightning/lightning_connection/commands/stop_notebook.py
   You can review all the downloaded commands under {HOME}/.lightning/lightning_connection/commands folder.

   Storing `show_notebooks` under {HOME}/.lightning/lightning_connection/commands/show_notebooks.py
   You can review all the downloaded commands under {HOME}/.lightning/lightning_connection/commands folder.

   Storing `show_artifacts` under {HOME}/.lightning/lightning_connection/commands/show_artifacts.py
   You can review all the downloaded commands under {HOME}/.lightning/lightning_connection/commands folder.

   Storing `download_artifacts` under {HOME}/.lightning/lightning_connection/commands/download_artifacts.py
   You can review all the downloaded commands under {HOME}/.lightning/lightning_connection/commands folder.

   You are connected to the local Lightning App.

Learn more `there <https://github.com/Lightning-AI/lightning/tree/master/docs/source-app/workflows/build_command_line_interface>`_.

----

**********************
The Disconnect Command
**********************

If you are already connected to a Lightning App, disconnect from the App using the following command:

.. code-block::

   lightning disconnect

.. code-block::

   You are disconnected from the local Lightning App.

----

*******************
Training Studio CLI
*******************

The Lightning Training Studio App provides a CLI to interact with the App once running.

.. code-block::

    lightning --help

    You are connected to the local Lightning App.

    Usage: lightning [OPTIONS] COMMAND [ARGS]...

      --help     Show this message and exit.

    Lightning App Commands
      create data        Create a Data association by providing a public S3 bucket and an optional mount point.
                         The contents of the bucket can be then mounted on experiments and sweeps and
                         accessed through the filesystem.
      delete data        Delete a data association. Note that this will not delete the data itself,
                         it will only make it unavailable to experiments and sweeps.
      delete experiment  Delete an experiment. Note that artifacts will still be available after the operation.
      delete sweep       Delete a sweep. Note that artifacts will still be available after the operation.
      download artifacts Download artifacts for experiments or sweeps.
      run experiment     Run an experiment by providing a script, the cloud compute type and optional
                         data entries to be made available at a given path.
      run sweep          Run a sweep by providing a script, the cloud compute type and optional
                         data entries to be made available at a given path. Hyperparameters can be
                         provided as lists (`model.lr="[0.01, 0.1]"`) or using distributions
                         (`model.lr="uniform(0.01, 0.1)"`, `model.lr="log_uniform(0.01, 0.1)"`).
                         Hydra multirun override syntax is also supported.
      show artifacts     Show artifacts for experiments or sweeps, in flat or tree layout.
      show data          List all data associations.
      show experiments   Show experiments and their statuses.
      show logs          Show logs of an experiment or a sweep. Optionally follow logs as they stream.
      show sweeps        Show all sweeps and their statuses, or the experiments for a given sweep.
      stop experiment    Stop an experiment. Note that currently experiments cannot be resumed.
      stop sweep         Stop all experiments in a sweep. Note that currently sweeps cannot be resumed.

----

**********
Next Steps
**********

.. raw:: html

   <br />
   <div class="display-card-container">
      <div class="row">

.. displayitem::
   :header: Run a Sweep or Experiment
   :description: Learn how to run a Sweep with your own python script
   :col_css: col-md-4
   :button_link: run_sweep.html
   :height: 180

.. displayitem::
   :header: Show Sweeps & Experiments
   :description: Learn how to view the existing sweeps
   :col_css: col-md-4
   :button_link: show_sweeps.html
   :height: 180

.. displayitem::
   :header: Stop or delete a Sweep & Experiment
   :description: Learn how to stop or delete an existing sweep
   :col_css: col-md-4
   :button_link: stop_or_delete_sweep.html
   :height: 180

..
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
