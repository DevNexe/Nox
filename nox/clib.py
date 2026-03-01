from __future__ import annotations

import ctypes
import io
import re
import sys
from pathlib import Path
from typing import Any, Dict, Optional

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
    raw = " ".join(type_str.replace("\t", " ").split())
    pointer_count = raw.count("*")
    base = raw.replace("*", "").strip()
    if base.startswith("const "):
        base = base[6:].strip()

    if base == "void" and pointer_count == 0:
        return None
    if base == "char" and pointer_count == 1:
        return ctypes.c_char_p
    if base == "char" and pointer_count == 2:
        return ctypes.POINTER(ctypes.c_char_p)
    if base == "void" and pointer_count >= 1:
        return ctypes.c_void_p

    ctype = _C_TYPE_MAP.get(base, ctypes.c_void_p)
    if ctype is None:
        ctype = ctypes.c_void_p
    for _ in range(pointer_count):
        ctype = ctypes.POINTER(ctype)
    return ctype

def _preprocess_header(header_path: str) -> str:
    try:
        import pcpp  # type: ignore

        class _SilentPreprocessor(pcpp.Preprocessor):
            def on_error(self, file, line, msg):
                pass

        pp = _SilentPreprocessor()
        pp.line_directive = None
        with open(header_path, encoding="utf-8", errors="replace") as f:
            src = f.read()
        pp.parse(src, header_path)
        out = io.StringIO()
        pp.write(out)
        return out.getvalue()
    except ImportError:
        pass

    with open(header_path, encoding="utf-8", errors="replace") as f:
        src = f.read()
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.DOTALL)
    src = re.sub(r"//[^\n]*", "", src)
    src = re.sub(r"^\s*#[^\n]*", "", src, flags=re.MULTILINE)
    return src

_FUNC_RE = re.compile(
    r"""
    ([\w\s\*]+?)        
    \s+
    (\w+)               
    \s*\(\s*
    ([^)]*)             
    \)\s*;
    """,
    re.VERBOSE | re.DOTALL,
)

_TYPEDEF_FUNC_RE = re.compile(
    r"""
    typedef\s+
    ([\w\s\*]+?)\s*     
    \(\s*\*\s*(\w+)\s*\)  
    \s*\(\s*([^)]*)\)\s*;
    """,
    re.VERBOSE | re.DOTALL,
)


def _parse_param_type(param: str) -> Any:
    param = param.strip()
    if not param or param == "void":
        return None
    parts = param.rsplit(None, 1)
    type_str = parts[0].strip() if len(parts) > 1 else param
    if type_str in {"const", "unsigned", "signed"}:
        type_str = param
    return _map_type(type_str)


def _parse_functions(header_content: str) -> Dict[str, Dict[str, Any]]:
    functions: Dict[str, Dict[str, Any]] = {}

    for m in _FUNC_RE.finditer(header_content):
        ret_raw = m.group(1).strip()
        name = m.group(2).strip()
        params_raw = m.group(3).strip()

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

class CLib:
    def __init__(self, lib: ctypes.CDLL, name: str) -> None:
        self._lib = lib
        self._name = name

    def get(self, attr: str) -> Any:
        try:
            fn = getattr(self._lib, attr)
        except AttributeError:
            raise RuntimeError(f"C library '{self._name}' has no symbol '{attr}'")
        
        def wrapper(*args):
            converted = []
            for arg in args:
                if isinstance(arg, str):
                    converted.append(arg.encode("utf-8"))
                else:
                    converted.append(arg)
            result = fn(*converted)
            if isinstance(result, bytes):
                return result.decode("utf-8")
            return result
        
        return wrapper
    
    def __repr__(self) -> str:
        return f"<CLib '{self._name}'>"

def _find_lib(base_path: str) -> str:
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

    if sys.platform != "win32":
        parent = p.parent
        for ext in exts:
            candidate = parent / f"lib{p.name}{ext}"
            if candidate.exists():
                return str(candidate)

    # Fallback to system dynamic loader search (PATH/system dirs).
    # This is required for libraries like opengl32.dll on Windows.
    if sys.platform == "win32":
        if p.suffix:
            return p.name
        return f"{p.name}.dll"
    if sys.platform == "darwin":
        if p.suffix:
            return p.name
        return f"lib{p.name}.dylib"
    if p.suffix:
        return p.name
    return f"lib{p.name}.so"

    raise FileNotFoundError(f"Cannot find C library for '{base_path}'")


def _uint_ref(value: int = 0) -> Any:
    return ctypes.c_uint(int(value))


