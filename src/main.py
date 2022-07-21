#!/usr/bin/python3

''' 
main.py
draws heatmap of eye tracking on jpeg extraction of whole slide image
'''

# ToDo:
#
# - option for only exporting heatmap for one image(?)
# - get rid of empty image parts on level extraction (?)
# - specify heatmap resolution in arguments. this will be the resolution in which
#   the layer extractions will return a thumbnail and the grid size will be matched(?)
#

import os
import sys
import csv
import argparse
from os.path import exists
from ImageSection import ImageSection
from EyeData import EyeData
from HeatMapUtils import HeatMapUtils
from openslide import open_slide
from openslide import OpenSlide, OpenSlideError
from openslide.deepzoom import DeepZoomGenerator

ROI_CHANGE_SIGNAL = "%7b%22"
wsiFileName = ""
wsiLevel = 0
parser = None

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
                    # 13 ET_GazeLeftx
                    # 14 ET_GazeLefty
                    # 15 right x
                    # 16 right y

                    eyeDataList.append(EyeData(
                      row[13],
                      row[14],
                      row[15],
                      row[16],
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
def verifyInput(arguments):
    if (len(sys.argv) != 7):
        terminate()

    if (not os.path.isfile(arguments.c)):
        print("CSV file not found!")
        print(arguments.c)
        terminate()

    if (not os.path.isfile(arguments.s)):
        print("SVS file not found!")
        terminate()

# prints usage and exits
def terminate():
    parser.print_help()
    parser.exit()

# reads the svs file and extracs the needed
def readSVS(file):
    wsiSlide = open_slide(file)
    return wsiSlide

# initialises argument parser
def initArgumentParser():
    global parser
    parser = argparse.ArgumentParser(description="Extract a jpg of given resolution out of a wsi and draw a heatmap out of given csv file data.")
    parser.add_argument("-c", type=str, help="Csv file path (relative to current path)")
    parser.add_argument("-s", type=str, help="Svs file path (relative to current path)")
    parser.add_argument("-r", help="Tuple of resolution [x,y]. You will need to make sure to use the correct aspect ratio.")
    parser.add_argument("-l", action='store_true', help="[OPTIONAL] Output the layer resolutions of given svs file.")
    #parser.add_argument("-d", type=str, help="If the csv file contains the svs filename you can input the relative directory path to the svs file. (Only used if -s is not used)")
    #parser.add_argument("-l", type=int, help="The given layer's resolution gets exported. (Only used if no -r is not used)")

# gets relsolution from input argument
# returns (x, y) integer
def getResolutionFromArgs(arguments):
    # get resolution from string
    comma = arguments.r.find(",")
    x = int(arguments.r[: comma])
    comma += 1
    y = int(arguments.r[comma :])

    return (x, y)

if __name__ == "__main__":
    initArgumentParser()
    arguments = parser.parse_args()
    verifyInput(arguments)

    # read data from csv. 
    # then choose which input (csv filename and specifyed direcotry or specifyed file) to use.
    csvData = readCSV(arguments.c)
    wsiFileName = arguments.s

    if (wsiFileName is None):
        print("No Filename found inside CSV file. Please specify file.")
        terminate()

    wsiSlide = readSVS(wsiFileName)

    if (arguments.l):
        print(f'Layer resolutions: {wsiSlide.level_dimensions}')
        exit()

    resolutionX, resolutionY = getResolutionFromArgs(arguments)
    heatMapUtils = HeatMapUtils(resolutionX, resolutionY)

    baseImage = heatMapUtils.extractJPG(wsiSlide)
    if (baseImage is None):
        exit()
    #baseImage.show()

    imageWithSections = heatMapUtils.drawRoiOnImage(baseImage, csvData)
    #imageWithSections.show()

    imageWithPoints = heatMapUtils.calculateActivityValues(baseImage, csvData)
    imageWithPoints = heatMapUtils.drawLegend(imageWithPoints)
    imageWithPoints.show()

    # going further from here...

    print("done.")
    input()
    