from __future__ import annotations

import ssl as _ssl
import re
import sys
import urllib.request
from pathlib import Path

from rich.console import Console
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    ProgressColumn,
    Task,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)
from rich.text import Text

_ctx = _ssl.create_default_context()
_ctx.check_hostname = False
_ctx.verify_mode = _ssl.CERT_NONE

DEFAULT_GITHUB_USER = "devnexe-alt"
LIBRARIES_DIRNAME = "Libraries"
FORBIDDEN_NAME_PARTS = ("devnexe", "devnexe-alt")
FORBIDDEN_EXACT_NAMES = ("nox",)


def _create_console() -> Console:
    import os

    force_ascii = os.getenv("Nox_ASCII", "").lower() in {"1", "true", "yes"}
    if force_ascii:
        return Console(legacy_windows=True, force_terminal=True, color_system="standard")
    return Console(force_terminal=True, color_system="truecolor")


console = _create_console()


class _CurrentSizeColumn(ProgressColumn):
    def render(self, task: Task) -> Text:
        value = task.completed / 1024
        return Text(f"{value:.1f} kB", style="cyan")


class _SpeedColumn(ProgressColumn):
    def render(self, task: Task) -> Text:
        speed = task.speed
        if speed is None or speed <= 0:
            return Text("0.0 kB/s", style="green")
        kb = speed / 1024
        if kb < 1024:
            return Text(f"{kb:.1f} kB/s", style="green")
        return Text(f"{kb / 1024:.1f} MB/s", style="green")


def libraries_root() -> Path:
    exe = Path(sys.argv[0]).resolve()
    if exe.suffix in (".exe",) or (not exe.suffix and exe.stat().st_mode & 0o111):
        return exe.parent / LIBRARIES_DIRNAME
    return Path(__file__).resolve().parent.parent / LIBRARIES_DIRNAME


def _is_github_url(text: str) -> bool:
    return "github.com/" in text.lower()


def _normalize_repo_spec(spec: str) -> tuple[str, str]:
    cleaned = spec.strip()

    if _is_github_url(cleaned):
        if cleaned.startswith("github.com/"):
            cleaned = "https://" + cleaned
        if cleaned.startswith("http://github.com/"):
            cleaned = cleaned.replace("http://", "https://", 1)
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


