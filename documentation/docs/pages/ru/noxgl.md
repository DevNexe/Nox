# NoxGL

`NoxGL` - современная OpenGL-библиотека для Nox.

Если библиотека не установлена, выполните:

```
nox package install NoxGL
```

Импорт:

```
connect NoxGL as gl
```

## Возможности

- Современный shader pipeline (`create_program`, `use_program`)
- Буферы (`VAO`, `VBO`, `EBO`)
- Текстуры (`create_texture_rgba`, `bind_texture`)
- Матрицы и камеры (`camera2d`, `camera3d`, `uniform_mat4`)
- Обработка ввода (`key_down`, `mouse_down`, `on_cursor`)
- Диагностика OpenGL (`check_gl`)

## Базовый пример (шейдер + меш)

```
connect NoxGL as gl

app = gl.create("NoxGL demo", 960, 540)

vs = """
#version 330 core
layout(location = 0) in vec3 aPos;
layout(location = 1) in vec3 aColor;
uniform mat4 u_mvp;
out vec3 vColor;
void main() {
    gl_Position = u_mvp * vec4(aPos, 1.0);
    vColor = aColor;
}
"""

fs = """
#version 330 core
in vec3 vColor;
out vec4 FragColor;
void main() {
    FragColor = vec4(vColor, 1.0);
}
"""

prog = app.create_program(vs, fs)
if not prog["ok"]:
    display(prog["log"])
    app.should_close(true)

verts = [
     0.0,  0.7, 0.0,   1.0, 0.2, 0.2,
    -0.7, -0.6, 0.0,   0.2, 1.0, 0.2,
     0.7, -0.6, 0.0,   0.2, 0.4, 1.0
]
mesh = gl.create_mesh_f32(app, verts, [3, 3])

define frame(g):
    g.use_program(prog["id"])
    g.uniform_mat4(prog["id"], "u_mvp", gl.mat4_identity())
    mesh.draw()

app.run(frame)
```

## Для 3D

- Используйте `camera3d()` для перспективы.
- Включайте depth test через `app.enable_depth(true)`.
- Для индексированной геометрии используйте `create_indexed_mesh_f32(...)`.
- Для mouse look используйте `app.on_cursor(...)`.
