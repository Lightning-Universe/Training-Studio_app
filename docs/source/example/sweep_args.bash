# Launch Sweeps over train.py file

# Specifying requirements in a requirements.txt file
lightning run sweep --requirements=requirements.txt \
    train.py \
    model.lr=0.001,0.1 \
    data.batch=32,64

# Specifying a list of requirements
# Specifying requirements in a file
lightning run sweep --requirements="imgaug==0.4.0","pandas>=1.5.0" \
    train.py \
    model.lr=0.001,0.1 \
    data.batch=32,64

# Specifying system packages
lightning run sweep --packages="ffmpeg libsm6 libxext6" \
    train.py \
    model.lr=0.001,0.1 \
    data.batch=32,64

# Running pip install . on the source dir before running
lightning run sweep --pip-install-source \
    train.py \
    model.lr=0.001,0.1 \
    data.batch=32,64

# Specifying cloud compute for each experiment in the sweep
lightning run sweep --cloud-compute=gpu-fast \
    train.py \
    model.lr=0.001,0.1 \
    data.batch=32,64
