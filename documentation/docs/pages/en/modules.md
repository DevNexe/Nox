# Modules

Use `connect` to import a module, and `from ... connect` to import selected names.

```
connect math
connect json as j
from string connect split, join as sjoin
```

## Resolution order

When you import `connect a.b`, Nox searches:

1. Current project (relative to the running script)
2. Installed libraries in `Libraries/`

Supported file layouts include:

- `a/b.nox`
- `a/b/__init__.nox`
- `Libraries/a/main.nox`

## Library management

Install into `Libraries/`:

```
py -m nox package install user/repo
```

Install by URL:

```
py -m nox package install https://github.com/user/repo
```

List and remove:

```
py -m nox package list
py -m nox package remove repo
```
