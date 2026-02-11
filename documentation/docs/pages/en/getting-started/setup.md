# Setup and Installation

Get Nox up and running quickly.

## Prerequisites

- Python 3.8 or higher
- A text editor or IDE
- Command line access

## Installation

1. Clone or download the Nox repository
2. Navigate to the project directory
3. No external dependencies required

## Running Nox Programs

### From Command Line

```bash
python -m nox your_program.nox
```

### Example File: hello.nox

```
display("Hello, Nox!")
```

Run it:

```bash
python -m nox hello.nox
```

## Your First Program

Create `first_program.nox`:

```
# Display messages
display("Welcome to Nox")

# Variables
name = "Alice"
age = 30

# Calculations
total = age * 2

# Display results
display("Name: " + name)
display("Age: " + age)
display("Double age: " + total)
```

Run it:

```bash
python -m nox first_program.nox
```

Output:

```
Welcome to Nox
Name: Alice
Age: 30
Double age: 60
```

## Troubleshooting

- **"command not found"**: Ensure Python is installed and in PATH
- **"No such file"**: Check that the .nox file exists in current directory
- **Syntax error**: Review syntax documentation for correct structure

## Next Steps

- Read the [syntax guide](../syntax/)
- Explore [types and operations](../types/)
- Learn about [control flow](../control-flow/)
