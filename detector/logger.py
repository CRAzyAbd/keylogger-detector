import logging
import os


LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "detector.log")


def get_logger(name="detector"):
    """Create and return a configured logger that writes to file and console."""
    os.makedirs(LOG_DIR, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)-8s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


if __name__ == "__main__":
    log = get_logger()
    log.debug("This is a DEBUG message — goes to the file only.")
    log.info("This is an INFO message — file and console.")
    log.warning("This is a WARNING — something looks off.")
    log.error("This is an ERROR — a real problem occurred.")
    log.critical("CRITICAL — keylogger-like process detected!")
    print(f"\nNow open the log file to see everything: {LOG_FILE}")
