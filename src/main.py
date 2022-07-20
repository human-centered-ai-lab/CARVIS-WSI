#!/usr/bin/python3

''' 
main.py
draws heatmap of eye tracking on jpeg extraction of whole slide image
'''

# ToDo:
#
# - heatmap gets drawn on specified layer of wsi image!
# - get rid of empty image parts on level extraction
# - specify heatmap resolution in arguments. this will be the resolution in which
#   the layer extractions will return a thumbnail and the grid size will be matched
# - get_thumbnail and read_region are running forever/failing at lower levels
# - framewidth and frameheight: slide bereich auf bildschirm!
#

import os
import sys
import csv
from os.path import exists
from ImageSection import ImageSection
from EyeData import EyeData
from HeatMapUtils import HeatMapUtils
from openslide import open_slide
from openslide import OpenSlide, OpenSlideError
from openslide.deepzoom import DeepZoomGenerator

ROI_CHANGE_SIGNAL = "%7b%22"
wsiLevel = 0

# options/settings via terminal args
# extract images, and save with heatmaps overlay and viewpath
# datapoints: eye tracking data is viewport specific

# usage: main.py <CSV File> <SVS FILE> <EXTRACTION LAYER>

# extracts the eye tracking data for all image sections
# returns: list of imageSections
def extractImageSections():
    pass

# reds csv and returns a nested list
def readCSV(file):
    ImageSectionList = []
    eyeDataList = []

    with open(file, newline='') as csvfile:
        csvFile = csv.reader(csvfile, delimiter=',')

        # sort data by ImageSections
        readOK = False
        imageSectionTimestamps = []

        for row in csvFile:
            if (row[0] == '1'): # line after "Row"
                readOK = True
                continue
            
            # in first line where timestamps are
            if (readOK):
                roiChangeColumn = row[11][:6]

                # initializing first image section
                # this does not have image section parameters,
                # so it only has "standard" values
                # -> user has not changed roi since start of the session
                if not ImageSectionList:
                    ImageSectionList.append(ImageSection(
                      "None",
                      0,
                      0,
                      0,
                      0,
                      0,
                      0,
                      0,
                      0,
                      0,
                      0,
                      0,
                      0,
                      0,
                      0
                    ))

                # until there is a new signal for roi change, save all eye tracking values
                # in eyeDataList and insert it to the existing and currently active image 
                # section (last one in ImageSectionList)
                if (roiChangeColumn != ROI_CHANGE_SIGNAL):
                    eyeDataList.append(EyeData(
                      row[17],
                      row[18],
                      row[19],
                      row[20],
                      row[21],
                      row[22],
                      row[23],
                      row[24],
                      row[25]))
                    
                    imageSectionTimestamps.append(row[1])

                # when there is a new roi change signal save all currently
                # collected data to existing image section and create a new one
                if (roiChangeColumn == ROI_CHANGE_SIGNAL):
                    ImageSectionList[-1].addTimestamps(imageSectionTimestamps)
                    ImageSectionList[-1].addEyeTracking(eyeDataList)

                    # after adding collected eye tracking data to corresponding image section
                    # clear the list so the next image section gets only its eye data
                    imageSectionTimestamps.clear()
                    eyeDataList.clear()

                    # now initialise a new ImageSection
                    # first get all needed parameters from the roi change string
                    roiChangeString = row[11]
                    nameStart = roiChangeString.find("Filename")
                    
                    if(nameStart == -1):
                        print("Something has gone terribly wrong. ROI change string has no Filename!")
                        exit()
                    
                    nameStart += 17 # offset for Filename%22%3a%22
                    nameEnd = roiChangeString.find(".svs")
                    nameEnd += 4 # offset for .svs

                    fileName = roiChangeString[nameStart : nameEnd]

                    # center x
                    centerXStart = roiChangeString.find("CurrentCenterX")
                    centerXStart += 20
                    centerXEnd = roiChangeString.find("CurrentCenterY")
                    centerXEnd -= 6

                    centerX = roiChangeString[centerXStart : centerXEnd]

                    # center y
                    centerYStart = roiChangeString.find("CurrentCenterY")
                    centerYStart += 20
                    centerYEnd = roiChangeString.find("CurrentDownsampleFactor")
                    centerYEnd -= 6

                    centerY = roiChangeString[centerYStart : centerYEnd]

                    # sample factor
                    sampleFactorStart = roiChangeString.find("CurrentDownsampleFactor")
                    sampleFactorStart += 29
                    sampleFactorEnd = roiChangeString.find("Width")
                    sampleFactorEnd -= 6

                    sampleFactor = roiChangeString[sampleFactorStart : sampleFactorEnd]

                    # width
                    widthStart = roiChangeString.find("Width")
                    widthStart += 11
                    widthEnd = roiChangeString.find("Height")
                    widthEnd -= 6

                    width = roiChangeString[widthStart : widthEnd]

                    # height

                    # now a new tmp substring is needed since there are 
                    # some parameters more than once in this string and otherwise
                    # and find only returns the location of the first appearance
                    # of a searched substring
                    roiChangeSubstring = roiChangeString[widthEnd:]
                    heightStart = roiChangeSubstring.find("Height")
                    heightStart += 12
                    heightEnd = roiChangeSubstring.find("CurrentCenterY")
                    heightEnd -= 6

                    height = roiChangeSubstring[heightStart : heightEnd]

                    # roi
                    roiStart = roiChangeSubstring.find("ViewROI")
                    roiStart += 7
                    roiEnd = roiChangeSubstring.find("TopLeft")

                    roi = roiChangeSubstring[roiStart : roiEnd]

                    # top left x
                    topLeftStart = roiChangeSubstring.find("TopLeft")
                    topLeftStart += 26
                    topLeftEnd = roiChangeSubstring.find("TopRight")
                    topLeftSubstring = roiChangeSubstring[topLeftStart : topLeftEnd]
                    topLeftEnd = topLeftSubstring.find("%2c%22")

                    topLeftX = topLeftSubstring[: topLeftEnd]

                    # top left y
                    topLeftYStart = topLeftSubstring.find("Y")
                    topLeftYStart += 7
                    topLeftYEnd = topLeftSubstring.find("TopRight")
                    topLeftYEnd -= 8

                    topLeftY = topLeftSubstring[topLeftYStart : topLeftYEnd]

                    # top right y
                    topRightStart = roiChangeSubstring.find("TopRight")
                    topRightStart += 27
                    topRightEnd = roiChangeSubstring.find("BottomLeft")
                    topRightSubstring = roiChangeSubstring[topRightStart : topRightEnd]
                    topRightEnd = topRightSubstring.find("%2c%22")

                    topRightX = topRightSubstring[: topRightEnd]

                    # top right y
                    topRightYStart = topRightSubstring.find("Y")
                    topRightYStart += 7
                    topRightYEnd = topRightSubstring.find("BottomLeft")
                    topRightYEnd -= 8

                    topRightY = topRightSubstring[topRightYStart : topRightYEnd]

                    # bottom left x
                    bottomLeftStart = roiChangeSubstring.find("BottomLeft")
                    bottomLeftStart += 29
                    bottomLeftEnd = roiChangeSubstring.find("BottomRight")
                    bottomLeftSubstring = roiChangeSubstring[bottomLeftStart : bottomLeftEnd]
                    bottomLeftEnd = bottomLeftSubstring.find("%2c%22")

                    bottomLeftX = bottomLeftSubstring[: bottomLeftEnd]

                    # bottom left y
                    bottomLeftYStart = bottomLeftSubstring.find("Y")
                    bottomLeftYStart += 7
                    bottomLeftYEnd = bottomLeftSubstring.find("BottomRight")
                    bottomLeftYEnd -= 8

                    bottomLeftY = bottomLeftSubstring[bottomLeftYStart : bottomLeftYEnd]

                    # bottom right x
                    bottomRightStart = roiChangeSubstring.find("BottomRight")
                    bottomRightStart += 30
                    bottomRightSubstring = roiChangeSubstring[bottomRightStart :]
                    bottomtRightEnd = bottomRightSubstring.find("%2c%22")

                    bottomRightX = bottomRightSubstring[: bottomtRightEnd]

                    # bottom right y
                    bottomRightYStart = bottomRightSubstring.find("Y")
                    bottomRightYStart += 7
                    bottomRightYEnd = bottomRightSubstring.find("%7d%7d%7d%7d")

                    bottomRightY = bottomRightSubstring[bottomRightYStart : bottomRightYEnd]


                    ImageSectionList.append(ImageSection(
                      fileName,
                      centerX,
                      centerY,
                      sampleFactor,
                      width,
                      height,
                      roi,
                      topLeftX,
                      topLeftY,
                      topRightX,
                      topRightY,
                      bottomLeftX,
                      bottomLeftY,
                      bottomRightX,
                      bottomRightY
                      ))

        # also don't forget to save all pending eye tracking data
        ImageSectionList[-1].addTimestamps(imageSectionTimestamps)
        ImageSectionList[-1].addEyeTracking(eyeDataList)

        imageSectionTimestamps.clear()
        eyeDataList.clear()

        return ImageSectionList

