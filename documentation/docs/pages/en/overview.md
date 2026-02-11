# Nox Language

Nox is a python-like scripting language with explicit blocks, a compact standard library, and a simple runtime model. This wiki documents the current syntax and runtime.

## Quick Example

```
define add(a, b):
    result a + b

x = add(2, 3)
display("sum", x)
```

Key ideas: indentation for blocks, `define` for functions, `result` for return, and `display` for output.

## Key Features

### Core Language Constructs
- **Indentation-based blocks** - Python-like syntax using spaces
- **Variables and types** - Dynamic typing with numbers, strings, lists, dicts, tuples, sets
- **Functions** - Defined with `define`, return values with `result`
- **Control flow** - `if/else`, `for`, `while`, `match/case`
- **pass statement** - Placeholder no-op for empty blocks
- **none value** - Represents absence of value

### Data Structure Features
- **Multiline structures** - Lists, dicts, tuples, and function calls can span multiple lines
- **String slicing** - Python-style slice notation `[start:stop:step]`
- **Indexing and access** - Access elements with `[index]` or `.attribute`
- **Collections** - Lists, dictionaries, tuples, sets, and strings

### Advanced Features
- **Lambda expressions** - In-line anonymous functions
- **Decorators** - Function decoration with `@`
- **Classes and OOP** - Object-oriented programming with inheritance
- **Traits** - Interface-like contracts for classes
- **Exception handling** - try/except/finally blocks
- **Async/await** - Asynchronous function support
- **Pattern matching** - `match` statement for complex conditionals

## Example with New Features

```
# Multiline dictionary
config = {
    "database": "localhost",
    "port": 5432,
    "options": [
        "ssl",
        "compression"
    ]
}

# String slicing
url = "https://example.com"
host = url[8:]          # "example.com"

# Function with multiline arguments
define process(data, options, verbose):
    if verbose == none:
        pass
    else:
        display(verbose)
    result data

result = process(
    config,
    ["prod"],
    none
)
```