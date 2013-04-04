#! /bin/bash

RUN_DIR=$(readlink -f .run)
SRC_DIR=$(readlink -f src)
#export PYTHONPATH=${SRC_DIR}:${RUN_DIR}/lib/python2.7/site-packages/autobahn-0.5.14-py2.7.egg
export PYTHONPATH=${SRC_DIR}:${RUN_DIR}/AutobahnPython/autobahn

python -m server.webapp
