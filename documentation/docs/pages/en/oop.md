# OOP

## Classes

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

## Structs

```
struct User:
    name: str
    age: int

user = User{name: "Ann", age: 20}
user.name = "Bob"
```

## Traits

```
trait Serializable:
    define to_json(self):
        result ""

class Person:
    implement Serializable
```