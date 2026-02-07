# Стандартная библиотека

- `math`: abs, min, max, floor, ceil, sqrt, pow
- `string`: split, join, lower, upper, replace, startswith
- `time`: now, sleep
- `json`: encode, decode
- `fs`: read, write, exists
- `os`: cwd, listdir
- `http`: serve

```
connect json
text = json.encode({"a": 1})
obj = json.decode(text)
```