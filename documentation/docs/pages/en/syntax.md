# Syntax

## Blocks

Blocks are defined by indentation (spaces only). Tabs are not allowed.

```
if x > 0:
    display("positive")
else:
    display("non-positive")
```

## Multiline Structures

Code inside brackets `()`, `[]`, `{}` can span multiple lines. Indentation is ignored inside brackets.

```
# Multiline list
items = [
    1,
    2,
    3,
    4,
    5
]

# Multiline dictionary
config = {
    "host": "localhost",
    "port": 8080,
    "features": ["api", "web"]
}

# Multiline function call
result = process(
    arg1,
    arg2,
    arg3
)

# Multiline tuple
coordinates = (
    x,
    y,
    z
)
```

## Comments

```
# This is a comment
```

## Pass Statement

The `pass` statement is a null operation — when executed, nothing happens. It is useful as a placeholder when a statement is required syntactically, but no code needs to be executed.

```
if condition:
    pass
else:
    display("condition is false")

define placeholder_function():
    pass
```