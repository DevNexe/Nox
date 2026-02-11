# Common Patterns

Useful code patterns for Nox programming.

## Checking for None

```
value = get_value()

if value == none:
    display("No value")
else:
    display("Value: " + value)
```

## Default Values

```
config = get_config()

if config == none:
    config = {
        "host": "localhost",
        "port": 8080
    }
```

## Safe Collection Access

```
items = get_items()

if items != none and len(items) > 0:
    for item in items:
        process(item)
```

## Filter and Transform

```
numbers = [1, 2, 3, 4, 5]
even_numbers = []

for num in numbers:
    if num % 2 == 0:
        even_numbers.append(num)

display(even_numbers)  # [2, 4]
```

## String Processing

```
text = "Hello, World!"

# Uppercase
display(text.upper())

# Slice
display(text[0:5])     # "Hello"

# Replace
display(text.replace("World", "Nox"))

# Find
if "World" in text:
    display("Found!")
```

## Loop with Index

```
items = ["a", "b", "c"]

for i in range(len(items)):
    display(i + ": " + items[i])
```

## Multiline Readability

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

## Error Handling Pattern

```
define safe_operation(value):
    if value == none:
        return none
    
    if value < 0:
        return none
    
    return value * 2

result = safe_operation(10)

if result != none:
    display("Success: " + result)
else:
    display("Failed")
```

## Pass Placeholder

```
if condition:
    pass  # TODO: Implement later
else:
    actual_code()
```

## Working with Dictionaries

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

## Nested Loops with Control

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

## Function Returning None

```
define log_event(event):
    display("[LOG] " + event)
    # Returns none implicitly

result = log_event("User login")
# result == none
```
