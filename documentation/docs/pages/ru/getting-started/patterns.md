# Общие паттерны

Полезные паттерны кода для программирования на Nox.

## Проверка на None

```
value = get_value()

if value == none:
    display("Нет значения")
else:
    display("Значение: " + value)
```

## Значения по умолчанию

```
config = get_config()

if config == none:
    config = {
        "host": "localhost",
        "port": 8080
    }
```

## Безопасный доступ к коллекциям

```
items = get_items()

if items != none and len(items) > 0:
    for item in items:
        process(item)
```

## Фильтр и преобразование

```
numbers = [1, 2, 3, 4, 5]
even_numbers = []

for num in numbers:
    if num % 2 == 0:
        even_numbers.append(num)

display(even_numbers)  # [2, 4]
```

## Обработка строк

```
text = "Привет, Мир!"

# Прописные
display(text.upper())

# Срез
display(text[0:7])     # "Привет"

# Заменить
display(text.replace("Мир", "Nox"))

# Найти
if "Мир" in text:
    display("Найдено!")
```

## Цикл с индексом

```
items = ["a", "b", "c"]

for i in range(len(items)):
    display(i + ": " + items[i])
```

## многострочная читаемость

```
result = complex_function(
    param1,
    param2,
    options={
        "timeout": 30,
        "retry": 3
    }
)
```

## Паттерн обработки ошибок

```
define safe_operation(value):
    if value == none:
        return none
    
    if value < 0:
        return none
    
    return value * 2

result = safe_operation(10)

if result != none:
    display("Успех: " + result)
else:
    display("Ошибка")
```

## Pass заполнитель

```
if condition:
    pass  # TODO: Реализовать позже
else:
    actual_code()
```

## Работа со словарями

```
config = {
    "database": {
        "host": "localhost",
        "port": 5432
    },
    "cache": {
        "enabled": true,
        "ttl": 3600
    }
}

for section in config:
    display(section + ": " + config[section])
```

## Вложенные циклы с управлением

```
matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
]

for row in matrix:
    for value in row:
        display(value)
```

## Функция, возвращающая None

```
define log_event(event):
    display("[LOG] " + event)
    # Возвращает none неявно

result = log_event("User login")
# result == none
```
