# Types

Core types: numbers, strings, booleans, lists, tuples, dicts, sets, and none.

```
n = 42
pi = 3.14
name = "nox"
flag = true
items = [1, 2, 3]
point = (1, 2)
map = {"a": 1}
setv = {1, 2, 3}
empty = none
```

## None Type

The `none` type represents the absence of a value. It is similar to `null` in other languages.

```
x = none

if x == none:
    display("x is none")

if x != none:
    display("x has a value")

define get_optional():
    result none
```

## Indexing

Access individual elements using square brackets:

```
items[0]          # Get element at index 0
items[1] = 42     # Set element at index 1
```

## String Slicing

Extract substrings using Python-style slice notation `[start:stop:step]`.

```
text = "Nox Test"

# Basic slicing
text[0:3]         # "Nox" - from index 0 to 3
text[3:]          # "Test" - from index 3 to end
text[:3]          # "Nox" - from start to index 3
text[:]           # "Nox Test" - entire string (copy)

# Negative indices
text[-1]          # "t" - last character
text[-4:]         # "Test" - last 4 characters
text[:-1]         # "Nox Te" - all but last

# Step/stride
text[::2]         # "NxTs" - every 2nd character
text[::-1]        # "tseTxoN" - reversed

# Complex slices
text[1:6:2]       # "oT" - from index 1 to 6, every 2nd
```

String slicing works on any sequence type: strings, lists, tuples.

```
items = [1, 2, 3, 4, 5]
items[1:4]        # [2, 3, 4]
items[::2]        # [1, 3, 5]
items[::-1]       # [5, 4, 3, 2, 1]

tuple_data = (10, 20, 30, 40)
tuple_data[1:3]   # (20, 30)
```