# Control Flow

## If / Else

```
if a < b:
    display("smaller")
else if a == b:
    display("equal")
else:
    display("bigger")
```

## Pass Statement

The `pass` statement does nothing. It's useful as a placeholder when a statement is required but you don't want to execute any code.

```
if condition:
    pass
else:
    display("doing something")

if value == none:
    pass
else if value > 0:
    display("positive")
else:
    display("non-positive")
```

## repeat

```
count = 0
repeat count < 3:
    display(count)
    count = count + 1

repeat times 3:
    display("tick")
```

## for

```
for x in items:
    display(x)

for i in range(5):
    display(i)
```

### For with multiline structures

```
for item in [
    1,
    2,
    3,
    4,
    5
]:
    display(item)
```

## match

```
match x:
    case 1, 2:
        display("one or two")
    case 3:
        display("three")
    else:
        display("other")
```

### Match with multiline values

```
match status:
    case 200, 201, 204:
        display("success")
    case 400, 401, 403, 404:
        display("client error")
    case 500, 502, 503:
        display("server error")
    else:
        pass
```

## Nested Conditions with Multiline Data

```
if user == none:
    pass
else if user["age"] >= 18:
    display("Adult")
else:
    display("Child")

# Complex multiline condition
if check_permissions(
    user,
    [
        "read",
        "write",
        "delete"
    ]
):
    display("Access granted")
else:
    pass
```