import pytorch_lightning as pl
from lightning_transformers.task.nlp.language_modeling import LanguageModelingDataModule, LanguageModelingTransformer
from transformers import AutoTokenizer

model_name = "gpt2-xl"

tokenizer = AutoTokenizer.from_pretrained(model_name)

model = LanguageModelingTransformer(
    pretrained_model_name_or_path=model_name,
    tokenizer=tokenizer,
    deepspeed_sharding=True,  # defer initialization of the model to shard/load pre-train weights
)

dm = LanguageModelingDataModule(
    batch_size=1,
    dataset_name="wikitext",
    dataset_config_name="wikitext-2-raw-v1",
    tokenizer=tokenizer,
)
trainer = pl.Trainer(
    accelerator="auto",
    devices="auto",
    strategy="deepspeed_stage_3",
    precision=16,
    max_epochs=20,
)

trainer.fit(model, dm)
