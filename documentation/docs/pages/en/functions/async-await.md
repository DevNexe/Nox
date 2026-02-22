# Async / Await

Nox supports asynchronous functions with `async define` and `await`.

```
async define work(ms):
    await sleep(ms)
    result "done"
```

Task helpers:
- `create_task(fn, *args)` creates background task
- `gather([task1, task2])` waits for tasks and returns values
- `run_async(value)` unwraps async result

```
async define ping():
    await sleep(50)
    result 1

t = create_task(ping)
values = run_async(gather([t]))
display(values)
```
