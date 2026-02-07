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