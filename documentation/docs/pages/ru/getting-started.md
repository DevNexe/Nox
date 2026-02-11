# Быстрый старт

1. Создайте файл с расширением `.nox`.
2. Запустите: `py -m nox yourfile.nox`.
3. Можно запускать папку: `py -m nox path/to/folder`. Nox ищет `__main__.nox`, `main.nox` или `app.nox`.

## Структура проекта

```
project/
  main.nox
```

## Запуск

```
py -m nox main.nox
py -m nox examples
```

## Первая программа

Создайте `hello.nox`:

```
# Базовый вывод
display("Привет, Nox!")

# Переменные
name = "Мир"
display("Привет, " + name)

# Многострочные структуры
data = {
    "name": "Alice",
    "age": 30,
    "skills": [
        "Python",
        "Nox",
        "JavaScript"
    ]
}

# Доступ к данным
display(data["name"])
display(data["skills"][0])

# Срезы строк
text = "Nox"
display(text[0:3])      # Nox
display(text[3:])       # Lang
```

## Часто используемые паттерны

### Функция с многострочными аргументами

```
define greet(first_name, last_name, age):
    result first_name + " " + last_name + " is " + display(age)

name = greet(
    "John",
    "Doe",
    30
)

display(name)
```

### Условие с pass

```
define handle_value(x):
    if x == none:
        pass  # Ничего не делать для none
    else:
        display(x)
```

### Работа со срезами

```
items = [1, 2, 3, 4, 5]
display(items[1:4])     # [2, 3, 4]
display(items[::2])     # [1, 3, 5]

text = "Nox"
display(text[::-1])     # gnaLxoN
```