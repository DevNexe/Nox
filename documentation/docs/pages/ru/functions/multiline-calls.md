# многострочные вызовы функций

Вызовы функций могут занимать несколько строк с помощью скобок. Это улучшает удобочитаемость при передаче нескольких аргументов.

## Базовый многострочный вызов

```
result = process(
    arg1,
    arg2,
    arg3
)
```

## С аргументами в стиле ключевых слов

```
user = create_user(
    name="Alice",
    email="alice@example.com",
    age=30
)
```

## Вложенные многострочные вызовы

```
response = send_request(
    method="POST",
    url="http://api.example.com",
    headers={
        "Content-Type": "application/json",
        "Authorization": "Bearer token"
    },
    body={
        "user_id": 123,
        "action": "update"
    }
)
```

## многострочные вызовы с условиями

```
result = calculate(
    x if condition1 else 0,
    y if condition2 else default_y,
    z
)
```

## Вызов функции внутри многострочной структуры

```
data = {
    "users": get_users(
        limit=100,
        sort="name"
    ),
    "posts": fetch_posts(
        user_id=user_id,
        status="published"
    ),
    "comments": query(
        collection="comments",
        filter={
            "approved": true
        }
    )
}
```

## Цепочка многострочных вызовов

```
processed = transform(
    filter_data(
        load_data("file.txt"),
        field="active"
    ),
    format="json"
)
```

## С lambda функциями

```
items = process_with_callback(
    data,
    callback=lambda x: (
        transform(x)
    ),
    options={
        "timeout": 30,
        "retry": 3
    }
)
```

## Лучшие практики

- Используйте многострочность для удобочитаемости
- Выровняйте связанные аргументы
- Один аргумент на строку для ясности
- Используйте финальные запятые
