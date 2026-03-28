<div align="center">

<img src="documentation/docs/static/icon.png" alt="Nox Logo" width="120" />

# Nox

**A clean, expressive scripting language — built from scratch.**

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.12%2B-blue)](https://python.org)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)](#)

</div>

---

## What is Nox?

Nox is a **tree-walking interpreted language** with its own lexer, parser, AST, and interpreter — written entirely in pure Python, with zero use of `eval` or `exec`. It's fast to hack on, easy to read, and designed to grow.

It has classes, traits, structs, async/await, decorators, pattern matching, C/C++ FFI, a built-in HTTP server, and a GitHub-powered package manager. The docs site runs as a Nox web app.

---

## Getting Started

**Requires Python 3.8+**

```bash
git clone https://github.com/devnexe/nox
cd nox
python setup.py
```

The setup manager will guide you through everything:

```
  ███╗   ██╗ ██████╗ ██╗  ██╗
  ████╗  ██║██╔═══██╗╚██╗██╔╝
  ██╔██╗ ██║██║   ██║ ╚███╔╝
  ██║╚██╗██║██║   ██║ ██╔██╗
  ██║ ╚████║╚██████╔╝██╔╝ ██╗
  ╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝

  The Nox Programming Language — Toolchain Manager

  1) Install / setup environment
  2) Show activate instructions
  3) Build executable
  4) Update dependencies
  5) Exit
```

---

## The Language

### Variables & Types

```nox
x       = 42
pi      = 3.14
name    = "nox"
flag    = true
items   = [1, 2, 3]
point   = (10, 20)
mapping = {"key": "value"}
nothing = none
```

### Functions

```nox
define add(a, b=0):
    result a + b

define sum_all(*numbers):
    total = 0
    for n in numbers:
        total = total + n
    result total

square = lambda x: x * x

display add(3, 4)       # 7
display sum_all(1,2,3)  # 6
display square(9)       # 81
```

### Control Flow

```nox
if score >= 90:
    display("A")
else if score >= 70:
    display("B")
else:
    display("F")

for item in ["apple", "banana", "cherry"]:
    display(item)

repeat 5:
    display("tick")

repeat count < 10:
    count = count + 1

match status:
    case 200, 201:
        display("ok")
    case 404:
        display("not found")
    else:
        display("unknown")
```

### Classes, Structs & Traits

```nox
class Animal:
    define init(self, name):
        self.name = name

    define speak(self):
        result "..."

class Dog(Animal):
    define speak(self):
        result self.name + " says: Woof!"

dog = Dog("Rex")
display dog.speak()   # Rex says: Woof!
```

```nox
struct Point:
    x: float
    y: float

p = Point{x: 3.0, y: 4.0}
display p.x   # 3.0
```

```nox
trait Serializable:
    define to_json(self):
        result ""

class Config:
    implement Serializable

    define to_json(self):
        result json.encode({"version": "1.0"})
```

### Error Handling

```nox
try:
    data = fs.read("config.json")
except:
    display("Config not found, using defaults")
finally:
    display("Done")
```

### Async / Await

```nox
async define fetch(url):
    response = await http.get(url)
    result response["json"]

task = create_task(fetch, "https://api.example.com/data")
data = await task
display data
```

### Multiline Expressions

No backslash continuation — anything inside `()`, `[]`, `{}` spans lines freely:

```nox
config = {
    "host": "localhost",
    "port": 8080,
    "features": ["api", "web", "auth"]
}
```

### Slicing

```nox
text = "Hello, World!"
display text[0:5]    # Hello
display text[::-1]   # !dlroW ,olleH
display text[-6:]    # World!
```

---

## Standard Library

| Module     | What it does |
|------------|-------------|
| `math`     | `abs` `min` `max` `floor` `ceil` `sqrt` `pow` |
| `string`   | `split` `join` `lower` `upper` `replace` `startswith` |
| `time`     | `now` `sleep` |
| `json`     | `encode` `decode` |
| `fs`       | `read` `write` `exists` |
| `os`       | `cwd` `listdir` |
| `http`     | `serve` `get` `post` `request` |
| `clib`     | `load` `call` — C/C++ FFI via ctypes |
| `compiler` | `compile` — compile C/C++ source to native library |
| `process`  | `run` `shell` — spawn and control subprocesses |
| `asyncio`  | `create_task` `gather` `run` `sleep` |

---

## Package Manager

```bash
# Install from GitHub
python -m nox package install devnexe-alt/NoxWeb

# Short form (defaults to devnexe-alt org)
python -m nox package install NoxGram

# Full URL
python -m nox package install https://github.com/user/repo

# Manage
python -m nox package list
python -m nox package remove NoxWeb
```

Libraries live in `Libraries/` next to your script or binary.

---

## NoxWeb

A full web framework in Nox:

```nox
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

---

## NoxGram

Telegram bots in Nox:

```nox
connect NoxGram

b = NoxGram.bot("YOUR_TOKEN")

b.command("start", define handler(ctx):
    ctx["bot"].send_message(ctx["chat_id"], "Hello from Nox!")
)

b.poll()
```

---

## C / C++ Integration

```nox
connect compiler
connect clib

# Compile C source → native library
compiler.compile("mylib.c")

# Load and call
lib = clib.load("mylib.dll")
value = clib.call(lib, "add", 10, 5)
display value   # 15
```

```nox
# Or load an existing library via header
lib = clib.load("mylib.h")
display lib.get("greet")("Nox")
```

Auto-detects MSVC, GCC, or Clang. Strings auto-convert between Python `str` and C `char*`.

---

## Process Control

```nox
connect process

p = process.run("ffmpeg", "-i", "input.mp4", "output.gif")

repeat p.alive():
    for line in p.output():
        display line

display "Exit: " + string.str(p.wait())

# or kill it
p.kill()
```

---

## Folder Execution

```bash
python -m nox .
python -m nox my_project/
python -m nox examples/weather_app
```

Looks for `__main__.nox` → `main.nox` → `app.nox` automatically.

---

## Error Messages

```
Traceback:
  Error in main.nox at line 7 in process_data:
    5   items = [1, 2, 3]
    6
  >  7   display items[10]
    8

IndexError: list index out of range
```

---

## Compile to Binary

```bash
python setup.py build
```

Produces a standalone `nox.exe` / `nox` — no Python needed on target. Place `Libraries/` next to it.

---

## Documentation

```bash
python -m nox documentation
```

Opens at [http://localhost:8080](http://localhost:8080). Available in English and Russian.

---

## Architecture

| Component   | File                 | Role |
|-------------|----------------------|------|
| Lexer        | `nox/lexer.py`       | Tokenizes source with indent/dedent tracking |
| Parser       | `nox/parser.py`      | Recursive descent → AST |
| AST          | `nox/ast_nodes.py`   | Dataclass-based node definitions |
| Interpreter  | `nox/interpreter.py` | Tree-walking evaluator with closures |
| CLI          | `nox/cli.py`         | Entry point, error rendering, package manager |
| JIT          | `nox/jit.py`         | Optional Numba acceleration for numeric ops |
| clib         | `nox/clib.py`        | C FFI via ctypes |
| compiler     | `nox/compiler.py`    | C/C++ compilation via system compiler |
| process      | `nox/process.py`     | Subprocess control |

---

## Project Layout

```
nox/
├── nox/                 # interpreter source
│   ├── lexer.py
│   ├── parser.py
│   ├── ast_nodes.py
│   ├── interpreter.py
│   ├── cli.py
│   ├── compiler.py
│   ├── process.py
│   ├── clib.py
│   ├── jit.py
│   └── info.cfg
├── documentation/       # docs web app
├── Libraries/           # installed packages
├── requirements.txt
├── setup.py             # toolchain manager
└── LICENSE
```

---

<div align="center">

MIT License — see [LICENSE](LICENSE)

*Built with Python. No magic.*

</div>
