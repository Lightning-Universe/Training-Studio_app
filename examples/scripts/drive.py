import glob

# 1: Create a Drive with your data on s3.
# python -m lightning create drive --name example --source s3://pl-flash-data/wiki-test/ --mount_path /data/wiki-test/

# 2: Attach the Drive to an experiment
# python -m lightning run experiment drive.py --drives example

for filename in glob.iglob("/data/wiki-test/**/**", recursive=True):
    print(filename)
