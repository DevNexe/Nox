# Variadic Functions

Functions with variable numbers of arguments using `*args` and `**kwargs`.

## Basic *args

Collect positional arguments into a list:

```
define print_all(*args):
    for item in args:
        display(item)

print_all("a", "b", "c")
```

## Using *args in Calculations

```
define sum_all(*numbers):
    total = 0
    for n in numbers:
        total = total + n
    return total

display(sum_all(1, 2, 3, 4, 5))  # 15
```

## **kwargs for Keyword Arguments

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

## Combining Parameters

```
define flexible_function(name, *args, **kwargs):
    display("Name: " + name)
    
    if len(args) > 0:
        display("Args: ")
        for arg in args:
            display("  - " + arg)
    
    if len(kwargs) > 0:
        display("Options: ")
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

## Default and Variadic

```
define process_items(prefix, *items, **options):
    for item in items:
        display(prefix + ": " + item)
    
    if options["verbose"] == true:
        display("Done")

process_items(
    "Item",
    "a",
    "b",
    "c",
    verbose=true
)
```

## Returning from Variadic Functions

```
define combine(*values):
    result = none
    
    if len(values) > 0:
        result = 0
        for v in values:
            result = result + v
    
    return result
```

## Use Cases

- Building flexible APIs
- Creating wrapper functions
- Handling optional arguments
- Forwarding arguments to other functions
