# NoxGL

`NoxGL` is a modern OpenGL toolkit for Nox.

If you don't have this library, run:

```
nox package install NoxGL
```

Import:

```
connect NoxGL as gl
```

## Highlights

- Modern shader pipeline (`create_program`, `use_program`)
- Buffers (`VAO`, `VBO`, `EBO`)
- Textures (`create_texture_rgba`, `bind_texture`)
- Matrices and cameras (`camera2d`, `camera3d`, `uniform_mat4`)
- Input polling (`key_down`, `mouse_down`, `on_cursor`)
- OpenGL diagnostics (`check_gl`)

## Basic Shader + Mesh

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

## 3D Notes

- Use `camera3d()` for perspective rendering.
- Enable depth test with `app.enable_depth(true)`.
- For indexed geometry use `create_indexed_mesh_f32(...)`.
- Mouse look is available via `app.on_cursor(...)`.
