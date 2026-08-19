"""Tests for :mod:`aios.core.logging`."""

from __future__ import annotations

import json
import logging

import pytest

from aios.core.config import Config
from aios.core.logging import JSONFormatter, TextFormatter, get_logger, setup_logging


class TestJSONFormatter:
    """Verify JSON log envelope structure."""

    def test_produces_valid_json(self):
        fmt = JSONFormatter()
        record = logging.LogRecord(
            name="test", level=logging.INFO, pathname="", lineno=0,
            msg="hello", args=(), exc_info=None,
        )
        output = fmt.format(record)
        parsed = json.loads(output)
        assert parsed["level"] == "INFO"
        assert parsed["logger"] == "test"
        assert parsed["message"] == "hello"
        assert "timestamp" in parsed

    def test_extra_field_in_envelope(self):
        fmt = JSONFormatter()
        record = logging.LogRecord(
            name="test", level=logging.WARNING, pathname="", lineno=0,
            msg="warn", args=(), exc_info=None,
        )
        record.extra = {"key": "value"}  # type: ignore[attr-defined]
        parsed = json.loads(fmt.format(record))
        assert parsed["extra"] == {"key": "value"}


class TestTextFormatter:
    """Verify human-readable text format."""

    def test_contains_level_and_message(self):
        fmt = TextFormatter()
        record = logging.LogRecord(
            name="test.module", level=logging.ERROR, pathname="", lineno=0,
            msg="oops", args=(), exc_info=None,
        )
        output = fmt.format(record)
        assert "ERROR" in output
        assert "test.module" in output
        assert "oops" in output


class TestSetupLogging:
    """Verify root logger configuration."""

    def test_sets_root_level(self):
        cfg = Config(log_level="WARNING")
        returned_cfg = setup_logging(cfg)
        assert returned_cfg is cfg
        root = logging.getLogger()
        assert root.level == logging.WARNING

    def test_default_config_used_when_none(self):
        returned_cfg = setup_logging()
        assert returned_cfg.log_level in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}

    def test_attaches_handler(self):
        setup_logging()
        root = logging.getLogger()
        assert len(root.handlers) >= 1


class TestGetLogger:
    """Verify module logger factory."""

    def test_returns_logger_under_aios(self):
        log = get_logger("core.config")
        assert log.name == "aios.core.config"

    def test_preserves_full_aios_prefix(self):
        log = get_logger("aios.core.config")
        assert log.name == "aios.core.config"
