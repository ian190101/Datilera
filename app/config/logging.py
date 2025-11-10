from __future__ import annotations

import json
import logging
import sys
from datetime import datetime
from logging.config import dictConfig
from typing import Literal


def _json_formatter(record: logging.LogRecord) -> str:
    # Formato JSON simple y rápido, compatible con Cloud/ELK
    payload = {
        "ts": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
        "level": record.levelname,
        "logger": record.name,
        "msg": record.getMessage(),
        "module": record.module,
        "func": record.funcName,
        "line": record.lineno,
    }
    if record.exc_info:
        payload["exc_info"] = logging.Formatter().formatException(record.exc_info)
    return json.dumps(payload, ensure_ascii=False)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        return _json_formatter(record)


def setup_logging(
    level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO",
    json_logs: bool = False,
    sql_echo: bool = False,
) -> None:
    """
    Configura logging de la aplicación y librerías principales.

    level: nivel raíz de logging.
    json_logs: si True, emite logs en JSON; si False, formato de texto.
    sql_echo: si True, sube a INFO el logger sqlalchemy.engine.
    """
    formatter_name = "json" if json_logs else "std"

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "std": {
                    "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
                },
                "json": {
                    "()": "app.config.logging.JsonFormatter",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "stream": sys.stdout,
                    "formatter": formatter_name,
                    "level": level,
                },
            },
            "loggers": {
                # Uvicorn
                "uvicorn": {"handlers": ["console"], "level": level, "propagate": False},
                "uvicorn.error": {"handlers": ["console"], "level": level, "propagate": False},
                "uvicorn.access": {"handlers": ["console"], "level": level, "propagate": False},
                # SQLAlchemy: elevar a INFO si necesitas ver SQL (o usar settings.sql_echo)
                "sqlalchemy.engine": {
                    "handlers": ["console"],
                    "level": "INFO" if sql_echo else "WARNING",
                    "propagate": False,
                },
                # Tu app
                "app": {"handlers": ["console"], "level": level, "propagate": False},
            },
            "root": {"handlers": ["console"], "level": level},
        }
    )
    logging.getLogger("app").info("Logging configured (level=%s, json=%s, sql_echo=%s)", level, json_logs, sql_echo)
