import logging
import os
from logging import Handler
from logging.handlers import RotatingFileHandler
from typing import Any, Dict

LOGGING_EXCEPTIONS: Dict[str, Any] = {
    # you can actually use this if you want to disable all of loggers.
    # name: logging.CRITICAL for name in logging.root.manager.loggerDict
}


class Logger(logging.Logger):

    def __init__(
            self,
            name: str = "root",
            level: int = logging.INFO,
            use_default_handlers: bool = True,
            logging_exceptions: Dict[str, int] = LOGGING_EXCEPTIONS,  # noqa
    ) -> None:
        super().__init__(name, level)
        os.makedirs("logs", exist_ok=True)
        self.set_logging_exceptions(logging_exceptions)
        if use_default_handlers:
            self.set_default_handlers()

    def set_default_handlers(self) -> None:
        file: Handler = RotatingFileHandler(
            filename=f"./logs/{self.name}.log",
            encoding="utf-8",
            backupCount=0,
            maxBytes=104857600,  # 100mb as 1024^2 when 1 mb = 1024
            errors="warning",
        )
        file.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s %(name)s %(levelname)s -> %(message)s",
                datefmt="%Y.%m.%d %H:%M",
            )
        )
        stream: Handler = logging.StreamHandler()
        stream.setFormatter(
            logging.Formatter(
                fmt="%(levelname)s %(name)s -> %(message)s", datefmt="%Y.%m.%d %H:%M"
            )
        )
        for handler in (stream, file):
            self.handlers.append(handler)

    @staticmethod
    def set_logging_exceptions(exceptions: Dict[str, int]) -> None:
        for logger_name in exceptions:
            logging.getLogger(logger_name).setLevel(exceptions[logger_name])