def _int_ref(value: int = 0) -> Any:
    return ctypes.c_int(int(value))


def _float_ref(value: float = 0.0) -> Any:
    return ctypes.c_float(float(value))


def _double_ref(value: float = 0.0) -> Any:
    return ctypes.c_double(float(value))


def _pointer(value: Any) -> Any:
    return ctypes.pointer(value)


def _deref(value: Any) -> Any:
    return value.value


def _set_ref(ref: Any, value: Any) -> None:
    ref.value = value


def _float_array(values: Any) -> Any:
    items = [float(v) for v in values]
    arr_t = ctypes.c_float * len(items)
    return arr_t(*items)


def _int_array(values: Any) -> Any:
    items = [int(v) for v in values]
    arr_t = ctypes.c_int * len(items)
    return arr_t(*items)


def _uint_array(values: Any) -> Any:
    items = [int(v) for v in values]
    arr_t = ctypes.c_uint * len(items)
    return arr_t(*items)


def _byte_array(values: Any) -> Any:
    items = [int(v) & 0xFF for v in values]
    arr_t = ctypes.c_ubyte * len(items)
    return arr_t(*items)


def _c_string(value: Any) -> Any:
    return ctypes.c_char_p(str(value).encode("utf-8"))


def _c_string_array(values: Any) -> Any:
    if isinstance(values, str):
        values = [values]
    items = [str(v).encode("utf-8") for v in values]
    arr_t = ctypes.c_char_p * len(items)
    return arr_t(*items)


def _string_buffer(size: Any) -> Any:
    n = int(size)
    if n < 1:
        n = 1
    return ctypes.create_string_buffer(n)


def _buffer_text(buf: Any) -> str:
    raw = bytes(buf)
    end = raw.find(b"\x00")
    if end >= 0:
        raw = raw[:end]
    return raw.decode("utf-8", errors="replace")


def _make_func(addr: Any, restype: Any = None, argtypes: Any = None) -> Any:
    if addr is None:
        raise RuntimeError("make_func expects non-null address")
    if isinstance(addr, ctypes.c_void_p):
        addr = addr.value
    if not addr:
        raise RuntimeError("make_func expects non-zero address")
    if argtypes is None:
        argtypes = []
    if sys.platform == "win32":
        fn_type = ctypes.WINFUNCTYPE(restype, *argtypes)
    else:
        fn_type = ctypes.CFUNCTYPE(restype, *argtypes)
    return fn_type(int(addr))


def load(path: str, base_dir: str = None) -> CLib:
    p = Path(path)
    if not p.is_absolute():
        if base_dir:
            p = Path(base_dir) / p
        else:
            p = Path.cwd() / p

    if p.suffix == ".h":
        header_content = _preprocess_header(str(p))
        functions = _parse_functions(header_content)
        lib_path = _find_lib(str(p.with_suffix("")))
        lib = ctypes.CDLL(lib_path)
        for name, sig in functions.items():
            try:
                fn = getattr(lib, name)
                fn.restype = sig["restype"]
                if sig["argtypes"]:
                    fn.argtypes = sig["argtypes"]
            except AttributeError:
                pass
        return CLib(lib, p.stem)
    else:
        lib_path = _find_lib(str(p))
        lib = ctypes.CDLL(lib_path)
        return CLib(lib, p.stem)


def call(clib: Any, func_name: str, *args: Any) -> Any:
    if not isinstance(clib, CLib):
        raise RuntimeError("clib.call expects a CLib object as first argument")
    fn = clib.get(func_name)
    return fn(*args)

def _make_module_values() -> Dict[str, Any]:
    return {
        "load":   load,
        "call":   call,
        "uint_ref": _uint_ref,
        "int_ref": _int_ref,
        "float_ref": _float_ref,
        "double_ref": _double_ref,
        "pointer": _pointer,
        "deref": _deref,
        "set_ref": _set_ref,
        "float_array": _float_array,
        "int_array": _int_array,
        "uint_array": _uint_array,
        "byte_array": _byte_array,
        "c_string": _c_string,
        "c_string_array": _c_string_array,
        "string_buffer": _string_buffer,
        "buffer_text": _buffer_text,
        "make_func": _make_func,
        "c_int":        ctypes.c_int,
        "c_uint":       ctypes.c_uint,
        "c_ubyte":      ctypes.c_ubyte,
        "c_float":      ctypes.c_float,
        "c_double":     ctypes.c_double,
        "c_char_p":     ctypes.c_char_p,
        "c_void_p":     ctypes.c_void_p,
        "c_long":       ctypes.c_long,
        "c_size_t":     ctypes.c_size_t,
    }
