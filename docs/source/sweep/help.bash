# Get information about the Sweep command
lightning run sweep --help 

# Result:
usage: sweep [-h] ...
             script_path

positional arguments:
  script_path           The path to the script to run.

optional arguments:
  -h, --help            show this help message and exit
  --algorithm {grid_search,random_search,bayesian}
                        The search algorithm to use.
  --total_experiments TOTAL_EXPERIMENTS
                        The total number of experiments
  --parallel_experiments PARALLEL_EXPERIMENTS
                        Number of experiments to run.
  --requirements REQUIREMENTS [REQUIREMENTS ...]
                        List of requirements separated 
                        by a comma or requirements.txt filepath.
  --packages PACKAGES [PACKAGES ...]
                        List of system packages to be installed 
                        via apt install, separated by a comma.
  --cloud_compute {cpu,...,gpu,...,gpu-fast-multi}
                        The machine to use in the cloud.
  --name NAME           Configure your sweep name.
  --logger {tensorboard,wandb}
                        The logger to use with your sweep.
  --direction {minimize,maximize}
                        In which direction to optimize.
  --framework {pytorch_lightning,base}
                        Which framework you are using.
  --num_nodes NUM_NODES
                        The number of nodes.
  --disk_size DISK_SIZE
                        The disk size in Gigabytes.
  --data DATA [DATA ...] Provide a list of Data
                        in the format: `<name>` 
                        or `<name>:<mount_path>`
                        to mount to the experiments.
  --syntax {default,hydra}
                        Syntax for sweep parameters at the CLI.
  --pip-install-source  Run `pip install -e .` on 
                        the uploaded source before running