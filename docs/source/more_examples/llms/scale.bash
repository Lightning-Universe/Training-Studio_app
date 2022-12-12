# Run 1.4 Billion parameters model on 4 GPUS
lightning run experiment train.py \
    --name="lightning-gpt2-xl" \
    --model_type="gpt2-xl" \
    --batch_size=64  \
    --cloud_compute="gpu-fast-multi"

# Run 2.9 Billion parameters model on 4 GPUS
lightning run experiment train.py \
    --name="lightning-gpt2-xxl" \
    --model_type="gpt2-xxl" \
    --requirements="requirements-deepspeed.txt" \
    --batch_size=16  \
    --cloud_compute="gpu-fast-multi" \
    --strategy="deepspeed_stage_3_offload"
