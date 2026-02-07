# Functions

## Define

```
define add(a, b=10):
    result a + b

add(2, 3)
add(2)
```

## Varargs

```
define sum_all(*xs):
    total = 0
    for x in xs:
        total = total + x
    result total
```

## Lambda

```
square = lambda x: x * x
result square(5)
```