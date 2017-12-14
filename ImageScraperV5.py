'''
Author: Sabrina Flemming & Shreyan Sen
Class: CS229 at Stanford University
Date:

This program uses the google static maps api to source satalite image data, and will save the images
in the same folder in which this script is run

See https://developers.google.com/maps/documentation/static-maps/intro for more information on how
the API works

NOTE: ensure that your spreadsheet has columns in the order described by the
config variables in parseCsv(). If it does not, either adjust your spreadsheet
or adjust the config variables accordingly
'''
import urllib.parse
import csv
import os
import random
import sys
from urllib.request import *
from urllib.error import *

# Global variables used by the API
apiKey = "AIzaSyDifZ3ix-Db_U-Yc--HdSG7DoPmdoiG2H4"
baseURL = "https://maps.googleapis.com/maps/api/staticmap?"
# Tweakable variables to change how the image looks
imageSize = "640x640"
zoomLevel = 17
# Variables that deal with formatting the image PNG is reccomended as it is not lossy
scale = 2
imageFormat = "jpg"
mapType = "satellite"


def fetchImage(lat, lng, offset):
    '''
    Fetches an image from the google static map API
    parameter coords can be a lat lng pair in the following
    format: "lat,lng" or a qualified street address:
    "Jim's Cafe, New York, New York, USA"
    '''
    # Build a dict of params and their values
    paramMap = dict()
    paramMap["key"] = apiKey
    paramMap["zoom"] = zoomLevel
    # Add the offset to one or both to adjust where the imagery will show
    paramMap["center"] = str(float(lat) + float(offset)) + "," + lng
    paramMap["size"] = imageSize
    paramMap["scale"] = scale
    paramMap["format"] = imageFormat
    paramMap["maptype"] = mapType
    # Create URL to access image
    downloadURL = baseURL + urllib.parse.urlencode(paramMap)
    # Download image data to internal buffer
    return urllib.request.urlopen(downloadURL)


def writeImage(filename, data):
    '''
    Handles writing an image to a file
    '''
    f = open(filename, "wb")
    f.write(data.read())
    f.close()


def parseCsv(filename, offset):
    '''
    Parses a spreadsheet of the same format as Plant Data.xlsm
    Steps taken to properly format it:
        - File > Save as Plant Data.csv
        - Open the csv and reformat all cells to "General"
        - Split column 16 ("Lat,Lng") into two separate columns
    '''
    # Config variables: Used to adapt function to different spreadsheet
    idCol = 0
    nameCol = 1
    categoryCol = 14
    secondcategoryCol = 15
    latCol = 16
    lonCol = 17

    once_throughCol = 35
    natural_draftCol = 36
    mechanical_draftCol = 37
    dryCol = 38

    sourced = 0
    errors = 0

    if offset == "R":
        offset = random.uniform(0, 1)

    with open(filename) as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in reader:
            if (row[latCol] == "ND" or row[lonCol] == "ND"):
                # If the row doesn't contain a lat or lon, continue
                errors += 1
                continue
            elif (row[latCol] == "Lat"):
                # Skip the first line
                continue

            # Build coords string to pass in to fetchImage
            coords = row[latCol] + "," + row[lonCol]

            # Use to build 5-bit label
            mechdraft = 0
            natdraft = 0
            dry = 0
            once = 0
            nd = 0

            # Categorize

            if (row[mechanical_draftCol] == "1"):
                mechdraft = 1

            if (row[natural_draftCol] == "1"):
                natdraft = 1

            if (row[dryCol] == "1"):
                dry = 1

            if (row[once_throughCol] == "1"):
                once = 1

            if (row[categoryCol] == "ND"):
                nd = 1

            imageLabel = (str(mechdraft) + str(natdraft) + str(dry) + str(once) + str(nd))

            # Create directory structure compatible with TensorFlow
            writeDirectory = os.getcwd() + "/" + "Plants/" + imageLabel  # if you want to pool into a single folder drop the "imageLabel" option
            if not os.path.exists(writeDirectory):
                os.makedirs(writeDirectory)

            if float(offset) == 0:
                fileName = row[idCol] + "_" + row[nameCol] + "@" + row[latCol] + "+" \
                           + row[lonCol] + "_" + imageLabel + "." + imageFormat
            elif float(offset) > 0:
                fileName = row[idCol] + "_" + row[nameCol] + "@" + row[latCol] + "+" \
                           + row[lonCol] + "_offset" + offset + "_" + imageLabel + "." + imageFormat

            filePath = os.path.join(writeDirectory, fileName)
            try:
                # Try fetching the image and saving it
                # Adjust the offset Param accordingly (should be very, very
                # small as 1 degree of lat is approx 69 miles)

                data = fetchImage(row[latCol], row[lonCol], offset)
                writeImage(filePath, data)
                print("Saved image: ", filePath)
                sourced += 1
            except HTTPError as e:
                # Used to handle HTTP errors; Just prints error description and
                # continues trying to process the rest of the data csv
                errors += 1
                print(e.read(), "continuing to attempt sourcing images")

    print("Images succesfully sourced: ", sourced)
    print("Images not successfully sourced: ", errors)


if __name__ == "__main__":
    # Used to run the script if it is not imported into another python module
    # parseCsv(sys.argv[1], sys.argv[2])
    scriptPath = sys.argv[0]  # Location of script
    scriptFolder = os.path.dirname(scriptPath)  # Scripts stored here
    parseCsv(os.path.join(scriptFolder, "4_binomials_plant_data.csv"), 0)
