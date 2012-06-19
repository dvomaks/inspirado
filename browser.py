# -*- coding: utf-8 -*-

import sys
import signal
from PyQt4.QtCore import QEventLoop, QFileInfo, QFile, QFileInfo, QUrl, QIODevice, QTimer
from PyQt4.QtGui import QApplication, QImage
from PyQt4.QtWebKit import QWebPage, QWebView
from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkDiskCache, QNetworkRequest
from settings import JQUERY_PATH, CACHE_PATH, SAVE_PATH
from base import getlog, colorize, RED, GREEN

log = getlog('browser')

# Немного пофиксенный кеш
# QNetworkDiskCache не сохраняет данные с флагом saveToDisk=False
# Сохраняем все данные, выставляя им saveToDisk=True
class Cache(QNetworkDiskCache):

    def prepare(self, metaData):
        metaData.setSaveToDisk(True)
        return QNetworkDiskCache.prepare(self, metaData)


# Менеджер с отладкой
class Manager(QNetworkAccessManager):

    def __init__(self, parent=None):
        QNetworkAccessManager.__init__(self, parent)

    '''
    def createRequest(self, op, request, device=None):
        request.setRawHeader('User-Agent', 'bebe')
        if self.debug:
            for header in request.rawHeaderList():
                print '%s: %s' %(header, request.rawHeader(header))

            print type(request.originatingObject())
            print
        
        return QNetworkAccessManager.createRequest(self, op, request, device)
    '''

class Waiter():
    def __init__():
        self.timer = 

    def wait(self, signal, timeout):
        signal.connect()


# Браузер, который умеет ходить на указанные url'ы и выполнять там разные js-скрипты
# autojq - подгрузка JQuery к загруженной странице
class Browser(QWebPage):

    def __init__(self, autojq=True):
        QWebPage.__init__(self)
        self.autojq = autojq

        self.loop = QEventLoop()

        # не получилось использовать просто QTimer.singleShot
        # пришлось написать так
        self.timer = QTimer()
        self.timer.setSingleShot(True);

        # фиксенные кеш и менеджер
        self.cache = Cache()
        self.manager = Manager()

        self.cache.setCacheDirectory(CACHE_PATH)
        self.manager.setCache(self.cache)
        self.setNetworkAccessManager(self.manager)

        self.loadStarted.connect(self.onloadstarted)
        self.loadFinished.connect(self.onloadfinished)

    def onloadstarted(self):
        self.timer.stop()
        self.timer.timeout.disconnect()
        self.loaded = True
        self.loop.quit()

    def onloadfinished(self):
        self.timer.stop()
        self.timer.timeout.disconnect()
        self.loop.quit()

    def onloadtimeout(self):
        self.loop.quit()

    def onloadrecall(self):
        self.loop.quit()


    # логгирование сообщений об ошибках при выполнении js
    def javaScriptConsoleMessage(self, msg, line, source):
        log.warning(colorize('jsconsole(): %s line %d: %s' % (source, line, msg), RED))


    # засыпание на ms милисекунд
    def sleep(self, ms):
        self.timer.timeout.connect(self.loop.quit)
        self.timer.start(ms)
        self.loop.exec_()


    # выполнение javascript... все не так просто
    # выполнение js может вызвать загрузку страницы, которая будет выпоняться асинхронно
    # нам требуется синхронная загрузка, поэтому лепим костыли
    # 
    def js(self, script):
        log.debug('js(): evalute %s' % colorize(script))
        result = self.mainFrame().evaluateJavaScript(script).toString()
        log.debug('js(): result %s' % colorize(result))
        
        self.loaded = False
        self.timer.timeout.connect(self.onloadrecall)
        self.timer.start(10)
        self.loop.exec_()

        if self.loaded:
            self.timer.timeout.connect(self.onloadtimeout)
            self.timer.start(10000)
            self.loop.exec_()

        return result


    # подгрузка на страницу jQuery
    def jquerify(self):
        log.debug('jquerify(): load from %s' % colorize(JQUERY_PATH))
        jquery = open(JQUERY_PATH).read()
        self.mainFrame().evaluateJavaScript(jquery)


    # Высасывание страницы с указанного url
    # headers - правильные хидеры (например User-agent, Referrer), старые при этом затираются
    # pull - что выкачивать
    def get(self, url, headers=None, pull=None):
        log.debug('get(): url %s' % colorize(url))
        self.js('window.location = "%s"' % url)     # идем на url

        if self.autojq:                             # если 
            self.jquerify()                         # подгружаем jQuery


    # Сохранение высосанных данных (например картинок)
    # Данные берутся из кеша по url'у  и сохраняются в path
    def save(self, url, path):
        log.debug('save(): %s to %s ' % (colorize(url), colorize(path)))
        file = QFile(path)
        cached = self.cache.data(QUrl(url)).readAll()
        if file.open(QIODevice.WriteOnly):
            file.write(cached)
        file.close()
        return path


    # Получение картинки, сохраненной в кеше
    def image(self, url):
        cached = self.cache.data(QUrl(url))
        img = QImage()
        img.loadFromData(cached.readAll())
        return img


    # Показ отладочного окна
    def show(self):
        self.view = QWebView()
        self.view.setPage(self)
        self.view.show()


if __name__ == '__main__':

    def test():
        b = Browser()
        b.show()
        b.get('http://www.google.com')
        b.js("$('#gbqfq').val('hello world')")

    app = QApplication([])
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    QTimer.singleShot(0, test)
    sys.exit(app.exec_())