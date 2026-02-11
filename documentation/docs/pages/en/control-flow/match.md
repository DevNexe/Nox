# Match Statements

The `match` statement provides pattern matching for multiple cases. It evaluates a value against several patterns and executes the matching block.

## Basic Match

```
status = "success"

match status:
    case "success":
        display("Operation succeeded")
    case "error":
        display("Operation failed")
    case "pending":
        display("Waiting...")
    default:
        display("Unknown status")
```

## Match with Numbers

```
error_code = 404

match error_code:
    case 404:
        display("Not found")
    case 500:
        display("Server error")
    case 403:
        display("Forbidden")
    default:
        display("Unknown error: " + error_code)
```

## Match with Conditions

```
score = 85

match true:
    case score >= 90:
        display("Grade A")
    case score >= 80:
        display("Grade B")
    case score >= 70:
        display("Grade C")
    default:
        display("Grade F")
```

## Match with None

```
value = none

match value:
    case none:
        display("No value")
    case 0:
        display("Zero")
    default:
        display("Value: " + value)
```

## Nested Match

```
user_type = "admin"
action = "delete"

match user_type:
    case "admin":
        match action:
            case "delete":
                display("Admin can delete")
            case "create":
                display("Admin can create")
            default:
                display("Unknown action")
    case "user":
        display("Limited permissions")
    default:
        pass
```

## Match with Collections

```
response = {
    "status": 200,
    "type": "success"
}

match response["status"]:
    case 200:
        display("OK")
    case 201:
        display("Created")
    case 400:
        display("Bad request")
    default:
        display("Error: " + response["status"])
```

## Multiline Cases

```
match action:
    case "send_email":
        result = send_email(
            to=email,
            subject="Hello",
            body="Test message"
        )
        display("Email sent: " + result)
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

## Best Practices

- Use `match` for distinct cases
- Use `default` as fallback
- Keep cases simple; use functions for complex logic
- Avoid deep nesting
