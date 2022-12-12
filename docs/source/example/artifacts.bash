# Create a tree with your artifacts
lightning show artifacts

# Create a tree with your artifacts for a Sweep
lightning show artifacts --names grid_search

# Create a tree with your artifacts for several Experiments
lightning show artifacts --names my_first_training my_second_training

# Download artifacts from Sweep
lightning download artifacts --names grid_search --output_dir ./grid_search

# Download artifacts from several experiments
lightning download artifacts --names my_first_training my_second_training --output_dir ./experiments
