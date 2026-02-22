# Nox

> A clean, expressive scripting language with Python-like syntax, built from scratch in pure Python.

```
define greet(name):
    result "Hello, " + name + "!"

display greet("World")
```

---

## What is Nox?

Nox is a tree-walking interpreted language with indentation-based blocks, dynamic typing, and a compact standard library. It runs on top of Python but has its own lexer, parser, AST, and interpreter — no Python eval, no exec. It's designed to be readable, hackable, and fun to extend.

The language supports classes, traits, structs, async/await, decorators, pattern matching, C library integration via ctypes, and a built-in HTTP server. A package manager lets you install libraries directly from GitHub. Documentation runs as a Nox web app powered by NoxWeb.

---

## Quick Start

**Requirements:** Python 3.8+

```bash
# Run a script
python -m nox hello.nox

# Run a folder — Nox looks for __main__.nox, main.nox, or app.nox automatically
python -m nox my_project/

# This means you can run the entire project just by pointing at its directory:
python -m nox .
python -m nox examples/

# Install a library from GitHub
python -m nox package install user/repo

# List installed libraries
python -m nox package list

# Remove a library
python -m nox package remove LibraryName
```

**hello.nox:**
```
display("Hello, Nox!")
```

---

## Language Overview

### Variables & Types

```
x = 42
pi = 3.14
name = "nox"
flag = true
items = [1, 2, 3]
point = (1, 2)
mapping = {"key": "value"}
empty = none
```

### Functions

Functions are defined with `define` and return values with `result`:

```
define add(a, b=0):
    result a + b

define sum_all(*numbers):
    total = 0
    for n in numbers:
        total = total + n
    result total

square = lambda x: x * x
```

### Control Flow

```
# if / else if / else
if score >= 90:
    display("A")
else if score >= 80:
    display("B")
else:
    display("F")

# for loop
for item in items:
    display(item)

# repeat loop
repeat 5:
    display("tick")

repeat count < 10:
    count = count + 1

# match statement
match status:
    case 200, 201:
        display("ok")
    case 404:
        display("not found")
    else:
        display("unknown")
```

### Classes, Structs & Traits

```
class Point:
    define init(self, x, y):
        self.x = x
        self.y = y

    define distance(self):
        result (self.x ** 2 + self.y ** 2) ** 0.5

p = Point(3, 4)
display(p.distance())   # 5.0

struct User:
    name: str
    age: int

user = User{name: "Alice", age: 30}

trait Serializable:
    define to_json(self):
        result ""

class Person:
    implement Serializable
```

### Error Handling

```
try:
    result risky_operation()
except:
    display("something went wrong")
finally:
    display("done")
```

### Multiline Structures

Anything inside `()`, `[]`, or `{}` can span multiple lines — no backslash needed:

```
config = {
    "host": "localhost",
    "port": 8080,
    "features": [
        "api",
        "web",
        "auth"
    ]
}

result = process(
    user_data,
    filters=["active", "verified"],
    options={"timeout": 30}
)
```

### String Slicing

Python-style slicing works on strings, lists, and tuples:

```
text = "Hello, World!"
display(text[0:5])    # Hello
display(text[::-1])   # !dlroW ,olleH
display(text[-6:])    # World!
```

---

## Standard Library

| Module   | Functions |
|----------|-----------|
| `math`   | `abs`, `min`, `max`, `floor`, `ceil`, `sqrt`, `pow` |
| `string` | `split`, `join`, `lower`, `upper`, `replace`, `startswith` |
| `time`   | `now`, `sleep` |
| `json`   | `encode`, `decode` |
| `fs`     | `read`, `write`, `exists` |
| `os`     | `cwd`, `listdir` |
| `http`   | `serve`, `get`, `post`, `request` |
| `clib`   | `load`, `call` — C library FFI via ctypes |
| `asyncio`| `create_task`, `gather`, `run`, `sleep` |

```
connect json

data = json.encode({"message": "hello"})
obj = json.decode(data)
display(obj["message"])
```

---

## Modules & Packages

```
connect math
connect json as j
from string connect split, join

# Install from GitHub
# python -m nox package install devnexe-alt/NoxWeb
```

Libraries live in the `Libraries/` folder next to your script or binary. Each library has a `.nxinfo` manifest and a `main.nox` entry point.

---

## NoxWeb

Build web apps entirely in Nox:

```
connect NoxWeb

app = NoxWeb.web()
app.static("static")
app.templates("templates")

@app.get("/")
define home(req):
    result NoxWeb.render_template("index.html", {"title": "Nox"})

@app.get("/api/ping")
define ping(req):
    result NoxWeb.json({"status": "ok"})

app.run(8080)
```

Supports GET/POST routes, blueprints, static file serving, and template rendering with `{{ variable }}` substitution.

---

## NoxGram

Build Telegram bots in Nox:

```
connect NoxGram

b = NoxGram.bot("YOUR_TOKEN")

b.command("start", define handler(ctx):
    ctx["bot"].send_message(ctx["chat_id"], "Hello!")
)

b.poll()
```

Includes FSM (finite state machine) for multi-step conversations, middleware support, and filter-based routing.

---

## C Library Integration

Load and call native C libraries without a compiler at runtime:

```
connect clib

# Load via header file (auto-maps types)
lib = clib.load("mylib.h")
result = lib.get("add")(10, 5)
display(result)   # 15

# Or load binary directly
lib = clib.load("mylib.dll")
greet = lib.get("greet")
display(greet("Nox"))
```

Uses `pcpp` + `pycparser` for header preprocessing and `ctypes` for the actual FFI. Strings are automatically converted between Python `str` and C `char*`.

---

## Async Support

```
async define fetch_data(url):
    response = await http.get(url)
    result response["json"]

task = create_task(fetch_data, "https://api.example.com/data")
data = await task
```

---

## Project Structure

```
project/
├── main.nox           # entry point
├── Libraries/         # installed packages
│   ├── NoxWeb/
│   └── TGBot4Nox/
├── templates/
└── static/
```

---

## Compiling to Binary

Nox supports compilation via [Nuitka](https://nuitka.net/):

```bash
python -m nuitka --onefile \
  --include-package=nox \
  --include-package=rich \
  --output-filename=nox \
  --python-flag=-m nox
```

The resulting binary works standalone — no Python installation required on the target machine. The `Libraries/` folder should sit next to the binary.

---

## Error Messages

Nox shows styled tracebacks with line numbers and code context:

```
Traceback:
  Error in main.nox at line 7:
    5  items = [1, 2, 3]
    6
  ❱  7  display(items[10])
    8

IndexError: list index out of range
```

---

## Interpreter Architecture

| Component | File | Role |
|-----------|------|------|
| Lexer | `nox/lexer.py` | Tokenizes source with indent/dedent tracking |
| Parser | `nox/parser.py` | Recursive descent, produces AST |
| AST | `nox/ast_nodes.py` | Dataclass-based node definitions |
| Interpreter | `nox/interpreter.py` | Tree-walking evaluator with closures |
| CLI | `nox/cli.py` | Entry point, error rendering, package manager |
| JIT | `nox/jit.py` | Optional Numba acceleration for numeric ops |
| clib | `nox/clib.py` | C FFI via ctypes |

---

## Documentation

The documentation site is itself a Nox app. Run it with:

```bash
python -m nox documentation
```

Then open [http://localhost:8080](http://localhost:8080). Includes English and Russian docs.

---

## License

MIT — see [LICENSE](LICENSE)
