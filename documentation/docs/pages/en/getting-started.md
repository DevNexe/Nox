# Getting Started

1. Create a file with the extension `.nox`.
2. Run it with `py -m nox yourfile.nox`.
3. You can also run a folder: `py -m nox path/to/folder`. Nox looks for `__main__.nox`, `main.nox`, or `app.nox`.

## Project Layout

```
project/
  app.nox
  Libraries/
  templates/
  static/
```

## Running

```
py -m nox app.nox
py -m nox examples
```