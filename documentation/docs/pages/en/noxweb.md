# NoxWeb

## Basic App

```
connect NoxWeb

app = NoxWeb.web()
app.static("static")
app.templates("templates")

@app.get("/")
define home(req):
    result NoxWeb.render_template("index.html", {"name": "Nox"})

app.run(8080)
```

If you don't have this library, run the command:

```
nox package install NoxWeb
```

## Blueprints

```
bp = NoxWeb.blueprint()

@bp.get("/ping")
define ping(req):
    result "pong"

app.register(bp, "/api")
```