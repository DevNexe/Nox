# Standard Library

- `math`: abs, min, max, floor, ceil, sqrt, pow
- `string`: str, split, join, lower, upper, replace, startswith
- `time`: now, sleep
- `json`: encode, decode
- `fs`: read, write, exists
- `os`: cwd, listdir
- `http`: serve
- `asyncio`: create_task, gather, run, sleep
- `clib`: load, call

## HTTP helpers

`http` also provides:
- `request(method, url, headers=none, data=none, json_data=none, timeout=30)`
- `get(url, headers=none, timeout=30)`
- `post(url, headers=none, data=none, json_data=none, timeout=30)`

```
connect json
text = json.encode({"a": 1})
obj = json.decode(text)
```
