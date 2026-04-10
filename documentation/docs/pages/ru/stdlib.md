# Стандартная библиотека

Все модули стандартной библиотеки требуют `connect` для импорта, за исключением `http`, `string` и `fs`, которые доступны глобально.

- `math`: abs, min, max, floor, ceil, sqrt, pow (требует `connect math`)
- `string`: str, split, join, lower, upper, replace, startswith (доступен глобально)
- `time`: now, sleep (требует `connect time`)
- `json`: encode, decode (требует `connect json`)
- `fs`: read, write, exists (доступен глобально)
- `os`: cwd, listdir (требует `connect os`)
- `http`: serve, request, get, post (доступен глобально)
- `asyncio`: create_task, gather, run, sleep (требует `connect asyncio`)
- `clib`: load, call (требует `connect clib`)

## HTTP helpers

`http` также поддерживает:
- `request(method, url, headers=none, data=none, json_data=none, timeout=30)`
- `get(url, headers=none, timeout=30)`
- `post(url, headers=none, data=none, json_data=none, timeout=30)`

```
connect json
text = json.encode({"a": 1})
obj = json.decode(text)
```
