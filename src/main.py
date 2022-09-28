#!/usr/bin/python3

''' 
main.py
draws heatmap of eye tracking on jpeg extraction of whole slide image
'''

import os
import sys
import csv
import argparse
from os.path import exists
from ImageSection import ImageSection
from GazePoint import GazePoint
from HeatMapUtils import HeatMapUtils
from openslide import open_slide

EXPORT_DIR = "export/"
ROI_CHANGE_SIGNAL = "%7b%22"

wsiLevel = 0
parser = None

# parses all GazePoint parameters out of a roi string
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
# drops all GazePoints until first filename is found as ImageSection
def readCSV(file):
    ImageSectionsDict = { } # holds all image sections as list with filename as key
    ImageSectionList = [ ]  # holds all image sections with eye data and timestamps per image section
    imageSectionTimestamps = [ ] # holds all timestamps 
    gazePointList = [ ]   # all eye data
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
                    imageSection.addEyeTracking(gazePointList)
                    
                    # append image section
                    ImageSectionList.append(imageSection)

                    # clear collecting lists
                    imageSectionTimestamps.clear()
                    gazePointList.clear()

                    # new file
                    if (imageSection._fileName != oldFileName):
                        ImageSectionsDict[oldFileName] = ImageSectionList.copy()
                        oldFileName = imageSection._fileName
                        ImageSectionList.clear()                        

                # collect imageSectionTimnestamps and gazePointList here
                if (roiChangeColumn != ROI_CHANGE_SIGNAL):
                    # only if there was already a filename in csv file
                    # otherwise drop data
                    # also drop lines where are without eye tracking data
                    if (oldFileName != "None" and row[13] != ''):
                        imageSectionTimestamps.append(float(row[1]))

                        gazePoint = GazePoint(
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
                        gazePointList.append(gazePoint)

        # also don't forget to save all pending eye tracking data to last fileName in ImageSectionsDict
        if (len(ImageSectionList) >= 1):
            ImageSectionList[-1].addTimestamps(imageSectionTimestamps)
            ImageSectionList[-1].addEyeTracking(gazePointList)

            ImageSectionsDict[oldFileName] = ImageSectionList.copy()

            imageSectionTimestamps.clear()
            gazePointList.clear()

            return ImageSectionsDict.copy()

        else:
            return None

# checks if the user choosen input makes sense
def verifyInput(arguments):
    if (len(sys.argv) < 1):
        terminate()

    #if (not os.path.isfile(arguments.c)):
    #    print("ERROR: CSV file not found!\n")
    #    print(arguments.c)
    #    terminate()

    #if (not arguments.s is None):
    #    if (not os.path.isfile(arguments.s)):
    #        print("ERROR: SVS file not found!\n")
    #        terminate()

    if (arguments.r is None and arguments.l is None):
        print("ERROR: Specify ether render resolution or extraction layer!\n")
        terminate()

# prints usage and exits
def terminate():
    parser.print_help()
    parser.exit()

# reads the svs file and returns it
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
    parser.add_argument("-c", nargs='?', type=str, help="input directory path or csv file path (relative to current path. needs to contain svs files too.)")
    parser.add_argument("-r", nargs='?', help="Tuple of resolution [x,y]. You may want to make sure to use the correct aspect ratio.")
    parser.add_argument("-l", nargs='?', help="[OPTIONAL] Specify extraction layer. Resolution of layer will be read from the wsi metadata for every image seperately. Needed when -r is not used.")
    parser.add_argument("-t", nargs='?', help="[OPTIONAL] Specify cell size. How many pixels one side of the cell has (cells are always square). Default is 50.")
    parser.add_argument("-s", nargs='?', help="[OPTIONAL] Exports a hatched heatmap. Specify alpha value of hatching [0 - 255]. Default value is 170.")

# gets relsolution from input argument
# returns [x, y] tuple
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

# loads all svs files found inside the csv file into a dictionary
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

    csvFileList = []

    # check if export directory exists. if not create it
    if (not os.path.exists(EXPORT_DIR)):
        os.makedirs(EXPORT_DIR)

    # check if user has specifyed file or a directory
    if (not os.path.isfile(arguments.c)):
        print("No file specifyed, looking for a directory...")
        if (not os.path.isdir(arguments.c)):
            print("Need to specify at least input directory!")
            terminate()        

        # search for csv files inside given data directory
        for file in os.listdir(arguments.c):
            if (file.endswith(".csv")):
                inputDirectoryFile = arguments.c + file
                csvFileList.append(inputDirectoryFile)
                print(f'found: {file}')
        print(" ")
    else:
        csvFileList.append(arguments.c)        

    # now do this for every csv file
    for file in csvFileList:
        # read csv and svs files
        print(f'parsing {file}...')
        imageSectionsDict = readCSV(file)

        # check if meeting produced correct data
        if (imageSectionsDict is None):
            print("CSV File does not contain correct Image Section data!")
            print("-------------")
            continue

        print("loading svs...")
        wsiFilesDict = loadSVSFiles(imageSectionsDict)
        
        for fileName in wsiFilesDict:
            layer0Width, layer0Height = wsiFilesDict[fileName].level_dimensions[0]
            
            # check if layer or resolution is given for export
            exportPixelX = 0
            exportPixelY = 0
            heatmapUtils = object

            if (arguments.r):
                exportPixelX, exportPixelY = getResolutionFromArgs(arguments)
            
            else:
                exportPixelX, exportPixelY = wsiFilesDict[fileName].level_dimensions[int(arguments.l)]

            if (arguments.t):
                heatmapUtils = HeatMapUtils(exportPixelX, exportPixelY, layer0Width, layer0Height, arguments.t)

            else:
                heatmapUtils = HeatMapUtils(exportPixelX, exportPixelY, layer0Width, layer0Height)

            # working with files and extract information
            print(f'rendering thumbnail for {fileName}...')
            baseImage = heatmapUtils.extractJPG(wsiFilesDict[fileName])
            
            print("drawing roi...")
            roiImage = heatmapUtils.drawRoiOnImage(baseImage, imageSectionsDict[fileName])
            #roiImage = heatmapUtils.drawLegend(roiImage) # not for now...

            print("working on heatmap...")
            heatmapImage = heatmapUtils.getHeatmap(roiImage, imageSectionsDict[fileName])

            if (arguments.s):
                print("working on hatching...")
                alpha = int(arguments.s)
                hatchingImage = heatmapUtils.getHatchingHeatmap(baseImage, imageSectionsDict[fileName], alpha)
                #hatchingImage.show()

            # update name and save
            baseName = fileName[: len(fileName) - 4]
            pathologistName = file[6 : len(file) - 4]

            saveName = baseName
            hatchingName = baseName
            
            baseName += "_base_"
            baseName += pathologistName
            
            saveName += "_heatmap_"
            saveName += pathologistName
            saveName += ".jpg"

            hatchingName += "_hatching_"
            hatchingName += pathologistName
            hatchingName += ".jpg"
            
            print(f'saving {baseName} for pathologist {pathologistName}')

            # now save save image
            baseImage.save(EXPORT_DIR + baseName + ".jpg")
            heatmapImage.save(EXPORT_DIR + saveName)

            if (arguments.s):
                hatchingImage.save(EXPORT_DIR + hatchingName)

            # new line for every svs
            print(" ")

        # split off output for every csv file
        print("-------------")

    print("done.")
    