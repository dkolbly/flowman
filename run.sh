#! /bin/bash

RUN_DIR=$(readlink -f .run)
SRC_DIR=$(readlink -f src)
export PYTHONPATH=examples:${SRC_DIR}:${RUN_DIR}/lib/python2.7/site-packages/autobahn-0.6.0-py2.7.egg:${RUN_DIR}/lib/python2.7/site-packages/mongoengine-0.7.9-py2.7.egg:$PYTHONPATH

python -m server.webapp
