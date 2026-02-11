# Условные операторы If-Else

Условное выполнение: выполнять разный код на основе условий.

## Базовый оператор If

```
if условие:
    display("условие верно")
```

## If-Else

```
age = 18

if age >= 18:
    display("Взрослый")
else:
    display("Несовершеннолетний")
```

## If-Else If-Else

Несколько условий:

```
score = 85

if score >= 90:
    display("Оценка: A")
else if score >= 80:
    display("Оценка: B")
else if score >= 70:
    display("Оценка: C")
else:
    display("Оценка: F")
```

## Вложенные условные операторы

```
user_logged_in = true
is_admin = false

if user_logged_in:
    if is_admin:
        display("Добро пожаловать, Админ!")
    else:
        display("Добро пожаловать, Пользователь!")
else:
    display("Пожалуйста, войдите")
```

## многострочные условия

Используйте скобки для сложных условий:

```
if (
    age >= 18 and
    has_license and
    not is_suspended
):
    display("Можно ездить")
else:
    display("Нельзя ездить")
```

## Логические операторы

- `and` - оба условия должны быть верны
- `or` - хотя бы одно условие должно быть верно
- `not` - отрицает условие

```
if a > 0 and b > 0:
    display("Оба положительные")

if x == 0 or y == 0:
    display("Хотя бы одно равно нулю")

if not error:
    display("Ошибок нет")
```

## Операторы сравнения

- `==` равно
- `!=` не равно
- `<` меньше
- `>` больше
- `<=` меньше или равно
- `>=` больше или равно

```
if x == 5:
    display("x равно 5")

if name != "admin":
    display("Не админ")
```

## С None

```
if value == none:
    display("Нет значения")

if result != none:
    process(result)
```

## С коллекциями

```
items = [1, 2, 3]

if len(items) > 0:
    display(items[0])

if "key" in dictionary:
    display(dictionary["key"])

if value in items:
    display("Найдено")
```
