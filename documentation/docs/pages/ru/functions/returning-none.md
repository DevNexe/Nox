# Возврат None

Функции возвращают `none` по умолчанию, когда нет явного оператора return.

## Неявный возврат None

```
define greet(name):
    display("Привет, " + name)

result = greet("Alice")
display(result == none)  # true
```

## Явный возврат None

Явно вернуть `none`:

```
define validate(value):
    if value == none:
        return none
    
    if value < 0:
        return none
    
    return value * 2
```

## None в управлении потоком

```
define find_item(items, target):
    for item in items:
        if item == target:
            return item
    
    return none  # Не найдено

result = find_item([1, 2, 3], 5)
if result == none:
    display("Не найдено")
```

## Безопасные операции с None

```
define safe_operation(data):
    if data == none:
        return none
    
    transformed = transform_data(data)
    
    if transformed == none:
        return none
    
    return process(transformed)
```

## Значения None по умолчанию

```
define configure(name, value):
    result = none
    
    if value != none:
        result = save_config(name, value)
    
    return result
```

## Несколько путей возврата

```
define check_and_process(items):
    if items == none:
        display("Null items")
        return none
    
    if len(items) == 0:
        display("Empty items")
        return none
    
    return transform(items)
```

## Цепочка операций с проверкой None

```
define chain_operations(input):
    step1 = process1(input)
    if step1 == none:
        return none
    
    step2 = process2(step1)
    if step2 == none:
        return none
    
    return process3(step2)
```

## Лучшие практики

- Используйте осмысленные возвращаемые значения, если возможно
- Возвращайте `none` для случаев "нет результата"
- Проверяйте `none` перед использованием возвращаемых значений
- Документируйте, когда функции возвращают `none`
