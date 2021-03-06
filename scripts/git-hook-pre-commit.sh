#!/bin/bash

FILES=""
FILES="${FILES} $(find ./klaus -name '*.py' | tr '\n' ' ')"
ERRFLAG=0

OUTPUT=`pyflakes ${FILES} 2>&1`
if [ -n "$OUTPUT" ] ; then
    echo "pyflake errors:"
    echo "$OUTPUT"
    echo ""
    ERRFLAG=1
fi

OUTPUT=`pycodestyle ${FILES} | grep -Ev "E501|E402"`
if [ -n "$OUTPUT" ] ; then
    echo "pycodestyle errors:"
    echo "$OUTPUT"
    echo ""
    ERRFLAG=1
fi

if [ "${ERRFLAG}" == 1 ] ; then
    exit 1
fi
