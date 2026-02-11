# Returning None

Functions return `none` by default when no explicit return statement is present.

## Implicit None Return

```
define greet(name):
    display("Hello, " + name)

result = greet("Alice")
display(result == none)  # true
```

## Explicit None Return

Explicitly return `none`:

```
define validate(value):
    if value == none:
        return none
    
    if value < 0:
        return none
    
    return value * 2
```

## None in Control Flow

```
define find_item(items, target):
    for item in items:
        if item == target:
            return item
    
    return none  # Not found

result = find_item([1, 2, 3], 5)
if result == none:
    display("Not found")
```

## Safe Operations with None

```
define safe_operation(data):
    if data == none:
        return none
    
    transformed = transform_data(data)
    
    if transformed == none:
        return none
    
    return process(transformed)
```

## Default None Values

```
define configure(name, value):
    result = none
    
    if value != none:
        result = save_config(name, value)
    
    return result
```

## Multiple Return Paths

```
define check_and_process(items):
    if items == none:
        display("Null items")
        return none
    
    if len(items) == 0:
        display("Empty items")
        return none
    
    return transform(items)
```

## Function Chain with None Checks

```
define chain_operations(input):
    step1 = process1(input)
    if step1 == none:
        return none
    
    step2 = process2(step1)
    if step2 == none:
        return none
    
    return process3(step2)
```

## Best Practices

- Use meaningful return values when possible
- Return `none` for "no result" cases
- Check for `none` before using return values
- Document when functions return `none`
