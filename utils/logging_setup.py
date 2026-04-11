"""Logging helpers: console + timestamped file handler, and a stream bridge for RLM verbose output."""

from __future__ import annotations

import io
import logging
from datetime import datetime
from pathlib import Path


class _LoggingStream(io.TextIOBase):
    """Redirects write() calls (e.g. from RLM verbose print) into the logger."""

    def __init__(self, logger: logging.Logger, level: int = logging.INFO) -> None:
        self._logger = logger
        self._level = level
        self._buf = ""

    def write(self, s: str) -> int:
        self._buf += s
        while "\n" in self._buf:
            line, self._buf = self._buf.split("\n", 1)
            if line.strip():
                self._logger.log(self._level, "%s", line)
        return len(s)

    def flush(self) -> None:
        if self._buf.strip():
            self._logger.log(self._level, "%s", self._buf)
        self._buf = ""


def configure_logging(logs_dir: Path) -> logging.Logger:
    """Set up console + file logging and return the root logger for __main__."""
    logs_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = logs_dir / f"run_{timestamp}.log"

    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(console_handler)
    root.addHandler(file_handler)

    for noisy in ("openai", "httpcore", "httpx", "urllib3", "asyncio"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    logger = logging.getLogger("__main__")
    logger.info("Log file: %s", log_path)
    return logger
