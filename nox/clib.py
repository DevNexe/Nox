"""
clib — C library loader for Nox.
Supports loading .dll/.so/.dylib via header files (.h) or direct loading.

Dependencies (pure Python, no compiler needed):
    pip install pcpp pycparser
"""
from __future__ import annotations

import ctypes
import io
import re
import sys
from pathlib import Path
from typing import Any, Dict, Optional


# ─── ctypes type map ──────────────────────────────────────────────────────────

_C_TYPE_MAP: Dict[str, Any] = {
    "void":               None,
    "int":                ctypes.c_int,
    "unsigned":           ctypes.c_uint,
    "unsigned int":       ctypes.c_uint,
    "long":               ctypes.c_long,
    "unsigned long":      ctypes.c_ulong,
    "long long":          ctypes.c_longlong,
    "unsigned long long": ctypes.c_ulonglong,
    "short":              ctypes.c_short,
    "unsigned short":     ctypes.c_ushort,
    "char":               ctypes.c_char,
    "unsigned char":      ctypes.c_ubyte,
    "float":              ctypes.c_float,
    "double":             ctypes.c_double,
    "size_t":             ctypes.c_size_t,
    "char*":              ctypes.c_char_p,
    "const char*":        ctypes.c_char_p,
    "void*":              ctypes.c_void_p,
}


def _map_type(type_str: str) -> Any:
    t = type_str.strip().rstrip("*").strip()
    if type_str.strip().endswith("*"):
        t = type_str.strip()
    return _C_TYPE_MAP.get(t, ctypes.c_void_p)


# ─── Header preprocessing ─────────────────────────────────────────────────────

def _preprocess_header(header_path: str) -> str:
    """Try pcpp first, fall back to simple regex stripper."""
    try:
        import pcpp  # type: ignore

        class _SilentPreprocessor(pcpp.Preprocessor):
            def on_error(self, file, line, msg):
                pass  # silence errors from system includes

        pp = _SilentPreprocessor()
        pp.line_directive = None  # don't emit # line directives
        with open(header_path, encoding="utf-8", errors="replace") as f:
            src = f.read()
        pp.parse(src, header_path)
        out = io.StringIO()
        pp.write(out)
        return out.getvalue()
    except ImportError:
        pass

    # Fallback: strip macros and comments manually
    with open(header_path, encoding="utf-8", errors="replace") as f:
        src = f.read()
    # Remove block comments
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.DOTALL)
    # Remove line comments
    src = re.sub(r"//[^\n]*", "", src)
    # Remove preprocessor directives
    src = re.sub(r"^\s*#[^\n]*", "", src, flags=re.MULTILINE)
    return src


# ─── Function signature parser ────────────────────────────────────────────────

_FUNC_RE = re.compile(
    r"""
    ([\w\s\*]+?)        # return type (group 1)
    \s+
    (\w+)               # function name (group 2)
    \s*\(\s*
    ([^)]*)             # parameters (group 3)
    \)\s*;
    """,
    re.VERBOSE | re.DOTALL,
)

_TYPEDEF_FUNC_RE = re.compile(
    r"""
    typedef\s+
    ([\w\s\*]+?)\s*     # return type
    \(\s*\*\s*(\w+)\s*\)  # (*name)
    \s*\(\s*([^)]*)\)\s*;
    """,
    re.VERBOSE | re.DOTALL,
)


def _parse_param_type(param: str) -> Any:
    param = param.strip()
    if not param or param == "void":
        return None
    # grab the type, ignore name
    parts = param.rsplit(None, 1)
    type_str = parts[0].strip() if len(parts) > 1 else param
    # handle pointer in name like "int *ptr" → "int*"
    if "*" in param:
        base = param.replace("*", "").split()
        type_str = " ".join(base[:-1]) + "*" if len(base) > 1 else "void*"
    return _map_type(type_str)


