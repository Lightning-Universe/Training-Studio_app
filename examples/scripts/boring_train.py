from argparse import ArgumentParser

from lightning.pytorch import Trainer
from lightning.pytorch.callbacks import ModelCheckpoint
from lightning.pytorch.demos.boring_classes import BoringModel

if __name__ == "__main__":

    class BoringModelLogging(BoringModel):
        def validation_step(self, batch, batch_idx):
            res = super().validation_step(batch, batch_idx)
            self.log("val_loss", res["x"])
            return res

    parser = ArgumentParser()
    parser.add_argument("--max_epochs", type=float)
    args = parser.parse_args()

    model = BoringModelLogging()
    callback = ModelCheckpoint(save_last=True, monitor="val_loss")
    trainer = Trainer(max_epochs=int(args.max_epochs), limit_train_batches=5, callbacks=[callback])
    trainer.fit(model)
