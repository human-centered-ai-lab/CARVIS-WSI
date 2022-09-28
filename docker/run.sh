#!/bin/bash

while getopts "c:l:r:t:s" flag
do
    case "${flag}" in
        c) CSV_FILE=${OPTARG};;
        l) EXPORT_LAYER=${OPTARG};;
        r) EXPORT_RESOLUTION=${OPTARG};;
        t) CELL_SIZE=${OPTARG};;
        s) HATCHED=${OPTARG};;
    esac
done

PARAMETERS="python3 /src/main.py"

if [ ! -z $CSV_FILE ]; then
    PARAMETERS+=" -c /data/$CSV_FILE"
else
    PARAMETERS+=" -c /data/"
fi

if [ ! -z $EXPORT_LAYER ]; then
    PARAMETERS+=" -l $EXPORT_LAYER"
fi

if [ ! -z $EXPORT_RESOLUTION ]; then
    PARAMETERS+=" -r $EXPORT_RESOLUTION"
fi

if [ ! -z $CELL_SIZE ]; then
    PARAMETERS+=" -t $CELL_SIZE"
fi

if [ ! -z $CELL_SIZE ]; then
    PARAMETERS+=" -s $HATCHED"
fi

eval $PARAMETERS