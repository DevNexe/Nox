# Indexing and Collections

Indexing is used to access individual elements in sequences (strings, lists, tuples) and dictionaries.

## String Indexing

Access individual characters by index:

```
text = "Nox"

display(text[0])      # "N"
display(text[4])      # "L"
display(text[-1])     # "g"
display(text[-2])     # "n"
```

## List Indexing

Access list elements:

```
items = [10, 20, 30, 40]

display(items[0])     # 10
display(items[-1])    # 40
display(items[1:3])   # [20, 30]
```

## Dictionary Indexing

Access dictionary values by key:

```
person = {
    "name": "Alice",
    "age": 30,
    "city": "NYC"
}

display(person["name"])    # "Alice"
display(person["age"])     # 30
```

## Tuple Indexing

Tuples support indexing like lists:

```
point = (10, 20, 30)

display(point[0])     # 10
display(point[1])     # 20
display(point[-1])    # 30
```

## Iteration with Indexing

```
items = ["a", "b", "c"]

for i in range(3):
    display(items[i])

# Using enumerate
for pair in enumerate(items):
    index = pair[0]
    value = pair[1]
    display(index + ": " + value)
```

## Safe Access

```
# Check before accessing
items = [1, 2, 3]

if len(items) > 2:
    display(items[2])  # Safe: 3

# Use none for missing values
data = {
    "required": "value",
    "optional": none
}
```
