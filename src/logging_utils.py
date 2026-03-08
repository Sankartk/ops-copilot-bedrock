import json
import logging
import os
import time
from contextlib import contextmanager
from typing import Optional


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(record.created)),
            "level": record.levelname,
            "name": record.name,
            "msg": record.getMessage(),
        }
        # include "extra" fields if present
        for k, v in record.__dict__.items():
            if k in ("msg", "args", "levelname", "levelno", "name", "pathname", "filename",
                     "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
                     "created", "msecs", "relativeCreated", "thread", "threadName",
                     "processName", "process"):
                continue
            if k.startswith("_"):
                continue
            payload[k] = v
        return json.dumps(payload, ensure_ascii=False)


def get_logger(name: str) -> logging.Logger:
    level = os.getenv("OPS_LOG_LEVEL", "INFO").upper()
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if logger.handlers:
        return logger  # avoid double handlers in Streamlit reloads

    h = logging.StreamHandler()
    h.setLevel(level)
    h.setFormatter(JsonFormatter())
    logger.addHandler(h)
    logger.propagate = False
    return logger


@contextmanager
def timed(logger: logging.Logger, span: str, **fields):
    t0 = time.time()
    try:
        yield
        dt = time.time() - t0
        logger.info("span", extra={"span": span, "duration_ms": int(dt * 1000), **fields})
    except Exception as e:
        dt = time.time() - t0
        logger.exception("span_error", extra={"span": span, "duration_ms": int(dt * 1000), **fields})
        raise