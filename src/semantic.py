"""
Analizator semantyczny dla języka PyCpp.

Sprawdza:
  - czy zmienna jest zadeklarowana przed użyciem (w wyrażeniu, przypisaniu, wczytaj)
  - czy nie ma redeklaracji zmiennej (niech x: Calk = ... dwa razy dla tego samego x)
  - czy typy w wyrażeniach są zgodne (Calk vs Logiczny - patrz niżej)

Model typów:
  - 'Calk'     - liczba całkowita (int)
  - 'Logiczny' - wynik wyrażeń logicznych/porównań (bool), nie jest typem
                 zmiennej (zmienne mogą być tylko Calk), ale jest typem
                 *wyrażenia* używanym do sprawdzania warunków w jesli/dopoki.

Reguły typowania wyrażeń:
  - LICZBA                -> Calk
  - PRAWDA / FALSZ        -> Logiczny
  - ID (zmienna)          -> typ zadeklarowany (zawsze Calk w tym języku)
  - + - * /               -> Calk op Calk -> Calk
  - == != > < >= <=       -> Calk op Calk -> Logiczny
  - i / lub               -> Logiczny op Logiczny -> Logiczny
  - nie                   -> Logiczny -> Logiczny
  - unarny -              -> Calk -> Calk

Warunki w jesli/dopoki muszą mieć typ Logiczny.
Wyrażenie przypisywane do zmiennej Calk musi mieć typ Calk.
Argument wypisz(...) może być Calk, Logiczny lub StringLiteral.
"""

import ast_nodes as ast


class SemanticError(Exception):
    pass


CALK = 'Calk'
LOGICZNY = 'Logiczny'


