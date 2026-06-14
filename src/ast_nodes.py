"""
Węzły drzewa składniowego (AST) dla języka PyCpp.

Każdy węzeł to prosta klasa z polem `lineno` (numer linii w kodzie źródłowym),
używanym do raportowania błędów semantycznych.
"""


class Node:
    def __init__(self, lineno=None):
        self.lineno = lineno


# ---------------------------------------------------------------------------
# Program / blok instrukcji
# ---------------------------------------------------------------------------
class Program(Node):
    def __init__(self, statements):
        super().__init__()
        self.statements = statements  # list[Node]


# ---------------------------------------------------------------------------
# Deklaracja zmiennej: niech x: Calk = wyrażenie
# ---------------------------------------------------------------------------
class VarDecl(Node):
    def __init__(self, name, var_type, expr, lineno):
        super().__init__(lineno)
        self.name = name        # str
        self.var_type = var_type  # str, np. "Calk"
        self.expr = expr        # Node (wyrażenie)


# ---------------------------------------------------------------------------
# Przypisanie: x = wyrażenie
# ---------------------------------------------------------------------------
class Assign(Node):
    def __init__(self, name, expr, lineno):
        super().__init__(lineno)
        self.name = name
        self.expr = expr


# ---------------------------------------------------------------------------
# Instrukcja warunkowa: jesli/inaczej jesli/inaczej
# ---------------------------------------------------------------------------
class If(Node):
    def __init__(self, branches, else_body, lineno):
        super().__init__(lineno)
        # branches: list[(cond_expr, body_statements)]
        # pierwszy element to "jesli", kolejne to "inaczej jesli"
        self.branches = branches
        self.else_body = else_body  # list[Node] lub None


# ---------------------------------------------------------------------------
# Pętla: dopoki WARUNEK : blok
# ---------------------------------------------------------------------------
class While(Node):
    def __init__(self, cond, body, lineno):
        super().__init__(lineno)
        self.cond = cond
        self.body = body  # list[Node]


# ---------------------------------------------------------------------------
# wypisz(...)
# ---------------------------------------------------------------------------
class Print(Node):
    def __init__(self, arg, lineno):
        super().__init__(lineno)
        self.arg = arg  # Node (wyrażenie) albo StringLiteral


# ---------------------------------------------------------------------------
# wczytaj(zmienna)
# ---------------------------------------------------------------------------
class Read(Node):
    def __init__(self, name, lineno):
        super().__init__(lineno)
        self.name = name  # str - nazwa zmiennej, do której wczytujemy


# ---------------------------------------------------------------------------
# Wyrażenia
# ---------------------------------------------------------------------------
class BinOp(Node):
    """Operacja binarna: lewa op prawa (arytmetyczna, porównanie, logiczna)"""
    def __init__(self, op, left, right, lineno):
        super().__init__(lineno)
        self.op = op  # str, np. '+', '==', 'i', 'lub'
        self.left = left
        self.right = right


class UnaryOp(Node):
    """Operacja unarna: -wyrażenie, nie wyrażenie"""
    def __init__(self, op, operand, lineno):
        super().__init__(lineno)
        self.op = op  # '-' lub 'nie'
        self.operand = operand


class Number(Node):
    def __init__(self, value, lineno):
        super().__init__(lineno)
        self.value = value  # int


class Bool(Node):
    def __init__(self, value, lineno):
        super().__init__(lineno)
        self.value = value  # bool (True/False)


class Var(Node):
    """Odwołanie do zmiennej (użycie w wyrażeniu)"""
    def __init__(self, name, lineno):
        super().__init__(lineno)
        self.name = name


class StringLiteral(Node):
    def __init__(self, value, lineno):
        super().__init__(lineno)
        self.value = value  # str
