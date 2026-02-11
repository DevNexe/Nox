# Цикл Repeat

Оператор `repeat` выполняет блок кода указанное количество раз.

## Базовый repeat

```
repeat 5:
    display("Привет")
```

## Repeat с переменной

```
times = 3
repeat times:
    display("Итерация цикла")
```

## Вложенные repeat

```
repeat 3:
    repeat 2:
        display("*")
```

## Используя repeat с условиями

```
count = 0
repeat 10:
    if count > 5:
        pass
    else:
        display(count)
    count = count + 1
```

## Repeat с None

```
iterations = none
if iterations == none:
    iterations = 5

repeat iterations:
    display("Повторение")
```
