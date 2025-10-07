import logging
import sys
from typing import Literal


def configure_logging(
    level: Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'] = 'INFO',
) -> None:
    fmt = '[{asctime}] {levelname} {name}: {message}'
    formatter = logging.Formatter(fmt, style='{', datefmt='%Y-%m-%d %H:%M:%S')

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)

    for uv_logger_name in ('uvicorn', 'uvicorn.error', 'uvicorn.access'):
        uv_logger = logging.getLogger(uv_logger_name)
        uv_logger.handlers.clear()
        uv_logger.addHandler(console_handler)
        uv_logger.setLevel(level)
