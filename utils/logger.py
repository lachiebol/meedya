import logging
import sys

LOG_FILE = "subtitle_merger.log"
LOGGER_NAME = "media_library"

def get_logger():
    logger = logging.getLogger(LOGGER_NAME)
    if not logger.hasHandlers():
        logger.setLevel(logging.INFO)

        # File handler
        file_handler = logging.FileHandler(LOG_FILE, mode='a', encoding='utf-8')
        file_formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(file_formatter)
        logger.addHandler(console_handler)

    return logger


logger = get_logger()
