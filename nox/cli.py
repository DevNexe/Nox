from __future__ import annotations

from pathlib import Path
from typing import Optional

from .lexer import Lexer
from .parser import Parser
from .interpreter import Interpreter
from .errors import NoxSyntaxError, NoxRuntimeError
from . import __version__
import sys
from rich.console import Console
from rich.text import Text
import ssl as _ssl
_ctx = _ssl.create_default_context()
_ctx.check_hostname = False
_ctx.verify_mode = _ssl.CERT_NONE

_ERR_MARKER = ">"

def _ensure_utf8() -> None:
    import sys
    import io
    import os

    os.environ["PYTHONIOENCODING"] = "utf-8"

    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
                continue
            except Exception:
                pass
        try:
            if hasattr(stream, "buffer"):
                wrapped = io.TextIOWrapper(stream.buffer, encoding="utf-8", errors="replace")
                if stream is sys.stdout:
                    sys.stdout = wrapped
                else:
                    sys.stderr = wrapped
        except Exception:
            pass


_ensure_utf8()

def _create_console() -> Console:
    import os

    force_ascii = os.getenv("Nox_ASCII", "").lower() in {"1", "true", "yes"}
    if force_ascii:
        return Console(legacy_windows=True, force_terminal=True, color_system="standard")

    return Console(force_terminal=True, color_system="truecolor")


console = _create_console()

DEFAULT_GITHUB_USER = "devnexe-alt"
LIBRARIES_DIRNAME = "Libraries"


def _exe_dir() -> Path:
    try:
        import __compiled__  # type: ignore
        import sys
        return Path(sys.executable).parent
    except ImportError:
        return Path(__file__).resolve().parent.parent


def _libraries_root() -> Path:
    exe = Path(sys.argv[0]).resolve()
    if exe.suffix in (".exe",) or (not exe.suffix and exe.stat().st_mode & 0o111):
        path = exe.parent / LIBRARIES_DIRNAME
    else:
        path = Path(__file__).resolve().parent.parent / LIBRARIES_DIRNAME
    return path


