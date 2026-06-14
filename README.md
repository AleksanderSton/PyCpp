# PyCpp

Kompilator własnego języka programowania PyCpp do C++.

Projekt zaliczeniowy z przedmiotu **Budowa kompilatorów i semantyka języków programowania** .

Autor: Aleksander Stoń

---

## 1. Opis projektu

PyCpp to prosty język programowania o składni opartej na wcięciach
(jak w Pythonie), ze statycznym, mocnym typowaniem zmiennych. Kod źródłowy
PyCpp (plik `.pc`) jest tłumaczony (kompilowany) na kod źródłowy C++, który
następnie jest kompilowany przez `g++` i wykonywany.

Architektura kompilatora składa się z czterech etapów:

1. **Analiza leksykalna** (`lexer.py`) — tokenizacja kodu źródłowego,
   w tym obsługa wcięć (INDENT/DEDENT) na podstawie szerokości wcięcia
   (spacje lub taby).
2. **Analiza składniowa** (`parser.py`) — budowa drzewa AST (gramatyka
   LALR zaimplementowana w PLY/yacc).
3. **Analiza semantyczna** (`semantic.py`) — sprawdzanie deklaracji
   zmiennych, redeklaracji, zgodności typów w wyrażeniach i warunkach.
4. **Generowanie kodu** (`codegen.py`) — tłumaczenie AST na kod C++.

Całość spaja `main.py`, a skrypt `run.sh` automatyzuje cały proces
(kompilacja PyCpp → C++ → plik wykonywalny → uruchomienie).

---

## 2. Wymagania techniczne

- Python 3.10+
- biblioteka `ply` (Python Lex-Yacc)
- `g++` (kompilator C++, standard C++11 lub nowszy)

### Instalacja zależności (Linux / Zorin OS / Ubuntu)

```bash
sudo apt update
sudo apt install python3 python3-pip g++ make

pip install ply --break-system-packages
```

(jeśli używasz `venv`, wystarczy `pip install ply` bez flagi
`--break-system-packages`)

---

## 3. Sposób uruchomienia (dla prowadzącego)

### Szybki start

```bash
chmod +x run.sh
./run.sh examples/przyklad1.pc
```

Skrypt `run.sh`:
1. wywołuje `src/main.py`, który kompiluje plik `.pc` do `.cpp`
   (w tym samym katalogu co plik źródłowy),
2. kompiluje wygenerowany `.cpp` za pomocą `g++ -O2`,
3. uruchamia powstały plik wykonywalny.

W razie błędu leksykalnego, składniowego lub semantycznego, skrypt
wypisuje komunikat błędu z numerem linii i przerywa działanie
(kod wyjścia 1) bez próby kompilacji/uruchomienia.

### Uruchamianie poszczególnych etapów osobno

```bash
# tylko tokenizacja (podgląd potoku tokenów)
python3 src/lexer.py examples/przyklad1.pc

# tylko parsowanie (budowa AST)
python3 src/parser.py examples/przyklad1.pc

# tylko analiza semantyczna
python3 src/semantic.py examples/przyklad1.pc

# tylko generowanie kodu C++ (wypisuje na stdout)
python3 src/codegen.py examples/przyklad1.pc

# kompilacja PyCpp -> C++ (zapisuje plik .cpp, wypisuje jego ścieżkę)
python3 src/main.py examples/przyklad1.pc
```

---

## 4. Struktura projektu

```
PyCpp/
├── run.sh                  # skrypt automatyzujący kompilację i uruchomienie
├── README.md               # ten plik
├── src/
│   ├── lexer.py            # analiza leksykalna (tokeny, wcięcia, komentarze)
│   ├── ast_nodes.py         # definicje węzłów AST
│   ├── parser.py            # gramatyka i budowa AST (PLY/yacc)
│   ├── semantic.py          # analiza semantyczna (typy, deklaracje)
│   ├── codegen.py           # generator kodu C++
│   └── main.py              # punkt wejścia, łączy wszystkie etapy
└── examples/
    ├── przyklad1.pc                  # przykład ogólny (zmienne, jesli/inaczej, dopoki)
    ├── test_zmienne.pc                # deklaracje i przypisania zmiennych
    ├── test_operatory.pc              # operatory arytmetyczne, porównania, logiczne
    ├── test_warunki.pc                # jesli / inaczej jesli / inaczej
    ├── test_petla.pc                  # pętla dopoki
    ├── test_komentarze.pc             # komentarze jedno- i wieloliniowe
    ├── test_wejscie_wyjscie.pc        # wypisz / wczytaj
    ├── test_blad_niezadeklarowana.pc  # błąd: użycie niezadeklarowanej zmiennej
    ├── test_blad_redeklaracja.pc      # błąd: redeklaracja zmiennej
    ├── test_blad_typ_warunku.pc       # błąd: niezgodny typ warunku
    └── test_blad_wciecie.pc           # błąd: niepoprawne wcięcie
```

