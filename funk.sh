#!/bin/bash
PYTHONHOMEPATH="/home/lpouilloux/.local/"$(python -c "import sys,os; print os.sep.join(['lib', 'python' + sys.version[:3], 'site-packages'])")
export PYTHONPATH="$PYTHONHOMEPATH${PYTHONPATH:+:${PYTHONPATH}}"

exec ./funk "$@"
