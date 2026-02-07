# Errors

Nox shows a styled traceback with line numbers. Common error types include:

- SyntaxError
- NameError
- TypeError
- IndexError

```
try:
    display(items[10])
except:
    display("index error")
finally:
    display("done")
```