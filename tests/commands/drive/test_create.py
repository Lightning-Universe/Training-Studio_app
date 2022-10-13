import pytest

from lightning_hpo.commands.drive.create import DriveConfig


def test_create_drive():

    with pytest.raises(Exception, match='The `source` needs to start with "s3://"'):
        DriveConfig(name="str", source="a", mount_path="b")

    with pytest.raises(Exception, match="The `source` needs to end with in a trailing slash"):
        DriveConfig(name="str", source="s3://a", mount_path="b")

    with pytest.raises(Exception, match="The `mount_path` needs to start with in a trailing slash"):
        DriveConfig(name="str", source="s3://a/", mount_path="b")

    with pytest.raises(Exception, match="The `mount_path` needs to end with in a trailing slash"):
        DriveConfig(name="str", source="s3://a/", mount_path="/b")

    DriveConfig(name="str", source="s3://a/", mount_path="/b/")
