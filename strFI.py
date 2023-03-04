import time
import cv2
import os
import readFI
import shutil
from threading import Thread
from PIL import Image, ImageDraw, ImageFont

__frameProgress = 0
__pixelProgress = 0
__imageProgress = 0
__videoProgress = -1
__stopThread = False
__updateRate = 1
__quality = 1
__waterMark = True
__startTime = 0
__isGray = False

def ShowProgress():
    global __frameProgress
    global __pixelProgress
    global __imageProgress
    global __videoProgress
    global __stopThread
    global __updateRate
    global __startTime

    while True:
        time.sleep(__updateRate)

        if(__stopThread == True):
            return 
        
        os.system('cls')

        if(__videoProgress > -1):
            print("video is creating")
            print("video creating progress = " + "{:.2f}".format(__videoProgress) + "%")
            print("process run time = {:.0f} seconds".format(time.time() - __startTime))
        else:
            print("the video/image is processing")
            print("total process done = " + "{:.2f}".format(__frameProgress) + "%")
            print("current frame pixel info get = " + "{:.2f}".format(__pixelProgress) + "%")
            print("current frame creating = " + "{:.2f}".format(__imageProgress) + "%")
            print("process run time = {:.0f} seconds".format(time.time() - __startTime))

__progress = Thread(target = ShowProgress, args = ())

def __createPixel(r, g, b):
    pixel = []
    pixel.append(r)
    pixel.append(g)
    pixel.append(b)
    return pixel

def __getVideo(path:str):
    if(os.path.exists(path)) == False:
        return -1
    return cv2.VideoCapture(path)

def __getFrame(video:cv2.VideoCapture, index:int):
    video.set(1, index)
    frame = video.read()[1]

    return frame

def __getPixelData(frame):
    global __pixelProgress

    pixels = []
    height, width = frame.shape[0], frame.shape[1]
    __pixelProgress = w = h = count = 0

    for h in range(height):
        row = []

        for w in range(width):
            r, g, b = frame[h, w, 2], frame[h, w, 1], frame[h, w, 0]
            row.append(__createPixel(r, g, b))
            count += 1
            __pixelProgress = (count / (height * width)) * 100

        pixels.append(row)
    
    return pixels

def __createFramePixelData(projectName, index, pixelInfo):
    global __imageProgress
    global __quality
    
    count = 0
    w = h = 0
    size = 20 if __quality == 1 else 16 if __quality == 2 else 12 if __quality == 3 else 8 if __quality == 4 else 4 if __quality == 5 else 1
    fontSize = 15 if __quality == 1 else 12 if __quality == 2 else 9 if __quality == 3 else 6 if __quality == 4 else 3 if __quality == 5 else 1

    fnt = ImageFont.truetype(readFI.getTTF(), fontSize)
    img = Image.new('RGB', (len(pixelInfo[0]), len(pixelInfo)), color='black')
    draw = ImageDraw.Draw(img)

    while h <= len(pixelInfo) - size:
        while w <= len(pixelInfo[0]) - size:
            r = g = b = 0

            for i in range(size):
                for j in range(size):
                    r += pixelInfo[h + i][w + j][0]
                    g += pixelInfo[h + i][w + j][1]
                    b += pixelInfo[h + i][w + j][2]

                    count += 1
                    __imageProgress = (count / (len(pixelInfo) * len(pixelInfo[0]))) * 100

            r = int(r / (size * size))
            g = int(g / (size * size))
            b = int(b / (size * size))

            if(r == 0 and g == 0 and b == 0): draw.text((w, h), " ", font=fnt, fill=(r, g, b), align="center")
            else: draw.text((w, h), readFI.getChar(), font=fnt, fill=(r, g, b), align="center")
            w += size

        w = 0
        h += size

    if index <= 100 and __waterMark == True:
        tagF = ImageFont.truetype("fonts/watermark.otf", 7)
        draw.text((len(pixelInfo[0]) - 85, len(pixelInfo) - 8), "created by - abhijit", font=tagF, fill=(255, 255, 255), align="center")

    if(__isGray == True): img = img.convert("L")
    img.save(os.getcwd() + "/" + projectName + "/" + str(index + 1) + "_frame.jpg")
    __imageProgress = 0

def __createVid(projectName, frameWidth, frameHeight, frameRate, totalFrame):
    global __videoProgress
    
    count = 0
    size = (int(frameWidth), int(frameHeight))
    vid = cv2.VideoWriter(projectName + '.mp4', cv2.VideoWriter_fourcc(*'mp4v'), int(frameRate), size)

    for i in range(totalFrame):
        img = cv2.imread(os.getcwd() + "/" + projectName + "/" + str(i + 1) + "_frame.jpg")
        vid.write(img)
        count += 1
        __videoProgress = (count / totalFrame) * 100

    
    vid.release()
    print("video is created at '{0}'".format(os.getcwd() + "/" + projectName + '.mp4'))

def createStrvid(projectName:str, videoPath:str, quality:int, fileDirectory="texts/macbeth.txt", fontDirectory='fonts/watermark.otf', isGray=False, waterMark=True):
    global __frameProgress
    global __stopThread
    global __progress
    global __quality
    global __waterMark
    global __startTime
    global __isGray

    __quality = quality
    __waterMark = waterMark
    __startTime = time.time()
    __isGray = isGray

    if(readFI.assignVar(fileDirectory, fontDirectory) == 0):
        print("font or file does not exist.")
        return
    
    if(os.path.exists(os.getcwd() + "/" + projectName)) == True:
        print("the project name = {0} is exist in the current directory.".format(projectName))
        return
    if(os.path.exists(videoPath)) == False:
        print("the video is not found in the {0} directory".format(videoPath))
        return 

    os.mkdir(os.getcwd() + "/" + projectName)

    video = __getVideo(videoPath)

    __progress.start()

    totalFrame = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    __frameProgress = 0

    for i in range(totalFrame):
        frame = __getFrame(video, i)
        pixelInfo = __getPixelData(frame)
        __createFramePixelData(projectName, i, pixelInfo)

        __frameProgress = (i + 1) / totalFrame * 100

    __createVid(projectName, video.get(3), video.get(4), video.get(5), totalFrame)
    shutil.rmtree(os.getcwd() + "/" + projectName)

    video.release()
    __stopThread = True

def createStrimg(projectName:str, path:str, quality:int, frameIndex=0, isVideo=True, fileDirectory="texts/macbeth.txt", fontDirectory='fonts/watermark.otf', isGray=False, waterMark=True):
    global __stopThread
    global __progress
    global __quality
    global __waterMark
    global __startTime
    global __isGray
    
    __quality = quality
    __waterMark = waterMark
    __startTime = time.time()
    __isGray = isGray
    
    if(readFI.assignVar(fileDirectory, fontDirectory) == 0):
        print("font or file does not exist.")
        return
    
    if(os.path.exists(os.getcwd() + "/" + projectName)) == True:
        print("the project name = {0} is exist in the current directory.".format(projectName))
        return
    if(os.path.exists(path)) == False:
        print("the video/image is not found in the {0} directory".format(path))
        return 

    os.mkdir(os.getcwd() + "/" + projectName)
    __progress.start()

    if isVideo == True:
        video = __getVideo(path)

        frame = __getFrame(video, frameIndex)
        pixelInfo = __getPixelData(frame)
        __createFramePixelData(projectName, frameIndex, pixelInfo)
        video.release()

    else:
        image = cv2.imread(path)
        pixelInfo = __getPixelData(image)
        __createFramePixelData(projectName, 0, pixelInfo)

    __stopThread = True
    print("image is ready.. at = " + os.getcwd() + "/" + projectName)