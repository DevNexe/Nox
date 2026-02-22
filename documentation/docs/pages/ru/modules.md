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

Также можно использовать URL репозитория:

```
py -m nox package install https://github.com/user/repo
```

Другие команды:

```
py -m nox package list
py -m nox package remove repo
```

### Порядок поиска модулей

`connect a.b` ищет модуль:
1. В текущем проекте (относительно запускаемого файла)
2. В `Libraries/`
