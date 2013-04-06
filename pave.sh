#! /bin/bash

example="$1"

if ! test -f "examples/${example}/__init__.py"
then echo "${example}: No such example in examples/ directory"
     exit 1
fi

mongo flowman --eval 'db.dropDatabase()'

. setup.rc
PYTHONPATH="examples:${PYTHONPATH}"

python -m ${example}.pave

