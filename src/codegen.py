"""
Generator kodu C++ dla języka PyCpp.

Wejście: drzewo AST (Program z listą instrukcji).
Wyjście: tekst kodu C++ (jeden plik z funkcją main()).

Zakłada, że AST przeszło już analizę semantyczną (semantic.analyze) -
nie powtarza sprawdzania błędów, tylko generuje kod.
"""

import ast_nodes as ast


INDENT_UNIT = '    '  # 4 spacje


# Mapowanie operatorów PyCpp -> C++
BIN_OP_MAP = {
    '+': '+',
    '-': '-',
    '*': '*',
    '/': '/',
    '==': '==',
    '!=': '!=',
    '>': '>',
    '<': '<',
    '>=': '>=',
    '<=': '<=',
    'i': '&&',
    'lub': '||',
}

UNARY_OP_MAP = {
    '-': '-',
    'nie': '!',
}


class CodeGenerator:
    def __init__(self):
        self.lines = []

    def generate(self, program):
        self.lines = []
        self.lines.append('#include <iostream>')
        self.lines.append('using namespace std;')
        self.lines.append('')
        self.lines.append('int main() {')

        for stmt in program.statements:
            self._gen_stmt(stmt, 1)

        self.lines.append('')
        self.lines.append(INDENT_UNIT + 'return 0;')
        self.lines.append('}')
        self.lines.append('')

        return '\n'.join(self.lines)

    # -----------------------------------------------------------------
    # Instrukcje
    # -----------------------------------------------------------------
    def _gen_stmt(self, node, depth):
        if isinstance(node, ast.VarDecl):
            self._gen_var_decl(node, depth)
        elif isinstance(node, ast.Assign):
            self._gen_assign(node, depth)
        elif isinstance(node, ast.If):
            self._gen_if(node, depth)
        elif isinstance(node, ast.While):
            self._gen_while(node, depth)
        elif isinstance(node, ast.Print):
            self._gen_print(node, depth)
        elif isinstance(node, ast.Read):
            self._gen_read(node, depth)
        else:
            raise ValueError(f"Nieznany typ instrukcji w codegen: {type(node).__name__}")

    def _line(self, depth, text):
        self.lines.append(INDENT_UNIT * depth + text)

    def _gen_var_decl(self, node, depth):
        expr = self._gen_expr(node.expr)
        self._line(depth, f'int {node.name} = {expr};')

    def _gen_assign(self, node, depth):
        expr = self._gen_expr(node.expr)
        self._line(depth, f'{node.name} = {expr};')

    def _gen_if(self, node, depth):
        for i, (cond, body) in enumerate(node.branches):
            cond_str = self._gen_expr(cond)
            if i == 0:
                self._line(depth, f'if ({cond_str}) {{')
            else:
                self._line(depth, f'}} else if ({cond_str}) {{')
            for stmt in body:
                self._gen_stmt(stmt, depth + 1)

        if node.else_body is not None:
            self._line(depth, '} else {')
            for stmt in node.else_body:
                self._gen_stmt(stmt, depth + 1)

        self._line(depth, '}')

    def _gen_while(self, node, depth):
        cond_str = self._gen_expr(node.cond)
        self._line(depth, f'while ({cond_str}) {{')
        for stmt in node.body:
            self._gen_stmt(stmt, depth + 1)
        self._line(depth, '}')

    def _gen_print(self, node, depth):
        if isinstance(node.arg, ast.StringLiteral):
            text = self._escape_string(node.arg.value)
            self._line(depth, f'cout << "{text}" << endl;')
        else:
            expr = self._gen_expr(node.arg)
            self._line(depth, f'cout << {expr} << endl;')

    def _gen_read(self, node, depth):
        self._line(depth, f'cin >> {node.name};')

    # -----------------------------------------------------------------
    # Wyrażenia
    # -----------------------------------------------------------------
    def _gen_expr(self, node):
        if isinstance(node, ast.Number):
            return str(node.value)

        if isinstance(node, ast.Bool):
            return 'true' if node.value else 'false'

        if isinstance(node, ast.Var):
            return node.name

        if isinstance(node, ast.UnaryOp):
            op = UNARY_OP_MAP[node.op]
            operand = self._gen_expr(node.operand)
            return f'{op}({operand})'

        if isinstance(node, ast.BinOp):
            op = BIN_OP_MAP[node.op]
            left = self._gen_expr(node.left)
            right = self._gen_expr(node.right)
            return f'({left} {op} {right})'

        raise ValueError(f"Nieznany typ wyrażenia w codegen: {type(node).__name__}")

    @staticmethod
    def _escape_string(s):
        return s.replace('\\', '\\\\').replace('"', '\\"')


def generate(program):
    gen = CodeGenerator()
    return gen.generate(program)


# ---------------------------------------------------------------------------
# Tryb testowy
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    import sys
    from parser import parse
    from semantic import analyze

    if len(sys.argv) < 2:
        print("Użycie: python3 codegen.py <plik_zrodlowy>")
        sys.exit(1)

    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        code = f.read()

    tree = parse(code)
    analyze(tree)
    cpp_code = generate(tree)
    print(cpp_code)
