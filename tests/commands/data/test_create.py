import pytest

from lightning_training_studio.commands.data.create import DataConfig


def test_create_drive():

    with pytest.raises(Exception, match='The `source` needs to start with "s3://"'):
        DataConfig(name="str", source="a", mount_path="b")

    with pytest.raises(Exception, match="The `source` needs to end with in a trailing slash"):
        DataConfig(name="str", source="s3://a", mount_path="b")

    with pytest.raises(Exception, match="The `mount_path` needs to start with a leading slash"):
        DataConfig(name="str", source="s3://a/", mount_path="b")

    with pytest.raises(Exception, match="The `mount_path` needs to end with in a trailing slash"):
        DataConfig(name="str", source="s3://a/", mount_path="/b")

    DataConfig(name="str", source="s3://a/", mount_path="/b/")
