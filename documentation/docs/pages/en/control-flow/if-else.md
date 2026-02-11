# If-Else Statements

Conditional execution: execute different code based on conditions.

## Basic If Statement

```
if condition:
    display("condition is true")
```

## If-Else

```
age = 18

if age >= 18:
    display("Adult")
else:
    display("Minor")
```

## If-Else If-Else

Multiple conditions:

```
score = 85

if score >= 90:
    display("Grade: A")
else if score >= 80:
    display("Grade: B")
else if score >= 70:
    display("Grade: C")
else:
    display("Grade: F")
```

## Nested If Statements

```
user_logged_in = true
is_admin = false

if user_logged_in:
    if is_admin:
        display("Welcome, Admin!")
    else:
        display("Welcome, User!")
else:
    display("Please log in")
```

## Multiline Conditions

Use brackets for complex conditions:

```
if (
    age >= 18 and
    has_license and
    not is_suspended
):
    display("Can drive")
else:
    display("Cannot drive")
```

## Logical Operators

- `and` - both conditions must be true
- `or` - at least one condition must be true
- `not` - negates a condition

```
if a > 0 and b > 0:
    display("Both positive")

if x == 0 or y == 0:
    display("At least one is zero")

if not error:
    display("No errors")
```

## Comparison Operators

- `==` equal
- `!=` not equal
- `<` less than
- `>` greater than
- `<=` less or equal
- `>=` greater or equal

```
if x == 5:
    display("x is 5")

if name != "admin":
    display("Not admin")
```

## With None

```
if value == none:
    display("No value set")

if result != none:
    process(result)
```

## With Collections

```
items = [1, 2, 3]

if len(items) > 0:
    display(items[0])

if "key" in dictionary:
    display(dictionary["key"])

if value in items:
    display("Found")
```
