# Run default minGPT with 85.3 M parameters on a single GPU
lightning run experiment train.py \
    --name="lightning-gpt-2" \
    --cloud_compute="gpu-fast"

# Run default minGPT with 85.3 M parameters using DeepSpeed on a single GPU
lightning run experiment train.py \
    --name="lightning-gpt-2-deepspeed" \
    --cloud_compute="gpu-fast" \
    --requirements="requirements-deepspeed.txt" \
    --implementation="deepspeed"

# Run default minGPT with 85.3 M parameters using optimized xFormers layers on a single GPU
lightning run experiment train.py \
    --name="lightning-gpt-2-xformers" \
    --cloud_compute="gpu-fast" \
    --requirements="requirements-xformers.txt" \
    --implementation="xformers"
