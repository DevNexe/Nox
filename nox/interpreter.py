from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable
import threading
import urllib.request
import urllib.error
import sys
import urllib.parse
import json

from .ast_nodes import (
    Assign,
    AssignIndex,
    AssignAttr,
    Binary,
    Break,
    Call,
    ClassDef,
    TraitDef,
    Implement,
    StructDef,
    With,
    Continue,
    Pass,
    Define,
    Param,
    Expr,
    ExprStmt,
    For,
    GetAttr,
    If,
    ImportFrom,
    ImportModule,
    Index,
    Slice,
    ListLiteral,
    DictLiteral,
    SetLiteral,
    TupleLiteral,
    Lambda,
    Await,
    Literal,
    Match,
    Print,
    Program,
    RepeatTimes,
    Return,
    Try,
    Stmt,
    Unary,
    Var,
    While,
    StructInit,
    ExprStmt,
)
from .errors import (
    NoxRuntimeError,
    NoxNameError,
    NoxTypeError,
    NoxIndexError,
    NoxZeroDivisionError,
    NoxImportError,
    NoxSyntaxError,
    StackFrame,
)
from .jit import jit, NUMBA_AVAILABLE


@jit
def _add_num(a: float, b: float) -> float:
    return a + b


@jit
def _sub_num(a: float, b: float) -> float:
    return a - b


@jit
def _mul_num(a: float, b: float) -> float:
    return a * b


@jit
def _div_num(a: float, b: float) -> float:
    return a / b


@jit
def _lt_num(a: float, b: float) -> bool:
    return a < b


@jit
def _lte_num(a: float, b: float) -> bool:
    return a <= b


@jit
def _gt_num(a: float, b: float) -> bool:
    return a > b


@jit
def _gte_num(a: float, b: float) -> bool:
    return a >= b


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _get_libraries_root():
    exe = Path(sys.argv[0]).resolve()
    if exe.suffix in (".exe",) or (not exe.suffix and exe.stat().st_mode & 0o111):
        path = exe.parent / "Libraries"
    else:
        path = Path(__file__).resolve().parent.parent / "Libraries"
    return path

@dataclass
class Environment:
    values: Dict[str, Any]
    parent: Optional["Environment"] = None

    def get(self, name: str) -> Any:
        if name in self.values:
            return self.values[name]
        if self.parent is not None:
            return self.parent.get(name)
        raise NameError(f"Undefined variable '{name}'")

    def set(self, name: str, value: Any) -> None:
        self.values[name] = value


@dataclass
class Function:
    name: str
    params: List[Param]
    body: List[Stmt]
    closure: Environment
    is_async: bool = False
    file: Optional[str] = None
    line: Optional[int] = None
    column: Optional[int] = None

    def call(self, interpreter: "Interpreter", args: List[Any]) -> Any:
        local = Environment(values={}, parent=self.closure)
        bound = interpreter._bind_args(self.params, args, local)
        for name, value in bound.items():
            local.set(name, value)
        result = interpreter._exec_function_body(self.body, local)
        if self.is_async:
            return AsyncResult(result)
        return result


@dataclass
class Class:
    name: str
    methods: Dict[str, Function]
    parent: Optional["Class"] = None
    traits: List[str] = None

    def call(self, interpreter: "Interpreter", args: List[Any]) -> Any:
        instance = Instance(self)
        init = self.methods.get("init")
        if init is None and self.parent is not None:
            init = self.parent.methods.get("init")
        if init is not None:
            bound = BoundMethod(init, instance)
            bound.call(interpreter, args)
        elif args:
            raise RuntimeError(f"Class '{self.name}' does not take arguments")
        return instance

    def get_method(self, name: str) -> Optional[Function]:
        if name in self.methods:
            return self.methods[name]
        if self.parent is not None:
            return self.parent.get_method(name)
        return None


@dataclass
class Instance:
    klass: Class
    fields: Dict[str, Any] = None

    def __post_init__(self) -> None:
        if self.fields is None:
            self.fields = {}

    def get(self, name: str) -> Any:
        if name in self.fields:
            return self.fields[name]
        method = self.klass.get_method(name)
        if method is not None:
            return BoundMethod(method, self)
        raise RuntimeError(f"Undefined property '{name}'")

    def set(self, name: str, value: Any) -> None:
        self.fields[name] = value


@dataclass
class BoundMethod:
    function: Function
    instance: Instance

    def call(self, interpreter: "Interpreter", args: List[Any]) -> Any:
        return self.function.call(interpreter, [self.instance] + args)


@dataclass
class Trait:
    name: str
    methods: List[str]


@dataclass
class AsyncResult:
    value: Any


class Task:
    def __init__(self, worker: Callable[[], Any]) -> None:
        self._done = threading.Event()
        self._result: Any = None
        self._error: Optional[BaseException] = None

        def _run() -> None:
            try:
                self._result = worker()
            except BaseException as exc:
                self._error = exc
            finally:
                self._done.set()

        self._thread = threading.Thread(target=_run, daemon=True)
        self._thread.start()

    def done(self) -> bool:
        return self._done.is_set()

    def result(self, timeout_ms: Optional[int] = None) -> Any:
        timeout = None if timeout_ms is None else timeout_ms / 1000.0
        finished = self._done.wait(timeout)
        if not finished:
            raise RuntimeError("Task timeout")
        if self._error is not None:
            raise self._error
        return self._result


