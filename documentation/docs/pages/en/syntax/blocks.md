# Blocks

Blocks are defined by indentation (spaces only). Tabs are not allowed.

Code blocks are used in control structures, function definitions, and class definitions.

## Basic Block Structure

```
if x > 0:
    display("positive")
else:
    display("non-positive")
```

## Nested Blocks

Blocks can be nested at any depth:

```
if condition1:
    if condition2:
        display("both true")
    else:
        display("condition2 false")
else:
    display("condition1 false")
```

## Indentation Rules

- Use spaces only (4 spaces recommended)
- Tabs are **not allowed** and will cause an error
- All lines at the same indentation level belong to the same block
- Indentation must be consistent throughout the file
