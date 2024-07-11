import logging


def setup_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not getattr(logger, 'is_logger_setup', False):

        # Create console handler and set level to debug
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Add formatter to handlers
        ch.setFormatter(formatter)

        # Add handlers to logger
        logger.addHandler(ch)

        # Mark logger as setup
        logger.is_logger_setup = True

    return logger
