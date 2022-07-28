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
# - accomondate for different wsi files in one person's csv file
# - heatmap gets drawn on specified layer of wsi image!
# - get rid of empty image parts on level extraction
# - specify heatmap resolution in arguments. this will be the resolution in which
#   the layer extractions will return a thumbnail and the grid size will be matched
# - get_thumbnail and read_region are running forever/failing at lower levels
# - framewidth and frameheight: slide bereich auf bildschirm!
#

from curses import newpad
import os
import sys
import csv
import argparse
from os.path import exists
from ImageSection import ImageSection
from EyeData import EyeData
from HeatMapUtils import HeatMapUtils
from PersonWsiData import PersonWsiData
from openslide import open_slide
from openslide import OpenSlide, OpenSlideError
from openslide.deepzoom import DeepZoomGenerator

ROI_CHANGE_SIGNAL = "%7b%22"
wsiFileName = ""
wsiLevel = 0
parser = None

# reds csv and returns a nested list
# drops all EyeData until first filename is found as ImageSection
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
                # so it only has "None" values
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

                # until there is a new signal for roi change, drop all data
                if (roiChangeColumn != ROI_CHANGE_SIGNAL):
                    # ToDo: this should add data to the last image section!
                    continue

                # when there is a new roi change signal save all currently
                # collected data to existing image section and create a new one
                if (roiChangeColumn == ROI_CHANGE_SIGNAL):
                    ImageSectionList[-1].addTimestamps(imageSectionTimestamps)
                    ImageSectionList[-1].addEyeTracking(eyeDataList)

                    # after adding collected eye tracking data to corresponding image section
                    # clear the list for the next image section
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

                    # now add the filled out image section to the image section list
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

# loads all files found inside the csv files into dictionary.
# also sort csvData (ImageSections) by fileNames
# returns a dictionary as nested dictionary
# personWsiData[ImageName] = {ImageSection, ImageSection, ...}
def loadSVSFiles(csvData):
    personWsiData = { }
    imageSectionList = [ ]
    for imageSection in csvData:
        imageName = imageSection._fileName
        
        # redo:
        # first image sections needs to have a filename. save this as filename for the upcomming image sections
        # until another filename comes up
        if (imageName == 'None'):
            print("no file name for this image section")
            continue

        # just add to existing image
        if (imageName in personWsiData):
            imageSectionList.append(imageSection)
            personWsiData[imageName].appendImageSections(imageSectionList)

        # new image for frames
        else:
            imageSectionList.clear()
            wsiImage = readSVS(imageName)
            if (wsiImage is None):
                # bad
                continue            

            personWsiData[imageName] = PersonWsiData(wsiImage)
            imageSectionList.append(imageSection)
    
    lastKey = list(personWsiData.keys())[-1]
    personWsiData[lastKey].appendImageSections(imageSectionList)
    imageSectionList.clear()

    return personWsiData

if __name__ == "__main__":
    initArgumentParser()
    arguments = parser.parse_args()
    verifyInput(arguments)

    # read data from csv. 
    # then choose which input (csv filename and specifyed direcotry or specifyed file) to use.
    csvData = readCSV(arguments.c)

    #for imageSection in csvData:
    #    for timestamps in imageSection._eyeTracking:
    #        print(f'time: {timestamps}')

    '''wsiFileName = arguments.s
    if (wsiFileName is None):
        print("No Filename found inside CSV file. Please specify file.")
        terminate()'''

    personWsiData = loadSVSFiles(csvData)

    #for smth in personWsiData:
    #    print(f'loaded: {smth}')

    # ToDo: make extraction multi threaded
    # extract thumbnail of person's wsi images
    #resolutionX, resolutionY = getResolutionFromArgs(arguments)
    #heatMapUtils = HeatMapUtils(resolutionX, resolutionY)
    #for wsi in personWsiData:
    #    baseImage = heatMapUtils.extractJPG(personWsiData[wsi]._wsi)
    #    baseImage.show()


    #wsiSlide = readSVS(wsiFileName)

    #if (arguments.l):
    #    print(f'Layer resolutions: {wsiSlide.level_dimensions}')
    #    exit()

    print("done.")
    input()
    