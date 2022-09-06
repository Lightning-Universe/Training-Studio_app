:orphan:

###########
Run a Sweep
###########

.. _run_sweep:

.. join_slack::
   :align: left

----

**************************
1. Check available options
**************************

The Training Studio App CLI provides an help.

.. code-block::

   lightning run sweep --help

Here is the output of such command above:

.. code-block::

   You are connected to the local Lightning App.
   usage: sweep [-h] [--n_trials N_TRIALS] [--simultaneous_trials SIMULTANEOUS_TRIALS]
               [--requirements REQUIREMENTS [REQUIREMENTS ...]] [--framework FRAMEWORK]
               [--cloud_compute CLOUD_COMPUTE] [--sweep_id SWEEP_ID] [--num_nodes NUM_NODES]
               [--logger LOGGER] [--direction {minimize,maximize}]
               script_path

   positional arguments:
   script_path           The path to the script to run.

   optional arguments:
   -h, --help            show this help message and exit
   --n_trials N_TRIALS   Number of trials to run.
   --simultaneous_trials SIMULTANEOUS_TRIALS
                           Number of trials to run.
   --requirements REQUIREMENTS [REQUIREMENTS ...]
                           Requirements file.
   --framework FRAMEWORK
                           The framework you are using.
   --cloud_compute CLOUD_COMPUTE
                           The machine to use in the cloud.
   --sweep_id SWEEP_ID   The sweep you want to run upon.
   --num_nodes NUM_NODES
                           The number of nodes to train upon.
   --logger LOGGER       The logger to use with your sweep.
   --direction {minimize,maximize}
                           In which direction to optimize.

----

**************
2. Run a Sweep
**************

In this example, we are going to run a Sweep from this `train.py <https://github.com/Lightning-AI/lightning-hpo/blob/master/examples/scripts/train.py>`_ file.

Here is the command line with the hyper-parameters.

.. code-block::

   lightning run sweep train.py \
      --n_trials=10 \
      --logger="tensorboard" \
      --direction=maximize \

      # HyperParameters with their distribution
      --model.lr="log_uniform(0.001, 0.1)" \
      --model.gamma="uniform(0.5, 0.8)" \
      --data.batch_size="categorical([32, 64])"

Finally, your code is uploaded to the App and the Training Studio App responds the Sweep ``1dbfed8a`` was launched.

.. code-block::

   You are connected to the local Lightning App.
   upload ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100.0%
   Launched a sweep 1dbfed8a
   Your command execution was successful.

.. note:: We are currently supporting only categorical, log_uniform and uniform distribution. Simply open an issue to request more.