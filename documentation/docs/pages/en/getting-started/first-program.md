# First Program

Write and run your first Nox program.

## Minimal Program

```
display("Hello, World!")
```

## Working with Variables

```
x = 5
y = 3
sum_result = x + y

display("Sum: " + sum_result)
```

## Simple Arithmetic

```
# Basic operations
a = 10
b = 3

display(a + b)      # 13
display(a - b)      # 7
display(a * b)      # 30
display(a / b)      # 3.33...
display(a % b)      # 1
display(a ** b)     # 1000
```

## Working with Strings

```
greeting = "Hello"
name = "Alice"
message = greeting + ", " + name + "!"

display(message)          # "Hello, Alice!"
display(len(message))     # 13
display(message[0])       # "H"
display(message[7:12])    # "Alice"
```

## Control Flow

```
age = 25

if age >= 18:
    display("Adult")
else:
    display("Minor")

# Loop
for i in range(5):
    display(i)
```

## Functions

```
define add_numbers(x, y):
    return x + y

result = add_numbers(5, 3)
display(result)  # 8
```

## Collections

```
fruits = ["apple", "banana", "cherry"]

for fruit in fruits:
    display(fruit)

person = {
    "name": "Bob",
    "age": 30,
    "city": "NYC"
}

display(person["name"])  # "Bob"
```

## Complete Example

```
# Calculate and display statistics
numbers = [10, 20, 30, 40, 50]
total = 0

for num in numbers:
    total = total + num

average = total / len(numbers)

display("Numbers: " + numbers)
display("Total: " + total)
display("Average: " + average)
```

## Next Steps

- Add more complex functions
- Explore string slicing and manipulation
- Use multiline structures for readable code
- Check out all [Nox features](../overview/)
