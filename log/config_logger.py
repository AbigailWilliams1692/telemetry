#######################################################
# @Project: Telemetry
# @Module: config_logger.py
# @Description: This module provides functions to configure and retrieve logger instances.
# @Author: AbigailWilliams1692
# @CreationDate: 2025-07-23
#######################################################

#######################################################
# Import Libraries
#######################################################
# Standard Libraries
import logging


#######################################################
# Function: get_logger
#######################################################
def get_logger(name: str, log_level: int) -> logging.Logger:
    """
    Get a logger with the specified name.

    :param name: The name of the logger.
    :param log_level: The logging level (e.g., logging.DEBUG, logging.INFO).
    :return: A logger instance.
    """
    # Create a logger with the specified name and log level.
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # Check if the logger already has handlers to avoid duplicate logs.
    if not logger.hasHandlers():
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
