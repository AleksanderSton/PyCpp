"""
PyCpp - główny punkt wejścia kompilatora.

Wczytuje plik źródłowy (.pc), wykonuje:
  1. analizę leksykalną + składniową (parser.parse)
  2. analizę semantyczną (semantic.analyze)
  3. generowanie kodu C++ (codegen.generate)

Zapisuje wygenerowany kod C++ do pliku <nazwa>.cpp w tym samym katalogu
co plik źródłowy.

Błędy lekserskie/składniowe/semantyczne są raportowane w przyjazny sposób
z numerem linii i programem zakańcza się kodem wyjścia 1.
"""

import sys
import os

from parser import parse
from semantic import analyze, SemanticError


def compile_file(source_path):
    if not os.path.isfile(source_path):
        print(f"Błąd: plik '{source_path}' nie istnieje")
        sys.exit(1)

    with open(source_path, 'r', encoding='utf-8') as f:
        source = f.read()

    # --- Analiza leksykalna + składniowa ---
    try:
        tree = parse(source)
    except SyntaxError as e:
        print(f"Błąd składniowy: {e}")
        sys.exit(1)

    if tree is None:
        print("Błąd: plik źródłowy jest pusty albo nie zawiera żadnych instrukcji")
        sys.exit(1)

    # --- Analiza semantyczna ---
    try:
        analyze(tree)
    except SemanticError as e:
        print(f"Błąd semantyczny: {e}")
        sys.exit(1)

    # --- Generowanie kodu C++ ---
    from codegen import generate
    cpp_code = generate(tree)

    base, _ = os.path.splitext(source_path)
    cpp_path = base + '.cpp'

    with open(cpp_path, 'w', encoding='utf-8') as f:
        f.write(cpp_code)

    return cpp_path


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Użycie: python3 main.py <plik_zrodlowy.pc>")
        sys.exit(1)

    out_path = compile_file(sys.argv[1])
    print(out_path)