from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .ast_nodes import (
    Assign,
    AssignAttr,
    AssignIndex,
    Await,
    Binary,
    Break,
    Call,
    ClassDef,
    Continue,
    Define,
    DictLiteral,
    Expr,
    ExprStmt,
    For,
    GetAttr,
    If,
    ImportFrom,
    ImportModule,
    Index,
    Lambda,
    ListLiteral,
    Literal,
    Match,
    Param,
    Pass,
    Print,
    Program,
    RepeatTimes,
    Return,
    SetLiteral,
    Slice,
    Stmt,
    StructDef,
    StructInit,
    TraitDef,
    Try,
    TupleLiteral,
    Unary,
    Var,
    While,
    With,
)
from .lexer import Lexer
from .parser import Parser


@dataclass
class FormatSummary:
    formatted: list[Path] = field(default_factory=list)
    unchanged: list[Path] = field(default_factory=list)
    skipped_comments: list[Path] = field(default_factory=list)


class NoxFormatter:
    def __init__(self, indent: str = "    ") -> None:
        self.indent = indent

    def format_source(self, source: str) -> str:
        tokens = Lexer(source).tokenize()
        program = Parser(tokens).parse()
        text = self._program(program)
        if not text.endswith("\n"):
            text += "\n"
        return text

    def _program(self, program: Program) -> str:
        lines: list[str] = []
        prev_block = False
        for stmt in program.statements:
            is_block = self._is_block_stmt(stmt)
            if lines and (prev_block or is_block):
                lines.append("")
            lines.extend(self._stmt(stmt, 0))
            prev_block = is_block
        return "\n".join(lines)

    def _is_block_stmt(self, stmt: Stmt) -> bool:
        return isinstance(
            stmt,
            (Define, ClassDef, StructDef, TraitDef, If, While, RepeatTimes, For, Match, Try, With),
        )

    def _stmt(self, stmt: Stmt, level: int) -> list[str]:
        pref = self.indent * level

        if isinstance(stmt, Assign):
            return [f"{pref}{stmt.name} = {self._expr(stmt.value)}"]
        if isinstance(stmt, AssignIndex):
            return [f"{pref}{self._expr(stmt.target)}[{self._expr(stmt.index)}] = {self._expr(stmt.value)}"]
        if isinstance(stmt, AssignAttr):
            return [f"{pref}{self._expr(stmt.target)}.{stmt.name} = {self._expr(stmt.value)}"]
        if isinstance(stmt, Print):
            args = ", ".join(self._expr(v) for v in stmt.values)
            return [f"{pref}display({args})"]
        if isinstance(stmt, ExprStmt):
            return [f"{pref}{self._expr(stmt.expr)}"]
        if isinstance(stmt, Return):
            if stmt.value is None:
                return [f"{pref}result"]
            return [f"{pref}result {self._expr(stmt.value)}"]
        if isinstance(stmt, Break):
            return [f"{pref}break"]
        if isinstance(stmt, Continue):
            return [f"{pref}continue"]
        if isinstance(stmt, Pass):
            return [f"{pref}pass"]
        if isinstance(stmt, ImportModule):
            module = ".".join(stmt.module)
            if stmt.alias:
                return [f"{pref}connect {module} as {stmt.alias}"]
            return [f"{pref}connect {module}"]
        if isinstance(stmt, ImportFrom):
            module = ".".join(stmt.module)
            names = []
            for name, alias in stmt.names:
                if alias:
                    names.append(f"{name} as {alias}")
                else:
                    names.append(name)
            return [f"{pref}from {module} connect {', '.join(names)}"]
        if isinstance(stmt, With):
            lines = [f"{pref}with {self._expr(stmt.expr)} as {stmt.name}:"]
            lines.extend(self._block(stmt.body, level + 1))
            return lines
        if isinstance(stmt, StructDef):
            lines = [f"{pref}struct {stmt.name}:"]
            if stmt.fields:
                for field in stmt.fields:
                    lines.append(f"{self.indent * (level + 1)}{field}: any")
            else:
                lines.append(f"{self.indent * (level + 1)}pass")
            return lines
        if isinstance(stmt, TraitDef):
            lines = [f"{pref}trait {stmt.name}:"]
            if stmt.methods:
                for method in stmt.methods:
                    lines.append(f"{self.indent * (level + 1)}define {method}():")
                    lines.append(f"{self.indent * (level + 2)}pass")
            else:
                lines.append(f"{self.indent * (level + 1)}pass")
            return lines
        if isinstance(stmt, ClassDef):
            header = f"class {stmt.name}"
            if stmt.parent:
                header += f"({stmt.parent})"
            header += ":"
            lines = [pref + header]
            if stmt.traits:
                for trait in stmt.traits:
                    lines.append(f"{self.indent * (level + 1)}implement {trait}")
            if stmt.methods:
                for i, method in enumerate(stmt.methods):
                    if i > 0:
                        lines.append("")
                    lines.extend(self._stmt(method, level + 1))
            if not stmt.methods and not stmt.traits:
                lines.append(f"{self.indent * (level + 1)}pass")
            return lines
        if isinstance(stmt, Define):
            lines: list[str] = []
            for dec in stmt.decorators or []:
                lines.append(f"{pref}@{self._expr(dec)}")
            async_head = "async " if stmt.is_async else ""
            params = ", ".join(self._param(p) for p in stmt.params)
            lines.append(f"{pref}{async_head}define {stmt.name}({params}):")
            lines.extend(self._block(stmt.body, level + 1))
            return lines
        if isinstance(stmt, If):
            lines = [f"{pref}if {self._expr(stmt.condition)}:"]
            lines.extend(self._block(stmt.then_body, level + 1))
            for cond, body in stmt.elif_parts:
                lines.append(f"{pref}else if {self._expr(cond)}:")
                lines.extend(self._block(body, level + 1))
            if stmt.else_body is not None:
                lines.append(f"{pref}else:")
                lines.extend(self._block(stmt.else_body, level + 1))
            return lines
        if isinstance(stmt, While):
            lines = [f"{pref}repeat {self._expr(stmt.condition)}:"]
            lines.extend(self._block(stmt.body, level + 1))
            return lines
        if isinstance(stmt, RepeatTimes):
            lines = [f"{pref}repeat times {self._expr(stmt.count)}:"]
            lines.extend(self._block(stmt.body, level + 1))
            return lines
        if isinstance(stmt, For):
            lines = [f"{pref}for {stmt.name} in {self._expr(stmt.iterable)}:"]
            lines.extend(self._block(stmt.body, level + 1))
            return lines
        if isinstance(stmt, Match):
            lines = [f"{pref}match {self._expr(stmt.value)}:"]
            for patterns, body in stmt.cases:
                pats = ", ".join(self._expr(p) for p in patterns)
                lines.append(f"{self.indent * (level + 1)}case {pats}:")
                lines.extend(self._block(body, level + 2))
            if stmt.otherwise is not None:
                lines.append(f"{self.indent * (level + 1)}else:")
                lines.extend(self._block(stmt.otherwise, level + 2))
            return lines
        if isinstance(stmt, Try):
            lines = [f"{pref}try:"]
            lines.extend(self._block(stmt.try_body, level + 1))
            if stmt.except_body is not None:
                lines.append(f"{pref}except:")
                lines.extend(self._block(stmt.except_body, level + 1))
            if stmt.finally_body is not None:
                lines.append(f"{pref}finally:")
                lines.extend(self._block(stmt.finally_body, level + 1))
            return lines

        raise RuntimeError(f"Unsupported statement for formatter: {type(stmt).__name__}")

    def _block(self, statements: list[Stmt], level: int) -> list[str]:
        if not statements:
            return [f"{self.indent * level}pass"]
        lines: list[str] = []
        prev_block = False
        for stmt in statements:
            is_block = self._is_block_stmt(stmt)
            if lines and (prev_block or is_block):
                lines.append("")
            lines.extend(self._stmt(stmt, level))
            prev_block = is_block
        return lines

    def _param(self, p: Param) -> str:
        head = f"*{p.name}" if p.is_vararg else p.name
        if p.default is not None:
            return f"{head} = {self._expr(p.default)}"
        return head

    def _expr(self, expr: Expr, min_prec: int = 0) -> str:
        if isinstance(expr, Literal):
            return self._literal(expr.value)
        if isinstance(expr, Var):
            return expr.name
        if isinstance(expr, Lambda):
            params = ", ".join(self._param(p) for p in expr.params)
            return f"lambda {params}: {self._expr(expr.body)}"
        if isinstance(expr, Await):
            body = self._expr(expr.expr, 7)
            out = f"await {body}"
            if min_prec > 7:
                return f"({out})"
            return out
        if isinstance(expr, Unary):
            right = self._expr(expr.expr, 7)
            if expr.op == "not":
                out = f"not {right}"
            else:
                out = f"{expr.op}{right}"
            if min_prec > 7:
                return f"({out})"
            return out
        if isinstance(expr, Binary):
            prec = self._bin_prec(expr.op)
            left = self._expr(expr.left, prec)
            right = self._expr(expr.right, prec + 1)
            out = f"{left} {expr.op} {right}"
            if prec < min_prec:
                return f"({out})"
            return out
        if isinstance(expr, Call):
            callee = self._expr(expr.callee, 8)
            args = ", ".join(self._expr(a) for a in expr.args)
            return f"{callee}({args})"
        if isinstance(expr, GetAttr):
            return f"{self._expr(expr.target, 8)}.{expr.name}"
        if isinstance(expr, Index):
            return f"{self._expr(expr.target, 8)}[{self._expr(expr.index)}]"
        if isinstance(expr, Slice):
            start = self._expr(expr.start) if expr.start is not None else ""
            stop = self._expr(expr.stop) if expr.stop is not None else ""
            if expr.step is None:
                return f"{self._expr(expr.target, 8)}[{start}:{stop}]"
            step = self._expr(expr.step)
            return f"{self._expr(expr.target, 8)}[{start}:{stop}:{step}]"
        if isinstance(expr, ListLiteral):
            return f"[{', '.join(self._expr(i) for i in expr.items)}]"
        if isinstance(expr, SetLiteral):
            return f"{{{', '.join(self._expr(i) for i in expr.items)}}}"
        if isinstance(expr, DictLiteral):
            parts = [f"{self._expr(k)}: {self._expr(v)}" for k, v in expr.items]
            return f"{{{', '.join(parts)}}}"
        if isinstance(expr, TupleLiteral):
            if not expr.items:
                return "()"
            if len(expr.items) == 1:
                return f"({self._expr(expr.items[0])},)"
            return f"({', '.join(self._expr(i) for i in expr.items)})"
        if isinstance(expr, StructInit):
            fields = ", ".join(f"{name}: {self._expr(value)}" for name, value in expr.fields)
            return f"{expr.name}{{{fields}}}"
        raise RuntimeError(f"Unsupported expression for formatter: {type(expr).__name__}")

    def _bin_prec(self, op: str) -> int:
        if op == "or":
            return 1
        if op == "and":
            return 2
        if op in {"==", "!="}:
            return 3
        if op in {"<", "<=", ">", ">="}:
            return 4
        if op in {"+", "-"}:
            return 5
        if op in {"*", "/"}:
            return 6
        return 0

    def _literal(self, value: object) -> str:
        if value is True:
            return "true"
        if value is False:
            return "false"
        if value is None:
            return "none"
        if isinstance(value, str):
            return self._quote(value)
        return str(value)

    def _quote(self, text: str) -> str:
        escaped = (
            text.replace("\\", "\\\\")
            .replace('"', '\\"')
            .replace("\n", "\\n")
            .replace("\t", "\\t")
        )
        return f'"{escaped}"'


