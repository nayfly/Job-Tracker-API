import json
import logging
import contextvars
from datetime import datetime


# contextvar used to store the current request id for the formatter
request_id_var: contextvars.ContextVar[str | None] = contextvars.ContextVar("request_id", default=None)


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        # base fields
        data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        # pull request id from contextvar if not explicitly on record
        rid = getattr(record, "request_id", None) or request_id_var.get()
        if rid:
            data["request_id"] = rid
        # include exception info if any
        if record.exc_info:
            data["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(data)


def setup_logging(json_output: bool = True) -> None:
    """Configure root logger for the app.

    If ``json_output`` is True (default) logs are formatted as simple
    JSON objects. Otherwise standard human-readable logging is used.
    """
    handler = logging.StreamHandler()
    if json_output:
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers[:] = [handler]
