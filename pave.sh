#! /bin/bash

example="$1"

if ! test -f "examples/${example}/__init__.py"
then echo "${example}: No such example in examples/ directory"
     exit 1
fi

mongo flowman --eval 'db.dropDatabase()'

mkdir -p .run/lib/app
rm -f .run/lib/app/${example}
ln -s $(readlink -f examples/${example}) .run/lib/app/${example}
cat > .run/lib/app/application.py <<EOF
NAME="${example}"
HOME="$(readlink -f examples/${example})"
import ${example} as MODULE
EOF

. setup.rc
#PYTHONPATH="examples:${PYTHONPATH}"

python -m ${example}.pave


#PYTHONPATH= python -c "import 
python -c "from application import MODULE; print MODULE.__doc__"
