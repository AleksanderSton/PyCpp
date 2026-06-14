#!/bin/bash
#
# Użycie: ./run.sh program.pc
#
# Kompiluje plik źródłowy języka PyCpp do C++ (przez src/main.py),
# następnie kompiluje wygenerowany kod za pomocą g++ i uruchamia program.

set -e

if [ -z "$1" ]; then
    echo "Użycie: ./run.sh program.pc"
    exit 1
fi

SOURCE="$1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ ! -f "$SOURCE" ]; then
    echo "Błąd: plik '$SOURCE' nie istnieje"
    exit 1
fi

# 1. Kompilacja PyCpp -> C++
CPP_FILE=$(python3 "$SCRIPT_DIR/src/main.py" "$SOURCE")
if [ $? -ne 0 ]; then
    exit 1
fi

# 2. Kompilacja C++ -> plik wykonywalny
BIN_FILE="${CPP_FILE%.cpp}"
g++ -O2 -o "$BIN_FILE" "$CPP_FILE"

# 3. Uruchomienie
"$BIN_FILE"