# Create a tree with your artifacts
lightning show artifacts

# Download artifacts from Sweep
lightning download artifacts --names {SWEEP_NAME} --output_dir {SWEEP_NAME}

# Download artifacts from several experiments
lightning download artifacts --names {EXP_NAME_0} {EXP_NAME_1} ...