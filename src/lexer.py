import ply.lex as lex


# ---------------------------------------------------------------------------
# Słowa kluczowe
# ---------------------------------------------------------------------------
keywords = {
    'niech': 'NIECH',
    'Calk': 'CALK',
    'jesli': 'JESLI',
    'inaczej': 'INACZEJ',
    'dopoki': 'DOPOKI',
    'wypisz': 'WYPISZ',
    'wczytaj': 'WCZYTAJ',
    'i': 'AND',
    'lub': 'OR',
    'nie': 'NOT',
    'prawda': 'PRAWDA',
    'falsz': 'FALSZ',
}

tokens = [
    'ID',
    'LICZBA',
    'STRING',
    'PLUS', 'MINUS', 'MNOZENIE', 'DZIELENIE',
    'ROWNE', 'NIEROWNE', 'WIEKSZE', 'MNIEJSZE', 'WIEKSZE_ROWNE', 'MNIEJSZE_ROWNE',
    'PRZYPISANIE',
    'LPAREN', 'RPAREN',
    'DWUKROTEK',
    'NEWLINE',
    'INDENT',
    'DEDENT',
] + list(keywords.values())


# ---------------------------------------------------------------------------
# Proste reguły tokenów (operatory, nawiasy)
# ---------------------------------------------------------------------------
t_PLUS = r'\+'
t_MINUS = r'-'
t_MNOZENIE = r'\*'
t_DZIELENIE = r'/'
t_ROWNE = r'=='
t_NIEROWNE = r'!='
t_WIEKSZE_ROWNE = r'>='
t_MNIEJSZE_ROWNE = r'<='
t_WIEKSZE = r'>'
t_MNIEJSZE = r'<'
t_PRZYPISANIE = r'='
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_DWUKROTEK = r':'


# ---------------------------------------------------------------------------
# Identyfikatory i słowa kluczowe
# ---------------------------------------------------------------------------
def t_ID(t):
    r'[a-zA-Ząćęłńóśźż_][a-zA-Z0-9ąćęłńóśźżĄĆĘŁŃÓŚŹŻ_]*'
    t.type = keywords.get(t.value, 'ID')
    return t


# ---------------------------------------------------------------------------
# Liczby
# ---------------------------------------------------------------------------
def t_LICZBA(t):
    r'\d+'
    t.value = int(t.value)
    return t


# ---------------------------------------------------------------------------
# Stringi (tylko literały, np. dla wypisz("..."))
# ---------------------------------------------------------------------------
def t_STRING(t):
    r'"([^"\\]|\\.)*"'
    t.value = t.value[1:-1]  # usuń otaczające cudzysłowy
    return t


# ---------------------------------------------------------------------------
# Komentarze jednoliniowe (komentarze wieloliniowe ''' ''' są usuwane
# w preprocessingu, patrz _strip_multiline_comments)
# ---------------------------------------------------------------------------
def t_comment_singleline(t):
    r'\#.*'
    pass  # ignorowany


# ---------------------------------------------------------------------------
# Obsługa wcięć i nowych linii
# ---------------------------------------------------------------------------
# Strategia:
#  - lexer działa w dwóch fazach:
#      1) standardowy tokenizer PLY produkuje "surowy" potok tokenów,
#        w którym NEWLINE jest emitowany na końcu każdej niepustej linii,
#        a wcięcie linii jest mierzone i zapisywane jako (NEWLINE z poziomem wcięcia)
#      2) druga faza (post-processing) przelicza poziomy wcięć na INDENT/DEDENT
#
# Aby to zrobić w PLY w prosty sposób, zliczamy wcięcie na początku linii
# osobnym tokenem WS (whitespace), który jest widzialny tylko bezpośrednio
# po NEWLINE (czyli na początku linii logicznej).

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    t.type = 'NEWLINE'
    return t


# Białe znaki na początku linii (po NEWLINE) - liczymy szerokość wcięcia.
# Spacja = 1, Tab = 8 (standardowa konwencja, jak w Pythonie).
def _indent_width(s):
    width = 0
    for ch in s:
        if ch == '\t':
            width += 8 - (width % 8)
        else:
            width += 1
    return width


# Spacje/taby w środku linii (nie na początku) ignorujemy normalnie.
t_ignore = ' \t'


def t_error(t):
    raise SyntaxError(f"Nieznany znak '{t.value[0]}' w linii {t.lineno}")


# ---------------------------------------------------------------------------
# Preprocessing: usuwanie wieloliniowych komentarzy ''' ... '''
# ---------------------------------------------------------------------------
import re