def _read_version_from_info_cfg() -> str:
    candidates = [
        Path(__file__).resolve().parent / "info.cfg",
        _exe_dir() / "nox" / "info.cfg",
        _exe_dir() / "info.cfg",
    ]

    for path in candidates:
        if not path.exists():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue

        for raw in text.splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or line.startswith(";"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
            elif ":" in line:
                key, value = line.split(":", 1)
            else:
                continue
            if key.strip().lower() == "version":
                parsed = value.strip().strip("'\"")
                if parsed:
                    return parsed

    return "unknown"


def run_source(source: str, base_dir: Path | None = None, current_file: Path | None = None) -> None:
    tokens = Lexer(source).tokenize()
    program = Parser(tokens).parse()
    Interpreter(base_dir=base_dir, current_file=current_file).run(program)


def _indent_width(line: str) -> int:
    width = 0
    for ch in line:
        if ch == " ":
            width += 1
        elif ch == "\t":
            width += 4 - (width % 4)
        else:
            break
    return width


def _repl_continuation_kind(lines: list[str]) -> str | None:
    headers: list[str] = []
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if _indent_width(line) != 0:
            continue
        headers.append(stripped)

    if not headers:
        return None

    first = headers[0]
    last = headers[-1]

    if first.startswith("if "):
        if last.startswith("else:"):
            return None
        return "if"

    if first == "try:":
        if last.startswith("finally:"):
            return None
        return "try"

    return None


def _is_repl_continuation(stripped: str, kind: str | None) -> bool:
    if kind == "if":
        return stripped.startswith("else if ") or stripped == "else:"
    if kind == "try":
        return stripped == "except:" or stripped == "finally:"
    return False


def _print_repl_help() -> None:
    console.print("REPL commands:")
    console.print("  help  Show this help")
    console.print("  quit  Exit the REPL")
    console.print("  exit  Exit the REPL")
    console.print("Tips:")
    console.print("  Expressions print their result automatically.")
    console.print("  After block bodies, press Enter to continue with else/else if/except/finally.")
    console.print("  Press Enter again to execute the block if there is no continuation.")


def _run_repl() -> int:
    console.print(f"Nox {__version__}")
    console.print("Use help for commands, quit or exit to leave.")

    interpreter = Interpreter(base_dir=Path.cwd(), current_file=Path("<repl>"))
    primary_prompt = ">>> "
    secondary_prompt = "... "
    carry_line: str | None = None

    while True:
        try:
            lines: list[str] = []
            prompt = primary_prompt
            expecting_block = False
            continuation_kind: str | None = None
            waiting_for_continuation = False

            while True:
                if carry_line is not None:
                    line = carry_line
                    carry_line = None
                else:
                    line = input(prompt)
                stripped = line.strip()

                if not lines and stripped in {"quit", "exit"}:
                    return 0
                if not lines and stripped == "help":
                    _print_repl_help()
                    break
                if not lines and stripped == "":
                    break

                if waiting_for_continuation:
                    if stripped == "":
                        break
                    if not _is_repl_continuation(stripped, continuation_kind):
                        carry_line = line
                        break
                    waiting_for_continuation = False
                    expecting_block = False

                if expecting_block and stripped and not line[:1].isspace():
                    line = "    " + line

                if stripped == "":
                    continuation_kind = _repl_continuation_kind(lines)
                    if continuation_kind is not None:
                        waiting_for_continuation = True
                        prompt = secondary_prompt
                        continue
                    break

                lines.append(line)
                prompt = secondary_prompt
                expecting_block = line.rstrip().endswith(":")
                if expecting_block:
                    continue
                if len(lines) == 1:
                    break

            if not lines:
                continue

            tokens = Lexer("\n".join(lines)).tokenize()
            program = Parser(tokens).parse()
            result = interpreter.run_repl(program)
            if result is not None:
                console.print(repr(result))
        except EOFError:
            console.print()
            return 0
        except KeyboardInterrupt:
            console.print()
            continue
        except NoxSyntaxError as exc:
            _print_error("SyntaxError", str(exc))
        except NoxRuntimeError as exc:
            error_name = getattr(exc, "display_name", "RuntimeError")
            _print_error(error_name, str(exc))
        except Exception as exc:
            _print_error("Internal Error", str(exc))

def _resolve_run_target(path: str, cwd: Optional[Path] = None) -> Path:
    base = cwd or Path.cwd()
    target = Path(path)
    if not target.is_absolute():
        target = base / path

    if not target.exists():
        exe = Path(sys.argv[0]).resolve()
        if exe.suffix in (".exe",) or (not exe.suffix and exe.stat().st_mode & 0o111):
            alt = exe.parent / path
        else:
            alt = Path(__file__).resolve().parent.parent / path
        if alt.exists():
            target = alt

    if target.is_dir():
        for name in ("__main__.nox", "main.nox", "app.nox"):
            if (target / name).exists():
                return target / name
        raise RuntimeError("Directory has no __main__.nox, main.nox, or app.nox")

    if not target.exists():
        raise FileNotFoundError(f"No such file or directory: '{path}'")

    return target

def _format_code_snippet(path: str, line: int | None, context: int = 3) -> tuple[list[tuple[int, str]], int]:
    if line is None:
        return [], 0
    try:
        source = Path(path).read_text(encoding="utf-8")
    except Exception:
        return [], 0
    lines = source.splitlines()
    if line < 1 or line > len(lines):
        return [], 0
    start = max(line - context - 1, 0)
    end = min(line + context, len(lines))
    snippet = [(idx + 1, lines[idx]) for idx in range(start, end)]
    return snippet, start + 1


def _render_traceback_panel(
    path: str,
    line: int | None,
    scope: str | None,
    lines: list[tuple[int, str]],
    highlight_line: int | None,
) -> None:
    line_text = str(line) if line is not None else "?"

    header = Text()
    header.append("Error", style="bold red")
    header.append(" in ")
    header.append(path, style="yellow")
    header.append(" at line ")
    header.append(line_text, style="magenta")
    if scope and scope != "<module>":
        header.append(" in ")
        header.append(scope, style="green")

    console.print("[bold red]Traceback:[/bold red]")
    indented_header = Text("  ")
    indented_header.append_text(header)
    indented_header.append(":")
    console.print(indented_header)
    if lines:
        for ln, content in lines:
            is_err = (ln == highlight_line)
            marker = _ERR_MARKER if is_err else " "
            row = Text()
            if is_err:
                row.append(f"    {marker} {ln}", style="bold red")
                row.append(f" {content}", style="bold")
            else:
                row.append(f"    {marker} {ln}", style="dim")
                row.append(f" {content}")
            console.print(row)


def _print_error(title: str, message: str) -> None:
    console.print(f"[bold red]{title}:[/bold red] {message}")


def _is_github_url(text: str) -> bool:
    return "github.com/" in text.lower()


def _normalize_repo_spec(spec: str) -> tuple[str, str]:
    cleaned = spec.strip()

    if _is_github_url(cleaned):
        if cleaned.startswith("github.com/"):
            cleaned = "https://" + cleaned
        if cleaned.startswith("http://github.com/"):
            cleaned = cleaned.replace("http://", "https://", 1)
        if cleaned.startswith("https://github.com/"):
            repo_url = cleaned
        else:
            repo_url = cleaned
    else:
        if "/" in cleaned:
            repo_url = f"https://github.com/{cleaned}"
        else:
            repo_url = f"https://github.com/{DEFAULT_GITHUB_USER}/{cleaned}"

    if repo_url.endswith(".git"):
        repo_url = repo_url[:-4]

    repo_name = repo_url.rstrip("/").split("/")[-1]
    return repo_url, repo_name


def _package_install(spec: str) -> int:
    import shutil
    import urllib.request
    import zipfile

    repo_url, repo_name = _normalize_repo_spec(spec)
    libs_root = _libraries_root()
    libs_root.mkdir(parents=True, exist_ok=True)
    target_dir = libs_root / repo_name
    tmp_root = libs_root / ".tmp"
    tmp_root.mkdir(parents=True, exist_ok=True)
    tmp_path = tmp_root / repo_name

    if target_dir.exists():
        raise RuntimeError(f"Library already installed: {repo_name}")

    if tmp_path.exists():
        shutil.rmtree(tmp_path, ignore_errors=True)

    zip_path = tmp_root / f"{repo_name}.zip"
    zip_urls = [
        repo_url.rstrip("/") + "/archive/refs/heads/main.zip",
        repo_url.rstrip("/") + "/archive/refs/heads/master.zip",
    ]

    downloaded = False
    for url in zip_urls:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "nox-package-manager"})
            with urllib.request.urlopen(req, timeout=30, context=_ctx) as resp:
                with open(zip_path, "wb") as f:
                    f.write(resp.read())
            downloaded = True
            break
        except Exception:
            continue

    if not downloaded:
        raise RuntimeError("Failed to download repository (main/master not found)")

    try:
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(tmp_root)
        extracted = next(tmp_root.glob(f"{repo_name}-*"), None)
        if extracted is None or not extracted.exists():
            raise RuntimeError("Failed to extract GitHub zip")
        if tmp_path.exists():
            shutil.rmtree(tmp_path, ignore_errors=True)
        shutil.move(str(extracted), str(tmp_path))
    finally:
        if zip_path.exists():
            zip_path.unlink(missing_ok=True)

    nxinfo = tmp_path / ".nxinfo"
    if not nxinfo.exists():
        shutil.rmtree(tmp_path, ignore_errors=True)
        raise RuntimeError("Not a Nox library: .nxinfo not found")

    try:
        shutil.move(str(tmp_path), str(target_dir))
    finally:
        if tmp_path.exists():
            shutil.rmtree(tmp_path, ignore_errors=True)

    git_dir = target_dir / ".git"
    if git_dir.exists():
        shutil.rmtree(git_dir, ignore_errors=True)

    console.print(Text(f"Installed {repo_name} into {target_dir}", style="green"))
    return 0


