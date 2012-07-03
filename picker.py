# -*- coding: utf-8 -*-

import signal
from PyQt4.QtCore import QTimer
from PyQt4.QtGui import QApplication
from PyQt4.QtNetwork import QNetworkProxy
from base import newnym, getlog, colorize, RED, GREEN
from settings import TOR_HOST, TOR_PORT
from browser import Browser


log = getlog('picker')

class Picker(QApplication):
    
    def __init__(self):
        QApplication.__init__(self, [])
        # qt из коробки не дружит с Сtrl-С
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        self.init()


    # задание размера изображения, набора символов
    def init(self):
        raise NotImplementedError('This method is not implemented')


    # выкачивание с сайта тонн капчи и разбиение ее на символы
    def collect(self):
        raise NotImplementedError('This method is not implemented')


    # создание и обучение нейронной сети на основе выкачанных капч
    def analyze(self):
        raise NotImplementedError('This method is not implemented')


    # получение бонуса
    def pickup(self):
        raise NotImplementedError('This method is not implemented')


    def startcollect(self):
        QTimer.singleShot(0, self.collect)


    def startanalyze(self):
        QTimer.singleShot(0, self.analyze)


    def startpickup(self, purse):
        # ставим Tor в качестве прокси, чтобы ходить на сайт по многу раз
        proxy = QNetworkProxy(QNetworkProxy.Socks5Proxy, TOR_HOST, TOR_PORT)
        QNetworkProxy.setApplicationProxy(proxy)
        newnym()

        '''
        b = Browser()
        b.get('http://2ip.ru/')
        ip = b.js("$('div.ip big').text()")
        hostname = b.js("$('.ip-info-entry table:eq(1) tr:eq(0) td').text().trim()")
        os = b.js("$('.ip-info-entry table:eq(1) tr:eq(1) td').text().trim()")
        browser = b.js("$('.ip-info-entry table:eq(1) tr:eq(2) td').text().trim()")
        location = b.js("$('.ip-info-entry table:eq(1) tr:eq(3) td').text().trim()")
        provider = b.js("$('.ip-info-entry table:eq(1) tr:eq(4) td').text().trim()")

        log.info('start(): proxy: %s:%s, ip: %s, hostname: %s, os: %s, browser: %s, location: %s, provider: %s' % 
                 (colorize((TOR_HOST, TOR_PORT, ip, hostname, os, browser, location, provider))))

        '''
        self.purse = purse
        QTimer.singleShot(0, self.pickup)