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
display(p.sum())
```

## Inheritance

```
class Animal:
    define speak(self):
        result "..."

class Dog(Animal):
    define speak(self):
        result "woof"
```

## Traits

Traits define required method names. `implement` is validated when the class is created.

```
trait Serializable:
    define to_json(self):
        pass

class User:
    implement Serializable

    define to_json(self):
        result "{}"
```

## Structs

Struct fields are fixed by declaration.

```
struct User:
    name: str
    age: int

user = User{name: "Ann", age: 20}
user.name = "Bob"
```
