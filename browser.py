# -*- coding: utf-8 -*-

import sys
import signal
from PyQt4.QtCore import QEventLoop, QFileInfo, QFile, QFileInfo, QUrl, QIODevice, QTimer
from PyQt4.QtGui import QApplication, QImage
from PyQt4.QtWebKit import QWebPage, QWebView
from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkDiskCache, QNetworkRequest
from settings import JQUERY_PATH, CACHE_PATH
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

# 

class Waiter():
    def __init__(self):
        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.loop = QEventLoop()
        self.timer.timeout.connect(self.ontimeout)


    def onsignal(self):
        self.timer.stop()
        self.loop.quit()
        self.waited = True


    def ontimeout(self):
        self.loop.quit()
        self.waited = False


    def wait(self, signal, ms):
        signal.connect(self.onsignal)
        self.timer.start(ms)
        self.loop.exec_()
        return self.waited


# Браузер, который умеет ходить на указанные url'ы и выполнять там разные js
# autojq - подгрузка JQuery к загруженной странице
# timeoutsec - т.к ходим через Tor, позволяем страницам грузится подольше
class Browser(QWebPage):

    def __init__(self, autojq=True, timeoutsec=120):
        QWebPage.__init__(self)
        self.autojq = autojq
        self.timeoutsec = timeoutsec

        self.loop = QEventLoop()
        self.waiter = Waiter()

        # фиксенные кеш и менеджер
        self.cache = Cache()
        self.manager = Manager()

        self.cache.setCacheDirectory(CACHE_PATH)
        self.manager.setCache(self.cache)
        self.setNetworkAccessManager(self.manager)

        log.info('init(): autojq: %s, timeoutsec: %s, cache: %s' % colorize((autojq, timeoutsec, CACHE_PATH)))


    # логгирование сообщений об ошибках при выполнении js
    #def javaScriptConsoleMessage(self, msg, line, source):
        #log.warning(colorize('jsconsole(): %s line %d: %s' % (source, line, msg), RED))


    # засыпание на sec секунд
    def sleep(self, sec):
        log.info('sleep(): start')
        QTimer.singleShot(sec * 1000, self.loop.quit)
        self.loop.exec_()
        log.info('sleep(): finish')


    # выполнение javascript... все не так просто
    # выполнение js может вызвать загрузку страницы, которая будет выпоняться асинхронно
    # нам требуется синхронная загрузка, поэтому воспользуемся waiter'ом
    def js(self, script):
        
        # выполняем js
        log.debug('js(): evalute %s' % colorize(script))
        result = self.mainFrame().evaluateJavaScript(script).toString()
        log.debug('js(): result %s' % colorize(result))
        
        # подождем немножко, вдруг прилетит сигнал о начале загрузки
        if self.waiter.wait(self.loadStarted, 30):
            # началась загрузка, ждем ее окончания за разумное время
            log.debug('js(): loading start')
            if self.waiter.wait(self.loadFinished, self.timeoutsec * 1000):
                log.debug('js(): loading fifnish')
            else:
                log.debug('js(): loading timeout')

            # подгружаем jQuery, если указано
            if self.autojq:
                self.jquerify()

        return result


    # подгрузка на страницу jQuery
    def jquerify(self):
        log.debug('jquerify(): load from %s' % colorize(JQUERY_PATH))
        jquery = open(JQUERY_PATH).read()
        self.mainFrame().evaluateJavaScript(jquery)


    # высасывание страницы с указанного url
    # headers - правильные хидеры (например User-agent, Referrer), старые при этом затираются
    # pull - что выкачивать
    def get(self, url, headers=None, pull=None):
        log.info('get(): url: %s' % colorize(url))
        self.js('window.location = "%s"' % url)     # идем на url


    # сохранение высосанных данных (например картинок)
    # данные берутся из кеша по url'у  и сохраняются в path
    def save(self, url, path):
        log.info('save(): %s to %s' % (colorize((url, path))))
        file = QFile(path)
        cached = self.cache.data(QUrl(url)).readAll()
        if file.open(QIODevice.WriteOnly):
            file.write(cached)
        file.close()
        return path


    # получение картинки, сохраненной в кеше
    def image(self, url):
        log.info('image(): from %s' % colorize(url))
        cached = self.cache.data(QUrl(url))
        img = QImage()
        img.loadFromData(cached.readAll())
        return img


    # показ отладочного окна
    def show(self):
        self.view = QWebView()
        self.view.setPage(self)
        self.view.show()


if __name__ == '__main__':

    def test1():
        '''
        b = Browser()
        b.show()
        b.get('http://www.opennet.ru')
        print b.js("$('div').length")
        b.js("$('input:eq(1)').val('hello')")
        '''
        

        b = Browser()
        b.show()
        b.get('http://2ip.ru/')
        print b.js("$('div.ip big').text()")

        '''
        newnym()
        b = Browser()
        b.show()
        b.get('http://2ip.ru/')
        print b.js("$('div.ip big').text()")

        newnym()
        b = Browser()
        b.show()
        b.get('http://2ip.ru/')
        print b.js("$('div.ip big').text()")
        '''
     

    def ontimeout():
        print 10

    def test2():
        print 0
        QTimer.singleShot(5000, ontimeout)

    app = QApplication([])


    signal.signal(signal.SIGINT, signal.SIG_DFL)
    QTimer.singleShot(0, test1)
    sys.exit(app.exec_())