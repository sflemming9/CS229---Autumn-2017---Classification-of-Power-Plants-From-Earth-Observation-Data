# Resize images
import PIL
from PIL import Image
import os
import sys

# Define workspace paths
scriptPath = sys.argv[0]  # Location of script
scriptFolder = os.path.dirname(scriptPath)  # Scripts stored here


def resizeImage(basewidth, fileName):
    img = Image.open(fileName)
    wpercent = (basewidth / float(img.size[0]))
    hsize = int((float(img.size[1]) * float(wpercent)))
    img = img.resize((basewidth, hsize), PIL.Image.ANTIALIAS)
    img.save(fileName[:fileName]-4 + fileName[len(fileName)-4:])

def resizeImagesInDirectory(directory):
    filesAndDirectoriesList = os.listdir(directory)
    for item in filesAndDirectoriesList:
        if(os.path.isdir(item)) != true:
            resizeImage(item)


def resizeImagesInDirectoryRecursive(directory):
    filesAndDirectoriesList = os.listdir(directory)
    for item in filesAndDirectoriesList:
        if(!os.path.isdir(item)):
            resizeImage(item)   
        else:
            resizeImagesInDirectoryRecursive(item)

while __name__ == "__main__":
    basewidth = 224
    contents = os.listdir(scriptFolder)
    print(contents)
