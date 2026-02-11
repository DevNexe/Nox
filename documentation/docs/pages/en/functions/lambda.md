# Lambda Functions

Lambda functions are anonymous, inline functions. They are useful for simple operations.

## Basic Lambda

```
square = lambda x: x * x

display(square(5))  # 25
```

## Lambda with Multiple Parameters

```
add = lambda x, y: x + y

result = add(3, 4)
display(result)     # 7
```

## Lambda Returning None

```
log = lambda msg: display(msg)

log("Message")  # Also displays: none
```

## Lambda in Collections

```
items = [
    lambda: 1 + 1,
    lambda: 2 * 3,
    lambda: 5 - 2
]

for func in items:
    display(func())
```

## Lambda with Conditionals

```
absolute = lambda x: x if x > 0 else -x

display(absolute(-5))   # 5
display(absolute(3))    # 3
```

## Comparing with None

```
check_value = lambda v: v != none

if check_value(42):
    display("Has value")
```

## Lambda with Multiline Structures

```
process = lambda data: transform(
    data,
    options={
        "format": "json",
        "validate": true
    }
)
```

## Storing Lambdas

```
operations = {
    "add": lambda a, b: a + b,
    "multiply": lambda a, b: a * b,
    "divide": lambda a, b: a / b if b != 0 else none
}

display(operations["add"](10, 5))  # 15
```

## Limitations

- Keep lambda functions simple
- For complex logic, use regular `define` functions
- Avoid long lambda expressions