def _has_comment_outside_strings(source: str) -> bool:
    i = 0
    n = len(source)
    in_string = False
    in_triple = False
    while i < n:
        ch = source[i]
        if not in_string:
            if ch == '"':
                if i + 2 < n and source[i : i + 3] == '"""':
                    in_string = True
                    in_triple = True
                    i += 3
                    continue
                in_string = True
                in_triple = False
                i += 1
                continue
            if ch == "#":
                return True
            i += 1
            continue

        if ch == "\\" and not in_triple:
            i += 2
            continue
        if in_triple:
            if i + 2 < n and source[i : i + 3] == '"""':
                in_string = False
                in_triple = False
                i += 3
                continue
            i += 1
            continue
        if ch == '"':
            in_string = False
            i += 1
            continue
        i += 1
    return False


def _collect_targets(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    if path.is_dir():
        return sorted(p for p in path.rglob("*.nox") if p.is_file())
    return []


def format_targets(targets: list[str]) -> FormatSummary:
    formatter = NoxFormatter()
    summary = FormatSummary()

    seen: set[Path] = set()
    all_targets: list[Path] = []
    for raw in targets:
        p = Path(raw).resolve()
        for item in _collect_targets(p):
            key = item.resolve()
            if key not in seen:
                seen.add(key)
                all_targets.append(key)

    for path in all_targets:
        source = path.read_text(encoding="utf-8")
        if _has_comment_outside_strings(source):
            summary.skipped_comments.append(path)
            continue
        formatted = formatter.format_source(source)
        if formatted == source:
            summary.unchanged.append(path)
            continue
        path.write_text(formatted, encoding="utf-8")
        summary.formatted.append(path)

    return summary

