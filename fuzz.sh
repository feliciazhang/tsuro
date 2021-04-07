#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

export IS_TYPE_CHECKING="True"
export PATH="$PATH:~/.local/bin/"

for i in $(seq 0 100); do
    echo "Running $i"
    python3 -m TestHarnesses.fuzzers.xrules.fuzz | ../6/xrules | grep -v '"legal"' | grep -v '"cheating"' || true
done
