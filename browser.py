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

    def __init__(self, parent=None, debug=False):
        QNetworkAccessManager.__init__(self, parent)
        self.debug = debug

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


# Собственно, браузер
# Умеет ходить на указанные url'ы и выполнять там разные js-скрипты
# Использует пофиксенные кеш и менеджер
class Browser(QWebPage):

    def __init__(self, autojquerify=True, debug=False):
        QWebPage.__init__(self)
        self.autojquerify = autojquerify
        self.debug = debug

        self.cache = Cache()
        self.manager = Manager(debug=debug)
        self.waitloadstart = QEventLoop()
        self.loop = QEventLoop()
        self.cache.setCacheDirectory(CACHE_PATH)
        self.manager.setCache(self.cache)
        self.setNetworkAccessManager(self.manager)

        self.loadStarted.connect(self.onloadstarted)
        self.loadFinished.connect(self.loop.quit)

    def onloadstarted(self):
        self.loaded = True
        self.loop.quit()

    # Логгирование сообщений об ошибках при выполнении js
    def javaScriptConsoleMessage(self, msg, line, source):
        log.warning(colorize('jsconsole(): %s line %d: %s' % (source, line, msg), RED))

    # Засыпание на ms милисекунд
    def sleep(self, ms):
        QTimer.singleShot(ms, self.loop.quit)
        self.loop.exec_()

    # Выполнение js-скрипта
    def js(self, script):
        log.debug('js(): evalute %s' % colorize(script))
        result = self.mainFrame().evaluateJavaScript(script).toString()
        log.debug('js(): result %s' % colorize(result))
        
        self.loaded = False
        QTimer.singleShot(100, self.loop.quit)
        self.loop.exec_()

        if self.loaded:
            QTimer.singleShot(10000, self.loop.quit)
            self.loop.exec_()
            self.loaded = False


        self.loop.exec_()
        return result

    # Подгрузка на страницу jQuery
    def jquerify(self):
        log.info('jquerify(): load from %s' % colorize(JQUERY_PATH))
        jquery = open(JQUERY_PATH).read()
        self.mainFrame().evaluateJavaScript(jquery)

    # Высасывание страницы с указанного url
    # headers - правильные хидеры (например User-agent, Referrer), старые при этом затираются
    # pull - что выкачивать
    def get(self, url, headers = None, pull = None):
        log.info('get(): url %s' % colorize(url))
        self.js('window.location = "%s"' % url)     # идем на url

        if self.autojquerify:                       # если 
            self.jquerify()                         # подгружаем jQuery

    # Сохранение высосанных данных (например картинок)
    # Данные берутся из кеша по url'у  и сохраняются в path
    def save(self, url, path):
        log.info('save(): %s to %s ' % (colorize(url), colorize(path)))
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

    app = QApplication([])
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    QTimer.singleShot(0, test)
    sys.exit(app.exec_())