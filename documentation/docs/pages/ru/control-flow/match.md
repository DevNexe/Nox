# Оператор Match

Оператор `match` предоставляет сопоставление с образцом для нескольких случаев. Это оценивает значение против нескольких образцов и выполняет соответствующий блок.

## Базовый match

```
status = "success"

match status:
    case "success":
        display("Операция успешна")
    case "error":
        display("Операция не удалась")
    case "pending":
        display("Ожидание...")
    default:
        display("Неизвестный статус")
```

## Match с числами

```
error_code = 404

match error_code:
    case 404:
        display("Не найдено")
    case 500:
        display("Ошибка сервера")
    case 403:
        display("Доступ запрещен")
    default:
        display("Неизвестная ошибка: " + error_code)
```

## Match с условиями

```
score = 85

match true:
    case score >= 90:
        display("Оценка A")
    case score >= 80:
        display("Оценка B")
    case score >= 70:
        display("Оценка C")
    default:
        display("Оценка F")
```

## Match с None

```
value = none

match value:
    case none:
        display("Нет значения")
    case 0:
        display("Ноль")
    default:
        display("Значение: " + value)
```

## Вложенный match

```
user_type = "admin"
action = "delete"

match user_type:
    case "admin":
        match action:
            case "delete":
                display("Админ может удалять")
            case "create":
                display("Админ может создавать")
            default:
                display("Неизвестное действие")
    case "user":
        display("Ограниченные права")
    default:
        pass
```

## Match с коллекциями

```
response = {
    "status": 200,
    "type": "success"
}

match response["status"]:
    case 200:
        display("ОК")
    case 201:
        display("Создано")
    case 400:
        display("Неправильный запрос")
    default:
        display("Ошибка: " + response["status"])
```

## многострочные case

```
match action:
    case "send_email":
        result = send_email(
            to=email,
            subject="Привет",
            body="Сообщение тестирования"
        )
        display("Email отправлен: " + result)
    case "log_event":
        log(
            event_type="action",
            details={
                "action": action,
                "timestamp": now()
            }
        )
    default:
        pass
```

## Лучшие практики

- Используйте `match` для различных случаев
- Используйте `default` как резервный вариант
- Держите case простыми; используйте функции для сложной логики
- Избегайте глубокой вложенности
