# Определение функций

Функции — это переиспользуемые блоки кода, которые выполняют определенную задачу.

## Базовое определение функции

```
define greet(name):
    display("Привет, " + name)

greet("Alice")
```

## Функция с возвращаемым значением

```
define add(a, b):
    return a + b

result = add(5, 3)
display(result)     # 8
```

## Функция с несколькими параметрами

```
define full_name(first, last, middle):
    return first + " " + middle + " " + last

name = full_name("John", "Doe", "Q")
display(name)       # "John Q Doe"
```

## Функция, возвращающая None

Функции возвращают `none` по умолчанию:

```
define log_message(msg):
    display("[LOG] " + msg)

result = log_message("Привет")
display(result == none)  # true
```

## Явный возврат None

```
define find_user(id):
    if id > 0:
        return get_user(id)
    return none
```

## Необязательные параметры со значениями по умолчанию

```
define create_user(name, email):
    return {
        "name": name,
        "email": email,
        "created": true
    }

user = create_user("Alice", "alice@example.com")
```

## Вложенные функции

```
define outer(x):
    define inner(y):
        return x + y
    return inner(10)

display(outer(5))  # 15
```

## Рекурсивные функции

```
define factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

display(factorial(5))  # 120
```

## Функция с многострочным телом

```
define process_data(items):
    if items == none:
        return none
    
    result = []
    for item in items:
        result.append(item * 2)
    
    return result
```

## Лучшие практики

- Используйте описательные имена функций
- Держите функции сосредоточенными на одной задаче
- Добавляйте комментарии для объяснения сложной логики
- Используйте `return` для раннего выхода при необходимости
