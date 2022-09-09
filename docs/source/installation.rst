
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

1.  Install the ``lightning-hpo`` package

    .. code:: bash

        git clone https://github.com/Lightning-AI/lightning-hpo


        cd lightning-hpo


        pip install -r requirements.txt -r requirements/test.txt --find-links https://download.pytorch.org/whl/cpu/torch_stable.html


        pip install git+https://github.com/Lightning-AI/lightning.git@small_fixes


        pip install -e .
