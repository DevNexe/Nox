# Numbers and Strings

Core types for data in Nox.

## Numbers

### Integers

Whole numbers without decimal points:

```
x = 42
y = -10
z = 0
```

### Floats

Numbers with decimal points:

```
pi = 3.14159
temperature = -273.15
epsilon = 1e-6
```

### Operations

```
# Arithmetic
a = 10 + 5      # 15
b = 10 - 3      # 7
c = 5 * 6       # 30
d = 20 / 4      # 5
e = 17 % 5      # 2
f = 2 ** 10     # 1024

# Comparisons return true or false
display(5 > 3)           # true
display(10 <= 10)        # true
display(3 != 3)          # false

# Multiline arithmetic
result = (
    10 +
    20 +
    30
)
display(result)  # 60
```

## Strings

Text data enclosed in quotes. Supports single `'` or double `"` quotes.

### String Basics

```
name = "Alice"
greeting = 'Hello'

# Concatenation
message = "Hello, " + name

# Length
text = "Nox"
display(len(text))       # 7

# Repetition
repeated = "ab" * 3      # "ababab"
```

### Multiline Strings

Use triple quotes for multiline strings:

```
poem = """
Roses are red,
Violets are blue,
Code is quite fun,
When it works through!
"""

html = """
<html>
    <body>
        <p>Hello</p>
    </body>
</html>
"""
```

### String Methods

```
text = "Python"

display(text.upper())         # "PYTHON"
display(text.lower())         # "python"

# Check if substring exists
if "nth" in text:
    display("Found!")

# Find index
index = text.find("o")        # 4

# Replace
new_text = text.replace("Python", "Nox")
```

### String Operations

```
# Slicing
word = "Nox"
display(word[0:3])           # "Nox"
display(word[-4:])           # "Lang"
display(word[::-1])          # "gnaLxoN"

# Type conversion
num = 42
text = str(num)              # "42"

text = "123"
num = int(text)              # 123
```
