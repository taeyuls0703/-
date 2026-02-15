import logging
import sys
from pathlib import Path

def setup_logging(log_file="app.log", level=logging.INFO):
    """Configures logging for the application."""

    log_path = Path("logs") / log_file
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_path, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

    logging.info("Logging initialized.")

def get_logger(name):
    """Returns a logger instance with the given name."""
    return logging.getLogger(name)
