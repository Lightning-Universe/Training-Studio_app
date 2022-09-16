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

The Training Studio App CLI provides its own help.

.. code-block::

   lightning run sweep --help

   Here is the output of the command:

.. code-block::

   You are connected to the local Lightning App.
   usage: sweep [-h] [--n_trials N_TRIALS] [--simultaneous_trials SIMULTANEOUS_TRIALS]
               [--requirements REQUIREMENTS [REQUIREMENTS ...]] [--framework FRAMEWORK]
               [--cloud_compute CLOUD_COMPUTE] [--name NAME] [--logger LOGGER]
               [--direction {minimize,maximize}]
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
   --name NAME           The sweep you want to run upon.
                           The number of nodes to train upon.
   --logger LOGGER       The logger to use with your sweep.
   --direction {minimize,maximize}
                           In which direction to optimize.

----

**************
2. Run a Sweep
**************

In this example, we are going to run a Sweep from this `train.py <https://github.com/Lightning-AI/lightning-hpo/blob/master/examples/scripts/train.py>`_ file.

Download the training script as follows. Alternatively, you can use ``curl``.

.. code-block::

   wget https://raw.githubusercontent.com/Lightning-AI/lightning-hpo/master/examples/scripts/train.py


Here is the command line with the hyper-parameters. Under the hood, it uses `Optuna <https://optuna.org/>`_ and a `bayesian sampling strategy <https://optuna.readthedocs.io/en/stable/_modules/optuna/samplers/_tpe/sampler.html>`_.

.. code-block::

   lightning run sweep train.py \
      --n_trials=3 \
      --simultaneous_trials=1 \
      --logger="tensorboard" \
      --direction=maximize \
      --cloud_compute=cpu-medium \
      --model.lr="log_uniform(0.001, 0.1)" \
      --model.gamma="uniform(0.5, 0.8)" \
      --data.batch_size="categorical([32, 64])"

Finally, your code is uploaded to the App and the Training Studio App responds that the Sweep ``1dbfed8a`` was launched.

.. code-block::

   You are connected to the local Lightning App.
   upload ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100.0%
   Launched a sweep 1dbfed8a
   Your command execution was successful.

**********************************
3. Configure your hyper-parameters
**********************************

We currently only support ``categorical``, ``log_uniform``, and ``uniform`` distributions. Please open a feature request to add more!

To use either ``log_uniform`` or ``uniform`` distributions, simply pass the ``low`` and ``high`` values to be sampled from.

Here is the general format:

.. code-block::

   lightning run sweep ... --X="log_uniform(low_value, high_value)"

   lightning run sweep ... --X="uniform(low_value, high_value)"

Here is an example to sample the model learning rate taken from the command above

.. code-block::

   lightning run sweep ... --model.lr="log_uniform(0.001, 0.1)"

To use the ``categorical`` distribution, pass a list of elements as follows:

.. code-block::

   lightning run sweep ... --X="categorical([..., ..., ...])"

Here is an example to sample the data batch size taken from the command above.

.. code-block::

   lightning run sweep ... --data.batch_size="categorical([32, 64])"

----

**********
Next Steps
**********

.. raw:: html

   <br />
   <div class="display-card-container">
      <div class="row">

.. displayitem::
   :header: Show Sweeps
   :description: Learn how to view the existing sweeps
   :col_css: col-md-4
   :button_link: show_sweeps.html
   :height: 180

.. displayitem::
   :header: Stop or delete a Sweep
   :description: Learn how to stop or delete an existing sweep
   :col_css: col-md-4
   :button_link: stop_or_delete_sweep.html
   :height: 180

.. displayitem::
   :header: Run a Notebook
   :description: Learn how to run a notebook locally or in the cloud
   :col_css: col-md-4
   :button_link: run_notebook.html
   :height: 180

.. raw:: html

      </div>
   </div>
