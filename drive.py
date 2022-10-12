import os

# 1: Create a Drive
# python -m lightning create drive --name example --source s3://pl-flash-data/wiki-test/ --mount_path /content/data/something/

# 2: Attach the Drive to an experiment
# python -m lightning run experiment drive.py --drives example

for root_dir, directories, files in os.walk("/content/data/something/"):
    for file in files:
        print(os.path.join(root_dir, file))
