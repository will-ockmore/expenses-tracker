import os
import json
import logging.config


def setup_logging(
    default_path='logging_config.json',
    default_level=logging.INFO,
):
    """
    Setup logging configuration
    """
    path = default_path
    if os.path.exists(path):
        with open(path, 'rt') as infile:
            config = json.load(infile)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)
