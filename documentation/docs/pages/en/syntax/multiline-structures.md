# Multiline Structures

Code inside brackets `()`, `[]`, `{}` can span multiple lines. Indentation is ignored inside brackets.

This feature makes it easy to write readable and well-formatted code for complex data structures and function calls.

## Multiline Lists

```
items = [
    1,
    2,
    3,
    4,
    5
]
```

## Multiline Dictionaries

```
config = {
    "host": "localhost",
    "port": 8080,
    "features": ["api", "web"]
}

# Nested multiline structure
database_config = {
    "primary": {
        "host": "db1.example.com",
        "port": 5432
    },
    "replica": {
        "host": "db2.example.com",
        "port": 5432
    }
}
```

## Multiline Function Calls

```
result = process(
    arg1,
    arg2,
    arg3
)

data = complex_calculation(
    value1,
    value2,
    options={
        "timeout": 30,
        "retry": 3
    }
)
```

## Multiline Tuples

```
coordinates = (
    x,
    y,
    z
)
```

## Mixing Multiline Structures

Structures can be nested and mixed:

```
response = {
    "status": 200,
    "data": [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"}
    ],
    "callback": lambda x: process(
        x,
        verbose=true
    )
}
```

## Rules

- Newlines inside `()`, `[]`, `{}` don't require special syntax
- Indentation is ignored inside brackets
- Trailing commas are allowed
- Comments work inside multiline structures
