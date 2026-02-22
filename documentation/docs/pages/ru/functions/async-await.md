# Async / Await

Nox поддерживает асинхронные функции через `async define` и `await`.

```
async define work(ms):
    await sleep(ms)
    result "done"
```

Хелперы для задач:
- `create_task(fn, *args)` создаёт фоновую задачу
- `gather([task1, task2])` ждёт задачи и возвращает значения
- `run_async(value)` разворачивает async-результат

```
async define ping():
    await sleep(50)
    result 1

t = create_task(ping)
values = run_async(gather([t]))
display(values)
```
