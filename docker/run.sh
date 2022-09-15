#!/bin/bash

if [ $# -eq 1 ]; then
    python3 /src/main.py -c /data/ -l $1
else
    python3 /src/main.py -c /data/$1 -l $2
fi