# With Statement

`with expr as name:` binds value to `name` inside a block.

If value has `close()`, Nox calls it automatically when block ends.

```
with open("log.txt", "r") as f:
    text = f.read()
    display(text)
```

This is useful for files and other closable resources.
