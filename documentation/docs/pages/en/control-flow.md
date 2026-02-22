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

## match

```
match status:
    case 200, 201, 204:
        display("success")
    case 400, 404:
        display("client error")
    else:
        display("other")
```

## try / except / finally

```
try:
    value = items[10]
except:
    display("fallback")
finally:
    display("done")
```

## with

`with` binds a resource to a name for a block. If the resource has `close()`, Nox calls it automatically.

```
with open("app.log", "r") as f:
    text = f.read()
```

## pass

```
if condition:
    pass
else:
    display("work")
```
