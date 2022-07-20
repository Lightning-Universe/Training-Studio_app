import os
import tarfile

def extract_tarfile(file_path: str, extract_path: str, mode: str):
    if os.path.exists(file_path):
        with tarfile.open(file_path, mode=mode) as tar_ref:
            for member in tar_ref.getmembers():
                try:
                    tar_ref.extract(member, path=extract_path, set_attrs=False)
                except PermissionError:
                    raise PermissionError(f"Could not extract tar file {file_path}")

extract_tarfile("sweep-9ff4c95b-1033-4bdd-889d-e513ed19c67c", ".", "r:gz")