def _read_simple_config(path: Path) -> dict[str, str]:
    def _strip_inline_comment(text: str) -> str:
        in_single = False
        in_double = False
        escaped = False
        for idx, ch in enumerate(text):
            if escaped:
                escaped = False
                continue
            if ch == "\\":
                escaped = True
                continue
            if ch == "'" and not in_double:
                in_single = not in_single
                continue
            if ch == '"' and not in_single:
                in_double = not in_double
                continue
            if ch == "#" and not in_single and not in_double:
                return text[:idx].rstrip()
        return text.rstrip()

    data: dict[str, str] = {}
    try:
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = _strip_inline_comment(raw).strip()
            if not line or line.startswith("#") or line.startswith(";"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
            elif ":" in line:
                key, value = line.split(":", 1)
            else:
                continue
            data[key.strip().lower()] = value.strip().strip("'\"")
    except OSError:
        pass
    return data


def _parse_dependency_list(raw: str | None) -> list[str]:
    if not raw:
        return []
    normalized = raw.replace("\r", "\n").replace(",", "\n").replace(";", "\n")
    items = [item.strip() for item in normalized.splitlines()]
    return [item for item in items if item]


def _dependency_specs(meta: dict[str, str]) -> list[str]:
    return _parse_dependency_list(meta.get("depends") or meta.get("dependencies") or meta.get("requires"))


def _maybe_read_text_ref(base_dir: Path, value: str | None) -> str | None:
    if not value:
        return None
    candidate = (base_dir / value).resolve()
    try:
        if candidate.exists() and candidate.is_file():
            return candidate.read_text(encoding="utf-8")
    except OSError:
        pass
    return value


def _resolved_description(base_dir: Path, meta: dict[str, str]) -> str | None:
    raw = _maybe_read_text_ref(base_dir, meta.get("description"))
    if raw is None:
        return None

    text = raw.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"!\[[^\]]*\]\([^)]+\)", "", text)
    text = re.sub(r"<img\b[^>]*>", "", text, flags=re.IGNORECASE)
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"^\s{0,3}#{1,6}\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s{0,3}>\s?", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.MULTILINE)
    text = re.sub(r"[*_~]+", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = "\n".join(line.strip() for line in text.splitlines())
    text = "\n".join(line for line in text.splitlines() if line)
    text = text.strip()
    return text or None


def _resolved_dependencies(base_dir: Path, meta: dict[str, str]) -> list[str]:
    raw = meta.get("depends") or meta.get("dependencies") or meta.get("requires")
    resolved = _maybe_read_text_ref(base_dir, raw)
    return _parse_dependency_list(resolved)


def _validate_entry_file(base_dir: Path, meta: dict[str, str]) -> Path:
    entry = meta.get("entry")
    if not entry:
        raise RuntimeError("Library .nxinfo must declare entry")
    entry_path = (base_dir / entry).resolve()
    if not entry_path.exists() or not entry_path.is_file():
        raise RuntimeError(f"Library entry file not found: {entry}")
    return entry_path


def _parse_version_tuple(raw: str) -> tuple[int, ...]:
    parts: list[int] = []
    current = ""
    for ch in raw:
        if ch.isdigit():
            current += ch
            continue
        if current:
            parts.append(int(current))
            current = ""
    if current:
        parts.append(int(current))
    return tuple(parts)


def _current_nox_version() -> str:
    info_path = Path(__file__).resolve().parent / "info.cfg"
    meta = _read_simple_config(info_path)
    return meta.get("version", "unknown")


def _validate_library_name(name: str, source: str) -> None:
    normalized = name.strip().lower()
    if not normalized:
        raise RuntimeError(f"Invalid empty library name in {source}")
    if normalized in FORBIDDEN_EXACT_NAMES:
        raise RuntimeError(f"Forbidden library name '{name}' in {source}")
    for part in FORBIDDEN_NAME_PARTS:
        if part in normalized:
            raise RuntimeError(f"Forbidden library name '{name}' in {source}")


def _validate_nox_version(meta: dict[str, str]) -> None:
    current_raw = _current_nox_version()
    current = _parse_version_tuple(current_raw)
    if not current:
        return

    exact_raw = meta.get("nox_version") or meta.get("nox-version")
    min_raw = meta.get("min_nox_version") or meta.get("min-nox-version")
    max_raw = meta.get("max_nox_version") or meta.get("max-nox-version")
    requires_raw = meta.get("nox_requires") or meta.get("nox-requires")

    if requires_raw:
        parts = [part.strip() for part in requires_raw.replace(";", ",").split(",") if part.strip()]
        for part in parts:
            if part.startswith(">="):
                min_raw = part[2:].strip()
            elif part.startswith("<="):
                max_raw = part[2:].strip()
            elif part.startswith("=="):
                exact_raw = part[2:].strip()
            elif part.startswith("="):
                exact_raw = part[1:].strip()

    if exact_raw:
        exact = _parse_version_tuple(exact_raw)
        if exact and current != exact:
            raise RuntimeError(
                f"Library requires Nox version {exact_raw}, current version is {current_raw}"
            )

    if min_raw:
        minimum = _parse_version_tuple(min_raw)
        if minimum and current < minimum:
            raise RuntimeError(
                f"Library requires Nox >= {min_raw}, current version is {current_raw}"
            )

    if max_raw:
        maximum = _parse_version_tuple(max_raw)
        if maximum and current > maximum:
            raise RuntimeError(
                f"Library requires Nox <= {max_raw}, current version is {current_raw}"
            )


def _download_with_progress(label: str, url: str, destination: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "nox-package-manager"})
    with urllib.request.urlopen(req, timeout=30, context=_ctx) as resp:
        total_header = resp.headers.get("Content-Length")
        total = int(total_header) if total_header and total_header.isdigit() else None
        with destination.open("wb") as f:
            if total is None:
                progress = Progress(
                    TextColumn("[bold yellow]Collecting[/bold yellow] [bold]{task.fields[label]}[/bold] [dim]-------------------------------------[/dim]"),
                    _CurrentSizeColumn(),
                    _SpeedColumn(),
                    console=console,
                    transient=False,
                )
            else:
                progress = Progress(
                    TextColumn("[bold yellow]Collecting[/bold yellow] [bold]{task.fields[label]}[/bold]"),
                    BarColumn(bar_width=37),
                    DownloadColumn(),
                    TransferSpeedColumn(),
                    TimeRemainingColumn(),
                    console=console,
                    transient=False,
                )
            with progress:
                task_id = progress.add_task("download", total=total, label=label)
                while True:
                    chunk = resp.read(64 * 1024)
                    if not chunk:
                        break
                    f.write(chunk)
                    progress.update(task_id, advance=len(chunk))


