# None Type

The `none` value represents the absence of a value. It is the only value of the `none` type.

## What is None?

`none` is used when:
- A function doesn't return a meaningful value
- A variable should have no value
- You need to check if something is missing

```
result = none

if result == none:
    display("No result yet")
```

## Returning None

Functions return `none` by default if no explicit return value is given:

```
define greet(name):
    display("Hello, " + name)
    # Implicitly returns none

x = greet("Alice")
display(x == none)  # true
```

Explicitly return `none`:

```
define safe_divide(a, b):
    if b == 0:
        return none
    return a / b

result = safe_divide(10, 0)
if result == none:
    display("Cannot divide by zero")
```

## Checking for None

```
if value != none:
    process(value)

# Multiline structure
data = {
    "optional_field": none,
    "required_field": "value"
}

if data["optional_field"] == none:
    display("Field not set")
```

## None in Collections

```
items = [1, none, 3]
optional_dict = {
    "a": 1,
    "b": none
}

if items[1] == none:
    display("Item not found")
```

## Common Patterns

```
# Default None values
define find_user(id):
    if id < 0:
        return none
    return get_user_from_db(id)

user = find_user(-1)
display(user != none)  # false

# Check for none in conditions
define process_data(data):
    if data == none:
        pass  # Skip processing
    else:
        transform(data)
```
