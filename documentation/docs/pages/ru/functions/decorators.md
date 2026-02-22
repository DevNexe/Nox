# Декораторы

Декораторы оборачивают или изменяют функции в момент определения.

```
define logger(fn):
    define wrapped(*args):
        display("call", fn)
        result fn(*args)
    result wrapped

@logger
define greet(name):
    result "Привет, " + name

display(greet("Nox"))
```

Декоратором может быть:
- функция Nox
- bound-метод
- класс (вызывается с декорируемой целью)
- встроенный callable
