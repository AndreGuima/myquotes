import json
import logging
import os
import sys
from logging.config import dictConfig
from typing import Literal

# =========================================================
# Configuração central de logging do MyQuotes
# =========================================================

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
LogFormat = Literal["text", "json"]

RESERVED_ATTRS = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
    "taskName",
}


def get_log_level() -> LogLevel:
    """
    Define o nível de log baseado no ambiente.
    """
    env = os.getenv("ENV", "development").lower()

    if env in ("prod", "production"):
        return "INFO"

    if env in ("staging",):
        return "INFO"

    # development / local / test
    return "DEBUG"


def get_log_format() -> LogFormat:
    value = os.getenv("LOG_FORMAT", "").strip().lower()
    if value == "json":
        return "json"

    env = os.getenv("ENV", "development").lower()
    if env in ("prod", "production", "staging"):
        return "json"

    return "text"


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "logger": record.name,
            "event": record.getMessage(),
        }

        extras = {
            key: value
            for key, value in record.__dict__.items()
            if key not in RESERVED_ATTRS and not key.startswith("_")
        }
        if extras:
            payload.update(extras)

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=False, default=str)


def setup_logging() -> None:
    """
    Inicializa a configuração global de logging.
    Deve ser chamada UMA vez no startup da aplicação.
    """
    log_level = get_log_level()
    log_format = get_log_format()

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "json": {
                    "()": "core.logging_config.JsonFormatter",
                },
                "default": {
                    "format": (
                        "%(asctime)s | "
                        "%(levelname)-8s | "
                        "%(name)s | "
                        "%(message)s"
                    ),
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
                "verbose": {
                    "format": (
                        "%(asctime)s | "
                        "%(levelname)-8s | "
                        "%(name)s | "
                        "%(filename)s:%(lineno)d | "
                        "%(message)s"
                    ),
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "level": log_level,
                    "formatter": (
                        "json"
                        if log_format == "json"
                        else ("verbose" if log_level == "DEBUG" else "default")
                    ),
                    "stream": sys.stdout,
                }
            },
            "root": {
                "level": log_level,
                "handlers": ["console"],
            },
            "loggers": {
                # Uvicorn
                "uvicorn": {
                    "level": "INFO",
                    "handlers": ["console"],
                    "propagate": False,
                },
                "uvicorn.error": {
                    "level": "INFO",
                    "handlers": ["console"],
                    "propagate": False,
                },
                "uvicorn.access": {
                    "level": "WARNING",
                    "handlers": ["console"],
                    "propagate": False,
                },
            },
        }
    )


def get_logger(name: str) -> logging.Logger:
    """
    Retorna um logger padronizado para o módulo.
    """
    return logging.getLogger(name)
