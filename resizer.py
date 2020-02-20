
import os
import sys
from PIL import Image

def resize(folder, fileName, factor,k):
    filePath = os.path.join(folder, fileName)
    im = Image.open(filePath)
    w, h  = im.size
    newIm = im.resize((int(w*factor), int(h*factor)))
    newIm.save(str(k)+".png", quality = 95)

def bulkResize(imageFolder, factor):
    imgExts = ["jpg","tif"]
    for path, dirs, files in os.walk(imageFolder):
	k=1
        for fileName in files:
            ext = fileName[-3:].lower()
            if ext in imgExts:
		print "Resizing"+" "+fileName
		resize(imageFolder, fileName, factor,k)
		k = k + 1

if __name__ == "__main__":
    imageFolder=sys.argv[1] # first arg is path to image folder
    resizeFactor=float(sys.argv[2])/100.0# 2nd is resize in %
    bulkResize(imageFolder, resizeFactor)
