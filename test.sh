#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

export IS_TYPE_CHECKING="True"
export PATH="$PATH:~/.local/bin/"

echo "Running unit tests..."
./xtest

echo "Running xtiles integration tests..."
cd ../3
cat "tile-tests/1-in.json" | ./xtiles | jq -cMS '.' | diff - <(cat "tile-tests/1-out.json" | jq -cMS '.')
cat "tile-tests/2-in.json" | ./xtiles | jq -cMS '.' | diff - <(cat "tile-tests/2-out.json" | jq -cMS '.')
cat "tile-tests/3-in.json" | ./xtiles | jq -cMS '.' | diff - <(cat "tile-tests/3-out.json" | jq -cMS '.')

echo "Running xboard integration tests..."
cd ../4
for i in $(seq 1 53); do
    cat "board-tests/$i-in.json" | ./xboard | diff - <(cat "board-tests/$i-out.json")
done

echo "Running robserver integration tests... (this may open some windows)"
cd ../Tsuro && LOG_LEVEL=WARNING python3 -m TestHarnesses.robserver_tester TestHarnesses/robserver_input/1-in.json &
cd ../5
./robserver 127.0.0.1 1337

echo "Running xrules integration tests..."
cd ../6
for i in $(seq 1 96); do
    cat "rules-tests/$i-in.json" | ./xrules | diff - "rules-tests/$i-out.json"
done

echo "Running xref integration tests..."
cd ../7
for i in $(seq 2 2); do
    cat "ref-tests/$i-in.json" | ./xref | jq -cMS '.' | diff - <(cat "ref-tests/$i-out.json" | jq -cMS '.')
done
