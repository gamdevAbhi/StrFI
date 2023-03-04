import os

__fileDirectory = ''
__fontDirectory = ''
__canProceed = False
__currentLine = 0
__currentLineWord = ''

def assignVar(fileDirectory, fontDirectory):
    global __fileDirectory
    global __fontDirectory
    global __canProceed
    global __currentLine
    global __currentLineWord

    if (os.path.exists(fileDirectory) == False or os.path.exists(fontDirectory) == False): return 0
    __fileDirectory = fileDirectory
    __fontDirectory = fontDirectory
    __canProceed = True
    __currentLine = 0
    __currentLineWord = ''

    return 1

def getChar():
    global __currentLine
    global __canProceed
    global __currentLineWord

    if(__canProceed == False): return

    file = open(__fileDirectory, 'r', encoding='UTF-8')

    while __currentLineWord == '' or __currentLineWord == '\n':

        for i in range(__currentLine + 1):
            __currentLineWord = file.readline()
            
        if(__currentLineWord == '' and __currentLine == 0): return 'a'
        elif(__currentLineWord == ''): __currentLine = 0
        else: __currentLine += 1

        __currentLineWord = __currentLineWord.replace(" ", '')

    file.close()
    word = __currentLineWord[0]
    __currentLineWord = __currentLineWord[1:]

    return word

def getTTF():
    global __fontDirectory

    return __fontDirectory

