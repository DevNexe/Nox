from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class StackFrame:
    file: str
    line: int | None
    column: int | None
    name: str


class NoxSyntaxError(Exception):
    def __init__(self, message: str, line: int | None = None, column: int | None = None) -> None:
        super().__init__(message)
        self.line = line
        self.column = column


class NoxRuntimeError(RuntimeError):
    def __init__(
        self,
        message: str,
        line: int | None = None,
        column: int | None = None,
        stack: Optional[List[StackFrame]] = None,
    ) -> None:
        super().__init__(message)
        self.line = line
        self.column = column
        self.stack = stack or []
        self.display_name = "RuntimeError"


class NoxNameError(NoxRuntimeError):
    def __init__(self, message: str, line: int | None = None, column: int | None = None, stack=None) -> None:
        super().__init__(message, line, column, stack)
        self.display_name = "NameError"


class NoxTypeError(NoxRuntimeError):
    def __init__(self, message: str, line: int | None = None, column: int | None = None, stack=None) -> None:
        super().__init__(message, line, column, stack)
        self.display_name = "TypeError"


class NoxIndexError(NoxRuntimeError):
    def __init__(self, message: str, line: int | None = None, column: int | None = None, stack=None) -> None:
        super().__init__(message, line, column, stack)
        self.display_name = "IndexError"


class NoxZeroDivisionError(NoxRuntimeError):
    def __init__(self, message: str, line: int | None = None, column: int | None = None, stack=None) -> None:
        super().__init__(message, line, column, stack)
        self.display_name = "ZeroDivisionError"


class NoxImportError(NoxRuntimeError):
    def __init__(self, message: str, line: int | None = None, column: int | None = None, stack=None) -> None:
        super().__init__(message, line, column, stack)
        self.display_name = "ImportError"
