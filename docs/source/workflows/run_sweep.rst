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

The Research Studio App CLI provides its own help.

You can run the following command to learn more:

.. code-block::

   lightning run experiment --help

.. code-block::

   lightning run sweep --help

----

********************
2. Run an Experiment
********************

In this example, we are going to run a Sweep from this `train.py <https://github.com/Lightning-AI/lightning-hpo/blob/master/examples/scripts/train.py>`_ file.

Download the training script as follows. Alternatively, you can use ``curl``.

.. code-block::

   wget https://raw.githubusercontent.com/Lightning-AI/lightning-hpo/master/examples/scripts/train.py

.. code-block::

   lightning run experiment train.py

**************
3. Run a Sweep
**************

In order to run a Sweep, you can pass arguments as follow to perform ``grid_search``.

.. code-block::

   lightning run sweep train.py --model.lr "[0.001, 0.01, 0.1]" --data.batch "[32, 64]" --algorithm="grid_search"

Finally, your code is uploaded to the App and the Research Studio App responds that the Sweep ``1dbfed8a`` was launched.

.. code-block::

   You are connected to the local Lightning App.
   upload ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100.0%
   Launched a sweep 1dbfed8a
   Your command execution was successful.

**********************************
3. Configure your hyper-parameters
**********************************

In order to randomize your sweeps, you can decide upon which strategy to run upon.

We support ``grid_search``, ``random_search`` and ``bayesian`` algorithms.

When using ``grid_search`` algorithm, you would need to pass list of elements to be selected as follows:

.. code-block::

   lightning run sweep train.py --model.lr "[0.001, 0.01, 0.1]" --data.batch "[32, 64]" --algorithm="grid_search"

Alternatively, you can create a range

.. code-block::

   lightning run sweep train.py --model.lr "[0.001, 0.01, 0.1]" --data.batch "range(16, 128, 16)" --algorithm="grid_search"

When using ``random_search`` or ``bayesian`` algorithm, you can select from distribution as follows:

We currently only support ``categorical``, ``log_uniform``, and ``uniform`` distributions. Please open a feature request to add more!

Under the hood, it uses `Optuna <https://optuna.org/>`_ and a `bayesian sampling strategy <https://optuna.readthedocs.io/en/stable/_modules/optuna/samplers/_tpe/sampler.html>`_.

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


Here is an example Sweep doing ``baysian`` optimization.

.. code-block::

   lightning run sweep train.py \
      --total_experiments=100 \
      --parallel_experiments=5 \
      --logger="tensorboard" \
      --direction=maximize \
      --model.lr="log_uniform(0.001, 0.01)" \
      --model.gamma="uniform(0.5, 0.8)" \
      --data.batch_size="categorical([32, 64])" \
      --algorithm="bayesian"

----

**********
Next Steps
**********

.. raw:: html

   <br />
   <div class="display-card-container">
      <div class="row">

.. displayitem::
   :header: Show Sweeps & Experiments
   :description: Learn how to view the existing sweeps
   :col_css: col-md-6
   :button_link: show_sweeps.html
   :height: 180

.. displayitem::
   :header: Stop or delete a Sweep & Experiments
   :description: Learn how to stop or delete an existing sweep
   :col_css: col-md-6
   :button_link: stop_or_delete_sweep.html
   :height: 180

..
   .. displayitem::
      :header: Run a Notebook
      :description: Learn how to run a notebook locally or in the cloud
      :col_css: col-md-4
      :button_link: run_notebook.html
      :height: 180

.. raw:: html

      </div>
   </div>
