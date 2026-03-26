"""Nox package."""

from pathlib import Path

__all__ = ["lexer", "parser", "interpreter", "ast_nodes"]


def _read_version() -> str:
    info_path = Path(__file__).resolve().parent / "info.cfg"
    try:
        for raw in info_path.read_text(encoding="utf-8").splitlines():
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
    except OSError:
        pass
    return "unknown"


__version__ = _read_version()