---

## 5. Specyfikacja języka PyCpp

### 5.1. Ogólne zasady

- Składnia oparta na **wcięciach** (jak w Pythonie) — blok kodu
  (ciało `jesli`, `inaczej`, `dopoki`) musi być wcięty względem
  nagłówka bloku. Wcięcie liczone jest jako szerokość białych znaków
  (spacja = 1, tabulator = 8, jak w Pythonie); poziomy wcięć muszą być
  konsekwentne.
- Każda instrukcja zajmuje jedną linię (kończy się znakiem nowej linii).
- Wszystkie słowa kluczowe są zapisane po polsku, **bez polskich
  znaków diakrytycznych** (np. `dopoki`, nie `dopóki`).

### 5.2. Słowa kluczowe

| Słowo kluczowe | Znaczenie                                  |
|-----------------|---------------------------------------------|
| `niech`         | deklaracja zmiennej                          |
| `Calk`          | typ całkowity (mapowany na `int` w C++)      |
| `jesli`         | instrukcja warunkowa — if                    |
| `inaczej`       | instrukcja warunkowa — else / else if        |
| `dopoki`        | pętla — while                                |
| `wypisz`        | wypisanie wartości na ekran                  |
| `wczytaj`       | wczytanie wartości z klawiatury              |
| `i`             | operator logiczny AND (`&&`)                 |
| `lub`           | operator logiczny OR (`||`)                  |
| `nie`           | operator logiczny NOT (`!`)                  |
| `prawda`        | wartość logiczna prawda (`true`)             |
| `falsz`         | wartość logiczna fałsz (`false`)             |

### 5.3. Zmienne

Deklaracja zmiennej zawsze podaje typ i wartość początkową:

```
niech x: Calk = 10
```

Przypisanie do istniejącej zmiennej:

```
x = x + 1
```

Wymagania semantyczne:
- zmienna musi być zadeklarowana przed użyciem,
- nie można zadeklarować zmiennej o nazwie, która już istnieje
  (redeklaracja jest błędem),
- typ wyrażenia przypisywanego do zmiennej musi być zgodny z jej typem
  (`Calk`).

Jedyny dostępny typ zmiennej to `Calk` (odpowiednik `int` w C++).
Wartości logiczne (`prawda`, `falsz`, wyniki porównań) mają typ
wewnętrzny `Logiczny` i mogą występować tylko jako wyrażenia (np.
warunki `jesli`/`dopoki` lub argumenty operatorów logicznych) —
nie można zadeklarować zmiennej typu logicznego.

### 5.4. Operatory

**Arytmetyczne** (operandy typu `Calk`, wynik typu `Calk`):

| Operator | Znaczenie     | Odpowiednik C++ |
|----------|---------------|-----------------|
| `+`      | dodawanie     | `+`             |
| `-`      | odejmowanie   | `-`             |
| `*`      | mnożenie      | `*`             |
| `/`      | dzielenie     | `/` (całkowite) |
| `-x`     | minus unarny  | `-x`            |

**Porównania** (operandy typu `Calk`, wynik typu `Logiczny`):

| Operator | Znaczenie      | Odpowiednik C++ |
|----------|----------------|-----------------|
| `==`     | równe          | `==`            |
| `!=`     | różne          | `!=`            |
| `>`      | większe        | `>`             |
| `<`      | mniejsze       | `<`             |
| `>=`     | większe-równe  | `>=`            |
| `<=`     | mniejsze-równe | `<=`            |

**Logiczne** (operandy typu `Logiczny`, wynik typu `Logiczny`):

| Operator | Znaczenie   | Odpowiednik C++ |
|----------|-------------|-----------------|
| `i`      | koniunkcja  | `&&`            |
| `lub`    | alternatywa | `\|\|`          |
| `nie`    | negacja     | `!`             |

**Przypisanie:**

| Operator | Znaczenie  |
|----------|------------|
| `=`      | przypisanie wartości do zmiennej |

### 5.5. Priorytety operatorów

Od najniższego do najwyższego:

