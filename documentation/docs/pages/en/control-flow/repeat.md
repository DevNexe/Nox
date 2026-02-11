# Repeat Loops

The `repeat` statement executes a block of code a specified number of times.

## Basic Repeat

```
repeat 5:
    display("Hello")
```

## Repeat with Variable

```
times = 3
repeat times:
    display("Loop iteration")
```

## Nested Repeat

```
repeat 3:
    repeat 2:
        display("*")
```

## Using Repeat with Conditions

```
count = 0
repeat 10:
    if count > 5:
        pass
    else:
        display(count)
    count = count + 1
```

## Repeat with None

```
iterations = none
if iterations == none:
    iterations = 5

repeat iterations:
    display("Repeating")
```
