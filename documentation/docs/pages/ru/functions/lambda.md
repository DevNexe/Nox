# Lambda функции

Lambda функции — это анонимные встроенные функции. Они полезны для простых операций.

## Базовая lambda

```
square = lambda x: x * x

display(square(5))  # 25
```

## Lambda с несколькими параметрами

```
add = lambda x, y: x + y

result = add(3, 4)
display(result)     # 7
```

## Lambda, возвращающая None

```
log = lambda msg: display(msg)

log("Сообщение")  # Также выводит: none
```

## Lambda в коллекциях

```
items = [
    lambda: 1 + 1,
    lambda: 2 * 3,
    lambda: 5 - 2
]

for func in items:
    display(func())
```

## Lambda с условиями

```
absolute = lambda x: x if x > 0 else -x

display(absolute(-5))   # 5
display(absolute(3))    # 3
```

## Сравнение с None

```
check_value = lambda v: v != none

if check_value(42):
    display("Есть значение")
```

## Lambda с многострочными структурами

```
process = lambda data: transform(
    data,
    options={
        "format": "json",
        "validate": true
    }
)
```

## Хранение Lambda

```
operations = {
    "add": lambda a, b: a + b,
    "multiply": lambda a, b: a * b,
    "divide": lambda a, b: a / b if b != 0 else none
}

display(operations["add"](10, 5))  # 15
```

## Ограничения

- Держите lambda функции простыми
- Для сложной логики используйте обычные `define` функции
- Избегайте длинных lambda выражений
