import ply.yacc as yacc

from lexer import tokens, build_lexer  # noqa: F401  (tokens wymagane przez PLY)
import ast_nodes as ast


# ---------------------------------------------------------------------------
# Priorytety operatorów (od najniższego do najwyższego)
# ---------------------------------------------------------------------------
precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('right', 'NOT'),
    ('nonassoc', 'ROWNE', 'NIEROWNE', 'WIEKSZE', 'MNIEJSZE', 'WIEKSZE_ROWNE', 'MNIEJSZE_ROWNE'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MNOZENIE', 'DZIELENIE'),
    ('right', 'UMINUS'),  # minus unarny
)


# ---------------------------------------------------------------------------
# Program = sekwencja instrukcji najwyższego poziomu
# ---------------------------------------------------------------------------
def p_program(p):
    'program : stmt_list'
    p[0] = ast.Program(p[1])


# ---------------------------------------------------------------------------
# Lista instrukcji (rekurencyjnie)
# ---------------------------------------------------------------------------
def p_stmt_list_multi(p):
    'stmt_list : stmt_list stmt'
    p[0] = p[1] + [p[2]]


def p_stmt_list_single(p):
    'stmt_list : stmt'
    p[0] = [p[1]]


# ---------------------------------------------------------------------------
# Pojedyncza instrukcja
# ---------------------------------------------------------------------------
def p_stmt(p):
    '''stmt : var_decl
            | assign
            | if_stmt
            | while_stmt
            | print_stmt
            | read_stmt'''
    p[0] = p[1]


# ---------------------------------------------------------------------------
# Deklaracja zmiennej: niech ID : CALK = wyrazenie NEWLINE
# ---------------------------------------------------------------------------
def p_var_decl(p):
    'var_decl : NIECH ID DWUKROTEK CALK PRZYPISANIE expr NEWLINE'
    p[0] = ast.VarDecl(p[2], 'Calk', p[6], p.lineno(1))


# ---------------------------------------------------------------------------
# Przypisanie: ID = wyrazenie NEWLINE
# ---------------------------------------------------------------------------
def p_assign(p):
    'assign : ID PRZYPISANIE expr NEWLINE'
    p[0] = ast.Assign(p[1], p[3], p.lineno(1))


# ---------------------------------------------------------------------------
# Instrukcja warunkowa (opcja A - inaczej jesli jako chain)
# ---------------------------------------------------------------------------
def p_if_stmt(p):
    '''if_stmt : JESLI expr DWUKROTEK NEWLINE INDENT stmt_list DEDENT elif_chain else_opt'''
    branches = [(p[2], p[6])] + p[8]
    p[0] = ast.If(branches, p[9], p.lineno(1))


def p_elif_chain_multi(p):
    'elif_chain : elif_chain INACZEJ JESLI expr DWUKROTEK NEWLINE INDENT stmt_list DEDENT'
    p[0] = p[1] + [(p[4], p[8])]


def p_elif_chain_empty(p):
    'elif_chain : empty'
    p[0] = []


def p_else_opt_present(p):
    'else_opt : INACZEJ DWUKROTEK NEWLINE INDENT stmt_list DEDENT'
    p[0] = p[5]


def p_else_opt_empty(p):
    'else_opt : empty'
    p[0] = None


# ---------------------------------------------------------------------------
# Pętla: dopoki expr : NEWLINE INDENT stmt_list DEDENT
# ---------------------------------------------------------------------------
def p_while_stmt(p):
    'while_stmt : DOPOKI expr DWUKROTEK NEWLINE INDENT stmt_list DEDENT'
    p[0] = ast.While(p[2], p[6], p.lineno(1))


# ---------------------------------------------------------------------------
# wypisz(expr | string) NEWLINE
# ---------------------------------------------------------------------------
def p_print_stmt_expr(p):
    'print_stmt : WYPISZ LPAREN expr RPAREN NEWLINE'
    p[0] = ast.Print(p[3], p.lineno(1))


def p_print_stmt_string(p):
    'print_stmt : WYPISZ LPAREN STRING RPAREN NEWLINE'
    p[0] = ast.Print(ast.StringLiteral(p[3], p.lineno(1)), p.lineno(1))


# ---------------------------------------------------------------------------
# wczytaj(ID) NEWLINE
# ---------------------------------------------------------------------------
def p_read_stmt(p):
    'read_stmt : WCZYTAJ LPAREN ID RPAREN NEWLINE'
    p[0] = ast.Read(p[3], p.lineno(1))


# ---------------------------------------------------------------------------
# Wyrażenia
# ---------------------------------------------------------------------------
def p_expr_binop_arith(p):
    '''expr : expr PLUS expr
            | expr MINUS expr
            | expr MNOZENIE expr
            | expr DZIELENIE expr'''
    p[0] = ast.BinOp(p[2], p[1], p[3], p.lineno(2))


def p_expr_binop_compare(p):
    '''expr : expr ROWNE expr
            | expr NIEROWNE expr
            | expr WIEKSZE expr
            | expr MNIEJSZE expr
            | expr WIEKSZE_ROWNE expr
            | expr MNIEJSZE_ROWNE expr'''
    p[0] = ast.BinOp(p[2], p[1], p[3], p.lineno(2))


def p_expr_binop_logic(p):
    '''expr : expr AND expr
            | expr OR expr'''
    p[0] = ast.BinOp(p[2], p[1], p[3], p.lineno(2))


def p_expr_not(p):
    'expr : NOT expr'
    p[0] = ast.UnaryOp('nie', p[2], p.lineno(1))


def p_expr_uminus(p):
    'expr : MINUS expr %prec UMINUS'
    p[0] = ast.UnaryOp('-', p[2], p.lineno(1))


def p_expr_group(p):
    'expr : LPAREN expr RPAREN'
    p[0] = p[2]


def p_expr_number(p):
    'expr : LICZBA'
    p[0] = ast.Number(p[1], p.lineno(1))


def p_expr_bool_true(p):
    'expr : PRAWDA'
    p[0] = ast.Bool(True, p.lineno(1))


def p_expr_bool_false(p):
    'expr : FALSZ'
    p[0] = ast.Bool(False, p.lineno(1))


def p_expr_var(p):
    'expr : ID'
    p[0] = ast.Var(p[1], p.lineno(1))


# ---------------------------------------------------------------------------
# Reguła pomocnicza - puste wyprowadzenie
# ---------------------------------------------------------------------------
def p_empty(p):
    'empty :'
    p[0] = None


# ---------------------------------------------------------------------------
# Obsługa błędów składniowych
# ---------------------------------------------------------------------------
def p_error(p):
    if p is None:
        raise SyntaxError("Nieoczekiwany koniec pliku (brakuje instrukcji lub wcięcia)")
    raise SyntaxError(
        f"Błąd składniowy w linii {p.lineno}: nieoczekiwany token '{p.value}' (typ: {p.type})"
    )


# ---------------------------------------------------------------------------
# Budowanie parsera
# ---------------------------------------------------------------------------
_parser = yacc.yacc()


def parse(source):
    lexer = build_lexer(source)
    return _parser.parse(lexer=lexer)


# ---------------------------------------------------------------------------
# Tryb testowy
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Użycie: python3 parser.py <plik_zrodlowy>")
        sys.exit(1)

    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        code = f.read()

    tree = parse(code)
    print(tree)
    print(tree.statements)
