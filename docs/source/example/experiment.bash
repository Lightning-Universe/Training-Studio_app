# Submit an experiment
lightning run experiment train.py --name my_first_training

# Submit another experiment on GPU
lightning run experiment train.py --name my_second_training --cloud_compute="gpu"