def _format_installed_label(name: str, version: str | None) -> str:
    if version:
        return f"{name} {version}"
    return name


def _read_installed_meta(target_dir: Path) -> tuple[str, str | None]:
    meta = _read_simple_config(target_dir / ".nxinfo")
    return meta.get("name") or target_dir.name, meta.get("version")


def _install_dependencies(
    base_dir: Path,
    meta: dict[str, str],
    seen: set[str],
    stack: list[str],
    session: dict[str, object],
) -> None:
    deps = _resolved_dependencies(base_dir, meta)
    if not deps:
        return

    session["has_dependencies"] = True
    for dep in deps:
        _install_recursive(dep, seen, stack, session)


def _install_recursive(spec: str, seen: set[str], stack: list[str], session: dict[str, object]) -> int:
    import shutil
    import zipfile

    repo_url, repo_name = _normalize_repo_spec(spec)
    _validate_library_name(repo_name, "repository name")
    stack_key = repo_url.lower()
    if stack_key in stack:
        cycle = " -> ".join([*stack, stack_key])
        raise RuntimeError(f"Cyclic library dependency detected: {cycle}")
    if stack_key in seen:
        return 0

    libs_root = libraries_root()
    libs_root.mkdir(parents=True, exist_ok=True)
    target_dir = libs_root / repo_name
    tmp_root = libs_root / ".tmp"
    tmp_root.mkdir(parents=True, exist_ok=True)
    tmp_path = tmp_root / repo_name

    if target_dir.exists():
        seen.add(stack_key)
        display_name, version = _read_installed_meta(target_dir)
        suffix = f" ({version})" if version else ""
        console.print(
            f"[green]Requirement already satisfied:[/green] [bold]{display_name}[/bold] "
            f"[cyan]in[/cyan] [dim]{target_dir}[/dim]{suffix}"
        )
        return 0

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
            _download_with_progress(repo_name, url, zip_path)
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

    meta = _read_simple_config(nxinfo)
    display_name = meta.get("name") or repo_name
    version = meta.get("version")
    _validate_library_name(display_name, ".nxinfo")
    _validate_nox_version(meta)
    _validate_entry_file(tmp_path, meta)

    stack.append(stack_key)
    try:
        shutil.move(str(tmp_path), str(target_dir))
        git_dir = target_dir / ".git"
        if git_dir.exists():
            shutil.rmtree(git_dir, ignore_errors=True)

        installed = session.setdefault("installed", [])
        if isinstance(installed, list):
            installed.append((display_name, version))

        _install_dependencies(target_dir, meta, seen, stack, session)
        seen.add(stack_key)
        return 0
    finally:
        if tmp_path.exists():
            shutil.rmtree(tmp_path, ignore_errors=True)
        if stack and stack[-1] == stack_key:
            stack.pop()


