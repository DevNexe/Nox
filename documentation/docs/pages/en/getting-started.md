# Getting Started

1. Create a file with the extension `.nox`.
2. Run it with `py -m nox yourfile.nox`.
3. You can also run a folder: `py -m nox path/to/folder`. Nox looks for `__main__.nox`, `main.nox`, or `app.nox`.

## Project Layout

```
project/
  main.nox
```

## Running

```
py -m nox main.nox
py -m nox examples
```

## First Program

Create `hello.nox`:

```
# Basic output
display("Hello, Nox!")

# Variables
name = "World"
display("Hello, " + name)

# Multiline structures
data = {
    "name": "Alice",
    "age": 30,
    "skills": [
        "Python",
        "Nox",
        "JavaScript"
    ]
}

# Accessing data
display(data["name"])
display(data["skills"][0])

# String slicing
text = "Nox Test"
display(text[0:3])      # Nox
display(text[3:])       # Test
```

## Common Patterns

### Function with multiline arguments

```
define greet(first_name, last_name, age):
    result first_name + " " + last_name + " is " + display(age)

name = greet(
    "John",
    "Doe",
    30
)

display(name)
```

### Conditional with pass

```
define handle_value(x):
    if x == none:
        pass  # Do nothing for none
    else:
        display(x)
```

### Working with slices

```
items = [1, 2, 3, 4, 5]
display(items[1:4])     # [2, 3, 4]
display(items[::2])     # [1, 3, 5]

text = "Nox"
display(text[::-1])     # xoN
```