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

    lightning connect {APP_ID_OR_NAME_OR_LOCALHOST} --yes

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

    Storing `show_artefacts` under {HOME}/.lightning/lightning_connection/commands/show_artefacts.py
    You can review all the downloaded commands under {HOME}/.lightning/lightning_connection/commands folder.

    Storing `download_artefacts` under {HOME}/.lightning/lightning_connection/commands/download_artefacts.py
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
        delete sweep
        download artefacts
        run notebook
        run sweep
        show artefacts
        show notebooks
        show sweeps
        stop notebook
        stop sweep
