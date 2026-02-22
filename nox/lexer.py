from __future__ import annotations

from typing import Iterable, List

from .tokens import Token, TokenType
from .errors import NoxSyntaxError


KEYWORDS = {
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "repeat": TokenType.REPEAT,
    "not": TokenType.NOT,
    "and": TokenType.AND,
    "or": TokenType.OR,
    "define": TokenType.DEFINE,
    "for": TokenType.FOR,
    "in": TokenType.IN,
    "match": TokenType.MATCH,
    "case": TokenType.CASE,
    "break": TokenType.BREAK,
    "continue": TokenType.CONTINUE,
    "pass": TokenType.PASS,
    "times": TokenType.TIMES,
    "connect": TokenType.CONNECT,
    "from": TokenType.FROM,
    "as": TokenType.AS,
    "lambda": TokenType.LAMBDA,
    "trait": TokenType.TRAIT,
    "implement": TokenType.IMPLEMENT,
    "async": TokenType.ASYNC,
    "await": TokenType.AWAIT,
    "struct": TokenType.STRUCT,
    "with": TokenType.WITH,
    "try": TokenType.TRY,
    "except": TokenType.EXCEPT,
    "finally": TokenType.FINALLY,
    "class": TokenType.CLASS,
    "display": TokenType.PRINT,
    "input": TokenType.INPUT,
    "len": TokenType.LEN,
    "none": TokenType.NONE,
    "result": TokenType.RETURN,
}


