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
match x:
    case 1, 2:
        display("one or two")
    case 3:
        display("three")
    else:
        display("other")
```