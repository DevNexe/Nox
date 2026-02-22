# Functions

## Define

```
define add(a, b=10):
    result a + b

add(2, 3)
add(2)
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
display(square(5))
```

## Decorators

```
define logger(fn):
    define wrapped(*args):
        display("call", fn)
        result fn(*args)
    result wrapped

@logger
define greet(name):
    result "Hello, " + name
```

## Async functions and await

```
async define ping(delay_ms):
    await sleep(delay_ms)
    result "ok"

define main():
    task = create_task(ping, 50)
    result run_async(gather([task]))
```

## Multiline calls

```
result = process_data(
    user_data,
    ["active", "verified"],
    {"timeout": 30},
    true
)
```

## Returning none

```
define find_item(items, target):
    for item in items:
        if item == target:
            result item
    result none
```