class SemanticAnalyzer:
    def __init__(self):
        # Płaska tabela symboli (brak zagnieżdżonych zakresów - jeden
        # globalny "main" jak w prostym skrypcie)
        self.symbols = {}  # name -> type

    def analyze(self, program):
        for stmt in program.statements:
            self._check_stmt(stmt)

    # -----------------------------------------------------------------
    # Instrukcje
    # -----------------------------------------------------------------
    def _check_stmt(self, node):
        if isinstance(node, ast.VarDecl):
            self._check_var_decl(node)
        elif isinstance(node, ast.Assign):
            self._check_assign(node)
        elif isinstance(node, ast.If):
            self._check_if(node)
        elif isinstance(node, ast.While):
            self._check_while(node)
        elif isinstance(node, ast.Print):
            self._check_print(node)
        elif isinstance(node, ast.Read):
            self._check_read(node)
        else:
            raise SemanticError(
                f"Nieznany typ instrukcji: {type(node).__name__} (linia {node.lineno})"
            )

    def _check_var_decl(self, node):
        if node.name in self.symbols:
            raise SemanticError(
                f"Linia {node.lineno}: zmienna '{node.name}' została już zadeklarowana"
            )
        expr_type = self._check_expr(node.expr)
        if expr_type != CALK:
            raise SemanticError(
                f"Linia {node.lineno}: nie można przypisać wartości typu "
                f"'{expr_type}' do zmiennej typu 'Calk'"
            )
        self.symbols[node.name] = CALK

    def _check_assign(self, node):
        if node.name not in self.symbols:
            raise SemanticError(
                f"Linia {node.lineno}: zmienna '{node.name}' nie została zadeklarowana "
                f"(użyj 'niech {node.name}: Calk = ...')"
            )
        expr_type = self._check_expr(node.expr)
        var_type = self.symbols[node.name]
        if expr_type != var_type:
            raise SemanticError(
                f"Linia {node.lineno}: nie można przypisać wartości typu "
                f"'{expr_type}' do zmiennej '{node.name}' typu '{var_type}'"
            )

    def _check_if(self, node):
        for cond, body in node.branches:
            cond_type = self._check_expr(cond)
            if cond_type != LOGICZNY:
                raise SemanticError(
                    f"Linia {node.lineno}: warunek instrukcji 'jesli' musi być "
                    f"typu logicznego (otrzymano '{cond_type}')"
                )
            for stmt in body:
                self._check_stmt(stmt)

        if node.else_body is not None:
            for stmt in node.else_body:
                self._check_stmt(stmt)

    def _check_while(self, node):
        cond_type = self._check_expr(node.cond)
        if cond_type != LOGICZNY:
            raise SemanticError(
                f"Linia {node.lineno}: warunek pętli 'dopoki' musi być "
                f"typu logicznego (otrzymano '{cond_type}')"
            )
        for stmt in node.body:
            self._check_stmt(stmt)

    def _check_print(self, node):
        if isinstance(node.arg, ast.StringLiteral):
            return
        # dowolny typ Calk lub Logiczny można wypisać
        self._check_expr(node.arg)

    def _check_read(self, node):
        if node.name not in self.symbols:
            raise SemanticError(
                f"Linia {node.lineno}: zmienna '{node.name}' nie została zadeklarowana "
                f"(użyj 'niech {node.name}: Calk = ...' przed 'wczytaj')"
            )
        if self.symbols[node.name] != CALK:
            raise SemanticError(
                f"Linia {node.lineno}: 'wczytaj' wymaga zmiennej typu 'Calk'"
            )

    # -----------------------------------------------------------------
    # Wyrażenia - zwraca typ wyrażenia ('Calk' lub 'Logiczny')
    # -----------------------------------------------------------------
    def _check_expr(self, node):
        if isinstance(node, ast.Number):
            return CALK

        if isinstance(node, ast.Bool):
            return LOGICZNY

        if isinstance(node, ast.Var):
            if node.name not in self.symbols:
                raise SemanticError(
                    f"Linia {node.lineno}: zmienna '{node.name}' nie została zadeklarowana"
                )
            return self.symbols[node.name]

        if isinstance(node, ast.UnaryOp):
            operand_type = self._check_expr(node.operand)
            if node.op == '-':
                if operand_type != CALK:
                    raise SemanticError(
                        f"Linia {node.lineno}: operator unarny '-' wymaga typu "
                        f"'Calk' (otrzymano '{operand_type}')"
                    )
                return CALK
            if node.op == 'nie':
                if operand_type != LOGICZNY:
                    raise SemanticError(
                        f"Linia {node.lineno}: operator 'nie' wymaga typu "
                        f"'Logiczny' (otrzymano '{operand_type}')"
                    )
                return LOGICZNY
            raise SemanticError(f"Linia {node.lineno}: nieznany operator unarny '{node.op}'")

        if isinstance(node, ast.BinOp):
            left_type = self._check_expr(node.left)
            right_type = self._check_expr(node.right)

            arith_ops = {'+', '-', '*', '/'}
            compare_ops = {'==', '!=', '>', '<', '>=', '<='}
            logic_ops = {'i', 'lub'}

            if node.op in arith_ops:
                if left_type != CALK or right_type != CALK:
                    raise SemanticError(
                        f"Linia {node.lineno}: operator '{node.op}' wymaga operandów "
                        f"typu 'Calk' (otrzymano '{left_type}' i '{right_type}')"
                    )
                return CALK

            if node.op in compare_ops:
                if left_type != CALK or right_type != CALK:
                    raise SemanticError(
                        f"Linia {node.lineno}: operator porównania '{node.op}' wymaga "
                        f"operandów typu 'Calk' (otrzymano '{left_type}' i '{right_type}')"
                    )
                return LOGICZNY

            if node.op in logic_ops:
                if left_type != LOGICZNY or right_type != LOGICZNY:
                    raise SemanticError(
                        f"Linia {node.lineno}: operator '{node.op}' wymaga operandów "
                        f"typu 'Logiczny' (otrzymano '{left_type}' i '{right_type}')"
                    )
                return LOGICZNY

            raise SemanticError(f"Linia {node.lineno}: nieznany operator '{node.op}'")

        raise SemanticError(
            f"Linia {node.lineno}: nieznany typ wyrażenia: {type(node).__name__}"
        )


def analyze(program):
    analyzer = SemanticAnalyzer()
    analyzer.analyze(program)
    return analyzer.symbols


# ---------------------------------------------------------------------------
# Tryb testowy
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    import sys
    from parser import parse

    if len(sys.argv) < 2:
        print("Użycie: python3 semantic.py <plik_zrodlowy>")
        sys.exit(1)

    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        code = f.read()

    tree = parse(code)
    symbols = analyze(tree)
    print("OK - analiza semantyczna przeszła poprawnie")
    print("Symbole:", symbols)
