# Add data from an S3 bucket
# lightning create data --name {THE DATASET NAME} --source {WHERE THE DATA LIVES ON S3}
lightning create data --name mnist --source s3://lightning-example-public/MNIST/

# Create a table with your Datasets
lightning show data

# Use your data with an Experiment. Format `<name>:<mount_path>`
lightning run experiment train.py --name experiment_with_data --data mnist:/content/data/MNIST/
