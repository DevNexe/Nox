from __future__ import annotations

from typing import List, Optional

from .ast_nodes import (
    Assign,
    AssignIndex,
    AssignAttr,
    Binary,
    Call,
    Continue,
    Break,
    ClassDef,
    TraitDef,
    Implement,
    StructDef,
    With,
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
    Return,
    RepeatTimes,
    Try,
    Stmt,
    Unary,
    Var,
    While,
    StructInit,
)
from .token import Token, TokenType
from .errors import NoxSyntaxError


class Parser:
    def __init__(self, tokens: List[Token]) -> None:
        self.tokens = tokens
        self.current = 0

    def parse(self) -> Program:
        statements: List[Stmt] = []
        while not self._is_at_end():
            if self._match(TokenType.NEWLINE):
                continue
            statements.append(self._statement())
        return Program(statements)

    def _statement(self) -> Stmt:
        if self._match(TokenType.AT):
            return self._decorated_define()
        if self._match(TokenType.CONNECT):
            return self._with_loc(self._import_stmt(), self._previous())
        if self._match(TokenType.FROM):
            return self._with_loc(self._from_import_stmt(), self._previous())
        if self._match(TokenType.STRUCT):
            return self._with_loc(self._struct_stmt(), self._previous())
        if self._match(TokenType.TRAIT):
            return self._with_loc(self._trait_stmt(), self._previous())
        if self._match(TokenType.ASYNC):
            if self._match(TokenType.DEFINE):
                return self._with_loc(self._define_stmt(is_async=True), self._previous())
            token = self._peek()
            raise NoxSyntaxError("Expected define after async", token.line, token.column)
        if self._match(TokenType.DEFINE):
            return self._with_loc(self._define_stmt(), self._previous())
        if self._match(TokenType.CLASS):
            return self._with_loc(self._class_stmt(), self._previous())
        if self._match(TokenType.WITH):
            return self._with_loc(self._with_stmt(), self._previous())
        if self._match(TokenType.RETURN):
            return self._with_loc(self._return_stmt(), self._previous())
        if self._match(TokenType.BREAK):
            return self._with_loc(Break(), self._previous())
        if self._match(TokenType.CONTINUE):
            return self._with_loc(Continue(), self._previous())
        if self._match(TokenType.TRY):
            return self._with_loc(self._try_stmt(), self._previous())
        if self._match(TokenType.IF):
            return self._with_loc(self._if_stmt(), self._previous())
        if self._match(TokenType.REPEAT):
            return self._with_loc(self._repeat_stmt(), self._previous())
        if self._match(TokenType.FOR):
            return self._with_loc(self._for_stmt(), self._previous())
        if self._match(TokenType.MATCH):
            return self._with_loc(self._match_stmt(), self._previous())
        return self._simple_stmt()

    def _simple_stmt(self) -> Stmt:
        start_token = self._peek()
        if self._match(TokenType.PRINT):
            values: List[Expr] = []
            if self._match(TokenType.LPAREN):
                if not self._check(TokenType.RPAREN):
                    values.append(self._expression())
                    while self._match(TokenType.COMMA):
                        values.append(self._expression())
                self._consume(TokenType.RPAREN, "Expected ')' after print arguments")
                return self._with_loc(Print(values), self._previous())
            values.append(self._expression())
            while self._match(TokenType.COMMA):
                values.append(self._expression())
            return self._with_loc(Print(values), self._previous())

        if self._check(TokenType.IDENT):
            if self._check_next(TokenType.EQ):
                name = self._advance().value
                self._consume(TokenType.EQ, "Expected '=' after identifier")
                value = self._expression()
                return self._with_loc(Assign(name, value), start_token)
            if self._check_next(TokenType.LBRACKET):
                target = Var(self._advance().value)
                self._consume(TokenType.LBRACKET, "Expected '[' after identifier")
                index = self._expression()
                self._consume(TokenType.RBRACKET, "Expected ']' after index")
                self._consume(TokenType.EQ, "Expected '=' after index assignment")
                value = self._expression()
                return self._with_loc(AssignIndex(target, index, value), start_token)
            if (
                self._check_next(TokenType.DOT)
                and self._check_next_next(TokenType.IDENT)
                and self._check_next_next_next(TokenType.EQ)
            ):
                target = Var(self._advance().value)
                self._consume(TokenType.DOT, "Expected '.' after identifier")
                name = self._consume(TokenType.IDENT, "Expected attribute name").value
                self._consume(TokenType.EQ, "Expected '=' after attribute name")
                value = self._expression()
                return self._with_loc(AssignAttr(target, name, value), start_token)

        expr = self._expression()
        return self._with_loc(ExprStmt(expr), start_token)

    def _import_stmt(self) -> Stmt:
        module = self._module_path("Expected module name after connect")
        alias = None
        if self._match(TokenType.AS):
            alias = self._consume(TokenType.IDENT, "Expected alias name after 'as'").value
        return ImportModule(module, alias)

    def _from_import_stmt(self) -> Stmt:
        module = self._module_path("Expected module name after from")
        self._consume(TokenType.CONNECT, "Expected 'connect' after module name")
        names: List[tuple[str, Optional[str]]] = []
        name = self._consume(TokenType.IDENT, "Expected name to connect").value
        alias = None
        if self._match(TokenType.AS):
            alias = self._consume(TokenType.IDENT, "Expected alias name after 'as'").value
        names.append((name, alias))
        while self._match(TokenType.COMMA):
            name = self._consume(TokenType.IDENT, "Expected name to connect").value
            alias = None
            if self._match(TokenType.AS):
                alias = self._consume(TokenType.IDENT, "Expected alias name after 'as'").value
            names.append((name, alias))
        return ImportFrom(module, names)

    def _if_stmt(self) -> Stmt:
        condition = self._expression()
        self._consume(TokenType.COLON, "Expected ':' after if condition")
        self._consume(TokenType.NEWLINE, "Expected newline after ':'")
        then_body = self._block()

        elif_parts: List[tuple[Expr, List[Stmt]]] = []
        else_body = None
        while self._match(TokenType.ELSE):
            if self._match(TokenType.IF):
                elif_cond = self._expression()
                self._consume(TokenType.COLON, "Expected ':' after else if condition")
                self._consume(TokenType.NEWLINE, "Expected newline after ':'")
                elif_body = self._block()
                elif_parts.append((elif_cond, elif_body))
                continue
            self._consume(TokenType.COLON, "Expected ':' after else")
            self._consume(TokenType.NEWLINE, "Expected newline after ':'")
            else_body = self._block()
            break

        return If(condition, then_body, elif_parts, else_body)

    def _repeat_stmt(self) -> Stmt:
        if self._match(TokenType.TIMES):
            count = self._expression()
            self._consume(TokenType.COLON, "Expected ':' after repeat times condition")
            self._consume(TokenType.NEWLINE, "Expected newline after ':'")
            body = self._block()
            return RepeatTimes(count, body)
        condition = self._expression()
        self._consume(TokenType.COLON, "Expected ':' after repeat condition")
        self._consume(TokenType.NEWLINE, "Expected newline after ':'")
        body = self._block()
        return While(condition, body)

    def _for_stmt(self) -> Stmt:
        name_token = self._consume(TokenType.IDENT, "Expected loop variable after 'for'")
        self._consume(TokenType.IN, "Expected 'in' after loop variable")
        iterable = self._expression()
        self._consume(TokenType.COLON, "Expected ':' after for expression")
        self._consume(TokenType.NEWLINE, "Expected newline after ':'")
        body = self._block()
        return For(name_token.value, iterable, body)

    def _match_stmt(self) -> Stmt:
        value = self._expression()
        self._consume(TokenType.COLON, "Expected ':' after match expression")
        self._consume(TokenType.NEWLINE, "Expected newline after ':'")
        self._consume(TokenType.INDENT, "Expected indented block after match")
        cases: List[tuple[List[Expr], List[Stmt]]] = []
        while self._match(TokenType.CASE):
            patterns: List[Expr] = [self._expression()]
            while self._match(TokenType.COMMA):
                patterns.append(self._expression())
            self._consume(TokenType.COLON, "Expected ':' after case pattern")
            self._consume(TokenType.NEWLINE, "Expected newline after ':'")
            body = self._block()
            cases.append((patterns, body))
        otherwise_body = None
        if self._match(TokenType.ELSE):
            self._consume(TokenType.COLON, "Expected ':' after else")
            self._consume(TokenType.NEWLINE, "Expected newline after ':'")
            otherwise_body = self._block()
        self._consume(TokenType.DEDENT, "Expected end of match block")
        return Match(value, cases, otherwise_body)

    def _try_stmt(self) -> Stmt:
        self._consume(TokenType.COLON, "Expected ':' after try")
        self._consume(TokenType.NEWLINE, "Expected newline after ':'")
        try_body = self._block()
        except_body = None
        finally_body = None
        if self._match(TokenType.EXCEPT):
            self._consume(TokenType.COLON, "Expected ':' after except")
            self._consume(TokenType.NEWLINE, "Expected newline after ':'")
            except_body = self._block()
        if self._match(TokenType.FINALLY):
            self._consume(TokenType.COLON, "Expected ':' after finally")
            self._consume(TokenType.NEWLINE, "Expected newline after ':'")
            finally_body = self._block()
        if except_body is None and finally_body is None:
            token = self._previous()
            raise NoxSyntaxError("Expected except or finally after try block", token.line, token.column)
        return Try(try_body, except_body, finally_body)

    def _class_stmt(self) -> Stmt:
        name = self._consume(TokenType.IDENT, "Expected class name").value
        parent = None
        if self._match(TokenType.LPAREN):
            parent = self._consume(TokenType.IDENT, "Expected parent class name").value
            self._consume(TokenType.RPAREN, "Expected ')' after parent class")
        self._consume(TokenType.COLON, "Expected ':' after class name")
        self._consume(TokenType.NEWLINE, "Expected newline after ':'")
        self._consume(TokenType.INDENT, "Expected indented class body")
        methods: List[Define] = []
        traits: List[str] = []
        while not self._check(TokenType.DEDENT) and not self._is_at_end():
            if self._match(TokenType.NEWLINE):
                continue
            if self._match(TokenType.IMPLEMENT):
                trait_name = self._consume(TokenType.IDENT, "Expected trait name").value
                traits.append(trait_name)
                continue
            if self._match(TokenType.DEFINE):
                methods.append(self._define_stmt())
                continue
            token = self._peek()
            raise NoxSyntaxError("Only define statements are allowed inside class", token.line, token.column)
        self._consume(TokenType.DEDENT, "Expected end of class block")
        return ClassDef(name, methods, parent=parent, traits=traits)

    def _define_stmt(self, is_async: bool = False, decorators: Optional[List[Expr]] = None) -> Stmt:
        name = self._consume(TokenType.IDENT, "Expected function name").value
        self._consume(TokenType.LPAREN, "Expected '(' after function name")
        params = self._parse_params()
        self._consume(TokenType.RPAREN, "Expected ')' after parameters")
        self._consume(TokenType.COLON, "Expected ':' after function signature")
        self._consume(TokenType.NEWLINE, "Expected newline after ':'")
        body = self._block()
        return Define(name, params, body, is_async=is_async, decorators=decorators)

    def _decorated_define(self) -> Stmt:
        decorators: List[Expr] = []
        token = self._previous()
        decorators.append(self._expression())
        self._consume(TokenType.NEWLINE, "Expected newline after decorator")
        while self._match(TokenType.AT):
            decorators.append(self._expression())
            self._consume(TokenType.NEWLINE, "Expected newline after decorator")
        if self._match(TokenType.ASYNC):
            self._consume(TokenType.DEFINE, "Expected define after async")
            return self._with_loc(self._define_stmt(is_async=True, decorators=decorators), token)
        if self._match(TokenType.DEFINE):
            return self._with_loc(self._define_stmt(decorators=decorators), token)
        raise NoxSyntaxError("Expected define after decorator", token.line, token.column)

    def _struct_stmt(self) -> Stmt:
        name = self._consume(TokenType.IDENT, "Expected struct name").value
        self._consume(TokenType.COLON, "Expected ':' after struct name")
        self._consume(TokenType.NEWLINE, "Expected newline after ':'")
        self._consume(TokenType.INDENT, "Expected indented struct body")
        fields: List[str] = []
        while not self._check(TokenType.DEDENT) and not self._is_at_end():
            if self._match(TokenType.NEWLINE):
                continue
            field_name = self._consume(TokenType.IDENT, "Expected field name").value
            self._consume(TokenType.COLON, "Expected ':' after field name")
            # type name (ignored for now)
            self._consume(TokenType.IDENT, "Expected type name")
            self._consume(TokenType.NEWLINE, "Expected newline after field")
            fields.append(field_name)
        self._consume(TokenType.DEDENT, "Expected end of struct block")
        return StructDef(name, fields)

    def _with_stmt(self) -> Stmt:
        expr = self._expression()
        self._consume(TokenType.AS, "Expected 'as' after with expression")
        name = self._consume(TokenType.IDENT, "Expected name after 'as'").value
        self._consume(TokenType.COLON, "Expected ':' after with statement")
        self._consume(TokenType.NEWLINE, "Expected newline after ':'")
        body = self._block()
        return With(expr, name, body)

    def _trait_stmt(self) -> Stmt:
        name = self._consume(TokenType.IDENT, "Expected trait name").value
        self._consume(TokenType.COLON, "Expected ':' after trait name")
        self._consume(TokenType.NEWLINE, "Expected newline after ':'")
        self._consume(TokenType.INDENT, "Expected indented trait body")
        methods: List[str] = []
        while not self._check(TokenType.DEDENT) and not self._is_at_end():
            if self._match(TokenType.NEWLINE):
                continue
            if self._match(TokenType.DEFINE):
                method_name = self._consume(TokenType.IDENT, "Expected method name").value
                # Skip params and body (trait methods are declarations)
                self._consume(TokenType.LPAREN, "Expected '(' after method name")
                if not self._check(TokenType.RPAREN):
                    self._consume(TokenType.IDENT, "Expected parameter name")
                    while self._match(TokenType.COMMA):
                        if self._match(TokenType.STAR):
                            self._consume(TokenType.IDENT, "Expected parameter name")
                            break
                        self._consume(TokenType.IDENT, "Expected parameter name")
                self._consume(TokenType.RPAREN, "Expected ')' after parameters")
                self._consume(TokenType.COLON, "Expected ':' after method signature")
                self._consume(TokenType.NEWLINE, "Expected newline after ':'")
                self._block()
                methods.append(method_name)
                continue
            token = self._peek()
            raise NoxSyntaxError("Only define statements are allowed inside trait", token.line, token.column)
        self._consume(TokenType.DEDENT, "Expected end of trait block")
        return TraitDef(name, methods)

    def _return_stmt(self) -> Stmt:
        if self._check(TokenType.NEWLINE):
            return Return(None)
        return Return(self._expression())

    def _block(self) -> List[Stmt]:
        self._consume(TokenType.INDENT, "Expected indented block")
        statements: List[Stmt] = []
        while not self._check(TokenType.DEDENT) and not self._is_at_end():
            if self._match(TokenType.NEWLINE):
                continue
            statements.append(self._statement())
        self._consume(TokenType.DEDENT, "Expected end of block")
        return statements

    def _expression(self) -> Expr:
        if self._match(TokenType.LAMBDA):
            params = self._parse_params()
            self._consume(TokenType.COLON, "Expected ':' after lambda parameters")
            body = self._expression()
            return Lambda(params, body)
        return self._or()

    def _or(self) -> Expr:
        expr = self._and()
        while self._match(TokenType.OR):
            op = self._previous().value
            right = self._and()
            expr = Binary(expr, op, right)
        return expr

    def _and(self) -> Expr:
        expr = self._equality()
        while self._match(TokenType.AND):
            op = self._previous().value
            right = self._equality()
            expr = Binary(expr, op, right)
        return expr

    def _equality(self) -> Expr:
        expr = self._comparison()
        while self._match(TokenType.EQEQ, TokenType.NEQ):
            op = self._previous().value
            right = self._comparison()
            expr = Binary(expr, op, right)
        return expr

    def _comparison(self) -> Expr:
        expr = self._term()
        while self._match(TokenType.LT, TokenType.LTE, TokenType.GT, TokenType.GTE):
            op = self._previous().value
            right = self._term()
            expr = Binary(expr, op, right)
        return expr

    def _term(self) -> Expr:
        expr = self._factor()
        while self._match(TokenType.PLUS, TokenType.MINUS):
            op = self._previous().value
            right = self._factor()
            expr = Binary(expr, op, right)
        return expr

    def _factor(self) -> Expr:
        expr = self._unary()
        while self._match(TokenType.STAR, TokenType.SLASH):
            op = self._previous().value
            right = self._unary()
            expr = Binary(expr, op, right)
        return expr

    def _unary(self) -> Expr:
        if self._match(TokenType.AWAIT):
            expr = self._unary()
            return Await(expr)
        if self._match(TokenType.MINUS, TokenType.PLUS, TokenType.NOT):
            op = self._previous().value
            right = self._unary()
            return Unary(op, right)
        return self._primary()

    def _primary(self) -> Expr:
        if self._match(TokenType.NUMBER, TokenType.STRING):
            expr: Expr = Literal(self._previous().value)
            return self._postfix(expr)
        if self._match(TokenType.TRUE):
            return self._postfix(Literal(True))
        if self._match(TokenType.FALSE):
            return self._postfix(Literal(False))
        if self._match(TokenType.IDENT):
            expr = Var(self._previous().value)
            return self._postfix(expr)
        if self._match(TokenType.INPUT):
            expr = Var("input")
            return self._postfix(expr)
        if self._match(TokenType.LEN):
            expr = Var("len")
            return self._postfix(expr)
        if self._match(TokenType.LPAREN):
            if self._check(TokenType.RPAREN):
                self._consume(TokenType.RPAREN, "Expected ')'")
                return self._postfix(TupleLiteral([]))
            expr = self._expression()
            if self._match(TokenType.COMMA):
                items = [expr]
                if not self._check(TokenType.RPAREN):
                    items.append(self._expression())
                    while self._match(TokenType.COMMA):
                        if self._check(TokenType.RPAREN):
                            break
                        items.append(self._expression())
                self._consume(TokenType.RPAREN, "Expected ')' after tuple")
                return self._postfix(TupleLiteral(items))
            self._consume(TokenType.RPAREN, "Expected ')' after expression")
            return self._postfix(expr)
        if self._match(TokenType.LBRACE):
            if self._check(TokenType.RBRACE):
                self._consume(TokenType.RBRACE, "Expected '}'")
                return self._postfix(DictLiteral([]))
            first = self._expression()
            if self._match(TokenType.COLON):
                value = self._expression()
                items = [(first, value)]
                while self._match(TokenType.COMMA):
                    if self._check(TokenType.RBRACE):
                        break
                    key = self._expression()
                    self._consume(TokenType.COLON, "Expected ':' after dict key")
                    val = self._expression()
                    items.append((key, val))
                self._consume(TokenType.RBRACE, "Expected '}' after dict")
                return self._postfix(DictLiteral(items))
            # set literal
            items = [first]
            while self._match(TokenType.COMMA):
                if self._check(TokenType.RBRACE):
                    break
                items.append(self._expression())
            self._consume(TokenType.RBRACE, "Expected '}' after set")
            return self._postfix(SetLiteral(items))
        if self._match(TokenType.LBRACKET):
            items: List[Expr] = []
            if not self._check(TokenType.RBRACKET):
                items.append(self._expression())
                while self._match(TokenType.COMMA):
                    items.append(self._expression())
            self._consume(TokenType.RBRACKET, "Expected ']' after list literal")
            return self._postfix(ListLiteral(items))
        token = self._peek()
        raise NoxSyntaxError(f"Unexpected token {token.type}", token.line, token.column)

    def _parse_params(self) -> List[Param]:
        params: List[Param] = []
        if self._check(TokenType.RPAREN) or self._check(TokenType.COLON):
            return params
        vararg_seen = False
        while True:
            if self._match(TokenType.STAR):
                if vararg_seen:
                    token = self._previous()
                    raise NoxSyntaxError("Only one vararg parameter is allowed", token.line, token.column)
                name = self._consume(TokenType.IDENT, "Expected parameter name").value
                params.append(Param(name=name, default=None, is_vararg=True))
                vararg_seen = True
            else:
                name = self._consume(TokenType.IDENT, "Expected parameter name").value
                default = None
                if self._match(TokenType.EQ):
                    default = self._expression()
                params.append(Param(name=name, default=default, is_vararg=False))
            if not self._match(TokenType.COMMA):
                break
            if self._check(TokenType.RPAREN):
                break
        return params

    def _postfix(self, expr: Expr) -> Expr:
        while True:
            if self._match(TokenType.LPAREN):
                token = self._previous()
                args: List[Expr] = []
                if not self._check(TokenType.RPAREN):
                    args.append(self._expression())
                    while self._match(TokenType.COMMA):
                        args.append(self._expression())
                self._consume(TokenType.RPAREN, "Expected ')' after arguments")
                expr = self._with_expr_loc(Call(expr, args), token)
                continue
            if self._match(TokenType.LBRACKET):
                token = self._previous()
                index = self._expression()
                self._consume(TokenType.RBRACKET, "Expected ']' after index")
                expr = self._with_expr_loc(Index(expr, index), token)
                continue
            if self._match(TokenType.DOT):
                token = self._previous()
                name = self._consume(TokenType.IDENT, "Expected attribute name").value
                expr = self._with_expr_loc(GetAttr(expr, name), token)
                continue
            if self._match(TokenType.LBRACE):
                token = self._previous()
                if not isinstance(expr, Var):
                    raise NoxSyntaxError("Struct literal must start with struct name", token.line, token.column)
                fields: List[tuple[str, Expr]] = []
                if not self._check(TokenType.RBRACE):
                    field_name = self._consume(TokenType.IDENT, "Expected field name").value
                    self._consume(TokenType.COLON, "Expected ':' after field name")
                    field_value = self._expression()
                    fields.append((field_name, field_value))
                    while self._match(TokenType.COMMA):
                        if self._check(TokenType.RBRACE):
                            break
                        field_name = self._consume(TokenType.IDENT, "Expected field name").value
                        self._consume(TokenType.COLON, "Expected ':' after field name")
                        field_value = self._expression()
                        fields.append((field_name, field_value))
                self._consume(TokenType.RBRACE, "Expected '}' after struct literal")
                expr = self._with_expr_loc(StructInit(expr.name, fields), token)
                continue
            break
        return expr

    def _check_next_next(self, t: TokenType) -> bool:
        if self.current + 2 >= len(self.tokens):
            return False
        return self.tokens[self.current + 2].type == t

    def _check_next_next_next(self, t: TokenType) -> bool:
        if self.current + 3 >= len(self.tokens):
            return False
        return self.tokens[self.current + 3].type == t

    def _module_path(self, message: str) -> List[str]:
        parts = [self._consume(TokenType.IDENT, message).value]
        while self._match(TokenType.DOT):
            parts.append(self._consume(TokenType.IDENT, "Expected identifier after '.'").value)
        return parts

    def _with_loc(self, stmt: Stmt, token: Token) -> Stmt:
        setattr(stmt, "line", token.line)
        setattr(stmt, "column", token.column)
        return stmt

    def _with_expr_loc(self, expr: Expr, token: Token) -> Expr:
        setattr(expr, "line", token.line)
        setattr(expr, "column", token.column)
        return expr

    def _match(self, *types: TokenType) -> bool:
        for t in types:
            if self._check(t):
                self._advance()
                return True
        return False

    def _consume(self, t: TokenType, message: str) -> Token:
        if self._check(t):
            return self._advance()
        token = self._peek()
        raise NoxSyntaxError(message, token.line, token.column)

    def _check(self, t: TokenType) -> bool:
        if self._is_at_end():
            return False
        return self._peek().type == t

    def _check_next(self, t: TokenType) -> bool:
        if self.current + 1 >= len(self.tokens):
            return False
        return self.tokens[self.current + 1].type == t

    def _advance(self) -> Token:
        if not self._is_at_end():
            self.current += 1
        return self._previous()

    def _is_at_end(self) -> bool:
        return self._peek().type == TokenType.EOF

    def _peek(self) -> Token:
        return self.tokens[self.current]

    def _previous(self) -> Token:
        return self.tokens[self.current - 1]
