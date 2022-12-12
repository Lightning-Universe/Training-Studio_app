# Launch a Sweep over train.py file

# Using Grid Search Algorithm
lightning run sweep train.py \
    --model.lr="[0.001, 0.1]" \
    --data.batch="[32, 64]" \
    --algorithm="grid_search"

# Using Random Search Algorithm
lightning run sweep train.py \
    --total_experiments=3 \
    --model.lr="log_uniform(0.001, 0.1)" \
    --data.batch='categorical([32, 64])' \
    --algorithm="random_search"

# Using Bayesian Search Algorithm with parallel experiments
lightning run sweep train.py \
    --total_experiments=5 \
    --parallel_experiments=2 \
    --model.lr="log_uniform(0.001, 0.1)" \
    --data.batch='categorical([32, 64])' \
    --algorithm="bayesian"

# Install extra dependencies
lightning run sweep train.py ... --requirements="torchvision, deepspeed"

# Increase disk size to 80GB
lightning run sweep train.py ... --disk_size=80

# Use a GPU machine
lightning run sweep train.py ... --cloud_compute="gpu"

# Use a multi-GPU machine (4 x V100)
lightning run sweep train.py ... --cloud_compute="gpu-fast-multi"

# Use 2 nodes of multi-GPU machine (4 x V100)
lightning run sweep train.py ... --cloud_compute="gpu-fast-multi" --num_nodes=2
