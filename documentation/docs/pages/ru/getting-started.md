# Быстрый старт

1. Создайте файл с расширением `.nox`.
2. Запустите: `py -m nox yourfile.nox`.
3. Можно запускать папку: `py -m nox path/to/folder`. Nox ищет `__main__.nox`, `main.nox` или `app.nox`.

## Структура проекта

```
project/
  app.nox
  Libraries/
  templates/
  static/
```

## Запуск

```
py -m nox app.nox
py -m nox examples
```