import logging
import sys

LOG_FORMAT = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Bibliotecas que costumam poluir o console
_NOISY_LOGGERS = [
    "msmart",
    "connectlife",
    "httpx",
    "httpcore",
    "aiohttp",
    "urllib3",
    "uvicorn.access",
]


def setup_logging(*, level: int = logging.INFO) -> None:

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT))

    root = logging.getLogger()
    root.setLevel(level)

    # Remove handlers duplicados (reload do uvicorn)
    root.handlers.clear()
    root.addHandler(handler)

    # Silencia bibliotecas externas (WARNING+ apenas)
    for name in _NOISY_LOGGERS:
        logging.getLogger(name).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"dfrezzing.{name}")
