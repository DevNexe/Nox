# Цикл For

Оператор `for` выполняет итерацию над последовательностями: списки, строки, кортежи, словари и диапазоны.

## Итерация над списками

```
fruits = ["apple", "banana", "cherry"]

for fruit in fruits:
    display(fruit)
```

## Итерация над строками

```
word = "hello"

for char in word:
    display(char)
```

## Использование range()

```
for i in range(5):
    display(i)     # 0, 1, 2, 3, 4

for i in range(1, 4):
    display(i)     # 1, 2, 3

for i in range(0, 10, 2):
    display(i)     # 0, 2, 4, 6, 8
```

## Итерация над словарями

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

## Break и Continue

Паттерны для управления циклом:

```
items = [1, 2, 3, 4, 5]

# Пропустить итерацию
for item in items:
    if item == 3:
        pass  # Пропустить 3
    else:
        display(item)

# Ранний выход
for item in items:
    if item > 3:
        pass  # Логика выхода
    else:
        process(item)
```

## Вложенные циклы

```
for i in range(3):
    for j in range(3):
        display(i + "," + j)
```

## многострочные выражения

```
for item in (
    large_list or
    default_list or
    []
):
    process(item)
```

## С паттерн-подобными выборками

```
numbers = [1, 2, 3, 4, 5]

even_numbers = []
for n in numbers:
    if n % 2 == 0:
        even_numbers.append(n)

# Позже вывести все четные числа
for num in even_numbers:
    display(num)
```
