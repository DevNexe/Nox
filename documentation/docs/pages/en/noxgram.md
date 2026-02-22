# NoxGram

`NoxGram` is a lightweight Telegram bot toolkit for Nox.

If you don't have this library, run the command:

```
nox package install NoxGram
```

Import:

```
connect NoxGram
```

Create bot:

```
bot = NoxGram.bot("YOUR_TELEGRAM_BOT_TOKEN")
```

## Basic usage

```
connect NoxGram

bot = NoxGram.bot("TOKEN")

bot.command("start", lambda ctx: ctx["bot"].send_message(ctx["chat_id"], "Hello!"))

define on_text(ctx):
    text = ctx["text"]
    if text != none:
        ctx["bot"].send_message(ctx["chat_id"], "You said: " + text)

bot.on_message(on_text)
run_async(bot.poll())
```

## API highlights

- `bot.command(name, handler)`
- `bot.on_message(handler)`
- `bot.on_filter(filter_fn, handler)`
- `bot.use(middleware)`
- `bot.send_message(chat_id, text)`
- `bot.poll(interval_ms=700, timeout=20, max_batch=100)`

## FSM helpers

- `bot.state_set(chat_id, state)`
- `bot.state_get(chat_id)`
- `bot.state_clear(chat_id)`

## Builtin filters

- `NoxGram.filter_command(name)`
- `NoxGram.filter_text_contains(part)`