def _parse_functions(header_content: str) -> Dict[str, Dict[str, Any]]:
    functions: Dict[str, Dict[str, Any]] = {}

    for m in _FUNC_RE.finditer(header_content):
        ret_raw = m.group(1).strip()
        name = m.group(2).strip()
        params_raw = m.group(3).strip()

        # Skip obvious non-function matches
        if ret_raw in {"typedef", "struct", "enum", "union"}:
            continue
        if name.startswith("_"):
            continue

        ret_type = _map_type(ret_raw)
        arg_types = []
        if params_raw and params_raw != "void":
            for p in params_raw.split(","):
                pt = _parse_param_type(p)
                if pt is not None:
                    arg_types.append(pt)

        functions[name] = {"restype": ret_type, "argtypes": arg_types}

    return functions


# ─── Lib wrapper ──────────────────────────────────────────────────────────────

class CLib:
    """Wraps a ctypes CDLL and exposes its functions as callable attributes."""

    def __init__(self, lib: ctypes.CDLL, name: str) -> None:
        self._lib = lib
        self._name = name

    def get(self, attr: str) -> Any:
        try:
            return getattr(self._lib, attr)
        except AttributeError:
            raise RuntimeError(f"C library '{self._name}' has no symbol '{attr}'")

    def __repr__(self) -> str:
        return f"<CLib '{self._name}'>"


# ─── Public API ───────────────────────────────────────────────────────────────

def _find_lib(base_path: str) -> str:
    """Given a path (possibly without extension), find the actual library file."""
    p = Path(base_path)
    if p.exists():
        return str(p)

    if sys.platform == "win32":
        exts = [".dll"]
    elif sys.platform == "darwin":
        exts = [".dylib", ".so"]
    else:
        exts = [".so", ".so.0"]

    for ext in exts:
        candidate = p.with_suffix(ext)
        if candidate.exists():
            return str(candidate)

    # Also try lib prefix on Unix
    if sys.platform != "win32":
        parent = p.parent
        for ext in exts:
            candidate = parent / f"lib{p.name}{ext}"
            if candidate.exists():
                return str(candidate)

    raise FileNotFoundError(f"Cannot find C library for '{base_path}'")


def load(path: str) -> CLib:
    """
    Load a C library.

    - If path ends with .h, parses the header and loads matching .dll/.so
    - Otherwise loads the binary directly
    """
    p = Path(path)

    if p.suffix == ".h":
        # Parse header to get function signatures
        header_content = _preprocess_header(path)
        functions = _parse_functions(header_content)

        # Find matching binary
        lib_path = _find_lib(str(p.with_suffix("")))
        lib = ctypes.CDLL(lib_path)

        # Apply restype / argtypes
        for name, sig in functions.items():
            try:
                fn = getattr(lib, name)
                fn.restype = sig["restype"]
                if sig["argtypes"]:
                    fn.argtypes = sig["argtypes"]
            except AttributeError:
                pass  # symbol not in this lib, skip

        return CLib(lib, p.stem)
    else:
        lib_path = _find_lib(path)
        lib = ctypes.CDLL(lib_path)
        return CLib(lib, p.stem)


def call(clib: Any, func_name: str, *args: Any) -> Any:
    """Call a function from a CLib by name."""
    if not isinstance(clib, CLib):
        raise RuntimeError("clib.call expects a CLib object as first argument")
    fn = clib.get(func_name)
    return fn(*args)


# ─── Types exposed to Nox ─────────────────────────────────────────────────────

def _make_module_values() -> Dict[str, Any]:
    return {
        "load":   load,
        "call":   call,
        # expose ctypes basics for advanced users
        "c_int":        ctypes.c_int,
        "c_float":      ctypes.c_float,
        "c_double":     ctypes.c_double,
        "c_char_p":     ctypes.c_char_p,
        "c_void_p":     ctypes.c_void_p,
        "c_long":       ctypes.c_long,
        "c_size_t":     ctypes.c_size_t,
    }