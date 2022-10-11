#!/bin/bash

while getopts 'c:l:r:t:s:vp:i:u:o:ab' flag;
do
    case "${flag}" in
        c) CSV_FILE=${OPTARG};;
        l) EXPORT_LAYER=${OPTARG};;
        r) EXPORT_RESOLUTION=${OPTARG};;
        t) CELL_SIZE=${OPTARG};;
        s) HATCHED=${OPTARG};;
        v) VIEW_PATH=true;;
        p) PATH_STRENGTH=${OPTARG};;
        i) PATH_COLOR=${OPTARG};;
        u) POINT_RADIUS=${OPTARG};;
        o) POINT_COLOR=${OPTARG};;
        a) CELL_HEATMAP_LABEL=${OPTARG};;
        b) ROI_HEATMAP_LABEL=${OPTARG};;
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

if [ ! -z $VIEW_PATH ]; then
    PARAMETERS+=" -v"
fi

if [ ! -z $PATH_STRENGTH ]; then
    PARAMETERS+=" -p $PATH_STRENGTH"
fi

if [ ! -z $PATH_COLOR ]; then
    PARAMETERS+=" -i $PATH_COLOR"
fi

if [ ! -z $POINT_RADIUS ]; then
    PARAMETERS+=" -u $POINT_RADIUS"
fi

if [ ! -z $POINT_COLOR ]; then
    PARAMETERS+=" -o $POINT_COLOR"
fi

if [ ! -z $CELL_HEATMAP_LABEL ]; then
    PARAMETERS+=" -a"
fi

if [ ! -z $ROI_HEATMAP_LABEL ]; then
    PARAMETERS+=" -b"
fi

eval $PARAMETERS