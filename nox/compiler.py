from __future__ import annotations

import re
import sys
import shutil
import subprocess
from pathlib import Path


def _find_cl() -> str | None:
    import os

    if shutil.which("cl"):
        return "cl"

    program_files = [
        os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"),
        os.environ.get("ProgramFiles", "C:\\Program Files"),
    ]
    vs_paths = [
        "Microsoft Visual Studio\\2022\\Community\\VC\\Tools\\MSVC",
        "Microsoft Visual Studio\\2022\\Professional\\VC\\Tools\\MSVC",
        "Microsoft Visual Studio\\2022\\Enterprise\\VC\\Tools\\MSVC",
        "Microsoft Visual Studio\\2019\\Community\\VC\\Tools\\MSVC",
    ]

    for pf in program_files:
        for vs in vs_paths:
            base = Path(pf) / vs
            if not base.exists():
                continue
            versions = sorted(base.iterdir(), reverse=True)
            for ver in versions:
                cl = ver / "bin" / "Hostx64" / "x64" / "cl.exe"
                if cl.exists():
                    return str(cl)
    return None


def _find_compiler(is_cpp: bool = False) -> str | None:
    if sys.platform == "win32":
        candidates = ["g++", "clang++"] if is_cpp else ["gcc", "clang"]
        for cc in candidates:
            if shutil.which(cc):
                return cc
        return _find_cl()
    elif sys.platform == "darwin":
        candidates = ["clang++", "g++"] if is_cpp else ["clang", "gcc", "cc"]
    else:
        candidates = ["g++", "clang++"] if is_cpp else ["gcc", "clang", "cc"]

    for cc in candidates:
        if shutil.which(cc):
            return cc
    return None


def _install_hint() -> str:
    if sys.platform == "win32":
        return (
            "Install a C/C++ compiler:\n"
            "  Visual Studio 2022: https://visualstudio.microsoft.com\n"
            "  MinGW-w64:          https://www.mingw-w64.org\n"
            "  MSYS2:              https://www.msys2.org  (then: pacman -S mingw-w64-x86_64-gcc)\n"
            "  LLVM/Clang:         https://releases.llvm.org"
        )
    elif sys.platform == "darwin":
        return (
            "Install Xcode Command Line Tools:\n"
            "  xcode-select --install"
        )
    else:
        return (
            "Install a C/C++ compiler:\n"
            "  sudo apt install gcc g++     # Debian/Ubuntu\n"
            "  sudo dnf install gcc gcc-c++ # Fedora\n"
            "  sudo pacman -S gcc            # Arch"
        )


def _make_output_path(source: Path, output_path: str | None) -> Path:
    if output_path:
        return Path(output_path).resolve()
    if sys.platform == "win32":
        return source.with_suffix(".dll")
    elif sys.platform == "darwin":
        return source.with_suffix(".dylib")
    else:
        return source.with_suffix(".so")


def _patch_exports(source: Path) -> Path:
    text = source.read_text(encoding="utf-8")
    patched = re.sub(
        r'^(?!__declspec)([a-zA-Z_][\w\s\*]+)\s+(\w+)\s*\(([^;{]*)\)\s*\{',
        r'__declspec(dllexport) \1 \2(\3) {',
        text,
        flags=re.MULTILINE
    )
    tmp = source.parent / (source.stem + "_nox_tmp.c")
    tmp.write_text(patched, encoding="utf-8")
    return tmp


def compile_source(source_path: str, output_path: str | None = None, is_cpp: bool = False) -> str:
    source = Path(source_path).resolve()
    if not source.exists():
        raise FileNotFoundError(f"Source file not found: {source_path}")

    is_cpp = is_cpp or source.suffix in (".cpp", ".cxx", ".cc")
    cc = _find_compiler(is_cpp)

    if cc is None:
        kind = "C++" if is_cpp else "C"
        raise RuntimeError(f"No {kind} compiler found.\n{_install_hint()}")

    out = _make_output_path(source, output_path)

    tmp = None
    try:
        if sys.platform == "win32":
            tmp = _patch_exports(source)
            src_to_compile = tmp
        else:
            src_to_compile = source

        if cc.endswith("cl.exe") or cc == "cl":
            flags = [cc, str(src_to_compile), "/LD", f"/Fe{out}", "/nologo"]
        else:
            flags = [cc, str(src_to_compile), "-shared", "-o", str(out)]
            if sys.platform != "win32":
                flags.append("-fPIC")

        result = subprocess.run(flags, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Compilation failed:\n{result.stderr or result.stdout}")

    finally:
        if tmp and tmp.exists():
            tmp.unlink(missing_ok=True)

    return str(out)


def _make_module_values() -> dict:
    return {
        "compile": compile_source,
    }