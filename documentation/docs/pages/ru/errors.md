# Ошибки

Nox показывает стилизованный traceback с номерами строк. Частые типы ошибок:

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