
.. _install:


############
Installation
############

We strongly recommend to create a virtual environment first.
Don't know what this is? Follow our `beginner guide here <install_beginner.rst>`_.

**Requirements**

* Python 3.8.x or later (3.8.x, 3.9.x, 3.10.x)

Or read the `Apple Silicon Macs installation article <installation_mac.rst>`_ or the `Windows installation article <installation_win.rst>`_.

----

****************
Install with pip
****************

0.  Activate your virtual environment.

You can use `conda <https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-with-commands>`_ or `pyenv <https://github.com/pyenv/pyenv>`_.

1.  Install the ``lightning-hpo`` package

    .. code:: bash

        git clone https://github.com/Lightning-AI/lightning-hpo


        cd lightning-hpo


        pip install -r requirements.txt -r requirements/test.txt --find-links https://download.pytorch.org/whl/cpu/torch_stable.html


        pip install git+https://github.com/Lightning-AI/lightning.git@reduce_cost


        pip install -e .


----

**********
Next Steps
**********

.. raw:: html

   <br />
   <div class="display-card-container">
      <div class="row">

.. displayitem::
   :header: Run a Sweep with PyTorch Lightning
   :description: Discover PyTorch Lightning and train your first Model.
   :col_css: col-md-6
   :button_link: workflows/optimize_with_pytorch_lightning.html
   :height: 180

.. displayitem::
   :header: The Training Studio App
   :description: Manage Sweeps and Tools to accelerate Training.
   :col_css: col-md-6
   :button_link: training_studio.html
   :height: 180

.. raw:: html

   <hr class="docutils" style="margin: 50px 0 50px 0">

.. raw:: html

   <div style="display:none">
