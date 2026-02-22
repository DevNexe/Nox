# Getting Started

1. Create a `.nox` file.
2. Run it: `py -m nox yourfile.nox`.
3. You can run a folder too: `py -m nox path/to/folder`. Nox looks for `__main__.nox`, `main.nox`, or `app.nox`.

## Project Layout

```
project/
  main.nox
```

## First Program

Create `hello.nox`:

```
display("Hello, Nox!")

name = "World"
display("Hello, " + name)

items = [1, 2, 3, 4, 5]
display(items[1:4])

text = "NoxLang"
display(text[0:3])
display(text[3:])
```

## Common Patterns

### Function call with multiline args

```
define greet(first_name, last_name, age):
    result first_name + " " + last_name + " is " + string.str(age)

name = greet(
    "John",
    "Doe",
    30
)

display(name)
```

### Import and HTTP request

```
connect http

resp = http.get("https://httpbin.org/get")
if resp["status"] == 200:
    display("ok")
```

### Async task

```
async define work():
    await sleep(100)
    result 42

task = create_task(work)
result = run_async(gather([task]))
display(result)
```
