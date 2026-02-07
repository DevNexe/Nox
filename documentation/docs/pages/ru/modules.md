# Модули

Для импорта используйте `connect`, а для отдельных имен — `from ... connect`.

```
connect math
connect json as j
from string connect split
```

## Библиотеки

Установка библиотек в `Libraries/`:

```
py -m nox package install user/repo
```