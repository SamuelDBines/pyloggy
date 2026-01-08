from __future__ import annotations

import os
import sys
from dataclasses import dataclass, replace
from typing import Dict, Optional, TextIO, Union


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
    base = STYLES.get(name, STYLES["default"])
    return replace(base, **overrides) if overrides else base


StyleArg = Union[str, LogStyle, None]


class Log:
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
        self.debug = debug or (os.getenv("DEBUG_LOGS", "").lower() in {"1", "true", "yes"})

        if isinstance(style, str):
            self.style = get_style(style)
        elif isinstance(style, LogStyle):
            self.style = style
        else:
            self.style = STYLES["default"]

        # auto-disable in non-tty
        self.use_color = use_color and _is_tty(stream_out)
        self.use_icons = use_icons and _is_tty(stream_out)

        self.out = stream_out
        self.err_stream = stream_err

    def _fmt(self, *msg) -> str:
        return " ".join(str(m) for m in msg)

    def _prefix(self, icon: str, label: str) -> str:
        label = label.strip()
        if self.use_icons and icon:
            return f"{icon} {label}".strip()
        return label or ""

    def _write(self, stream: TextIO, prefix: str, color: str, *msg):
        text = self._fmt(*msg)
        if prefix:
            line = f"{prefix} {text}"
        else:
            line = text

        if self.use_color and color:
            stream.write(f"{color}{line}{bcolors.ENDC}\n")
        else:
            stream.write(f"{line}\n")
        stream.flush()

    def log(self, *msg):
        if self.debug:
            self._write(
                self.out,
                self._prefix(self.style.log_icon, self.style.log_label),
                self.style.log_color,
                *msg,
            )

    def ok(self, *msg):
        self._write(
            self.out,
            self._prefix(self.style.ok_icon, self.style.ok_label),
            self.style.ok_color,
            *msg,
        )

    def info(self, *msg):
        if self.debug:
            self._write(
                self.out,
                self._prefix(self.style.info_icon, self.style.info_label),
                self.style.info_color,
                *msg,
            )

    def warn(self, *msg):
        self._write(
            self.out,
            self._prefix(self.style.warn_icon, self.style.warn_label),
            self.style.warn_color,
            *msg,
        )

    def err(self, *msg):
        self._write(
            self.err_stream,
            self._prefix(self.style.err_icon, self.style.err_label),
            self.style.err_color,
            *msg,
        )
