# Modules

Use `connect` to import modules, and `from ... connect` for specific names.

```
connect math
connect json as j
from string connect split
```

## Libraries

Install libraries into `Libraries/` with:

```
py -m nox package install user/repo
```