1. `lub`
2. `i`
3. `nie` (unarny)
4. porównania: `==` `!=` `>` `<` `>=` `<=`
5. `+` `-`
6. `*` `/`
7. minus unarny (`-x`)

Nawiasy `( )` mogą być używane do zmiany kolejności obliczeń.

### 5.6. Instrukcja warunkowa

```
jesli WARUNEK:
    <instrukcje>
inaczej jesli WARUNEK:
    <instrukcje>
inaczej:
    <instrukcje>
```

- Część `inaczej jesli` może powtarzać się dowolną liczbę razy (chain,
  jak `elif` w Pythonie).
- Część `inaczej` jest opcjonalna.
- `inaczej jesli` i `inaczej` muszą być na tym samym poziomie wcięcia
  co odpowiadające im `jesli`.
- WARUNEK musi być wyrażeniem typu `Logiczny` (wynikiem porównania,
  operacji logicznej, lub wartością `prawda`/`falsz`); wyrażenia typu
  `Calk` w warunku są błędem semantycznym (brak ukrytej konwersji
  "niezerowe = prawda").

### 5.7. Pętla

```
dopoki WARUNEK:
    <instrukcje>
```

- Odpowiednik `while` w C++.
- WARUNEK musi być wyrażeniem typu `Logiczny` (te same reguły jak dla
  `jesli`).

### 5.8. Komentarze

**Jednoliniowe** — od znaku `#` do końca linii:

```
# to jest komentarz
niech x: Calk = 5  # komentarz nie jest obsługiwany jako "inline" po kodzie
```

**Wieloliniowe** — pomiędzy `'''` i `'''` (jak docstring w Pythonie),
mogą rozciągać się na wiele linii:

```
'''
To jest komentarz
wieloliniowy
'''
```

Komentarze są całkowicie ignorowane przez kompilator (usuwane przed
analizą leksykalną).

### 5.9. Instrukcje wejścia/wyjścia

**Wypisywanie wartości:**

```
wypisz(x)               # wypisuje wartość zmiennej / wyrażenia
wypisz("Tekst")          # wypisuje literał tekstowy
wypisz(x + 1)            # wypisuje wynik wyrażenia
wypisz(x > 0)            # wypisuje wynik wyrażenia logicznego (1/0)
```

Każde `wypisz` generuje nową linię na wyjściu (odpowiednik `cout << ... << endl;`).

**Wczytywanie wartości:**

```
niech x: Calk = 0
wczytaj(x)
```

`wczytaj` wymaga, aby argumentem była już zadeklarowana zmienna typu
`Calk`. Odpowiednik `cin >> x;` w C++.

### 5.10. Literały

- **Liczby całkowite**: ciąg cyfr, np. `0`, `42`, `1000`. Liczby ujemne
  uzyskuje się za pomocą minusa unarnego, np. `-5`.
- **Stringi**: tekst w cudzysłowach `"..."`, używany wyłącznie jako
  argument `wypisz(...)`. Język nie posiada typu zmiennej tekstowej.
- **Wartości logiczne**: `prawda`, `falsz`.

---

## 6. Obsługa błędów

Kompilator wykrywa i raportuje błędy na trzech poziomach, zawsze
z numerem linii, w której wystąpił problem:

| Rodzaj błędu             | Przykład komunikatu                                                              |
|--------------------------|-----------------------------------------------------------------------------------|
| Błąd leksykalny           | `Nieznany znak '@' w linii 3`                                                     |
| Błąd składniowy           | `Błąd składniowy w linii 6: nieoczekiwany token 'wypisz' (typ: WYPISZ)`           |
| Błąd semantyczny — niezadeklarowana zmienna | `Linia 6: zmienna 'y' nie została zadeklarowana`                  |
| Błąd semantyczny — redeklaracja             | `Linia 6: zmienna 'x' została już zadeklarowana`                  |
| Błąd semantyczny — niezgodny typ            | `Linia 5: warunek instrukcji 'jesli' musi być typu logicznego (otrzymano 'Calk')` |

W przypadku wykrycia błędu na którymkolwiek etapie, kompilacja jest
przerywana (kod wyjścia 1), plik `.cpp` nie jest generowany / program
nie jest kompilowany ani uruchamiany.

---

## 7. Przykładowy program

Plik `examples/przyklad1.pc`:

```
niech x: Calk = 10
jesli x > 10:
    wypisz("Wieksze niz 10")
inaczej jesli x == 10:
    wypisz("Rowne 10")
inaczej:
    wypisz("Mniejsze niz 10")

niech counter: Calk = 0
dopoki counter < 5:
    wypisz(counter)
    counter = counter + 1
```

