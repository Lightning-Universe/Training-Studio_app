# Launch Sweeps over train.py file using Hydra syntax
# For an example on how to use Lightning + Hydra see
# https://github.com/ashleve/lightning-hydra-template

# All Hydra override syntax is supported, use the
# syntax for Hydra multirun to define sweeps
# https://hydra.cc/docs/tutorials/basic/running_your_app/multi-run/
lightning run sweep --syntax hydra train.py \
    model.lr=0.001,0.1 \
    data.batch=32,64 \
    +trainer.accumulate_grad_batches=10