class Lexer:
    def __init__(self, source: str) -> None:
        if source.startswith("\ufeff"):
            source = source.lstrip("\ufeff")
        self.source = source
        self.bracket_depth = 0

    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []
        indent_stack = [0]
        lines = self.source.splitlines()

        line_index = 0
        line_no = 1
        while line_index < len(lines):
            raw_line = lines[line_index]
            if raw_line.strip() == "" or raw_line.lstrip().startswith("#"):
                line_index += 1
                line_no += 1
                continue

            indent = self._count_indent(raw_line, line_no)
            # Skip indent/dedent tracking when inside brackets
            if self.bracket_depth == 0:
                if indent > indent_stack[-1]:
                    indent_stack.append(indent)
                    tokens.append(Token(TokenType.INDENT, None, line_no, 1))
                elif indent < indent_stack[-1]:
                    while indent < indent_stack[-1]:
                        indent_stack.pop()
                        tokens.append(Token(TokenType.DEDENT, None, line_no, 1))
                    if indent != indent_stack[-1]:
                        raise NoxSyntaxError("Indentation error", line_no, 1)

            line_tokens, end_index, end_line_no, end_line_len = self._lex_line(lines, line_index, line_no, indent)
            tokens.extend(line_tokens)
            tokens.append(Token(TokenType.NEWLINE, None, end_line_no, end_line_len + 1))
            line_index = end_index + 1
            line_no = end_line_no + 1

        while len(indent_stack) > 1:
            indent_stack.pop()
            tokens.append(Token(TokenType.DEDENT, None, line_no + 1, 1))

        tokens.append(Token(TokenType.EOF, None, line_no + 1, 1))
        return tokens

    def _count_indent(self, line: str, line_no: int) -> int:
        count = 0
        for ch in line:
            if ch == " ":
                count += 1
            elif ch == "\t":
                raise NoxSyntaxError("Tabs are not allowed for indentation", line_no, count + 1)
            else:
                break
        return count

    def _lex_line(
        self,
        lines: List[str],
        line_index: int,
        line_no: int,
        indent: int,
    ) -> tuple[List[Token], int, int, int]:
        tokens: List[Token] = []
        i = indent
        line = lines[line_index]
        length = len(line)
        current_index = line_index
        current_line_no = line_no

        while True:
            while i < length:
                ch = line[i]
                col = i + 1

                if ch in " \r\t":
                    i += 1
                    continue

                if ch == "#":
                    i = length
                    break

                if ch.isalpha() or ch == "_":
                    start = i
                    i += 1
                    while i < length and (line[i].isalnum() or line[i] == "_"):
                        i += 1
                    text = line[start:i]
                    tok_type = KEYWORDS.get(text, TokenType.IDENT)
                    value = text if tok_type == TokenType.IDENT else text
                    tokens.append(Token(tok_type, value, current_line_no, start + 1))
                    continue

                if ch.isdigit():
                    start = i
                    i += 1
                    while i < length and line[i].isdigit():
                        i += 1
                    if i < length and line[i] == ".":
                        i += 1
                        while i < length and line[i].isdigit():
                            i += 1
                    number_text = line[start:i]
                    value = float(number_text) if "." in number_text else int(number_text)
                    tokens.append(Token(TokenType.NUMBER, value, current_line_no, start + 1))
                    continue

                if ch == '"':
                    if i + 2 < length and line[i : i + 3] == '"""':
                        start_col = i + 1
                        i += 3
                        chars: List[str] = []
                        while True:
                            if i + 2 < length and line[i : i + 3] == '"""':
                                i += 3
                                break
                            if i >= length:
                                chars.append("\n")
                                current_index += 1
                                current_line_no += 1
                                if current_index >= len(lines):
                                    raise NoxSyntaxError("Unterminated string", current_line_no - 1, start_col)
                                line = lines[current_index]
                                length = len(line)
                                i = 0
                                continue
                            if line[i] == "\\" and i + 1 < length:
                                i += 1
                                esc = line[i]
                                if esc == "n":
                                    chars.append("\n")
                                elif esc == "t":
                                    chars.append("\t")
                                else:
                                    chars.append(esc)
                                i += 1
                                continue
                            chars.append(line[i])
                            i += 1
                        tokens.append(Token(TokenType.STRING, "".join(chars), line_no, start_col))
                        continue

                    start = i
                    i += 1
                    chars = []
                    while i < length and line[i] != '"':
                        if line[i] == "\\" and i + 1 < length:
                            i += 1
                            esc = line[i]
                            if esc == "n":
                                chars.append("\n")
                            elif esc == "t":
                                chars.append("\t")
                            else:
                                chars.append(esc)
                            i += 1
                            continue
                        chars.append(line[i])
                        i += 1
                    if i >= length or line[i] != '"':
                        raise NoxSyntaxError("Unterminated string", current_line_no, start + 1)
                    i += 1
                    tokens.append(Token(TokenType.STRING, "".join(chars), current_line_no, start + 1))
                    continue

                if ch == "+":
                    i += 1
                    tokens.append(Token(TokenType.PLUS, "+", current_line_no, col))
                    continue
                if ch == "-":
                    i += 1
                    tokens.append(Token(TokenType.MINUS, "-", current_line_no, col))
                    continue
                if ch == "*":
                    i += 1
                    tokens.append(Token(TokenType.STAR, "*", current_line_no, col))
                    continue
                if ch == "/":
                    i += 1
                    tokens.append(Token(TokenType.SLASH, "/", current_line_no, col))
                    continue

                if ch == "=":
                    if i + 1 < length and line[i + 1] == "=":
                        i += 2
                        tokens.append(Token(TokenType.EQEQ, "==", current_line_no, col))
                    else:
                        i += 1
                        tokens.append(Token(TokenType.EQ, "=", current_line_no, col))
                    continue
                if ch == "!" and i + 1 < length and line[i + 1] == "=":
                    i += 2
                    tokens.append(Token(TokenType.NEQ, "!=", current_line_no, col))
                    continue
                if ch == "<":
                    if i + 1 < length and line[i + 1] == "=":
                        i += 2
                        tokens.append(Token(TokenType.LTE, "<=", current_line_no, col))
                    else:
                        i += 1
                        tokens.append(Token(TokenType.LT, "<", current_line_no, col))
                    continue
                if ch == ">":
                    if i + 1 < length and line[i + 1] == "=":
                        i += 2
                        tokens.append(Token(TokenType.GTE, ">=", current_line_no, col))
                    else:
                        i += 1
                        tokens.append(Token(TokenType.GT, ">", current_line_no, col))
                    continue

                if ch == "(":
                    i += 1
                    self.bracket_depth += 1
                    tokens.append(Token(TokenType.LPAREN, "(", current_line_no, col))
                    continue
                if ch == ")":
                    i += 1
                    self.bracket_depth = max(0, self.bracket_depth - 1)
                    tokens.append(Token(TokenType.RPAREN, ")", current_line_no, col))
                    continue
                if ch == "{":
                    i += 1
                    self.bracket_depth += 1
                    tokens.append(Token(TokenType.LBRACE, "{", current_line_no, col))
                    continue
                if ch == "}":
                    i += 1
                    self.bracket_depth = max(0, self.bracket_depth - 1)
                    tokens.append(Token(TokenType.RBRACE, "}", current_line_no, col))
                    continue
                if ch == "[":
                    i += 1
                    self.bracket_depth += 1
                    tokens.append(Token(TokenType.LBRACKET, "[", current_line_no, col))
                    continue
                if ch == "]":
                    i += 1
                    self.bracket_depth = max(0, self.bracket_depth - 1)
                    tokens.append(Token(TokenType.RBRACKET, "]", current_line_no, col))
                    continue
                if ch == ":":
                    i += 1
                    tokens.append(Token(TokenType.COLON, ":", current_line_no, col))
                    continue
                if ch == ",":
                    i += 1
                    tokens.append(Token(TokenType.COMMA, ",", current_line_no, col))
                    continue
                if ch == ".":
                    i += 1
                    tokens.append(Token(TokenType.DOT, ".", current_line_no, col))
                    continue
                if ch == "@":
                    i += 1
                    tokens.append(Token(TokenType.AT, "@", current_line_no, col))
                    continue

                raise NoxSyntaxError(f"Unexpected character '{ch}'", current_line_no, col)

            break

        return tokens, current_index, current_line_no, len(line)
