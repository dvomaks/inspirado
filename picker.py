# -*- coding: utf-8 -*-

import sys
import signal
from PyQt4.QtCore import QTimer
from PyQt4.QtGui import QApplication
from base import getlog, colorize, RED, GREEN

log = getlog('picker')

class Picker(QApplication):
    
    def __init__(self, info):
        QApplication.__init__(self, [])
        # qt из коробки не дружит с ctrl-c
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        self.info = info

        # выбираем нужный режим
        if self.info['mode'] == 'runup':
            QTimer.singleShot(0, self.runup)
        elif self.info['mode'] == 'pickup':
            QTimer.singleShot(0, self.pickup)

    def runup(self):
        raise NotImplementedError('This method is not implemented')

    def pickup(self):
        raise NotImplementedError('This method is not implemented')