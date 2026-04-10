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

## Command Line Interface

Nox provides several CLI commands for development:

- `nox fmt [files]`: Formats Nox source code files
- `nox lint [files]`: Lints Nox source code for errors and style issues
- `nox test [files]`: Runs tests for Nox projects

If no files are specified, `lint` and `test` scan the current directory recursively.

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