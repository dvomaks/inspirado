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
    formatter = Formatter('%(asctime)s %(name)-11s %(levelname)-8s %(message)s', '%d-%m-%y %H:%M:%S')
    handler = FileHandler('picker.log')
    handler.setFormatter(formatter)
    logger = getLogger(logname)
    logger.addHandler(handler)
    logger.setLevel(DEBUG)
    return logger


def colorize(message, color=YELLOW):
    if isinstance(message, (list, tuple)):
        return tuple(map(lambda el: COLOR_SEQ % color + str(el) + RESET_SEQ, message))
    return COLOR_SEQ % color + str(message) + RESET_SEQ


def newnym():
    print 'NEWNYM'
    conn = TorCtl.connect()
    conn.send_signal('NEWNYM')


if __name__ == '__main__':
    #parse(['run.py', '1', '1'])
    #print colorize('ololo')
    #print colorize((True, 'lalala'))

    log = getlog('test')
    log.debug('ololo')
