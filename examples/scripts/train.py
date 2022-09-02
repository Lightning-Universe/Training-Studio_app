import os
import sys

import torch
import torchvision.transforms as T
from pytorch_lightning import LightningDataModule, LightningModule
from pytorch_lightning.callbacks import ModelCheckpoint
from pytorch_lightning.utilities.cli import LightningCLI
from scripts.net import Net
from torch.nn import functional as F
from torchmetrics import Accuracy
from torchvision.datasets import MNIST

train_script_path = __file__


class ImageClassifier(LightningModule):
    def __init__(self, model=None, lr=1.0, gamma=0.7):
        super().__init__()
        self.save_hyperparameters(ignore="model")
        print(self.hparams)
        self.model = model or Net()
        self.val_acc = Accuracy()

        checkpoint_path = os.path.join(os.path.dirname(__file__), "demo_weights")
        if os.path.exists(checkpoint_path):
            self.load_state_dict(torch.load(checkpoint_path).state_dict())

    @property
    def example_input_array(self):
        return torch.zeros((1, 1, 28, 28))

    def forward(self, x):
        return self.model(x)

    def training_step(self, batch, batch_idx):
        x, y = batch
        logits = self.forward(x)
        loss = F.nll_loss(logits, y.long())
        self.log("train_loss", loss, on_step=True, on_epoch=True)
        return loss

    def validation_step(self, batch, batch_idx):
        x, y = batch
        logits = self.forward(x)
        loss = F.nll_loss(logits, y.long())
        self.log("val_acc", self.val_acc(logits, y))
        self.log("val_loss", loss)

    def configure_optimizers(self):
        return torch.optim.Adam(self.model.parameters(), lr=self.hparams.lr)


class MNISTDataModule(LightningDataModule):
    def __init__(self, batch_size: float = 32.0):
        super().__init__()
        self.save_hyperparameters()

    @property
    def transform(self):
        return T.Compose([T.ToTensor(), T.Normalize((0.1307,), (0.3081,))])

    def prepare_data(self) -> None:
        should_download = True
        exists = os.path.exists("./data/MNIST/raw")
        if exists:
            should_download = len(os.listdir("./data/MNIST/raw")) != 8
        if should_download:
            MNIST("./data", download=True)

    def train_dataloader(self):
        train_dataset = MNIST("./data", train=True, download=False, transform=self.transform)
        return torch.utils.data.DataLoader(train_dataset, batch_size=int(self.hparams.batch_size))

    def val_dataloader(self):
        val_dataset = MNIST("./data", train=False, download=False, transform=self.transform)
        return torch.utils.data.DataLoader(val_dataset, batch_size=int(self.hparams.batch_size))


if __name__ == "__main__":
    print(f"The provided arguments are {sys.argv}")
    cli = LightningCLI(
        ImageClassifier,
        MNISTDataModule,
        seed_everything_default=42,
        save_config_overwrite=True,
        run=False,
        trainer_defaults={
            "max_epochs": 10,
            "limit_train_batches": 10,
            "limit_val_batches": 5,
            "callbacks": [ModelCheckpoint(monitor="val_acc")],
        },
    )
    cli.trainer.fit(cli.model, datamodule=cli.datamodule)
