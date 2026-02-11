# Индексирование и коллекции

Индексирование используется для доступа к отдельным элементам в последовательностях (строки, списки, кортежи) и словарях.

## Индексирование строк

Доступ к отдельным символам по индексу:

```
text = "Nox"

display(text[0])      # "N"
display(text[4])      # "L"
display(text[-1])     # "g"
display(text[-2])     # "n"
```

## Индексирование списков

Доступ к элементам списка:

```
items = [10, 20, 30, 40]

display(items[0])     # 10
display(items[-1])    # 40
display(items[1:3])   # [20, 30]
```

## Индексирование словарей

Доступ к значениям словаря по ключу:

```
person = {
    "name": "Alice",
    "age": 30,
    "city": "NYC"
}

display(person["name"])    # "Alice"
display(person["age"])     # 30
```

## Индексирование кортежей

Кортежи поддерживают индексирование как списки:

```
point = (10, 20, 30)

display(point[0])     # 10
display(point[1])     # 20
display(point[-1])    # 30
```

## Итерация с индексами

```
items = ["a", "b", "c"]

for i in range(3):
    display(items[i])

# С использованием enumerate
for pair in enumerate(items):
    index = pair[0]
    value = pair[1]
    display(index + ": " + value)
```

## Безопасный доступ

```
# Проверьте перед доступом
items = [1, 2, 3]

if len(items) > 2:
    display(items[2])  # Безопасно: 3

# Используйте none для отсутствующих значений
data = {
    "required": "value",
    "optional": none
}
```
