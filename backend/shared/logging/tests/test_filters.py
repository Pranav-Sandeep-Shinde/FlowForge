import logging

from shared.logging.context import request_id_var
from shared.logging.filters import RequestIDFilter


def make_log_record() -> logging.LogRecord:
	return logging.LogRecord(
		name="test",
		level=logging.INFO,
		pathname=__file__,
		lineno=1,
		msg="test message",
		args=(),
		exc_info=None,
	)


def test_filter_adds_default_request_id_to_log_record():
	record = make_log_record()

	assert RequestIDFilter().filter(record) is True
	assert record.request_id == "-"


def test_filter_adds_current_request_id_to_log_record():
	token = request_id_var.set("request-123")
	try:
		record = make_log_record()

		assert RequestIDFilter().filter(record) is True
		assert record.request_id == "request-123"
	finally:
		request_id_var.reset(token)
