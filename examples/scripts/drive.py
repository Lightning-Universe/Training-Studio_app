import glob

from lightning.pytorch import Trainer
from lightning.pytorch.callbacks import ModelCheckpoint
from lightning.pytorch.demos.boring_classes import BoringModel

# 1: Create a Drive with your data on s3.
# python -m lightning create drive --name example --source s3://pl-flash-data/wiki-test/ --mount_path /data/wiki-test/

# 2: Attach the Drive to an experiment
# python -m lightning run experiment drive.py --drives example

if __name__ == "__main__":

    for filename in glob.iglob("/data/wiki-test/**/**", recursive=True):
        print(filename)

    class BoringModelLogging(BoringModel):
        def validation_step(self, batch, batch_idx):
            res = super().validation_step(batch, batch_idx)
            self.log("val_loss", res["x"])
            return res

    model = BoringModelLogging()
    callback = ModelCheckpoint(save_last=True, monitor="val_loss")
    trainer = Trainer(max_epochs=1, limit_train_batches=5, callbacks=[callback])
    trainer.fit(model)
