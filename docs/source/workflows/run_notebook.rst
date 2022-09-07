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
   usage: notebook [-h] [--requirements REQUIREMENTS [REQUIREMENTS ...]]
                  [--cloud_compute CLOUD_COMPUTE]
                  name

   positional arguments:
   name                  The name of your notebook to run.

   optional arguments:
   -h, --help            show this help message and exit
   --requirements REQUIREMENTS [REQUIREMENTS ...]
                           Requirements file.
   --cloud_compute CLOUD_COMPUTE
                           The machine to use in the cloud.

----

*****************
2. Run a Notebook
*****************

You can simply start a notebook as follows:

.. code-block::

   lightning run notebook my_notebook

.. code-block::

   You are connected to the local Lightning App.
   The notebook `my_notebook` has been created.
   Your command execution was successful
