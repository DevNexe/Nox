# Первая программа

Напишите и запустите вашу первую программу на Nox.

## Минимальная программа

```
display("Привет, Мир!")
```

## Работа с переменными

```
x = 5
y = 3
sum_result = x + y

display("Сумма: " + sum_result)
```

## Простая арифметика

```
# Основные операции
a = 10
b = 3

display(a + b)      # 13
display(a - b)      # 7
display(a * b)      # 30
display(a / b)      # 3.33...
display(a % b)      # 1
display(a ** b)     # 1000
```

## Работа со строками

```
greeting = "Привет"
name = "Alice"
message = greeting + ", " + name + "!"

display(message)          # "Привет, Alice!"
display(len(message))     # 13
display(message[0])       # "П"
display(message[7:12])    # "Alice"
```

## Управление потоком

```
age = 25

if age >= 18:
    display("Взрослый")
else:
    display("Несовершеннолетний")

# Цикл
for i in range(5):
    display(i)
```

## Функции

```
define add_numbers(x, y):
    return x + y

result = add_numbers(5, 3)
display(result)  # 8
```

## Коллекции

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

## Полный пример

```
# Вычисление и вывод статистики
numbers = [10, 20, 30, 40, 50]
total = 0

for num in numbers:
    total = total + num

average = total / len(numbers)

display("Числа: " + numbers)
display("Итого: " + total)
display("Среднее: " + average)
```

## Следующие шаги

- Добавьте более сложные функции
- Изучите срезы строк и манипуляции
- Используйте многострочные структуры для читаемого кода
- Посмотрите все [возможности Nox](../overview/)