def _package_list() -> int:
    libs_root = _libraries_root()
    if not libs_root.exists():
        console.print(Text("No libraries installed.", style="yellow"))
        return 0
    items = [p.name for p in libs_root.iterdir() if p.is_dir()]
    if not items:
        console.print(Text("No libraries installed.", style="yellow"))
        return 0
    for name in sorted(items):
        console.print(name)
    return 0


def _package_remove(name: str) -> int:
    import shutil

    libs_root = _libraries_root()
    target_dir = libs_root / name
    if not target_dir.exists():
        raise RuntimeError(f"Library not found: {name}")
    shutil.rmtree(target_dir)
    console.print(Text(f"Removed {name}", style="green"))
    return 0


def main(argv: Optional[list[str]] = None) -> int:
    import argparse
    import contextlib
    import io
    import sys

    original_cwd = Path.cwd()

    parser = argparse.ArgumentParser(prog="nox", description="Run Nox .nox scripts")
    parser.add_argument("-V", "--version", action="store_true", help="Show Nox version and exit")
    subparsers = parser.add_subparsers(dest="command")
    try:
        subparsers.required = False
    except Exception:
        pass

    run_parser = subparsers.add_parser("run", help="Run a .nox script or folder")
    run_parser.add_argument("file", help="Path to .nox file or folder")
    subparsers.add_parser("repl", help="Start the Nox REPL")

    pkg_parser = subparsers.add_parser("package", help="Manage Nox libraries")
    pkg_sub = pkg_parser.add_subparsers(dest="pkg_command")

    pkg_install = pkg_sub.add_parser("install", help="Install a library from GitHub")
    pkg_install.add_argument("spec", help="repo | user/repo | GitHub URL")

    pkg_sub.add_parser("list", help="List installed libraries")

    pkg_remove = pkg_sub.add_parser("remove", help="Remove an installed library")
    pkg_remove.add_argument("name", help="Library name")

    raw_argv = list(argv) if argv is not None else sys.argv[1:]
    if raw_argv and raw_argv[0] not in {"run", "package", "repl"} and not raw_argv[0].startswith("-"):
        raw_argv = ["run", *raw_argv]
    args = parser.parse_args(raw_argv)

    if args.version:
        console.print(f"Nox version: {_read_version_from_info_cfg()}")
        return 0

    if args.command is None:
        return _run_repl()

    if args.command == "package":
        try:
            if args.pkg_command == "install":
                return _package_install(args.spec)
            if args.pkg_command == "list":
                return _package_list()
            if args.pkg_command == "remove":
                return _package_remove(args.name)
            raise RuntimeError("Unknown package command")
        except Exception as exc:
            _print_error("RuntimeError", str(exc))
            return 3

    if args.command == "repl":
        return _run_repl()

    file_arg = args.file if args.command == "run" else None
    if file_arg is None:
        _print_error("RuntimeError", "missing script path")
        return 3

    output_buffer = io.StringIO()
    resolved_path: Path | None = None

    try:
        resolved_path = _resolve_run_target(file_arg, original_cwd)
        with contextlib.redirect_stdout(output_buffer):
            source = resolved_path.read_text(encoding="utf-8")
            run_source(source, base_dir=resolved_path.parent, current_file=resolved_path)
        sys.stdout.write(output_buffer.getvalue())
        return 0
    except KeyboardInterrupt:
        return 0
    except NoxSyntaxError as exc:
        source_path = resolved_path if resolved_path is not None else Path(file_arg)
        source = source_path.read_text(encoding="utf-8")
        lines = source.splitlines()
        err_line = exc.line
        snippet, _ = _format_code_snippet(str(source_path), err_line, context=3)
        _render_traceback_panel(str(source_path), err_line, None, snippet, err_line)
        console.print()
        _print_error("SyntaxError", str(exc))
        return 2
    except NoxRuntimeError as exc:
        err_scope: str | None = None
        if exc.stack:
            top = exc.stack[-1]
            err_line = top.line if top.line is not None else exc.line
            err_file = top.file or (str(resolved_path) if resolved_path is not None else file_arg)
            err_scope = top.name
        else:
            err_line = exc.line
            err_file = str(resolved_path) if resolved_path is not None else file_arg

        if err_file:
            snippet, _ = _format_code_snippet(err_file, err_line, context=3)
            _render_traceback_panel(err_file, err_line, err_scope, snippet, err_line)
            console.print()

        error_name = getattr(exc, "display_name", "RuntimeError")
        _print_error(error_name, str(exc))
        return 3
    except FileNotFoundError as exc:
        msg = str(exc)
        import re
        msg = re.sub(r"^\[Errno \d+\]\s*", "", msg)
        _print_error("Permission Error", msg)
        return 3
    except Exception as exc:
        _print_error("Internal Error", str(exc))
        return 1