_MULTILINE_COMMENT_RE = re.compile(r"'''.*?'''", re.DOTALL)


def _strip_multiline_comments(source):
    """
    Zamienia każdy komentarz ''' ... ''' (jedno- lub wieloliniowy) na
    odpowiadającą liczbę pustych linii, tak aby numery linii w resztę
    kodu pozostały niezmienione.
    """
    def repl(match):
        return '\n' * match.group(0).count('\n')

    return _MULTILINE_COMMENT_RE.sub(repl, source)


# ---------------------------------------------------------------------------
# Budowanie leksera bazowego (PLY)
# ---------------------------------------------------------------------------
_base_lexer = lex.lex()


# ---------------------------------------------------------------------------
# Wrapper: przekształca surowy potok tokenów na potok z INDENT/DEDENT
# ---------------------------------------------------------------------------
class IndentLexer:
    """
    Owija leksera PLY i dodatkowo wstawia tokeny INDENT/DEDENT
    na podstawie szerokości wcięć na początku każdej logicznej linii.
    """

    def __init__(self, source):
        self.source = _strip_multiline_comments(source)
        self.token_stream = self._generate_tokens()

    def _raw_tokens(self):
        """Generator surowych tokenów z PLY, działający linia po linii,
        żeby móc mierzyć wcięcia na początku każdej linii."""
        lexer = _base_lexer.clone()
        lines = self.source.split('\n')

        lineno = 0
        pending_newline = False

        for raw_line in lines:
            lineno += 1

            # Zmierz wcięcie linii (tylko spacje/taby na początku)
            stripped = raw_line.lstrip(' \t')
            indent_str = raw_line[:len(raw_line) - len(stripped)]

            # Linia pusta lub czysto-komentarzowa -> nie liczy się do wcięć,
            # ale może zawierać wieloliniowy komentarz - to obsłużymy uproszczono:
            # zakładamy, że ''' ... ''' nie przechodzi przez wiele linii z różnym wcięciem
            # w sposób, który psuje strukturę (typowy use-case w tym projekcie).
            if stripped == '' or stripped.startswith('#'):
                continue

            indent_width = _indent_width(indent_str)

            lexer.input(stripped)
            lexer.lineno = lineno

            line_tokens = []
            while True:
                tok = lexer.token()
                if not tok:
                    break
                if tok.type == 'NEWLINE':
                    continue  # NEWLINE dodamy ręcznie na końcu linii
                tok.lineno = lineno
                line_tokens.append(tok)

            if not line_tokens:
                continue

            yield ('LINE', indent_width, line_tokens, lineno)

    def _generate_tokens(self):
        indent_stack = [0]

        for kind, indent_width, line_tokens, lineno in self._raw_tokens():
            if indent_width > indent_stack[-1]:
                indent_stack.append(indent_width)
                tok = lex.LexToken()
                tok.type = 'INDENT'
                tok.value = None
                tok.lineno = lineno
                tok.lexpos = 0
                yield tok
            else:
                while indent_width < indent_stack[-1]:
                    indent_stack.pop()
                    tok = lex.LexToken()
                    tok.type = 'DEDENT'
                    tok.value = None
                    tok.lineno = lineno
                    tok.lexpos = 0
                    yield tok

                if indent_width != indent_stack[-1]:
                    raise SyntaxError(
                        f"Niezgodne wcięcie w linii {lineno}"
                    )

            for tok in line_tokens:
                yield tok

            nl = lex.LexToken()
            nl.type = 'NEWLINE'
            nl.value = '\n'
            nl.lineno = lineno
            nl.lexpos = 0
            yield nl

        # Na końcu plik: zamknij wszystkie pozostałe poziomy wcięć
        while len(indent_stack) > 1:
            indent_stack.pop()
            tok = lex.LexToken()
            tok.type = 'DEDENT'
            tok.value = None
            tok.lineno = lineno + 1
            tok.lexpos = 0
            yield tok

    def token(self):
        try:
            return next(self.token_stream)
        except StopIteration:
            return None

    # input() dla kompatybilności z interfejsem ply.lex
    def input(self, source):
        self.source = _strip_multiline_comments(source)
        self.token_stream = self._generate_tokens()


def build_lexer(source):
    return IndentLexer(source)


# ---------------------------------------------------------------------------
# Tryb testowy: uruchom plik bezpośrednio, aby zobaczyć potok tokenów
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Użycie: python3 lexer.py <plik_zrodlowy>")
        sys.exit(1)

    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        code = f.read()

    lx = build_lexer(code)
    while True:
        tok = lx.token()
        if not tok:
            break
        print(tok)