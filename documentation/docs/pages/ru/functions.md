# Функции

## define

```
define add(a, b=10):
    result a + b

add(2, 3)
add(2)
```

## Многострочные вызовы функций

Аргументы функции могут занимать несколько строк для лучшей читаемости:

```
define process_data(data, filters, options, verbose):
    if verbose == none:
        pass
    result data

result = process_data(
    user_data,
    [
        "active",
        "verified"
    ],
    {
        "timeout": 30,
        "retries": 3
    },
    true
)
```

## Varargs

```
define sum_all(*xs):
    total = 0
    for x in xs:
        total = total + x
    result total

sum_all(1, 2, 3, 4, 5)
```

## Lambda

```
square = lambda x: x * x
result square(5)

# Многострочные структуры с lambda
data = {
    "square": lambda x: x * x,
    "values": [1, 2, 3, 4, 5]
}
```

## Декораторы

```
define logger(fn):
    define wrapped(*args):
        display("call", fn)
        result fn(*args)
    result wrapped

@logger
define greet(name):
    result "Привет, " + name
```

## Async и await

```
async define ping(delay_ms):
    await sleep(delay_ms)
    result "ok"

task = create_task(ping, 50)
result = run_async(gather([task]))
```

## Функции с опциональными параметрами

```
define greet(name, greeting="Привет"):
    if name == none:
        pass
    else:
        display(greeting + ", " + name)

greet("Alice")
greet("Bob", "Привет")
```

## Возврат None

Функции могут возвращать `none` для указания отсутствия значения:

```
define find_item(items, target):
    for item in items:
        if item == target:
            result item
    result none

result = find_item(
    [1, 2, 3, 4, 5],
    10
)
```
