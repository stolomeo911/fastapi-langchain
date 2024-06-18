import logging
import os
import yaml
from yaml import Loader
from datetime import datetime
import boto3
#import psutil
#from pympler import asizeof


session_id = datetime.today().strftime('%Y%m%d')


def setup_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Create subfolder with the session ID
    session_folder = os.path.join('logs', session_id)
    if not os.path.exists(session_folder):
        os.makedirs(session_folder)

    # Create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # Create file handler and set level to debug
    log_file = os.path.join(session_folder, 'app.log')
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.DEBUG)

    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Add formatter to handlers
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(ch)
    logger.addHandler(fh)

    return logger


def set_log_file(logger, user_id):
    # Create logs folder if it doesn't exist
    logs_folder = 'logs'
    if not os.path.exists(logs_folder):
        os.makedirs(logs_folder)

    # Create subfolder with the session ID
    session_folder = os.path.join(logs_folder, session_id)
    if not os.path.exists(session_folder):
        os.makedirs(session_folder)

    # Remove existing file handlers
    for handler in logger.handlers[:]:
        if isinstance(handler, logging.FileHandler):
            logger.removeHandler(handler)

    # Define the log file name based on the user ID
    log_file = os.path.join(session_folder, f'{user_id}.log')

    # Remove existing file handlers
    for handler in logger.handlers[:]:
        if isinstance(handler, logging.FileHandler):
            logger.removeHandler(handler)

    # Create new file handler with the user-specific log file name
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)

    # Add new file handler to logger
    logger.addHandler(fh)


def get_yaml_config(path_file):
    dict_settings = yaml.load(open(path_file), Loader=Loader)
    return dict_settings


def _fetch_secret_key(name: str, env: str):
    """Fetch secret key from parameter store

    Args:
        name (string): secret key name as stored in parameter store
        env: (string): LOCAL to use local env variable with named as "name" ,
        DEV/PROD to use parameter store of the related environment
    Returns:
        _type_: _description_
    """

    if env == 'LOCAL':
        return os.environ[name]
    else:
        ssm = boto3.client("ssm")

        try:
            parameter = ssm.get_parameter(Name=name, WithDecryption=True)
            return parameter["Parameter"]["Value"]
        except ssm.exceptions.ParameterNotFound:
            return None


"""
def log_memory_usage(logger):
    process = psutil.Process()
    mem_info = process.memory_info()
    logger.info(f"Memory Usage: {mem_info.rss / (1024 * 1024)} MB")


def log_memory_usage_of_variable(logger, variable, variable_name):
    agent_size = asizeof.asizeof(variable)
    logger.info(f"Memory Usage of {variable_name}: {agent_size / (1024 * 1024)} MB")
"""