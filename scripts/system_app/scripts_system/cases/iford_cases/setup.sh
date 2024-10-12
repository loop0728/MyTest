#!/bin/sh

if [ -z "$1" ]; then
    source ./cases/platform/sys/setup.sh
    source ./cases/platform/bsp/setup.sh
else
    source ./cases/platform/sys/setup.sh $1
    source ./cases/platform/bsp/setup.sh $1
fi
