:orphan:

##########################
Show or download artifacts
##########################

.. _run_sweep:

.. join_slack::
   :align: left

----

******************
Show the arfefacts
******************

1. Check available options
^^^^^^^^^^^^^^^^^^^^^^^^^^

The Training Studio App CLI provides an help.

.. code-block::

   lightning show artefacts --help

Here is the output of such command above:

.. code-block::

   You are connected to the local Lightning App.
   usage: artefacts [-h] [--include INCLUDE] [--exclude EXCLUDE]

   optional arguments:
   -h, --help         show this help message and exit
   --include INCLUDE  Provide a regex to include some specific files.
   --exclude EXCLUDE  Provide a regex to exclude some specific files.


2. Show artifacts
^^^^^^^^^^^^^^^^^

.. code-block::

   lightning show artefacts

.. code-block::

   📂 root
   ┣━━ 📂 artifacts
   ┃   ┗━━ 📂 drive
   ┃       ┣━━ 📂 code
   ┃       ┃   ┗━━ 📂 root.file_server
   ┃       ┃       ┣━━ 📄 thomas-0f615232
   ┃       ┃       ┣━━ 📄 thomas-0f615232.meta
   ┃       ┃       ┣━━ 📄 thomas-1dbfed8a
   ┃       ┃       ┣━━ 📄 thomas-1dbfed8a.meta
   ┃       ┃       ┣━━ 📄 thomas-253b59ae
   ┃       ┃       ┣━━ 📄 thomas-253b59ae.meta
   ┃       ┃       ┣━━ 📄 thomas-32be6709
   ┃       ┃       ┣━━ 📄 thomas-32be6709.meta
   ┃       ┃       ┣━━ 📄 thomas-3623090a
   ┃       ┃       ┣━━ 📄 thomas-3623090a.meta
   ┃       ┃       ┣━━ 📄 thomas-3c60d734
   ┃       ┃       ┣━━ 📄 thomas-3c60d734.meta
   ┃       ┃       ┣━━ 📄 thomas-5bad4fb7
   ┃       ┃       ┣━━ 📄 thomas-5bad4fb7.meta
   ┃       ┃       ┣━━ 📄 thomas-85982a9b
   ┃       ┃       ┣━━ 📄 thomas-85982a9b.meta
   ┃       ┃       ┣━━ 📄 thomas-b4a4b274
   ┃       ┃       ┣━━ 📄 thomas-b4a4b274.meta
   ┃       ┃       ┣━━ 📄 thomas-b5c15503
   ┃       ┃       ┣━━ 📄 thomas-b5c15503.meta
   ┃       ┃       ┣━━ 📄 thomas-f5fee22a
   ┃       ┃       ┗━━ 📄 thomas-f5fee22a.meta
   ┃       ┣━━ 📂 logs
   ┃       ┃   ┣━━ 📂 thomas-0f615232
   ┃       ┃   ┃   ┣━━ 📂 0
   ┃       ┃   ┃   ┃   ┗━━ 📂 lightning_logs
   ┃       ┃   ┃   ┃       ┗━━ 📂 version_0
   ┃       ┃   ┃   ┃           ┣━━ 📄 config.yaml
   ┃       ┃   ┃   ┃           ┣━━ 📄 events.out.tfevents.1662468622.thomass-mbp.home.97536.0
   ┃       ┃   ┃   ┃           ┣━━ 📄 hparams.yaml
   ┃       ┃   ┃   ┃           ┗━━ 📂 checkpoints
   ┃       ┃   ┃   ┃               ┗━━ 📄 epoch=0-step=20.ckpt
   ┃       ┃   ┃   ┣━━ 📂 1
   ┃       ┃   ┃   ┃   ┗━━ 📂 lightning_logs
   ┃       ┃   ┃   ┃       ┗━━ 📂 version_0
   ┃       ┃   ┃   ┃           ┣━━ 📄 config.yaml
   ┃       ┃   ┃   ┃           ┣━━ 📄 events.out.tfevents.1662468638.thomass-mbp.home.97640.0
   ┃       ┃   ┃   ┃           ┣━━ 📄 hparams.yaml
   ┃       ┃   ┃   ┃           ┗━━ 📂 checkpoints
   ┃       ┃   ┃   ┃               ┗━━ 📄 epoch=0-step=20.ckpt
   ┃       ┃   ┃   ┣━━ 📂 2
   ┃       ┃   ┃   ┃   ┗━━ 📂 lightning_logs
   ┃       ┃   ┃   ┃       ┗━━ 📂 version_0
   ┃       ┃   ┃   ┃           ┣━━ 📄 config.yaml
   ┃       ┃   ┃   ┃           ┣━━ 📄 events.out.tfevents.1662468655.thomass-mbp.home.97763.0
   ┃       ┃   ┃   ┃           ┣━━ 📄 hparams.yaml
   ┃       ┃   ┃   ┃           ┗━━ 📂 checkpoints
   ┃       ┃   ┃   ┃               ┗━━ 📄 epoch=1-step=40.ckpt
   ┃       ┃   ┃   ┣━━ 📂 3
   ┃       ┃   ┃   ┃   ┗━━ 📂 lightning_logs
   ┃       ┃   ┃   ┃       ┗━━ 📂 version_0
   ┃       ┃   ┃   ┃           ┣━━ 📄 config.yaml
   ┃       ┃   ┃   ┃           ┣━━ 📄 events.out.tfevents.1662468670.thomass-mbp.home.97814.0
   ┃       ┃   ┃   ┃           ┣━━ 📄 hparams.yaml
   ┃       ┃   ┃   ┃           ┗━━ 📂 checkpoints
   ┃       ┃   ┃   ┃               ┗━━ 📄 epoch=0-step=20.ckpt
   ...

2. Show artifacts with filtering
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block::

   lightning show artefacts --include=thomas-0f615232 --exclude=.yaml

.. code-block::

   📂 root
   ┣━━ 📂 artifacts
   ┃   ┗━━ 📂 drive
   ┃       ┣━━ 📂 code
   ┃       ┃   ┗━━ 📂 root.file_server
   ┃       ┃       ┣━━ 📄 thomas-0f615232
   ┃       ┃       ┗━━ 📄 thomas-0f615232.meta
   ┃       ┗━━ 📂 logs
   ┃           ┗━━ 📂 thomas-0f615232
   ┃               ┣━━ 📂 0
   ┃               ┃   ┗━━ 📂 lightning_logs
   ┃               ┃       ┗━━ 📂 version_0
   ┃               ┃           ┣━━ 📄 events.out.tfevents.1662468622.thomass-mbp.home.97536.0
   ┃               ┃           ┗━━ 📂 checkpoints
   ┃               ┃               ┗━━ 📄 epoch=0-step=20.ckpt
   ...

******************
Download arfefacts
******************

1. Check available options
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block::

   lightning download artefacts --help

Here is the output of such command above:

.. code-block::

   You are connected to the local Lightning App.
   usage: artefacts [-h] [--include INCLUDE] [--exclude EXCLUDE] [--overwrite OVERWRITE] output_dir

   positional arguments:
   output_dir            Provide the output directory for the artefacts..

   optional arguments:
   -h, --help            show this help message and exit
   --include INCLUDE     Provide a regex to include some specific files.
   --exclude EXCLUDE     Provide a regex to exclude some specific files.
   --overwrite OVERWRITE Whether to overwrite the artefacts if they exist.

2. Download artifacts
^^^^^^^^^^^^^^^^^^^^^

.. code-block::

   mkdir output_artefacts
   lightning download artefacts ./output_artefacts