Wygenerowany kod C++:

```cpp
#include <iostream>
using namespace std;

int main() {
    int x = 10;
    if ((x > 10)) {
        cout << "Wieksze niz 10" << endl;
    } else if ((x == 10)) {
        cout << "Rowne 10" << endl;
    } else {
        cout << "Mniejsze niz 10" << endl;
    }
    int counter = 0;
    while ((counter < 5)) {
        cout << counter << endl;
        counter = (counter + 1);
    }

    return 0;
}
```

Wynik działania:

```
Rowne 10
0
1
2
3
4
```

---

## 8. Pliki testowe (examples/)

Każdy plik testowy demonstruje konkretną funkcjonalność wymaganą
przez specyfikację projektu:

| Plik | Testowana funkcjonalność |
|------|---------------------------|
| `test_zmienne.pc` | deklaracja zmiennej, przypisanie, wyrażenia z udziałem zmiennych |
| `test_operatory.pc` | operatory arytmetyczne, porównania, logiczne (`i`, `lub`, `nie`), minus unarny |
| `test_warunki.pc` | `jesli` / `inaczej jesli` / `inaczej`, w tym wiele gałęzi i brak `inaczej jesli` |
| `test_petla.pc` | pętla `dopoki` z różnymi warunkami (proste, złożone, zliczanie w dół) |
| `test_komentarze.pc` | komentarze jednoliniowe (`#`) i wieloliniowe (`'''...'''`) |
| `test_wejscie_wyjscie.pc` | `wypisz` (tekst, liczby, wyrażenia) oraz `wczytaj` z `stdin` |
| `test_blad_niezadeklarowana.pc` | błąd semantyczny — użycie niezadeklarowanej zmiennej |
| `test_blad_redeklaracja.pc` | błąd semantyczny — redeklaracja zmiennej |
| `test_blad_typ_warunku.pc` | błąd semantyczny — warunek typu `Calk` w `jesli` |
| `test_blad_wciecie.pc` | błąd składniowy — brak wcięcia po `:` |

Aby przetestować plik wymagający danych z klawiatury:

```bash
echo "7" | ./run.sh examples/test_wejscie_wyjscie.pc
```

Aby przetestować pliki z błędami (oczekiwany kod wyjścia 1,
bez generowania pliku `.cpp`):

```bash
python3 src/main.py examples/test_blad_niezadeklarowana.pc
python3 src/main.py examples/test_blad_redeklaracja.pc
python3 src/main.py examples/test_blad_typ_warunku.pc
python3 src/main.py examples/test_blad_wciecie.pc
```

---

## 9. Implementacja — szczegóły techniczne

- **Lekser** (`lexer.py`): zbudowany na bibliotece `ply.lex`. Wcięcia
  są obliczane w osobnym etapie przetwarzania (`IndentLexer`), który
  dzieli kod źródłowy na linie logiczne, mierzy szerokość wcięcia każdej
  linii i generuje tokeny `INDENT`/`DEDENT` na podstawie stosu poziomów
  wcięć (analogicznie do tokenizera Pythona). Komentarze wieloliniowe
  `'''...'''` są usuwane w preprocessingu (przed podziałem na linie),
  z zachowaniem numeracji linii.
- **Parser** (`parser.py`): gramatyka LALR zbudowana na `ply.yacc`,
  z jawnie zdefiniowanymi priorytetami i łącznością operatorów
  (`precedence`). Buduje drzewo AST z węzłów zdefiniowanych
  w `ast_nodes.py`.
- **Analiza semantyczna** (`semantic.py`): jednoprzebiegowy,
  rekurencyjny visitor po AST z płaską tabelą symboli (jeden zasięg
  globalny, odpowiadający funkcji `main()`). Wylicza i sprawdza typy
  wyrażeń (`Calk` / `Logiczny`).
- **Generator kodu** (`codegen.py`): rekurencyjne tłumaczenie AST na
  tekst kodu C++, z odwzorowaniem 1:1 instrukcji PyCpp na instrukcje
  C++ (`if/else if/else`, `while`, `cout`, `cin`).
- **`main.py`**: punkt wejścia — wczytuje plik źródłowy, wykonuje
  wszystkie etapy w sekwencji, przechwytuje wyjątki `SyntaxError`
  i `SemanticError`, zapisuje wynikowy plik `.cpp`.
- **`run.sh`**: skrypt bash łączący `main.py` z kompilacją `g++`
  i uruchomieniem programu.

