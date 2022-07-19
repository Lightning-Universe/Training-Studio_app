from lightning_hpo.objective import BaseObjective
from functools import partial
from subprocess import Popen
from lightning.app.storage import Path

class PyTorchLightningObjective(BaseObjective):

    """This component executes a PyTorch Lightning script
    and injects a callback in the Trainer at runtime in order to start tensorboard server."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 1. Keep track of the best model path.
        self.best_model_path = None
        self.best_model_score = None

    def configure_tracer(self):
        # 1. Override `configure_tracer``

        # 2. Import objects from lightning.pytorch
        from lightning.pytorch import Trainer
        from lightning.pytorch.callbacks import Callback

        # 3. Create a tracer.
        tracer = super().configure_tracer()

        # 4. Implement a callback to launch tensorboard server.
        class TensorboardServerLauncher(Callback):

            def __init__(self, work):
                # The provided `work` is the current ``PyTorchLightningScript`` work.
                self._work = work

            def on_train_start(self, trainer, *_):
                # Provide `host` and `port` in order for tensorboard to be usable in the cloud.
                self._work._process = Popen(
                    f"tensorboard --logdir='{trainer.logger.log_dir}' --host {self._work.host} --port {self._work.port}",
                    shell=True,
                )

        def trainer_pre_fn(self, *args, work=None, **kwargs):
            # Intercept Trainer __init__ call and inject a ``TensorboardServerLauncher`` component.
            kwargs['callbacks'].append(TensorboardServerLauncher(work))
            return {}, args, kwargs

        # 5. Patch the `__init__` method of the Trainer to inject our callback with a reference to the work.
        tracer.add_traced(Trainer, "__init__", pre_fn=partial(trainer_pre_fn, work=self))
        return tracer

    def run(self, *args, **kwargs):
        super().run(*args, **kwargs)

    def on_after_run(self, script_globals):
        import torch

        # 1. Once the script has finished to execute, we can collect its globals and access any objects.
        # Here, we are accessing the LightningCLI and the associated lightning_module
        lightning_module = script_globals["cli"].trainer.lightning_module

        # 2. From the checkpoint_callback, we are accessing the best model weights
        checkpoint = torch.load(script_globals["cli"].trainer.checkpoint_callback.best_model_path)

        # 3. Load the best weights and torchscript the model.
        lightning_module.load_state_dict(checkpoint["state_dict"])
        lightning_module.to_torchscript("model_weight.pt")

        # 4. Use lightning.app.storage.Path to create a reference to the torchscripted model
        # When running in the cloud on multiple machines, by simply passing this reference to another work,
        # it triggers automatically a transfer.
        self.best_model_path = Path("model_weight.pt")

        # 5. Keep track of the metrics.
        self.best_model_score = float(script_globals["cli"].trainer.checkpoint_callback.best_model_score)

    @classmethod
    def distributions(cls):
        return None