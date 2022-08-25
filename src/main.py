#!/usr/bin/python3

''' 
main.py
draws heatmap of eye tracking on jpeg extraction of whole slide image
'''

# ToDo:
#
# - draw roi intensity for how long it has been on the screen
# - should heatmap grid size be spacifyed by the user?
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

# parses all EyeData parameters out of a roi string
# returns image section with only the parsed parameters
def getRoiParameters(row):
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

    return ImageSection(
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
        bottomRightY)

# reds csv and returns a nested list
# drops all EyeData until first filename is found as ImageSection
def readCSV(file):
    ImageSectionsDict = { } # holds all image sections as list with filename as key
    ImageSectionList = [ ]  # holds all image sections with eye data and timestamps per image section
    imageSectionTimestamps = [ ] # holds all timestamps 
    eyeDataList = [ ]   # all eye data
    oldFileName = "None"

    with open(file, newline='') as csvfile:
        csvFile = csv.reader(csvfile, delimiter=',')

        # sort data by ImageSections
        readOK = False

        for row in csvFile:
            if (row[0] == '1'): # line after "Row"
                readOK = True
                continue
            
            # in first line where timestamps are
            if (readOK):
                roiChangeColumn = row[11][:6].strip()

                # drop lines where eye tracking data is empty
                # when there is a new roi change signal save all currently
                # collected data to existing image section and create a new one
                if (roiChangeColumn == ROI_CHANGE_SIGNAL):
                    # save old file data

                    # first get all parameters
                    imageSection = getRoiParameters(row)
                    
                    # then add collected lists
                    imageSection.addTimestamps(imageSectionTimestamps)
                    imageSection.addEyeTracking(eyeDataList)
                    
                    # append image section
                    ImageSectionList.append(imageSection)

                    # clear collecting lists
                    imageSectionTimestamps.clear()
                    eyeDataList.clear()

                    # new file
                    if (imageSection._fileName != oldFileName):
                        ImageSectionsDict[oldFileName] = ImageSectionList.copy()
                        oldFileName = imageSection._fileName
                        ImageSectionList.clear()                        

                # collect imageSectionTimnestamps and eyeDataList here
                if (roiChangeColumn != ROI_CHANGE_SIGNAL):
                    # only if there was already a filename in csv file
                    # otherwise drop data
                    # also drop lines where are without eye tracking data
                    if (oldFileName != "None" and row[13] != ''):
                        imageSectionTimestamps.append(float(row[1]))

                        eyeData = EyeData(
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
                            row[25]
                        )
                        eyeDataList.append(eyeData)

        # also don't forget to save all pending eye tracking data to last fileName in ImageSectionsDict
        ImageSectionList[-1].addTimestamps(imageSectionTimestamps)
        ImageSectionList[-1].addEyeTracking(eyeDataList)

        ImageSectionsDict[oldFileName] = ImageSectionList.copy()

        imageSectionTimestamps.clear()
        eyeDataList.clear()

        return ImageSectionsDict.copy()

# checks if the user choosen input makes sense
def verifyInput(arguments):
    if (len(sys.argv) < 3):
        terminate()

    if (not os.path.isfile(arguments.c)):
        print("CSV file not found!")
        print(arguments.c)
        terminate()

    if (not arguments.s is None):
        if (not os.path.isfile(arguments.s)):
            print("SVS file not found!")
            terminate()

# prints usage and exits
def terminate():
    parser.print_help()
    parser.exit()

# reads the svs file and extracs the needed
def readSVS(file):
    file = "data/" + file

    if (not os.path.isfile(file)):
        print(f'could not find: {file}')
        return
    
    wsiSlide = open_slide(file)
    return wsiSlide

# initialises argument parser
def initArgumentParser():
    global parser
    parser = argparse.ArgumentParser(description="Extract a jpg of given resolution out of a wsi and draw a heatmap out of given csv file data.")
    parser.add_argument("-c", type=str, help="Csv file path (relative to current path)")
    parser.add_argument("-r", help="Tuple of resolution [x,y]. You will need to make sure to use the correct aspect ratio.")
    parser.add_argument("-s", nargs='?', type=str, help="[OPTIONAL] Svs file path (relative to current path)")
    parser.add_argument("l", nargs='?', help="Specify extraction layer. Resolution of layer will be read from the wsi metadata for every image seperately.")

# gets relsolution from input argument
# returns (x, y) integer
def getResolutionFromArgs(arguments):
    # get resolution from string
    comma = arguments.r.find(",")
    x = int(arguments.r[: comma])
    comma += 1
    y = int(arguments.r[comma :])

    return (x, y)

# prints certain information about the csv file
def debugCSV(csvData):
    for imageSection in csvData:
        print(f'fileName: {imageSection._fileName}')

# loads all svs files found inside the csv file into a dict
# returns dict where filename is key and an wsi as the value
def loadSVSFiles(imageSectionDict):
    wsiFiles = { }
    for fileName in imageSectionDict.keys():
        if (fileName == "None"):
            continue

        wsiFiles[fileName] = readSVS(fileName)
        print(f'got: {fileName}')

    return wsiFiles.copy()

if __name__ == "__main__":
    initArgumentParser()
    arguments = parser.parse_args()
    verifyInput(arguments)

    # read csv and svs files
    print("loading csv...")
    imageSectionsDict = readCSV(arguments.c)
    print("loading svs...")
    wsiFilesDict = loadSVSFiles(imageSectionsDict)

    pixelCountX, pixelCountY = getResolutionFromArgs(arguments)
    heatmapUtils = HeatMapUtils(pixelCountX, pixelCountY)
    for fileName in wsiFilesDict:
        # get base image and draw roi on image
        print(f'rendering thumbnail for {fileName}...')
        baseImage = heatmapUtils.extractJPG(wsiFilesDict[fileName])
        
        print("drawing roi...")
        roiImage = heatmapUtils.drawRoiOnImage(baseImage, imageSectionsDict[fileName])
        roiImage = heatmapUtils.drawLegend(roiImage)
        #roiImage.show()

        print("calculating heatmap...")
        heatmapImage = heatmapUtils.getHeatmap(roiImage, imageSectionsDict[fileName])
        #heatmapImage = heatmapUtils.calculateActivityValues(roiImage, imageSectionsDict[fileName])
        heatmapImage.show()

    # this option needs to specify the image
    #if (arguments.l):
    #    print(f'Layer resolutions: {wsiSlide.level_dimensions}')
    #    exit()

    print("done.")
    input()
    