@dataclass
class StructType:
    name: str
    fields: List[str]

    def call(self, interpreter: "Interpreter", args: List[Any]) -> Any:
        if args:
            raise RuntimeError("Struct constructor does not take positional args")
        return StructInstance(self)


@dataclass
class StructInstance:
    struct: StructType
    fields: Dict[str, Any] = None

    def __post_init__(self) -> None:
        if self.fields is None:
            self.fields = {name: None for name in self.struct.fields}

    def get(self, name: str) -> Any:
        if name in self.fields:
            return self.fields[name]
        raise RuntimeError(f"Undefined field '{name}'")

    def set(self, name: str, value: Any) -> None:
        if name not in self.fields:
            raise RuntimeError(f"Unknown field '{name}'")
        self.fields[name] = value


@dataclass
class Module:
    name: str
    values: Dict[str, Any]

    def get(self, name: str) -> Any:
        if name in self.values:
            return self.values[name]
        raise RuntimeError(f"Undefined module attribute '{name}'")


def _module(name: str, values: Dict[str, Any]) -> Module:
    return Module(name, values)


class ReturnSignal(Exception):
    def __init__(self, value: Any) -> None:
        self.value = value


class BreakSignal(Exception):
    pass


class ContinueSignal(Exception):
    pass


class Interpreter:
    def __init__(
        self,
        base_dir: Optional[Path] = None,
        module_cache: Optional[Dict[str, Module]] = None,
        current_file: Optional[Path] = None,
    ) -> None:
        self.base_dir = base_dir
        self.current_file = current_file
        self.module_cache = module_cache if module_cache is not None else {}
        self.builtins = {
            "input": lambda: input(),
            "len": lambda x: len(x),
            "range": self._builtin_range,
            "sleep": self._builtin_sleep,
            "open": self._builtin_open,
            "create_task": self._builtin_create_task,
            "gather": self._builtin_gather,
            "run_async": self._builtin_run_async,
            "none": None,
        }
        self.env = Environment(values=dict(self.builtins))
        self.call_stack: List[StackFrame] = []
        self.module_line: Optional[int] = None
        self.module_column: Optional[int] = None
        self.traits: Dict[str, Trait] = {}
        self._install_stdlib()

    def run(self, program: Program) -> None:
        for stmt in program.statements:
            self._exec_with_loc(stmt)

    def run_repl(self, program: Program) -> Any:
        result: Any = None
        for stmt in program.statements:
            if isinstance(stmt, ExprStmt):
                result = self._eval(stmt.expr)
            else:
                self._exec_with_loc(stmt)
                result = None
        return result

    def _resolve_fs_path(self, path: str) -> Path:
        p = Path(path)
        if p.is_absolute():
            return p
        if self.base_dir:
            candidate = self.base_dir / p
            if candidate.exists():
                return candidate
        exe = Path(sys.argv[0]).resolve()
        if exe.suffix in (".exe",) or (not exe.suffix and exe.stat().st_mode & 0o111):
            candidate = exe.parent / p
        else:
            candidate = Path(__file__).resolve().parent.parent / p
        if candidate.exists():
            return candidate
        if self.base_dir:
            return self.base_dir / p
        return p

    def _exec(self, stmt: Stmt) -> None:
        if isinstance(stmt, Assign):
            value = self._eval(stmt.value)
            self.env.set(stmt.name, value)
            return
        if isinstance(stmt, AssignIndex):
            target = self._eval(stmt.target)
            index = self._eval(stmt.index)
            value = self._eval(stmt.value)
            target[index] = value
            return
        if isinstance(stmt, AssignAttr):
            target = self._eval(stmt.target)
            value = self._eval(stmt.value)
            if isinstance(target, Instance):
                target.set(stmt.name, value)
                return
            if isinstance(target, StructInstance):
                target.set(stmt.name, value)
                return
            raise RuntimeError("Attribute assignment only works on class instances")
            return
        if isinstance(stmt, Print):
            values = [self._eval(expr) for expr in stmt.values]
            print(*values)
            return
        if isinstance(stmt, ExprStmt):
            self._eval(stmt.expr)
            return
        if isinstance(stmt, Define):
            func = Function(stmt.name, stmt.params, stmt.body, self.env, is_async=stmt.is_async)
            func.file = str(self.current_file) if self.current_file is not None else None
            func.line = getattr(stmt, "line", None)
            func.column = getattr(stmt, "column", None)
            decorated: Any = func
            if stmt.decorators:
                for decorator_expr in reversed(stmt.decorators):
                    decorator = self._eval(decorator_expr)
                    decorated = self._apply_decorator(decorator, decorated, decorator_expr)
            self.env.set(stmt.name, decorated)
            return
        if isinstance(stmt, StructDef):
            self.env.set(stmt.name, StructType(stmt.name, stmt.fields))
            return
        if isinstance(stmt, With):
            resource = self._eval(stmt.expr)
            if hasattr(resource, "close") and callable(getattr(resource, "close")):
                try:
                    self.env.set(stmt.name, resource)
                    self._exec_block(stmt.body)
                finally:
                    resource.close()
            else:
                self.env.set(stmt.name, resource)
                self._exec_block(stmt.body)
            return
        if isinstance(stmt, TraitDef):
            self.traits[stmt.name] = Trait(stmt.name, stmt.methods)
            return
        if isinstance(stmt, ClassDef):
            methods: Dict[str, Function] = {}
            for method in stmt.methods:
                fn = Function(method.name, method.params, method.body, self.env, is_async=method.is_async)
                fn.file = str(self.current_file) if self.current_file is not None else None
                fn.line = getattr(method, "line", None)
                fn.column = getattr(method, "column", None)
                methods[method.name] = fn
            parent = self.env.get(stmt.parent) if stmt.parent else None
            if parent is not None and not isinstance(parent, Class):
                raise RuntimeError("Parent must be a class")
            klass = Class(stmt.name, methods, parent=parent, traits=stmt.traits or [])
            self._validate_traits(klass)
            self.env.set(stmt.name, klass)
            return
        if isinstance(stmt, ImportModule):
            module = self._load_module(stmt.module)
            name = stmt.alias if stmt.alias is not None else stmt.module[-1]
            self.env.set(name, module)
            return
        if isinstance(stmt, ImportFrom):
            module = self._load_module(stmt.module)
            for name, alias in stmt.names:
                value = module.get(name)
                self.env.set(alias if alias is not None else name, value)
            return
        if isinstance(stmt, Return):
            value = self._eval(stmt.value) if stmt.value is not None else None
            raise ReturnSignal(value)
        if isinstance(stmt, Break):
            raise BreakSignal()
        if isinstance(stmt, Continue):
            raise ContinueSignal()
        if isinstance(stmt, Pass):
            return
        if isinstance(stmt, If):
            if self._truthy(self._eval(stmt.condition)):
                self._exec_block(stmt.then_body)
                return
            for cond, body in stmt.elif_parts:
                if self._truthy(self._eval(cond)):
                    self._exec_block(body)
                    return
            if stmt.else_body is not None:
                self._exec_block(stmt.else_body)
            return
        if isinstance(stmt, While):
            while self._truthy(self._eval(stmt.condition)):
                try:
                    self._exec_block(stmt.body)
                except ContinueSignal:
                    continue
                except BreakSignal:
                    break
            return
        if isinstance(stmt, RepeatTimes):
            count = self._eval(stmt.count)
            if not isinstance(count, int):
                raise RuntimeError("repeat times expects an integer")
            for _ in range(count):
                try:
                    self._exec_block(stmt.body)
                except ContinueSignal:
                    continue
                except BreakSignal:
                    break
            return
        if isinstance(stmt, For):
            iterable = self._eval(stmt.iterable)
            for item in iterable:
                self.env.set(stmt.name, item)
                try:
                    self._exec_block(stmt.body)
                except ContinueSignal:
                    continue
                except BreakSignal:
                    break
            return
        if isinstance(stmt, Match):
            value = self._eval(stmt.value)
            for patterns, body in stmt.cases:
                if self._match_any_pattern(patterns, value):
                    self._exec_block(body)
                    return
            if stmt.otherwise is not None:
                self._exec_block(stmt.otherwise)
            return
        if isinstance(stmt, Try):
            signal: Optional[Exception] = None
            try:
                self._exec_block(stmt.try_body)
            except (ReturnSignal, BreakSignal, ContinueSignal) as ex:
                signal = ex
            except Exception as ex:
                if stmt.except_body is not None:
                    self._exec_block(stmt.except_body)
                else:
                    raise
            finally:
                if stmt.finally_body is not None:
                    self._exec_block(stmt.finally_body)
            if signal is not None:
                raise signal
            return
        raise RuntimeError(f"Unknown statement {stmt}")

    def _exec_block(self, statements: List[Stmt]) -> None:
        for stmt in statements:
            self._exec_with_loc(stmt)

    def _exec_function_body(self, statements: List[Stmt], env: Environment) -> Any:
        previous = self.env
        self.env = env
        try:
            for stmt in statements:
                self._exec_with_loc(stmt)
        except ReturnSignal as signal:
            return signal.value
        finally:
            self.env = previous
        return None

    def _exec_with_loc(self, stmt: Stmt) -> None:
        line = getattr(stmt, "line", None)
        column = getattr(stmt, "column", None)
        if self.call_stack:
            frame = self.call_stack[-1]
            frame.line = line
            frame.column = column
            if frame.file is None and self.current_file is not None:
                frame.file = str(self.current_file)
        else:
            self.module_line = line
            self.module_column = column
        try:
            self._exec(stmt)
        except (ReturnSignal, BreakSignal, ContinueSignal):
            raise
        except NoxRuntimeError as exc:
            if exc.line is None or not exc.stack:
                stack = self._build_stack(line, column)
                exc.line = line
                exc.column = column
                exc.stack = stack
            raise
        except NameError as exc:
            stack = self._build_stack(line, column)
            raise NoxNameError(str(exc), line, column, stack=stack) from None
        except TypeError as exc:
            stack = self._build_stack(line, column)
            raise NoxTypeError(str(exc), line, column, stack=stack) from None
        except IndexError as exc:
            stack = self._build_stack(line, column)
            raise NoxIndexError(str(exc), line, column, stack=stack) from None
        except ZeroDivisionError as exc:
            stack = self._build_stack(line, column)
            raise NoxZeroDivisionError(str(exc), line, column, stack=stack) from None
        except FileNotFoundError as exc:
            stack = self._build_stack(line, column)
            raise NoxImportError(str(exc), line, column, stack=stack) from None
        except Exception as exc:
            stack = self._build_stack(line, column)
            raise NoxRuntimeError(str(exc), line, column, stack=stack) from None

    def _eval(self, expr: Expr) -> Any:
        if isinstance(expr, Literal):
            return expr.value
        if isinstance(expr, Var):
            return self.env.get(expr.name)
        if isinstance(expr, Call):
            callee = self._eval(expr.callee)
            args = [self._eval(arg) for arg in expr.args]
            if isinstance(callee, Function):
                return self._call_function(callee, args, expr)
            if isinstance(callee, BoundMethod):
                return self._call_function(callee.function, [callee.instance] + args, expr)
            if isinstance(callee, Class):
                return self._call_class(callee, args, expr)
            if isinstance(callee, StructType):
                return callee.call(self, args)
            if callable(callee):
                return callee(*args)
            raise RuntimeError("Can only call functions")
        if isinstance(expr, Lambda):
            body_stmt = Return(expr.body)
            func = Function("<lambda>", expr.params, [body_stmt], self.env, is_async=False)
            return func
        if isinstance(expr, Await):
            value = self._eval(expr.expr)
            if isinstance(value, Task):
                return value.result()
            if isinstance(value, AsyncResult):
                return value.value
            return value
        if isinstance(expr, ListLiteral):
            return [self._eval(item) for item in expr.items]
        if isinstance(expr, DictLiteral):
            return {self._eval(k): self._eval(v) for k, v in expr.items}
        if isinstance(expr, SetLiteral):
            return {self._eval(item) for item in expr.items}
        if isinstance(expr, TupleLiteral):
            return tuple(self._eval(item) for item in expr.items)
        if isinstance(expr, StructInit):
            struct = self.env.get(expr.name)
            if not isinstance(struct, StructType):
                raise RuntimeError(f"'{expr.name}' is not a struct")
            inst = StructInstance(struct)
            for key, value_expr in expr.fields:
                inst.set(key, self._eval(value_expr))
            return inst
        if isinstance(expr, Index):
            target = self._eval(expr.target)
            index = self._eval(expr.index)
            return target[index]
        if isinstance(expr, Slice):
            target = self._eval(expr.target)
            start = self._eval(expr.start) if expr.start is not None else None
            stop = self._eval(expr.stop) if expr.stop is not None else None
            step = self._eval(expr.step) if expr.step is not None else None
            return target[start:stop:step]
        if isinstance(expr, GetAttr):
            target = self._eval(expr.target)
            if isinstance(target, Instance):
                return target.get(expr.name)
            if isinstance(target, StructInstance):
                return target.get(expr.name)
            if isinstance(target, Module):
                return target.get(expr.name)
            if hasattr(target, expr.name):
                return getattr(target, expr.name)
            raise RuntimeError("Attribute access only works on class instances")
        if isinstance(expr, Unary):
            right = self._eval(expr.expr)
            if expr.op == "-":
                return -right
            if expr.op == "+":
                return +right
            if expr.op == "not":
                return not self._truthy(right)
            raise RuntimeError(f"Unknown unary operator {expr.op}")
        if isinstance(expr, Binary):
            left = self._eval(expr.left)
            right = self._eval(expr.right)
            if expr.op == "and":
                return self._truthy(left) and self._truthy(right)
            if expr.op == "or":
                return self._truthy(left) or self._truthy(right)
            if expr.op == "+":
                if _is_number(left) and _is_number(right):
                    return _add_num(left, right) if NUMBA_AVAILABLE else left + right
                return left + right
            if expr.op == "-":
                if _is_number(left) and _is_number(right):
                    return _sub_num(left, right) if NUMBA_AVAILABLE else left - right
                return left - right
            if expr.op == "*":
                if _is_number(left) and _is_number(right):
                    return _mul_num(left, right) if NUMBA_AVAILABLE else left * right
                return left * right
            if expr.op == "/":
                if _is_number(left) and _is_number(right):
                    if right == 0:
                        raise ZeroDivisionError("division by zero")
                    return _div_num(left, right) if NUMBA_AVAILABLE else left / right
                return left / right
            if expr.op == "==":
                return left == right
            if expr.op == "!=":
                return left != right
            if expr.op == "<":
                if _is_number(left) and _is_number(right):
                    return _lt_num(left, right) if NUMBA_AVAILABLE else left < right
                return left < right
            if expr.op == "<=":
                if _is_number(left) and _is_number(right):
                    return _lte_num(left, right) if NUMBA_AVAILABLE else left <= right
                return left <= right
            if expr.op == ">":
                if _is_number(left) and _is_number(right):
                    return _gt_num(left, right) if NUMBA_AVAILABLE else left > right
                return left > right
            if expr.op == ">=":
                if _is_number(left) and _is_number(right):
                    return _gte_num(left, right) if NUMBA_AVAILABLE else left >= right
                return left >= right
            raise RuntimeError(f"Unknown binary operator {expr.op}")
        raise RuntimeError(f"Unknown expression {expr}")

    def _truthy(self, value: Any) -> bool:
        return bool(value)

    def _match_any_pattern(self, patterns: List[Expr], value: Any) -> bool:
        for pattern in patterns:
            if isinstance(pattern, Var) and pattern.name == "_":
                return True
            if self._eval(pattern) == value:
                return True
        return False

    def _builtin_range(self, *args: Any) -> List[int]:
        if len(args) == 1 and isinstance(args[0], int):
            return list(range(args[0]))
        if len(args) == 2 and all(isinstance(a, int) for a in args):
            return list(range(args[0], args[1]))
        if len(args) == 3 and all(isinstance(a, int) for a in args):
            return list(range(args[0], args[1], args[2]))
        raise RuntimeError("range expects 1-3 integer arguments")

    def _builtin_sleep(self, ms: Any) -> AsyncResult:
        import time

        if not isinstance(ms, (int, float)):
            raise RuntimeError("sleep expects a number")
        time.sleep(ms / 1000.0)
        return AsyncResult(None)

    def _builtin_open(self, path: Any, mode: Any = "r") -> Any:
        if not isinstance(path, str):
            raise RuntimeError("open expects a string path")
        if not isinstance(mode, str):
            raise RuntimeError("open expects a string mode")
        return open(path, mode, encoding="utf-8")

    def _invoke_callable(self, target: Any, args: List[Any]) -> Any:
        if isinstance(target, Function):
            temp = Interpreter(base_dir=self.base_dir, module_cache=self.module_cache, current_file=self.current_file)
            return target.call(temp, args)
        if isinstance(target, BoundMethod):
            temp = Interpreter(base_dir=self.base_dir, module_cache=self.module_cache, current_file=self.current_file)
            return target.function.call(temp, [target.instance] + args)
        if isinstance(target, Class):
            temp = Interpreter(base_dir=self.base_dir, module_cache=self.module_cache, current_file=self.current_file)
            return target.call(temp, args)
        if callable(target):
            return target(*args)
        raise RuntimeError("Target is not callable")

    def _builtin_create_task(self, target: Any, *args: Any) -> Task:
        return Task(lambda: self._invoke_callable(target, list(args)))

    def _builtin_gather(self, tasks: Any) -> AsyncResult:
        if not isinstance(tasks, list):
            raise RuntimeError("gather expects a list of tasks")
        results = []
        for task in tasks:
            if isinstance(task, Task):
                results.append(task.result())
            elif isinstance(task, AsyncResult):
                results.append(task.value)
            else:
                results.append(task)
        return AsyncResult(results)

    def _builtin_run_async(self, value: Any) -> Any:
        if isinstance(value, Task):
            return value.result()
        if isinstance(value, AsyncResult):
            return value.value
        return value

    def _builtin_http_request(
        self,
        method: Any,
        url: Any,
        headers: Any = None,
        data: Any = None,
        json_data: Any = None,
        timeout: Any = 30,
    ) -> Any:
        if not isinstance(method, str):
            raise RuntimeError("http.request expects string method")
        if not isinstance(url, str):
            raise RuntimeError("http.request expects string url")
        if not isinstance(timeout, (int, float)):
            raise RuntimeError("http.request expects numeric timeout")

        req_headers: Dict[str, str] = {}
        if headers is not None:
            if not isinstance(headers, dict):
                raise RuntimeError("http.request headers must be a dict")
            req_headers = {str(k): str(v) for k, v in headers.items()}

        body_bytes: Optional[bytes] = None
        if json_data is not None:
            body_bytes = json.dumps(json_data).encode("utf-8")
            if "Content-Type" not in req_headers:
                req_headers["Content-Type"] = "application/json"
        elif data is not None:
            if isinstance(data, bytes):
                body_bytes = data
            elif isinstance(data, str):
                body_bytes = data.encode("utf-8")
            elif isinstance(data, dict):
                body_bytes = urllib.parse.urlencode({str(k): str(v) for k, v in data.items()}).encode("utf-8")
                if "Content-Type" not in req_headers:
                    req_headers["Content-Type"] = "application/x-www-form-urlencoded"
            else:
                body_bytes = str(data).encode("utf-8")

        req = urllib.request.Request(url=url, data=body_bytes, method=method.upper(), headers=req_headers)
        try:
            with urllib.request.urlopen(req, timeout=float(timeout)) as resp:
                raw = resp.read()
                text = raw.decode("utf-8", errors="replace")
                out = {
                    "status": int(resp.status),
                    "text": text,
                    "headers": {k: v for (k, v) in resp.headers.items()},
                    "json": None,
                }
                try:
                    out["json"] = json.loads(text)
                except Exception:
                    pass
                return out
        except urllib.error.HTTPError as exc:
            text = exc.read().decode("utf-8", errors="replace")
            out = {
                "status": int(exc.code),
                "text": text,
                "headers": {k: v for (k, v) in exc.headers.items()},
                "json": None,
            }
            try:
                out["json"] = json.loads(text)
            except Exception:
                pass
            return out

    def _builtin_http_get(self, url: Any, headers: Any = None, timeout: Any = 30) -> Any:
        return self._builtin_http_request("GET", url, headers=headers, timeout=timeout)

    def _builtin_http_post(
        self,
        url: Any,
        headers: Any = None,
        data: Any = None,
        json_data: Any = None,
        timeout: Any = 30,
    ) -> Any:
        return self._builtin_http_request(
            "POST",
            url,
            headers=headers,
            data=data,
            json_data=json_data,
            timeout=timeout,
        )

    def _builtin_http_serve(self, routes: Any, port: Any = 8080, options: Any = None) -> None:
        import http.server
        import json as _json
        import socketserver
        import sys as _sys
        from urllib.parse import urlparse, parse_qs

        if not isinstance(port, int):
            raise RuntimeError("http.serve expects integer port")
        if not isinstance(routes, list):
            raise RuntimeError("http.serve expects list of routes")

        compiled: list[tuple[str, list[str], Any]] = []
        for route in routes:
            if not isinstance(route, dict):
                raise RuntimeError("http.serve route must be a dict")
            method = route.get("method")
            path = route.get("path")
            handler = route.get("handler")
            if not isinstance(method, str) or not isinstance(path, str):
                raise RuntimeError("http.serve route requires method and path")
            parts = [p for p in path.strip("/").split("/") if p != ""]
            compiled.append((method.upper(), parts, handler))

        static_dir = None
        log_enabled = True
        if isinstance(options, dict):
            static_dir = options.get("static")
            log_enabled = options.get("log", True)

        static_root = None
        if isinstance(static_dir, str) and static_dir.strip():
            static_root = self._resolve_fs_path(static_dir).resolve()

        def _match(method: str, path: str) -> tuple[Any, dict]:
            parts = [p for p in path.strip("/").split("/") if p != ""]
            for m, segs, handler in compiled:
                if m != method:
                    continue
                if len(segs) != len(parts):
                    continue
                params: dict[str, str] = {}
                matched = True
                for s, p in zip(segs, parts):
                    if s.startswith("<") and s.endswith(">"):
                        params[s[1:-1]] = p
                    elif s != p:
                        matched = False
                        break
                if matched:
                    return handler, params
            return None, {}

        interpreter = self

        class Handler(http.server.BaseHTTPRequestHandler):
            def _handle(self) -> None:
                parsed = urlparse(self.path)
                handler, params = _match(self.command.upper(), parsed.path)
                if handler is None and static_root is not None:
                    rel = parsed.path.lstrip("/")
                    if rel == "":
                        rel = "index.html"
                    candidate = (static_root / rel).resolve()
                    try:
                        if static_root.resolve() in candidate.parents or candidate == static_root.resolve():
                            if candidate.exists() and candidate.is_file():
                                data = candidate.read_bytes()
                                suffix = candidate.suffix.lower()
                                mime = "application/octet-stream"
                                if suffix == ".html":
                                    mime = "text/html; charset=utf-8"
                                elif suffix == ".css":
                                    mime = "text/css; charset=utf-8"
                                elif suffix == ".js":
                                    mime = "text/javascript; charset=utf-8"
                                elif suffix == ".json":
                                    mime = "application/json; charset=utf-8"
                                elif suffix in {".png", ".jpg", ".jpeg", ".gif", ".svg"}:
                                    mime = f"image/{suffix.lstrip('.')}"
                                self.send_response(200)
                                self.send_header("Content-Type", mime)
                                self.end_headers()
                                self.wfile.write(data)
                                if log_enabled:
                                    print(f"{self.command} {parsed.path} 200", file=_sys.__stdout__, flush=True)
                                return
                    except Exception:
                        pass

                if handler is None:
                    self.send_response(404)
                    self.send_header("Content-Type", "text/plain; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(b"Not Found")
                    if log_enabled:
                        print(f"{self.command} {parsed.path} 404", file=_sys.__stdout__, flush=True)
                    return

                length = int(self.headers.get("Content-Length", "0") or "0")
                body_bytes = self.rfile.read(length) if length > 0 else b""
                body_text = body_bytes.decode("utf-8", errors="replace")
                json_body = None
                if body_text:
                    try:
                        json_body = _json.loads(body_text)
                    except Exception:
                        json_body = None

                req = SimpleNamespace(
                    method=self.command.upper(),
                    path=parsed.path,
                    query={k: v[0] if len(v) == 1 else v for k, v in parse_qs(parsed.query).items()},
                    params=params,
                    headers={k: v for k, v in self.headers.items()},
                    body=body_text,
                    json=json_body,
                )

                try:
                    if isinstance(handler, Function):
                        result = handler.call(interpreter, [req])
                    elif isinstance(handler, BoundMethod):
                        result = handler.call(interpreter, [req])
                    elif callable(handler):
                        result = handler(req)
                    else:
                        raise RuntimeError("Handler is not callable")
                except Exception as exc:
                    self.send_response(500)
                    self.send_header("Content-Type", "text/plain; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(b"Internal Server Error")
                    if log_enabled:
                        import traceback as _traceback
                        print(f"{self.command} {parsed.path} 500", file=_sys.__stdout__, flush=True)
                        _traceback.print_exception(type(exc), exc, exc.__traceback__, file=_sys.__stdout__)
                    return

                status = 200
                headers: dict[str, str] = {}
                body = result
                if isinstance(result, tuple):
                    if len(result) == 2:
                        status, body = result
                    elif len(result) == 3:
                        status, body, headers = result

                if isinstance(body, (dict, list)):
                    body_bytes = _json.dumps(body).encode("utf-8")
                    headers.setdefault("Content-Type", "application/json; charset=utf-8")
                else:
                    body_bytes = str(body).encode("utf-8")
                    headers.setdefault("Content-Type", "text/html; charset=utf-8")

                self.send_response(int(status))
                for k, v in headers.items():
                    self.send_header(k, str(v))
                self.end_headers()
                self.wfile.write(body_bytes)
                if log_enabled:
                    print(f"{self.command} {parsed.path} {int(status)}", file=_sys.__stdout__, flush=True)

            def do_GET(self) -> None:
                self._handle()

            def do_POST(self) -> None:
                self._handle()

            def log_message(self, format: str, *args: Any) -> None:
                return

        with socketserver.TCPServer(("", port), Handler) as httpd:
            try:
                if log_enabled:
                    print(f"* Running on http://127.0.0.1:{port}", file=_sys.__stdout__, flush=True)
                    print(f"* Press CTRL+C to quit", file=_sys.__stdout__, flush=True)
                httpd.serve_forever()
            except KeyboardInterrupt:
                return

    def _install_stdlib(self) -> None:
        import math as _math
        import json as _json
        import os as _os
        import time as _time
        from . import process as _process_module
        from . import compiler as _compiler_module

        math_mod = _module(
            "math",
            {
                "abs": abs,
                "min": min,
                "max": max,
                "floor": _math.floor,
                "ceil": _math.ceil,
                "sqrt": _math.sqrt,
                "pow": pow,
                "sin": _math.sin,
                "cos": _math.cos,
                "tan": _math.tan,
                "pi": _math.pi,
            },
        )

        string_mod = _module(
            "string",
            {
                "str": lambda v: str(v),
                "split": lambda s, sep=None: s.split(sep),
                "join": lambda items, sep="": sep.join(items),
                "lower": lambda s: s.lower(),
                "upper": lambda s: s.upper(),
                "replace": lambda s, a, b: s.replace(a, b),
                "startswith": lambda s, p: s.startswith(p),
            },
        )

        time_mod = _module(
            "time",
            {
                "sleep": self._builtin_sleep,
                "now": lambda: int(_time.time() * 1000),
            },
        )

        json_mod = _module(
            "json",
            {
                "encode": lambda obj: _json.dumps(obj),
                "decode": lambda s: _json.loads(s),
            },
        )

        fs_mod = _module(
            "fs",
            {
                "read":   lambda path: self._resolve_fs_path(path).read_text(encoding="utf-8"),
                "write":  lambda path, text: self._resolve_fs_path(path).write_text(str(text), encoding="utf-8"),
                "exists": lambda path: self._resolve_fs_path(path).exists(),
            },
        )

        os_mod = _module(
            "os",
            {
                "cwd": lambda: str(_os.getcwd()),
                "listdir": lambda path=".": _os.listdir(path),
            },
        )

        http_mod = _module(
            "http",
            {
                "serve": self._builtin_http_serve,
                "request": self._builtin_http_request,
                "get": self._builtin_http_get,
                "post": self._builtin_http_post,
            },
        )

        asyncio_mod = _module(
            "asyncio",
            {
                "create_task": self._builtin_create_task,
                "gather": self._builtin_gather,
                "run": self._builtin_run_async,
                "sleep": self._builtin_sleep,
            },
        )

        process_mod = _module("process", _process_module._make_process_module())

        compiler_mod = _module("compiler", _compiler_module._make_module_values())

        from . import clib as _clib_module
        _base = str(self.base_dir) if self.base_dir else None
        _load_with_base = lambda path: _clib_module.load(path, base_dir=_base)
        clib_values = {**_clib_module._make_module_values(), "load": _load_with_base}
        clib_mod = _module("clib", clib_values)
        self.env.set("clib", clib_mod)

        self.env.set("process", process_mod)

        self.env.set("compiler", compiler_mod)

        self.env.set("math", math_mod)
        self.env.set("string", string_mod)
        self.env.set("time", time_mod)
        self.env.set("json", json_mod)
        self.env.set("fs", fs_mod)
        self.env.set("os", os_mod)
        self.env.set("http", http_mod)
        self.env.set("asyncio", asyncio_mod)

    def _bind_args(self, params: List[Param], args: List[Any], env: Environment) -> Dict[str, Any]:
        bound: Dict[str, Any] = {}
        positional = list(args)
        vararg_name = None

        for param in params:
            if param.is_vararg:
                vararg_name = param.name
                break

        required = [p for p in params if not p.is_vararg and p.default is None]
        if len(positional) < len(required):
            raise RuntimeError("Not enough arguments")

        if vararg_name is None and len(positional) > len([p for p in params if not p.is_vararg]):
            raise RuntimeError("Too many arguments")

        for param in params:
            if param.is_vararg:
                bound[param.name] = positional
                positional = []
                continue
            if positional:
                bound[param.name] = positional.pop(0)
            elif param.default is not None:
                bound[param.name] = self._eval_in_env(param.default, env)
            else:
                raise RuntimeError("Missing required argument")
        return bound

    def _eval_in_env(self, expr: Expr, env: Environment) -> Any:
        prev = self.env
        self.env = env
        try:
            return self._eval(expr)
        finally:
            self.env = prev

    def _validate_traits(self, klass: Class) -> None:
        for trait_name in klass.traits or []:
            trait = self.traits.get(trait_name)
            if trait is None:
                raise RuntimeError(f"Unknown trait '{trait_name}'")
            for method in trait.methods:
                if klass.get_method(method) is None:
                    raise RuntimeError(f"Class '{klass.name}' missing trait method '{method}'")

    def _call_function(self, function: Function, args: List[Any], call_expr: Expr) -> Any:
        line = getattr(call_expr, "line", None)
        column = getattr(call_expr, "column", None)
        file_name = function.file or (str(self.current_file) if self.current_file is not None else "<module>")
        self.call_stack.append(StackFrame(file_name, line, column, function.name))
        try:
            return function.call(self, args)
        finally:
            self.call_stack.pop()

    def _call_class(self, klass: Class, args: List[Any], call_expr: Expr) -> Any:
        line = getattr(call_expr, "line", None)
        column = getattr(call_expr, "column", None)
        file_name = str(self.current_file) if self.current_file is not None else "<module>"
        self.call_stack.append(StackFrame(file_name, line, column, klass.name))
        try:
            return klass.call(self, args)
        finally:
            self.call_stack.pop()

    def _apply_decorator(self, decorator: Any, target: Any, expr: Expr) -> Any:
        if isinstance(decorator, Function):
            return self._call_function(decorator, [target], expr)
        if isinstance(decorator, BoundMethod):
            return self._call_function(decorator.function, [decorator.instance, target], expr)
        if isinstance(decorator, Class):
            return self._call_class(decorator, [target], expr)
        if callable(decorator):
            return decorator(target)
        raise RuntimeError("Decorator must be callable")

    def _build_stack(self, line: int | None, column: int | None) -> List[StackFrame]:
        frames: List[StackFrame] = []
        file_name = str(self.current_file) if self.current_file is not None else "<module>"
        frames.append(StackFrame(file_name, self.module_line or line, self.module_column or column, "<module>"))
        frames.extend(self.call_stack)
        return frames

    def _load_module(self, module_parts: List[str]) -> Module:
        module_key = ".".join(module_parts)

        try:
            val = self.env.get(module_key)
            if isinstance(val, Module):
                return val
        except NameError:
            pass

        if module_key in self.module_cache:
            return self.module_cache[module_key]

        module_path = self._resolve_module_path(module_parts)
        if module_path is None:
            raise FileNotFoundError(f"Module not found: {'.'.join(module_parts)}")

        source = module_path.read_text(encoding="utf-8")
        from .lexer import Lexer
        from .parser import Parser

        try:
            tokens = Lexer(source).tokenize()
            program = Parser(tokens).parse()
        except NoxSyntaxError as exc:
            stack = [StackFrame(str(module_path), exc.line, exc.column, "<module>")]
            raise NoxRuntimeError(str(exc), exc.line, exc.column, stack=stack) from None

        module_env = Environment(values=dict(self.builtins))
        module_interpreter = Interpreter(
            base_dir=module_path.parent,
            module_cache=self.module_cache,
            current_file=module_path,
        )
        module_interpreter.env = module_env
        module_interpreter._install_stdlib()
        module_interpreter.run(program)

        module = Module(module_key, module_env.values)
        self.module_cache[module_key] = module
        return module

    def _resolve_module_path(self, module_parts: List[str]) -> Path | None:
        base_dir = self.base_dir if self.base_dir is not None else Path.cwd()
        candidates: List[Path] = []

        candidates.append(base_dir.joinpath(*module_parts).with_suffix(".nox"))
        candidates.append(base_dir.joinpath(*module_parts) / "__init__.nox")

        libs_root = _get_libraries_root()

        if libs_root.exists():
            lib_root = libs_root / module_parts[0]
            if len(module_parts) == 1:
                candidates.append(lib_root / f"{module_parts[0]}.nox")
                candidates.append(lib_root / "main.nox")
                candidates.append(lib_root / "__init__.nox")
            else:
                tail = module_parts[1:]
                candidates.append(lib_root.joinpath(*tail).with_suffix(".nox"))
                candidates.append(lib_root.joinpath(*tail) / "__init__.nox")

        for path in candidates:
            if path.exists():
                return path
        return None
