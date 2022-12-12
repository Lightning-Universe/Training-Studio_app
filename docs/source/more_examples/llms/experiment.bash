# Run default minGPT with 85.3 M parameters
lightning run experiment train.py \
    --name="lightning-gpt" \
    --cloud_compute="gpu-fast"

# Run default minGPT with 85.3 M parameters using DeepSpeed
lightning run experiment train.py \
    --name="lightning-gpt-deepspeed" \
    --cloud_compute="gpu-fast" \
    --requirements="requirements-deepspeed.txt" \
    --implementation="deepspeed"

# Run default minGPT with 85.3 M parameters using optimized xFormers layers
lightning run experiment train.py \
    --name="lightning-gpt-xformers" \
    --cloud_compute="gpu-fast" \
    --requirements="requirements-xformers.txt" \
    --implementation="xformers"
