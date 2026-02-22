# Decorators

Decorators wrap or transform functions at definition time.

```
define logger(fn):
    define wrapped(*args):
        display("call", fn)
        result fn(*args)
    result wrapped

@logger
define greet(name):
    result "Hello, " + name

display(greet("Nox"))
```

Decorator can be:
- a Nox function
- a bound method
- a class (called with the decorated target)
- a builtin callable
