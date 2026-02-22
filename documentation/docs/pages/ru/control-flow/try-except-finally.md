# Try / Except / Finally

Используйте `try` для кода, который может завершиться ошибкой, `except` для обработки, и `finally` для финализации.

```
try:
    value = items[10]
except:
    display("fallback")
finally:
    display("done")
```

Замечания:
- после `try` обязателен `except` и/или `finally`
- `finally` выполняется всегда
