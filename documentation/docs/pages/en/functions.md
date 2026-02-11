# Functions

## Define

```
define add(a, b=10):
    result a + b

add(2, 3)
add(2)
```

## Multiline Function Calls

Function arguments can span multiple lines for better readability:

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

# Multiline structures with lambda
data = {
    "square": lambda x: x * x,
    "values": [1, 2, 3, 4, 5]
}
```

## Functions with Optional Parameters

```
define greet(name, greeting="Hello"):
    if name == none:
        pass
    else:
        display(greeting + ", " + name)

greet("Alice")
greet("Bob", "Hi")
```

## Returning None

Functions can return `none` to indicate no value:

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