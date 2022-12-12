# Launch Sweeps over train.py file

# Using Grid Search Algorithm
lightning run sweep train.py \
    --name grid_search \
    --model.lr="[0.001, 0.1]" \
    --data.batch="[32, 64]" \
    --algorithm="grid_search"

# Using Random Search Algorithm
lightning run sweep train.py \
    --name random_search \
    --total_experiments=3 \
    --model.lr="log_uniform(0.001, 0.1)" \
    --data.batch='categorical([32, 64])' \
    --algorithm="random_search"

# Using Bayesian Search Algorithm with parallel experiments
lightning run sweep train.py \
    --name bayesian_search \
    --total_experiments=5 \
    --parallel_experiments=2 \
    --model.lr="log_uniform(0.001, 0.1)" \
    --data.batch='categorical([32, 64])' \
    --algorithm="bayesian"
