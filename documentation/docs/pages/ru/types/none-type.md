# Тип None

Значение `none` представляет отсутствие значения. Это единственное значение типа `none`.

## Что такое None?

`none` используется когда:
- Функция не возвращает значимое значение
- Переменная не должна иметь значение
- Нужно проверить отсутствие чего-либо

```
result = none

if result == none:
    display("Результата еще нет")
```

## Возврат None

Функции возвращают `none` по умолчанию, если не указано другого:

```
define greet(name):
    display("Привет, " + name)
    # Неявно возвращает none

x = greet("Alice")
display(x == none)  # true
```

Явно вернуть `none`:

```
define safe_divide(a, b):
    if b == 0:
        return none
    return a / b

result = safe_divide(10, 0)
if result == none:
    display("Нельзя делить на ноль")
```

## Проверка на None

```
if value != none:
    process(value)

# Многострочная структура
data = {
    "optional_field": none,
    "required_field": "value"
}

if data["optional_field"] == none:
    display("Поле не установлено")
```

## None в коллекциях

```
items = [1, none, 3]
optional_dict = {
    "a": 1,
    "b": none
}

if items[1] == none:
    display("Элемент не найден")
```

## Общие паттерны

```
# Значения none по умолчанию
define find_user(id):
    if id < 0:
        return none
    return get_user_from_db(id)

user = find_user(-1)
display(user != none)  # false

# Проверить none в условиях
define process_data(data):
    if data == none:
        pass  # Пропустить обработку
    else:
        transform(data)
```
