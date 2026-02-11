# Функции с переменным числом аргументов

Функции с переменным количеством аргументов с использованием `*args` и `**kwargs`.

## Базовый *args

Собирает позиционные аргументы в список:

```
define print_all(*args):
    for item in args:
        display(item)

print_all("a", "b", "c")
```

## Использование *args в вычислениях

```
define sum_all(*numbers):
    total = 0
    for n in numbers:
        total = total + n
    return total

display(sum_all(1, 2, 3, 4, 5))  # 15
```

## **kwargs для ключевых аргументов

```
define create_config(**options):
    config = {}
    for key in options:
        config[key] = options[key]
    return config

cfg = create_config(
    host="localhost",
    port=8080,
    debug=true
)
```

## Объединение параметров

```
define flexible_function(name, *args, **kwargs):
    display("Имя: " + name)
    
    if len(args) > 0:
        display("Args: ")
        for arg in args:
            display("  - " + arg)
    
    if len(kwargs) > 0:
        display("Опции: ")
        for key in kwargs:
            display("  - " + key + ": " + kwargs[key])

flexible_function(
    "test",
    "extra1",
    "extra2",
    debug=true,
    level=5
)
```

## Значения по умолчанию и переменные

```
define process_items(prefix, *items, **options):
    for item in items:
        display(prefix + ": " + item)
    
    if options["verbose"] == true:
        display("Готово")

process_items(
    "Item",
    "a",
    "b",
    "c",
    verbose=true
)
```

## Возврат из функций с переменными аргументами

```
define combine(*values):
    result = none
    
    if len(values) > 0:
        result = 0
        for v in values:
            result = result + v
    
    return result
```

## Варианты использования

- Построение гибких API
- Создание оборачивающих функций
- Обработка необязательных аргументов
- Передача аргументов другим функциям
