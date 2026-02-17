# pyloggy

`pyloggy` is a tiny, dependency-free logger for CLI scripts and tools.

It focuses on practical terminal output:
- level methods: `log`, `info`, `ok`, `warn`, `err`
- style presets (labels, icons, colors)
- auto TTY behavior (no ANSI noise in redirected logs)
- stream-aware output (`stdout` for normal logs, `stderr` for errors)

## Install

### From GitHub

```bash
pip install "git+https://github.com/SamuelDBines/pyloggy.git"
```

### Local editable install

```bash
pip install -e .
```

## Quick Start

```python
from loggy import Log

log = Log(debug=True, verbose=True, style="cli")

log.log("Boot sequence started")
log.info("Loading config")
log.ok("Connected")
log.warn("Retrying stale cache")
log.err("Connection failed")
```

## Pick The Right Method

- `log(...)`: debug-step output (hidden unless debug is enabled)
- `info(...)`: verbose progress output (hidden unless verbose/debug is enabled)
- `ok(...)`: success checkpoints
- `warn(...)`: non-fatal warnings
- `err(...)`: failures and errors (goes to `stderr`)

## How It Works

`Log` has two visibility toggles:
- `debug`: enables `log(...)`
- `verbose`: enables `info(...)` (also enabled if `debug=True`)

Always-on methods:
- `ok(...)`
- `warn(...)`
- `err(...)`

Routing:
- `log/info/ok/warn` write to `stdout`
- `err` writes to `stderr`

Formatting:
- prefix = icon + label (from selected style)
- message = all args joined by spaces
- ANSI color is applied only when enabled

## Constructor Reference

```python
Log(
    debug: bool = False,
    verbose: bool = False,
    use_color: bool = True,
    use_icons: bool = True,
    style: str | LogStyle | None = None,
    stream_out = sys.stdout,
    stream_err = sys.stderr,
)
```

### Typical Constructor Setups

```python
# quiet production defaults
Log()

# debug-heavy local dev
Log(debug=True, verbose=True, style="cli")

# CI-safe plain text output
Log(use_color=False, use_icons=False, style="plain")
```

## Style Presets

Built-in preset names:
- `default`
- `classic`
- `minimal`
- `cli`
- `emoji`
- `plain`

Use a preset:

```python
from loggy import Log

log = Log(style="minimal")
```

Customize a preset with `get_style`:

```python
from loggy import Log, get_style

custom = get_style(
    "cli",
    warn_icon="⚠",
    warn_label="[warning]",
)
log = Log(style=custom)
```

## Environment Variables

`pyloggy` supports these env flags:
- `DEBUG_LOGS=1` enables debug output
- `VERBOSE_LOGS=1` enables info output
- `NO_COLOR=1` disables color output
- `FORCE_COLOR=1` forces colors even in non-TTY contexts

Note: `NO_COLOR` takes priority over `FORCE_COLOR`.

## Package API

```python
from loggy import Log, LogStyle, STYLES, get_style
```

## Reusable Package Workflow

1. Keep API stable in `loggy/__init__.py`.
2. Update version in `pyproject.toml`.
3. Build distributions:

```bash
python -m build
```

4. Publish to PyPI (example):

```bash
python -m twine upload dist/*
```

## GitHub Pages Docs

This repository includes:
- `public/index.html` (static docs site)
- `.github/workflows/pages.yml` (deploy pipeline)

On push to `main`/`master`, GitHub Actions deploys `public/` to Pages.

## Local Docs Preview

Open `public/index.html` directly in your browser to preview docs changes before pushing.
