# Управление потоком

## If / Else

```
if a < b:
    display("smaller")
else if a == b:
    display("equal")
else:
    display("bigger")
```

## Оператор Pass

Оператор `pass` ничего не делает. Полезен как заполнитель, когда оператор требуется синтаксически, но вы не хотите выполнять никакой код.

```
if condition:
    pass
else:
    display("делаю что-то")

if value == none:
    pass
else if value > 0:
    display("положительное")
else:
    display("не положительное")
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

### For с многострочными структурами

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

### Match с многострочными значениями

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

## Вложенные условия с многострочными данными

```
if user == none:
    pass
else if user["age"] >= 18:
    display("Adult")
else:
    display("Child")

# Сложное многострочное условие
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