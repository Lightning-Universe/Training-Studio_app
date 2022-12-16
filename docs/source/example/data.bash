# Add data from an S3 bucket
# lightning add dataset --name {THE DATASET NAME} --source {WHERE THE DATA LIVES ON S3}
lightning add dataset --name mnist --source s3://lightning-example-public/MNIST/

# Create a table with your Datasets
lightning show datasets

# Use your data with an Experiment. Format `<name>:<mount_path>`
lightning run experiment train.py --name experiment_with_data --data mnist:/content/data/MNIST/
