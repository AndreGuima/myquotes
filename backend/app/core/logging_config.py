import logging
import os
import sys
from logging.config import dictConfig
from typing import Literal

# =========================================================
# Configuração central de logging do MyQuotes
# =========================================================

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


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


def setup_logging() -> None:
    """
    Inicializa a configuração global de logging.
    Deve ser chamada UMA vez no startup da aplicação.
    """
    log_level = get_log_level()

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
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
                    "formatter": "verbose" if log_level == "DEBUG" else "default",
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