def install(specs: str | list[str]) -> int:
    if isinstance(specs, str):
        spec_list = [specs]
    else:
        spec_list = list(specs)

    session: dict[str, object] = {"installed": [], "has_dependencies": False}
    seen: set[str] = set()
    result = 0
    for spec in spec_list:
        result = _install_recursive(spec, seen, [], session)

    installed = session.get("installed", [])
    if isinstance(installed, list) and installed:
        names = ", ".join(name for name, _version in installed)
        labels = ", ".join(_format_installed_label(name, version) for name, version in installed)
        console.print(f"[bold blue]Installing[/bold blue] [bold]{names}[/bold]")
        console.print()
        if bool(session.get("has_dependencies")):
            console.print("[bold magenta]Resolving dependencies ...[/bold magenta]")
            console.print()
        console.print(f"[bold green]Successfully installed[/bold green] [bold]{labels}[/bold]")

    return result


def _find_installed_package_dir(name: str) -> Path:
    libs_root = libraries_root()
    if not libs_root.exists():
        raise RuntimeError("No libraries installed.")

    direct = libs_root / name
    if direct.exists() and direct.is_dir():
        return direct

    normalized = name.strip().lower()
    for candidate in libs_root.iterdir():
        if not candidate.is_dir():
            continue
        meta = _read_simple_config(candidate / ".nxinfo")
        display_name = meta.get("name", candidate.name).strip().lower()
        if candidate.name.lower() == normalized or display_name == normalized:
            return candidate

    raise RuntimeError(f"Library not found: {name}")


def list_packages() -> int:
    libs_root = libraries_root()
    if not libs_root.exists():
        console.print(Text("No libraries installed.", style="yellow"))
        return 0
    items = [p.name for p in libs_root.iterdir() if p.is_dir() and not p.name.startswith(".")]
    if not items:
        console.print(Text("No libraries installed.", style="yellow"))
        return 0
    for name in sorted(items):
        nxinfo = libs_root / name / ".nxinfo"
        meta = _read_simple_config(nxinfo)
        display_name = meta.get("name") or name
        version = meta.get("version")
        deps = _resolved_dependencies(libs_root / name, meta)
        tail_parts: list[str] = []
        for key in ("author", "license", "homepage", "author_email"):
            value = meta.get(key)
            if value:
                tail_parts.append(value)
        line = display_name
        if version:
            line += f" {version}"
        if tail_parts:
            line += f" - {' | '.join(tail_parts)}"
        if deps:
            line += f" [depends: {', '.join(deps)}]"
        console.print(line)
    return 0


def description(name: str) -> int:
    package_dir = _find_installed_package_dir(name)
    meta = _read_simple_config(package_dir / ".nxinfo")
    display_name = meta.get("name") or package_dir.name
    version = meta.get("version")
    desc = _resolved_description(package_dir, meta)

    header = display_name
    if version:
        header += f" {version}"
    console.print(header)

    if desc:
        console.print()
        console.print(desc)
    else:
        console.print()
        console.print(Text("No description.", style="yellow"))

    tail_parts: list[str] = []
    for key in ("author", "license", "homepage", "author_email"):
        value = meta.get(key)
        if value:
            tail_parts.append(f"{key}: {value}")
    if tail_parts:
        console.print()
        for item in tail_parts:
            console.print(item)

    deps = _resolved_dependencies(package_dir, meta)
    if deps:
        console.print()
        console.print(f"depends: {', '.join(deps)}")

    entry = meta.get("entry")
    if entry:
        console.print(f"entry: {entry}")

    return 0


def remove(name: str) -> int:
    import shutil

    libs_root = libraries_root()
    target_dir = libs_root / name
    if not target_dir.exists():
        raise RuntimeError(f"Library not found: {name}")
    shutil.rmtree(target_dir)
    console.print(Text(f"Removed {name}", style="green"))
    return 0
