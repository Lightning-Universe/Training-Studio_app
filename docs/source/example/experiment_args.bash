# Submit an experiment

# Specifying requirements in a requirements.txt file
lightning run experiment --requirements=requirements.txt \
    train.py model.lr=0.001 data.batch=32

# Specifying a list of requirements
# Specifying requirements in a file
lightning run experiment --requirements=="imgaug==0.4.0","pandas>=1.5.0" \
    train.py model.lr=0.001 data.batch=32

# Specifying system packages
lightning run experiment --packages="ffmpeg libsm6 libxext6" \
    train.py model.lr=0.001,0.1 data.batch=32,64

# Running pip install . on the source dir before running
lightning run experiment --pip-install-source \
    train.py model.lr=0.001,0.1 data.batch=32,64

# Specifying cloud compute for each experiment in the sweep
lightning run experiment --cloud-compute=gpu-fast \
    train.py model.lr=0.001,0.1 data.batch=32,64
