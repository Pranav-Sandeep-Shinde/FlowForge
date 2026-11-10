import logging
from .context import request_id_var
class RequestIDFilter(logging.Filter):
    """
    Logging filter that adds the request ID to log records.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        return True