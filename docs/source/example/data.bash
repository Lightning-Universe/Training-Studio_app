# Add data from an S3 bucket
# lightning create data --name {THE DATASET NAME} --source {WHERE THE DATA LIVES ON S3}
lightning create data --name example --source s3://pl-flash-data/wiki-test/

# Create a table with your Datasets
lightning show data

# Use your data `--data` with an Experiment
lightning run experiment train.py ... --data example

# Use your data `--data` with an Sweep
lightning run sweep train.py ... --data example

# Optionally: Specify where to ligh the data
lightning run experiment ... --data example:/new_data/example
