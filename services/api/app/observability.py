"""Structured, correlated events without request bodies or credentials."""

import contextvars
import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from app.config import settings
from app.domain.models import now_iso

request_id = contextvars.ContextVar("request_id", default="background")
logger = logging.getLogger("company_brain")


class JsonFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps(
            {
                "timestamp": now_iso(),
                "level": record.levelname,
                "request_id": getattr(record, "correlation_id", request_id.get()),
                "event": record.getMessage(),
                **getattr(record, "fields", {}),
            }
        )


def configure():
    if any(getattr(h, "_brain", False) for h in logger.handlers):
        return
    path = Path(settings.log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(path, maxBytes=5_000_000, backupCount=3)
    handler.setFormatter(JsonFormatter())
    handler._brain = True
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False


def event(name, level=logging.INFO, **fields):
    logger.log(level, name, extra={"fields": fields, "correlation_id": request_id.get()})
