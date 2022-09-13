:orphan:

##############
Run a Notebook
##############

.. _run_notebook:

.. join_slack::
   :align: left

----

**************************
1. Check available options
**************************

The Training Studio App CLI provides its own help.

.. code-block::

   lightning run notebook --help

Here is the output of the command:

.. code-block::

   You are connected to the local Lightning App.
   usage: notebook [-h] [--name NAME] [--requirements REQUIREMENTS [REQUIREMENTS ...]]
                  [--cloud_compute CLOUD_COMPUTE]

   optional arguments:
   -h, --help              show this help message and exit
   --name NAME             The name of your notebook to run.
   --requirements REQUIREMENTS [REQUIREMENTS ...]
                           Requirements file.
   --cloud_compute CLOUD_COMPUTE
                           The machine to use in the cloud.
   --drive DRIVE           The path to a public S3 bucket to mount in the notebook.
   --drive_mount_dir DRIVE_MOUNT_DIR
                           The path where the drive will be mounted.

----

*****************
2. Run a Notebook
*****************

You can simply start a notebook as follows:

.. code-block::

   lightning run notebook --name=my_notebook

.. code-block::

   You are connected to the local Lightning App.
   The notebook `my_notebook` has been created.
   Your command execution was successful

----

*********************
3. Mount an S3 Bucket
*********************

You can mount a public S3 bucket to your notebook using the ``--drive`` flag as follows:

.. code-block::

   lightning run notebook --name=my_notebook --drive="s3://pl-flash-data/"

.. code-block::

   You are connected to the local Lightning App.
   The notebook `my_notebook` has been created.
   Your command execution was successful

.. note:: By default this will mount the bucket under ``/data``. The mount directory can be changed with the ``--drive_mount_dir`` flag.

----

**********
Next Steps
**********

.. raw:: html

   <br />
   <div class="display-card-container">
      <div class="row">

.. displayitem::
   :header: Run a Notebook with a Drive
   :description: Learn how to view the existing notebooks
   :col_css: col-md-4
   :button_link: run_notebook_with_drive.html
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
   :header: Run a Sweep
   :description: Learn how to run a Sweep with your own python script
   :col_css: col-md-4
   :button_link: run_sweep.html
   :height: 180


.. raw:: html

      </div>
   </div>
