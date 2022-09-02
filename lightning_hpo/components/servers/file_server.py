import json
import logging
import os
import tarfile
import traceback
import uuid
import zipfile
from pathlib import Path

import lightning as L
from lightning.app.storage import Drive

_logger = logging.getLogger(__name__)


class FileServer(L.LightningWork):
    def __init__(self, drive: Drive, base_dir: str = "", chunk_size=10240, **kwargs):
        """This component uploads, downloads files to your application.

        Arguments:
            drive: The drive can share data inside your application.
            base_dir: The local directory where the data will be stored.
            chunk_size: The quantity of bytes to download/upload at once.
        """
        super().__init__(
            cloud_build_config=L.BuildConfig(requirements=["Flask", "Flask-Cors"]),
            parallel=True,
            **kwargs,
        )
        # 1: Attach the arguments to the state.
        self.drive = drive
        self.base_dir = base_dir
        self.chunk_size = chunk_size

        # 2: Create a folder to store the data.
        if self.base_dir:
            os.makedirs(self.base_dir, exist_ok=True)

        # 3: Keep a reference to the uploaded filenames.
        self.uploaded_files = dict()

    def get_filepath(self, path: str) -> str:
        """Returns file path stored on the file server."""
        return os.path.join(self.base_dir, path)

    def get_random_filename(self) -> str:
        """Returns a random hash for the file name."""
        return uuid.uuid4().hex

    def upload_file(self, file, id):
        """Upload a file while tracking its progress."""
        # 1: Track metadata about the file
        filename = id
        uploaded_file = id
        meta_file = uploaded_file + ".meta"
        self.uploaded_files[filename] = {"progress": (0, None), "done": False}

        # 2: Create a stream and write bytes of
        # the file to the disk under `uploaded_file` path.
        with open(self.get_filepath(uploaded_file), "wb") as out_file:
            content = file.read(self.chunk_size)
            while content:
                # 2.1 Write the file bytes
                size = out_file.write(content)

                # 2.2 Update the progress metadata
                self.uploaded_files[filename]["progress"] = (
                    self.uploaded_files[filename]["progress"][0] + size,
                    None,
                )
                # 4: Read next chunk of data
                content = file.read(self.chunk_size)

        # 3: Update metadata that the file has been uploaded.
        full_size = self.uploaded_files[filename]["progress"][0]
        self.drive.put(self.get_filepath(uploaded_file))
        self.uploaded_files[filename] = {
            "progress": (full_size, full_size),
            "done": True,
            "uploaded_file": uploaded_file,
        }

        # 4: Write down the metadata about the file to the disk
        meta = {
            "original_path": filename,
            "display_name": os.path.splitext(filename)[0],
            "size": full_size,
            "drive_path": uploaded_file,
        }
        with open(self.get_filepath(meta_file), "wt") as f:
            json.dump(meta, f)

        # 5: Put the file to the drive.
        # It means other components can access get or list them.
        self.drive.put(self.get_filepath(meta_file))
        return meta

    def list_files(self, file_path: str):
        # 1: Get the local file path of the file server.
        file_path = self.get_filepath(file_path)

        # 2: If the file exists in the drive, transfer it locally.
        if not os.path.exists(file_path):
            self.drive.get(file_path)

        if os.path.isdir(file_path):
            result = set()
            for _, _, f in os.walk(file_path):
                for file in f:
                    if not file.endswith(".meta"):
                        for filename, meta in self.uploaded_files.items():
                            if meta["uploaded_file"] == file:
                                result.add(filename)
            return {"asset_names": [v for v in result]}

        # 3: If the filepath is a tar or zip file, list their contents
        if zipfile.is_zipfile(file_path):
            with zipfile.ZipFile(file_path, "r") as zf:
                result = zf.namelist()
        elif tarfile.is_tarfile(file_path):
            with tarfile.TarFile(file_path, "r") as tf:
                result = tf.getnames()
        else:
            raise ValueError("Cannot open archive file!")

        # 4: Returns the matching files.
        return {"asset_names": result}

    def run(self):
        # 1: Imports flask requirements.
        import flask
        from flask import Flask, request
        from flask_cors import CORS

        # 2: Create a flask app
        flask_app = Flask(__name__)
        CORS(flask_app)

        # 3: Define the upload file endpoint
        @flask_app.route("/uploadfile/<id>", methods=["PUT"])
        def upload_file(id: str):
            try:
                """Upload a file directly as form data."""
                f = request.files["file"]
                self.upload_file(f, id)
                resp = flask.Response("File uploaded successfully.")
                return resp
            except Exception:
                trace = str(traceback.print_exc())
                _logger.error(trace)
                resp = flask.Response(trace)
                resp.status_code = 505
                return resp

        @flask_app.get("/")
        def list_files():
            return self.list_files(str(Path(self.base_dir).resolve()))

        # 5: Start the flask app while providing the `host` and `port`.
        flask_app.run(host=self.host, port=self.port, load_dotenv=False)

    def alive(self):
        """Hack: Returns whether the server is alive."""
        return self.url != ""