# checks if the user choosen input makes sense
def verifyInput():
    if (len(sys.argv) != 4):
        terminate()

    if not exists(sys.argv[1]):
        print("File not found!")
        terminate()
    
    if not os.path.exists(sys.argv[2]):
        print("Given data directory does not exist!")
        print("Note that the directory parameter must be relative to your current path.")
        terminate()
    
    global wsiLevel
    wsiLevel = int(sys.argv[3])

# prints usage and exits
def terminate():
    print("usage: main.py <CSV FILE> <SVS DIRECTORY> <EXTRACTION LAYER>")
    exit()

# reads the svs file and extracs the needed
def readSVS(file):
    if not exists(file):
        print(f'The needed WSI file: {file} does not exist!')
        terminate()

    wsiSlide = open_slide(file)
    return wsiSlide

if __name__ == "__main__":
    verifyInput()

    csvData = readCSV(sys.argv[1])

    wsiFileName = csvData[1]._fileName
    print(f'real filename: {wsiFileName}')
    wsiSlide = readSVS(sys.argv[2] + wsiFileName)

    dims = wsiSlide.level_dimensions
    print(f'wsi level: {wsiLevel}')
    print(f'image level {wsiLevel} dimensions: {dims[wsiLevel][0]}, {dims[wsiLevel][1]}\nlevel 0 dimensions: {wsiSlide.dimensions}')
    heatMapUtils = HeatMapUtils(dims[wsiLevel][0], dims[wsiLevel][1])

    baseImage = heatMapUtils.extractLayer(wsiSlide, wsiLevel)
    if (baseImage is None):
        exit()

    imageWithSections = heatMapUtils.drawRoiOnImage(baseImage, csvData)
    imageWithSections.show()

    # going further from here...

    print("done!")
    input()
    