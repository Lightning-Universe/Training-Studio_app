import glob

# 1: Create Data from s3.
# python -m lightning create data --name example --source s3://pl-flash-data/wiki-test/

# 2: Attach the Data to an experiment
# python -m lightning run experiment data.py --data example

for filename in glob.iglob("/data/example/**/**", recursive=True):
    print(filename)
