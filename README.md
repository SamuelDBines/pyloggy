# loggy (name it whatever)

A tiny, dependency-free Python logger with:
- ANSI colors (auto-disabled when not in a TTY)
- Optional icons (auto-disabled when not in a TTY)
- Simple log levels: log / info / ok / warn / err
- Per-project overrides for labels, icons, and colors

## Install

### Local dev install (recommended while iterating)
From another project:

```bash
pip install "git+https://github.com/SamuelDBines/pyloggy.git"
```

## Usage

```python
from loggy import Log

from loggy import Log

p = Log(debug=True, style="minimal")

p.log("starting…")
p.info("hello")
p.ok("done")
p.warn("something odd")
p.err("boom")
```

### Style overrides
```python
from loggy import Log, get_style

p = Log(debug=True, style=get_style("cli", warn_icon="⚠", warn_label="[W]"))
p.warn("visible")
```