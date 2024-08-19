import os
import shutil

from src.config_util import CONF_DIR, CONF_PATH


def create_mock(**kwargs):
    return type("MockObject", (), kwargs)()


def mock_config_start():
    os.mkdir(CONF_DIR)
    shutil.copyfile(f"src/{CONF_PATH}", CONF_PATH)


def mock_config_end():
    shutil.rmtree(CONF_DIR)
