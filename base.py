# -*- coding: utf-8 -*-

from logging import getLogger, FileHandler, Formatter, DEBUG
from TorCtl import TorCtl

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = (i + 30 for i in range(8))
RESET_SEQ = '\x1b[0m'
COLOR_SEQ = '\x1b[1;%dm'

def siteinfo(id):
    return dict({'implem': id})


def purseinfo(id):
    return dict({'purse': 'R' + id})

# Разбор аргументов программы
def parse(argv):
    scriptname = argv[0]
    args = argv[1:]
    argnum = len(args)

    if argnum == 1:
        info = siteinfo(args[0])
        info['mode'] = 'runup'
        return info

    if argnum == 2:
        sinfo = siteinfo(args[0])
        pinfo = purseinfo(args[1])
        info = dict(sinfo.items() + pinfo.items())
        info['mode'] = 'pickup'
        return info

    raise Exception('Invalid number of arguments.\n' + 'Usage: %s site_id [purse_id]' % scriptname)


def getlog(logname):
    formatter = Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
    handler = FileHandler('picker.log')
    handler.setFormatter(formatter)
    logger = getLogger(logname)
    logger.addHandler(handler)
    logger.setLevel(DEBUG)
    return logger


def colorize(message, color = WHITE):
    return COLOR_SEQ % color + message + RESET_SEQ


def newnym():
    conn = TorCtl.connect()
    conn.send_signal("NEWNYM")


if __name__ == '__main__':
    parse(['run.py', '1', '1'])