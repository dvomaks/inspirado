# -*- coding: utf-8 -*-

from logging import getLogger, FileHandler, Formatter, DEBUG
from simplejson import loads

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = (i + 30 for i in range(8))
RESET_SEQ = '\x1b[0m'
COLOR_SEQ = '\x1b[1;%dm'

def getSiteData():
    pass


def getPurseData():
    pass


def parseSourceFile(path):
    data = open(path).read()
    return loads(data, encoding='ascii')


def getData(args):
    scriptName = args[0]
    args = args[1:]
    argsNumber = len(args)
    if argsNumber == 1:
        return parseSourceFile(args[0])
    if argsNumber == 2:
        siteData = getSiteData(args[0])
        purseData = getPurseData(args[1])
        return dict(siteData.items() + purseData.items())
    raise Exception('Invalid number of arguments.\n' + 'Usage: %s [site_id purse_id] | [source_file]' % scriptName)


def getLog(logname):
    formatter = Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
    handler = FileHandler('picker.log')
    handler.setFormatter(formatter)
    logger = getLogger(logname)
    logger.addHandler(handler)
    logger.setLevel(DEBUG)
    return logger


def colorize(message, color = WHITE):
    return COLOR_SEQ % color + message + RESET_SEQ