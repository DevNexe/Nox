# Try / Except / Finally

Use `try` to protect code that may fail, `except` to recover, and `finally` for cleanup.

```
try:
    value = items[10]
except:
    display("fallback")
finally:
    display("done")
```

Notes:
- `except` and/or `finally` must be present
- `finally` always runs
