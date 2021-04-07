#!/usr/bin/env bash
# A script to regenerate all of the static dependency diagrams in README.md

pydeps Common --reverse --exclude 'Common.*_test' 'typing_extensions' 'dataclasses' 'pyrsistent' 'pytest' 'Player' 'Common.tsuro_types' 'Common.validation' 'Common.typeguard' 'Common.result' 'Common.color' 'Common.util' --max-bacon=0  -o Planning/common-static.png -T png --noshow
pydeps Admin --reverse -xx Player Common --exclude hypothesis 'Admin.*_test' pytest 'Common.*_test' 'typing_extensions' 'dataclasses' 'pyrsistent' 'pytest' 'Player' 'Common.tsuro_types' 'Common.validation' 'Common.typeguard' 'Common.result' 'Common.color' 'Common.util' --max-bacon 2 -o Planning/admin-static.png -T png --noshow
pydeps Player --reverse -xx Player Common --exclude 'Player.*_test' 'typing_extensions' 'dataclasses' 'pyrsistent' 'pytest'  websockets -o Planning/player-static.png -T png --noshow --cluster
