# Multiline Function Calls

Function calls can span multiple lines by using brackets. This improves readability when passing many arguments.

## Basic Multiline Call

```
result = process(
    arg1,
    arg2,
    arg3
)
```

## With Keyword-style Arguments

```
user = create_user(
    name="Alice",
    email="alice@example.com",
    age=30
)
```

## Nested Multiline Calls

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

## Multiline with Conditionals

```
result = calculate(
    x if condition1 else 0,
    y if condition2 else default_y,
    z
)
```

## Function Call Inside Multiline Structure

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

## Chained Multiline Calls

```
processed = transform(
    filter_data(
        load_data("file.txt"),
        field="active"
    ),
    format="json"
)
```

## With Lambda Functions

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

## Best Practices

- Use multiline for readability
- Align related arguments
- One argument per line for clarity
- Use trailing commas
