# For Loops

The `for` statement iterates over sequences: lists, strings, tuples, dictionaries, and ranges.

## Iterating Over Lists

```
fruits = ["apple", "banana", "cherry"]

for fruit in fruits:
    display(fruit)
```

## Iterating Over Strings

```
word = "hello"

for char in word:
    display(char)
```

## Using range()

```
for i in range(5):
    display(i)     # 0, 1, 2, 3, 4

for i in range(1, 4):
    display(i)     # 1, 2, 3

for i in range(0, 10, 2):
    display(i)     # 0, 2, 4, 6, 8
```

## Iterating Over Dictionaries

```
person = {
    "name": "Alice",
    "age": 30,
    "city": "NYC"
}

for key in person:
    display(key)           # "name", "age", "city"

for pair in person.items():
    name = pair[0]
    value = pair[1]
    display(name + ": " + value)
```

## Break and Continue

Patterns for loop control:

```
items = [1, 2, 3, 4, 5]

# Skip iteration
for item in items:
    if item == 3:
        pass  # Skip 3
    else:
        display(item)

# Early exit pattern
for item in items:
    if item > 3:
        pass  # Exit logic
    else:
        process(item)
```

## Nested Loops

```
for i in range(3):
    for j in range(3):
        display(i + "," + j)
```

## Multiline Expressions

```
for item in (
    large_list or
    default_list or
    []
):
    process(item)
```

## With List Comprehension-like Patterns

```
numbers = [1, 2, 3, 4, 5]

even_numbers = []
for n in numbers:
    if n % 2 == 0:
        even_numbers.append(n)

# Later display all even numbers
for num in even_numbers:
    display(num)
```
