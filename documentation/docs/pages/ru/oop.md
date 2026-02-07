# ООП

## Классы

```
class Point:
    define init(self, x, y):
        self.x = x
        self.y = y

    define sum(self):
        result self.x + self.y

p = Point(2, 5)
result p.sum()
```

## Структуры

```
struct User:
    name: str
    age: int

user = User{name: "Ann", age: 20}
user.name = "Bob"
```

## Трейты

```
trait Serializable:
    define to_json(self):
        result ""

class Person:
    implement Serializable
```