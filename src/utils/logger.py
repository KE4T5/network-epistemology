"""Script with logging configuration."""
import logging
import sys

import config


FORMATTER = logging.Formatter(config.LOGGER_MESSAGE_FORMATTER)


def _get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    return console_handler


def _get_file_handler():
    file_handler = logging.FileHandler(config.PATH_LOGS)
    file_handler.setFormatter(FORMATTER)
    return file_handler


def get_logger(logger_name):
    """Creates logger."""
    logger = logging.getLogger(logger_name)
    for h in logger.handlers:
        logger.removeHandler(h)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(_get_console_handler())
    logger.addHandler(_get_file_handler())
    logger.propagate = False
    return logger
