# -*- coding: utf-8 -*-

import signal
from PyQt4.QtCore import QTimer
from PyQt4.QtGui import QApplication
from PyQt4.QtNetwork import QNetworkProxy
from base import getlog, colorize, RED, GREEN
from settings import TOR_HOST, TOR_PORT
from browser import Browser


log = getlog('picker')

class Picker(QApplication):
    
    def __init__(self, info):
        QApplication.__init__(self, [])
        # qt из коробки не дружит с Сtrl-С
        signal.signal(signal.SIGINT, signal.SIG_DFL)

        self.info = info

        # выбираем нужный режим
        if info['mode'] == 'collect':
            mode = self.collect
        elif info['mode'] == 'analyze':
            mode = self.analyze
        elif info['mode'] == 'pickup':
            mode = self.pickup

        QTimer.singleShot(0, mode)

        print info

        if info['mode'] == 'pickup':
            # ставим Tor в качестве прокси, чтобы ходить на сайт по многу раз
            log.info('tor proxy: %s' % (colorize('%s:%s' % (TOR_HOST, TOR_PORT))))
            proxy = QNetworkProxy(QNetworkProxy.Socks5Proxy, TOR_HOST, TOR_PORT)
            QNetworkProxy.setApplicationProxy(proxy)
            '''
            b = Browser()
            #b.show()
            b.get('http://2ip.ru/')
            ip = b.js("$('div.ip big').text()")
            print ip
            '''


    # выкачивание с сайта тонн капчи и разбиение ее на символы
    def collect(self):
        raise NotImplementedError('This method is not implemented')


    # создание и обучение нейронной сети на основе выкачанных капч
    def analyze(self):
        raise NotImplementedError('This method is not implemented')


    # получение бонуса
    def pickup(self):
        raise NotImplementedError('This method is not implemented')