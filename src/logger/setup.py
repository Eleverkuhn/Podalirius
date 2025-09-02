import logging.config
import json, pathlib


def setup_logging():
    config_file = pathlib.Path("src/logger/config.json")
    with open(config_file) as f_in:
        config = json.load(f_in)
    logging.config.dictConfig(config)
