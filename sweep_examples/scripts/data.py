import glob

# 1: Add dataset from s3.
# python -m lightning add dataset --name example --source s3://pl-flash-data/wiki-test/

# 2: Attach the Data to an experiment
# python -m lightning run experiment data.py --dataset example

for filename in glob.iglob("/data/example/**/**", recursive=True):
    print(filename)
