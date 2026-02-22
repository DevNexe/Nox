from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any


class TokenType(Enum):
    EOF = auto()
    NEWLINE = auto()
    INDENT = auto()
    DEDENT = auto()

    IDENT = auto()
    NUMBER = auto()
    STRING = auto()

    TRUE = auto()
    FALSE = auto()
    IF = auto()
    ELSE = auto()
    REPEAT = auto()
    NOT = auto()
    AND = auto()
    OR = auto()
    DEFINE = auto()
    RETURN = auto()
    FOR = auto()
    IN = auto()
    MATCH = auto()
    CASE = auto()
    BREAK = auto()
    CONTINUE = auto()
    PASS = auto()
    TIMES = auto()
    CONNECT = auto()
    FROM = auto()
    AS = auto()
    LAMBDA = auto()
    TRAIT = auto()
    IMPLEMENT = auto()
    ASYNC = auto()
    AWAIT = auto()
    STRUCT = auto()
    WITH = auto()
    TRY = auto()
    EXCEPT = auto()
    FINALLY = auto()
    CLASS = auto()
    PRINT = auto()
    INPUT = auto()
    LEN = auto()
    NONE = auto()

    PLUS = auto()
    MINUS = auto()
    STAR = auto()
    SLASH = auto()

    EQ = auto()
    EQEQ = auto()
    NEQ = auto()
    LT = auto()
    LTE = auto()
    GT = auto()
    GTE = auto()

    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    COLON = auto()
    COMMA = auto()
    DOT = auto()
    AT = auto()


@dataclass(frozen=True)
class Token:
    type: TokenType
    value: Any
    line: int
    column: int

    def __repr__(self) -> str:
        return f"Token({self.type}, {self.value}, {self.line}:{self.column})"
