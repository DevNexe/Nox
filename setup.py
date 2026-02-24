#!/usr/bin/env python3

import subprocess
import sys
from pathlib import Path

RESET  = "\033[0m"
BOLD   = "\033[1m"
GREEN  = "\033[32m"
CYAN   = "\033[36m"
YELLOW = "\033[33m"
RED    = "\033[31m"
DIM    = "\033[2m"


def c(color: str, text: str) -> str:
    return f"{color}{text}{RESET}"


def banner():
    print()
    print(c(BOLD, "  ███╗   ██╗ ██████╗ ██╗  ██╗"))
    print(c(BOLD, "  ████╗  ██║██╔═══██╗╚██╗██╔╝"))
    print(c(BOLD, "  ██╔██╗ ██║██║   ██║ ╚███╔╝ "))
    print(c(BOLD, "  ██║╚██╗██║██║   ██║ ██╔██╗ "))
    print(c(BOLD, "  ██║ ╚████║╚██████╔╝██╔╝ ██╗"))
    print(c(BOLD, "  ╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝"))
    print()
    print(c(DIM, "  The Nox Programming Language — Toolchain Manager"))
    print()


def step(n: int, total: int, msg: str):
    print(f"  {c(GREEN, 'info')} [{n}/{total}] {msg}")


def warn(msg: str):
    print(f"  {c(YELLOW, 'warn')} {msg}")


def error(msg: str):
    print(f"  {c(RED, 'error')} {msg}")


def success(msg: str):
    print(f"  {c(GREEN, '✓')} {msg}")


def run(cmd: list[str], silent: bool = False) -> int:
    if not silent:
        print(f"  {c(DIM, '$ ' + ' '.join(cmd))}")
    result = subprocess.run(cmd, capture_output=silent)
    return result.returncode


def get_venv_python() -> str:
    if sys.platform == "win32":
        return str(Path(".venv") / "Scripts" / "python.exe")
    return str(Path(".venv") / "bin" / "python")


def get_venv_pip() -> str:
    if sys.platform == "win32":
        return str(Path(".venv") / "Scripts" / "pip.exe")
    return str(Path(".venv") / "bin" / "pip")


def check_venv() -> bool:
    venv_dir = Path(".venv")
    if not venv_dir.exists():
        error(".venv not found — run install first (option 1)")
        return False
    return True


# ── Commands ──────────────────────────────────────────────────────────────────

def cmd_install():
    print()
    print(c(BOLD, "  Install Nox Environment"))
    print()
    print(f"     python:       {c(CYAN, sys.version.split()[0])}")
    print(f"     environment:  {c(CYAN, '.venv')}")
    print(f"     packages:     {c(CYAN, 'rich, pcpp, pycparser, cffi')}")
    print()

    try:
        answer = input(f"  Proceed? {c(DIM, '(y/N)')} ").strip().lower()
    except KeyboardInterrupt:
        print()
        warn("Cancelled")
        return

    if answer not in ("y", "yes"):
        warn("Cancelled")
        return

    print()
    total = 3
    venv_dir = Path(".venv")

    step(1, total, "Setting up virtual environment")
    if venv_dir.exists():
        warn(".venv already exists, skipping")
    else:
        if run([sys.executable, "-m", "venv", ".venv"], silent=True) != 0:
            error("Failed to create virtual environment")
            return
        success("Virtual environment created")

    print()
    step(2, total, "Updating pip")
    run([get_venv_pip(), "install", "--upgrade", "pip", "-q"], silent=True)
    success("pip updated")

    print()
    step(3, total, "Installing dependencies")
    if run([get_venv_pip(), "install", "-r", "requirements.txt", "-q"], silent=True) != 0:
        error("Failed to install dependencies")
        return
    success("Dependencies installed")

    print()
    print(c(GREEN, "  Nox installed successfully!"))
    print()
    if sys.platform == "win32":
        print(f"  Activate: {c(CYAN, '.venv\\Scripts\\activate')}")
    else:
        print(f"  Activate: {c(CYAN, 'source .venv/bin/activate')}")
    print()


def cmd_activate():
    print()
    if not check_venv():
        return
    print(c(BOLD, "  Activate the environment:"))
    print()
    if sys.platform == "win32":
        print(f"    cmd:        {c(CYAN, '.venv\\Scripts\\activate.bat')}")
        print(f"    powershell: {c(CYAN, '.venv\\Scripts\\Activate.ps1')}")
    else:
        print(f"    {c(CYAN, 'source .venv/bin/activate')}")
    print()
    print(c(DIM, "  Then run: python -m nox <file.nox>"))
    print()


def cmd_build():
    print()
    if not check_venv():
        return

    print(c(BOLD, "  Building Nox executable..."))
    print()
    total = 2

    step(1, total, "Installing Nuitka")
    if run([get_venv_pip(), "install", "nuitka", "-q"], silent=True) != 0:
        error("Failed to install Nuitka")
        return
    success("Nuitka ready")

    print()
    step(2, total, "Compiling")
    print()

    if run([
        get_venv_python(), "-m", "nuitka",
        "--onefile",
        "--include-package=nox",
        "--include-package=rich",
        "--nofollow-import-to=numba",
        "--include-data-files=nox/info.cfg=nox/info.cfg",
        "--output-filename=nox",
        "--python-flag=-m",
        "nox",
    ]) != 0:
        print()
        error("Build failed")
        return

    print()
    exe = "nox.exe" if sys.platform == "win32" else "nox"
    success(f"Built {c(CYAN, exe)}")
    print()
    print(c(GREEN, "  Nox is ready!"))
    print(f"  {c(DIM, 'Run: ./' + exe + ' <file.nox>')}")
    print()


def cmd_update():
    print()
    if not check_venv():
        return
    print(c(BOLD, "  Updating dependencies..."))
    print()
    if run([get_venv_pip(), "install", "--upgrade", "-r", "requirements.txt", "-q"], silent=True) != 0:
        error("Update failed")
        return
    success("All packages updated")
    print()


# ── Menu ──────────────────────────────────────────────────────────────────────

def menu():
    banner()

    venv_ok = Path(".venv").exists()
    status = c(GREEN, "installed") if venv_ok else c(YELLOW, "not installed")

    print(f"  Environment status: {status}")
    print()
    print(f"  {c(CYAN, '1)')} Install / setup environment")
    print(f"  {c(CYAN, '2)')} Show activate instructions")
    print(f"  {c(CYAN, '3)')} Build executable")
    print(f"  {c(CYAN, '4)')} Update dependencies")
    print(f"  {c(CYAN, '5)')} Exit")
    print()

    try:
        choice = input(f"  {c(BOLD, 'Choose')} {c(DIM, '[1-5]:')} ").strip()
    except KeyboardInterrupt:
        print()
        print()
        sys.exit(0)

    print()

    if choice == "1":
        cmd_install()
    elif choice == "2":
        cmd_activate()
    elif choice == "3":
        cmd_build()
    elif choice == "4":
        cmd_update()
    elif choice == "5":
        sys.exit(0)
    else:
        error(f"Unknown option: '{choice}'")
        print()

    input(f"  {c(DIM, 'Press Enter to continue...')} ")
    menu()


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd == "install":
            cmd_install()
        elif cmd == "activate":
            cmd_activate()
        elif cmd == "build":
            cmd_build()
        elif cmd == "update":
            cmd_update()
        else:
            error(f"Unknown command: '{cmd}'")
            print(f"  Run without arguments for interactive menu")
            sys.exit(1)
    else:
        menu()


if __name__ == "__main__":
    main()