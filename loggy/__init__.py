"""pyloggy: a tiny, dependency-free logger for CLI apps.

The public API is intentionally small:
- `Log`: logger class with `log/info/ok/warn/err` methods
- `LogStyle`: immutable style configuration
- `STYLES`: built-in style presets
- `get_style`: helper to override a named preset
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, replace
from typing import Dict, TextIO, Union


class bcolors:
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    WARNING_ORANGE = "\033[38;5;208m"
    DIM = "\033[2m"
    BOLD = "\033[1m"
    CYAN = "\033[96m"
    GRAY = "\033[90m"


def _is_tty(stream: TextIO) -> bool:
    try:
        return stream.isatty()
    except Exception:
        return False


def _env_true(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class LogStyle:
    # labels
    log_label: str = "[Log]"
    ok_label: str = "[OK]"
    info_label: str = "[Info]"
    warn_label: str = "[Warn]"
    err_label: str = "[Error]"

    # icons
    log_icon: str = "•"
    ok_icon: str = "✅"
    info_icon: str = "ℹ️"
    warn_icon: str = "⚠️"
    err_icon: str = "❌"

    # colors
    log_color: str = bcolors.DIM
    ok_color: str = bcolors.OKGREEN
    info_color: str = bcolors.OKBLUE
    warn_color: str = bcolors.WARNING_ORANGE
    err_color: str = bcolors.FAIL


# ---- Built-in presets ----
STYLES: Dict[str, LogStyle] = {
    "default": LogStyle(),
    "classic": LogStyle(
        log_icon="",
        ok_icon="",
        info_icon="",
        warn_icon="",
        err_icon="",
        log_label="[LOG]",
        ok_label="[OK]",
        info_label="[INFO]",
        warn_label="[WARN]",
        err_label="[ERR]",
    ),
    "minimal": LogStyle(
        log_icon="•",
        ok_icon="✓",
        info_icon="i",
        warn_icon="!",
        err_icon="x",
        log_label="",
        ok_label="",
        info_label="",
        warn_label="",
        err_label="",
        log_color=bcolors.GRAY,
        info_color=bcolors.GRAY,
        warn_color=bcolors.WARNING_ORANGE,
        err_color=bcolors.FAIL,
    ),
    "cli": LogStyle(
        log_icon="›",
        ok_icon="✔",
        info_icon="ℹ",
        warn_icon="▲",
        err_icon="✖",
        log_label="[step]",
        ok_label="[ok]",
        info_label="[info]",
        warn_label="[warn]",
        err_label="[error]",
        log_color=bcolors.DIM,
        ok_color=bcolors.OKGREEN,
        info_color=bcolors.CYAN,
        warn_color=bcolors.WARNING_ORANGE,
        err_color=bcolors.FAIL,
    ),
    "emoji": LogStyle(
        log_icon="📝",
        ok_icon="✅",
        info_icon="🧠",
        warn_icon="⚠️",
        err_icon="💥",
        log_label="[Log]",
        ok_label="[OK]",
        info_label="[Info]",
        warn_label="[Warn]",
        err_label="[Error]",
    ),
    "plain": LogStyle(
        log_icon="",
        ok_icon="",
        info_icon="",
        warn_icon="",
        err_icon="",
        log_color="",
        ok_color="",
        info_color="",
        warn_color="",
        err_color="",
    ),
}


def get_style(name: str, **overrides) -> LogStyle:
    """Return a built-in style by name, with optional field overrides."""
    base = STYLES.get(name, STYLES["default"])
    return replace(base, **overrides) if overrides else base


StyleArg = Union[str, LogStyle, None]


class Log:
    """A tiny logger with style presets and optional color/icon output."""

    def __init__(
        self,
        debug: bool = False,
        verbose: bool = False,
        use_color: bool = True,
        use_icons: bool = True,
        style: StyleArg = None,
        stream_out: TextIO = sys.stdout,
        stream_err: TextIO = sys.stderr,
    ):
        self.debug = debug or _env_true("DEBUG_LOGS")
        self.verbose = verbose or _env_true("VERBOSE_LOGS")

        if isinstance(style, str):
            self.style = get_style(style)
        elif isinstance(style, LogStyle):
            self.style = style
        else:
            self.style = STYLES["default"]

        self.out = stream_out
        self.err_stream = stream_err

        force_color = _env_true("FORCE_COLOR")
        no_color = "NO_COLOR" in os.environ

        self.use_icons = use_icons and _is_tty(self.out)
        self._use_color_out = use_color and not no_color and (force_color or _is_tty(self.out))
        self._use_color_err = use_color and not no_color and (force_color or _is_tty(self.err_stream))

    def _fmt(self, *msg: object) -> str:
        return " ".join(str(m) for m in msg)

    def _prefix(self, icon: str, label: str) -> str:
        normalized_label = label.strip()
        if self.use_icons and icon:
            return f"{icon} {normalized_label}".strip()
        return normalized_label or ""

    def _write(self, stream: TextIO, prefix: str, color: str, use_color: bool, *msg: object) -> None:
        text = self._fmt(*msg)
        line = f"{prefix} {text}" if prefix else text

        if use_color and color:
            stream.write(f"{color}{line}{bcolors.ENDC}\n")
        else:
            stream.write(f"{line}\n")
        stream.flush()

    def log(self, *msg: object) -> None:
        if self.debug:
            self._write(
                self.out,
                self._prefix(self.style.log_icon, self.style.log_label),
                self.style.log_color,
                self._use_color_out,
                *msg,
            )

    def ok(self, *msg: object) -> None:
        self._write(
            self.out,
            self._prefix(self.style.ok_icon, self.style.ok_label),
            self.style.ok_color,
            self._use_color_out,
            *msg,
        )

    def info(self, *msg: object) -> None:
        if self.debug or self.verbose:
            self._write(
                self.out,
                self._prefix(self.style.info_icon, self.style.info_label),
                self.style.info_color,
                self._use_color_out,
                *msg,
            )

    def warn(self, *msg: object) -> None:
        self._write(
            self.out,
            self._prefix(self.style.warn_icon, self.style.warn_label),
            self.style.warn_color,
            self._use_color_out,
            *msg,
        )

    def err(self, *msg: object) -> None:
        self._write(
            self.err_stream,
            self._prefix(self.style.err_icon, self.style.err_label),
            self.style.err_color,
            self._use_color_err,
            *msg,
        )


__all__ = ["Log", "LogStyle", "STYLES", "get_style"]
