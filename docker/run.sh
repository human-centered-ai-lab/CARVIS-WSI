#!/bin/bash

while getopts 'c:l:r:t:s:vp:i:j:u:o:d:f:abe' flag;
do
    case "${flag}" in
        c) CSV_FILE=${OPTARG};;
        l) EXPORT_LAYER=${OPTARG};;
        r) EXPORT_RESOLUTION=${OPTARG};;
        t) CELL_SIZE=${OPTARG};;
        s) HATCHED=${OPTARG};;
        v) VIEW_PATH=true;;
        p) PATH_STRENGTH=${OPTARG};;
        i) PATH_COLOR_START=${OPTARG};;
        j) PATH_COLOR_END=${OPTARG};;
        u) POINT_RADIUS=${OPTARG};;
        o) POINT_COLOR=${OPTARG};;
        a) CELL_HEATMAP_LABEL=true;;
        b) ROI_HEATMAP_LABEL=true;;
        d) HEATMAP_BACKGROUND_ALPHA=${OPTARG};;
        e) VIEWPATH_COLOR_LEGEND=true;;
        f) CANNY_EDGE_DETECTION=${OPTARG};;
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

if [ ! -z $VIEW_PATH ]; then
    PARAMETERS+=" -v"
fi

if [ ! -z $CELL_SIZE ]; then
    PARAMETERS+=" -t $CELL_SIZE"
fi

if [ ! -z $HATCHED ]; then
    PARAMETERS+=" -s $HATCHED"
fi

if [ ! -z $PATH_STRENGTH ]; then
    PARAMETERS+=" -p $PATH_STRENGTH"
fi

if [ ! -z $PATH_COLOR_START ]; then
    PARAMETERS+=" -i $PATH_COLOR_START"
fi

if [ ! -z $PATH_COLOR_END ]; then
    PARAMETERS+=" -j $PATH_COLOR_END"
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

if [ ! -z $HEATMAP_BACKGROUND_ALPHA ]; then
    PARAMETERS+=" -d $HEATMAP_BACKGROUND_ALPHA"
fi

if [ ! -z $VIEWPATH_COLOR_LEGEND ]; then
    PARAMETERS+=" -e"
fi

if [ ! -z $CANNY_EDGE_DETECTION ]; then
    PARAMETERS+=" -f $CANNY_EDGE_DETECTION"
fi

eval $PARAMETERS