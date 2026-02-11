from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Any


@dataclass
class Program:
    statements: List[Stmt]


class Stmt:
    pass


@dataclass
class Assign(Stmt):
    name: str
    value: Expr


@dataclass
class Print(Stmt):
    values: List[Expr]


@dataclass
class ExprStmt(Stmt):
    expr: Expr


@dataclass
class If(Stmt):
    condition: Expr
    then_body: List[Stmt]
    elif_parts: List[tuple[Expr, List[Stmt]]]
    else_body: Optional[List[Stmt]]


@dataclass
class While(Stmt):
    condition: Expr
    body: List[Stmt]


@dataclass
class For(Stmt):
    name: str
    iterable: Expr
    body: List[Stmt]


@dataclass
class Match(Stmt):
    value: Expr
    cases: List[tuple[List[Expr], List[Stmt]]]
    otherwise: Optional[List[Stmt]]


@dataclass
class Return(Stmt):
    value: Optional[Expr]


@dataclass
class Define(Stmt):
    name: str
    params: List["Param"]
    body: List[Stmt]
    is_async: bool = False
    decorators: Optional[List["Expr"]] = None


@dataclass
class Break(Stmt):
    pass


@dataclass
class Continue(Stmt):
    pass


@dataclass
class Pass(Stmt):
    pass


@dataclass
class AssignIndex(Stmt):
    target: Expr
    index: Expr
    value: Expr


@dataclass
class RepeatTimes(Stmt):
    count: Expr
    body: List[Stmt]


@dataclass
class Try(Stmt):
    try_body: List[Stmt]
    except_body: Optional[List[Stmt]]
    finally_body: Optional[List[Stmt]]


@dataclass
class ClassDef(Stmt):
    name: str
    methods: List[Define]
    parent: Optional[str] = None
    traits: List[str] = None


@dataclass
class AssignAttr(Stmt):
    target: Expr
    name: str
    value: Expr


@dataclass
class ImportModule(Stmt):
    module: List[str]
    alias: Optional[str]


@dataclass
class ImportFrom(Stmt):
    module: List[str]
    names: List[tuple[str, Optional[str]]]


@dataclass
class TraitDef(Stmt):
    name: str
    methods: List[str]


@dataclass
class Implement(Stmt):
    trait_name: str


@dataclass
class StructDef(Stmt):
    name: str
    fields: List[str]


@dataclass
class With(Stmt):
    expr: Expr
    name: str
    body: List[Stmt]


class Expr:
    pass


@dataclass
class Binary(Expr):
    left: Expr
    op: str
    right: Expr


@dataclass
class Unary(Expr):
    op: str
    expr: Expr


@dataclass
class Literal(Expr):
    value: Any


@dataclass
class Var(Expr):
    name: str


@dataclass
class Call(Expr):
    callee: Expr
    args: List[Expr]


@dataclass
class ListLiteral(Expr):
    items: List[Expr]


@dataclass
class Index(Expr):
    target: Expr
    index: Expr


@dataclass
class Slice(Expr):
    target: Expr
    start: Optional[Expr]
    stop: Optional[Expr]
    step: Optional[Expr] = None


@dataclass
class DictLiteral(Expr):
    items: List[tuple[Expr, Expr]]


@dataclass
class SetLiteral(Expr):
    items: List[Expr]


@dataclass
class TupleLiteral(Expr):
    items: List[Expr]


@dataclass
class Lambda(Expr):
    params: List["Param"]
    body: Expr


@dataclass
class Await(Expr):
    expr: Expr


@dataclass
class Param:
    name: str
    default: Optional[Expr] = None
    is_vararg: bool = False


@dataclass
class GetAttr(Expr):
    target: Expr
    name: str


@dataclass
class StructInit(Expr):
    name: str
    fields: List[tuple[str, Expr]]
