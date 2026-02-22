# NoxGram

`NoxGram` — легковесная библиотека для Telegram-ботов на Nox.

Если у вас отсутствует эта библиотека запустите команду:

```
nox package install NoxGram
```

Импорт:

```
connect NoxGram
```

Создание бота:

```
bot = NoxGram.bot("YOUR_TELEGRAM_BOT_TOKEN")
```

## Базовое использование

```
connect NoxGram

bot = NoxGram.bot("TOKEN")

bot.command("start", lambda ctx: ctx["bot"].send_message(ctx["chat_id"], "Привет!"))

define on_text(ctx):
    text = ctx["text"]
    if text != none:
        ctx["bot"].send_message(ctx["chat_id"], "Ты написал: " + text)

bot.on_message(on_text)
run_async(bot.poll())
```

## Основные методы

- `bot.command(name, handler)`
- `bot.on_message(handler)`
- `bot.on_filter(filter_fn, handler)`
- `bot.use(middleware)`
- `bot.send_message(chat_id, text)`
- `bot.poll(interval_ms=700, timeout=20, max_batch=100)`

## FSM-хелперы

- `bot.state_set(chat_id, state)`
- `bot.state_get(chat_id)`
- `bot.state_clear(chat_id)`

## Встроенные фильтры

- `NoxGram.filter_command(name)`
- `NoxGram.filter_text_contains(part)`
