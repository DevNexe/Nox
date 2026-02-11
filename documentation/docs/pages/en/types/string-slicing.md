# String Slicing

String slicing extracts a portion of a string using the syntax `string[start:stop:step]`.

## Basic Slicing

Extract a substring from `start` to `stop`:

```
text = "Hello, World!"

display(text[0:5])    # "Hello"
display(text[7:12])   # "World"
display(text[0:1])    # "H"
```

## Slicing Without Start or Stop

Omit `start` to start from the beginning, or omit `stop` to go to the end:

```
word = "Python"

display(word[:4])     # "Pyth"
display(word[2:])     # "thon"
display(word[:])      # "Python" (entire string)
```

## Negative Indices

Negative indices count from the end:

```
text = "Nox"

display(text[-4:])    # "Lang"
display(text[:-2])    # "NoxLa"
display(text[-5:-2])  # "Lan"
```

## Step Parameter

The step controls the direction and interval:

```
text = "0123456789"

display(text[0:10:2])   # "02468"
display(text[1:8:2])    # "1357"
display(text[::-1])     # "9876543210" (reverse)
display(text[5:1:-1])   # "5432" (backward, stop before 1)
```

## Examples

```
# Extract every other character
code = "Python"
display(code[::2])      # "Pto"

# Get last 3 characters
url = "example.com"
display(url[-3:])       # "com"

# Reverse a string
word = "level"
reversed_word = word[::-1]
display(reversed_word)  # "level"

# Skip first and last character
name = "Alice"
middle = name[1:-1]
display(middle)         # "lic"
```

## Rules

- `[start:stop]` does not include the character at `stop`
- Indices can be negative (count from end)
- `step` can be negative (traverse backward)
- Out of range indices don't cause errors, they use boundary values
