# Числа и строки

Основные типы данных в Nox.

## Числа

### Целые числа

Целые числа без десятичной точки:

```
x = 42
y = -10
z = 0
```

### Числа с плавающей точкой

Числа с десятичной точкой:

```
pi = 3.14159
temperature = -273.15
epsilon = 1e-6
```

### Операции

```
# Арифметика
a = 10 + 5      # 15
b = 10 - 3      # 7
c = 5 * 6       # 30
d = 20 / 4      # 5
e = 17 % 5      # 2
f = 2 ** 10     # 1024

# Сравнения возвращают true или false
display(5 > 3)           # true
display(10 <= 10)        # true
display(3 != 3)          # false

# Многострочная арифметика
result = (
    10 +
    20 +
    30
)
display(result)  # 60
```

## Строки

Текстовые данные в кавычках. Поддерживает одинарные `'` и двойные `"` кавычки.

### Основы строк

```
name = "Alice"
greeting = 'Hello'

# Конкатенация
message = "Hello, " + name

# Длина
text = "Nox"
display(len(text))       # 7

# Повторение
repeated = "ab" * 3      # "ababab"
```

### Многострочные строки

Используйте тройные кавычки для многострочных строк:

```
poem = """
Розы красные,
Фиалки синие,
Код полезный,
Когда работает!
"""

html = """
<html>
    <body>
        <p>Привет</p>
    </body>
</html>
"""
```

### Методы строк

```
text = "Python"

display(text.upper())         # "PYTHON"
display(text.lower())         # "python"

# Проверить наличие подстроки
if "nth" in text:
    display("Найдено!")

# Найти индекс
index = text.find("o")        # 4

# Заменить
new_text = text.replace("Python", "Nox")
```

### Операции со строками

```
# Срез
word = "Nox"
display(word[0:3])           # "Nox"
display(word[-4:])           # "Lang"
display(word[::-1])          # "gnaLxoN"

# Преобразование типа
num = 42
text = str(num)              # "42"

text = "123"
num = int(text)              # 123
```
