# Define Functions

Functions are reusable blocks of code that perform a specific task.

## Basic Function Definition

```
define greet(name):
    display("Hello, " + name)

greet("Alice")
```

## Function with Return Value

```
define add(a, b):
    return a + b

result = add(5, 3)
display(result)     # 8
```

## Function with Multiple Parameters

```
define full_name(first, last, middle):
    return first + " " + middle + " " + last

name = full_name("John", "Doe", "Q")
display(name)       # "John Q Doe"
```

## Function Returning None

Functions return `none` by default:

```
define log_message(msg):
    display("[LOG] " + msg)

result = log_message("Hello")
display(result == none)  # true
```

## Explicit None Return

```
define find_user(id):
    if id > 0:
        return get_user(id)
    return none
```

## Optional Parameters with Defaults

```
define create_user(name, email):
    return {
        "name": name,
        "email": email,
        "created": true
    }

user = create_user("Alice", "alice@example.com")
```

## Nested Functions

```
define outer(x):
    define inner(y):
        return x + y
    return inner(10)

display(outer(5))  # 15
```

## Recursive Functions

```
define factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

display(factorial(5))  # 120
```

## Function with Multiline Body

```
define process_data(items):
    if items == none:
        return none
    
    result = []
    for item in items:
        result.append(item * 2)
    
    return result
```

## Best Practices

- Use descriptive function names
- Keep functions focused on one task
- Add comments explaining complex logic
- Use `return` to exit early when needed
