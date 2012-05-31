from PyQt4.QtCore import QUrl, QFile, QFileInfo, QIODevice, QEventLoop
from PyQt4.QtGui import QApplication, QImage
from PyQt4.QtWebKit import QWebPage, QWebView
from PyQt4.QtNetwork import QNetworkAccessManager, QNetworkDiskCache
from settings import JQUERY_PATH, CACHE_PATH, SAVE_PATH
from base import getLog, colorize, RED, GREEN

log = getLog('browser')

# Немного пофиксенный кеш
# QNetworkDiskCache не сохраняет данные с флагом saveToDisk=False
# Сохраняем все данные, выставляя им saveToDisk=True
class Cache(QNetworkDiskCache):

    def prepare(self, metaData):
        metaData.setSaveToDisk(True)
        return QNetworkDiskCache.prepare(self, metaData)


# Собственно, браузер
# Умеет ходить на указанные url'ы и выполнять там разные js-скрипты
# Использует пофиксенные кеш и менеджер
class Browser(QWebPage):

    def __init__(self, debug = False):
        QWebPage.__init__(self)
        self.cache = Cache()
        self.manager = QNetworkAccessManager()
        self.loop = QEventLoop()
        self.shown = False
        self.cache.setCacheDirectory(CACHE_PATH)
        self.manager.setCache(self.cache)
        self.setNetworkAccessManager(self.manager)
        self.loadFinished.connect(self.loop.quit)

    # Логгирование сообщений об ошибках при выполнении js
    def javaScriptConsoleMessage(self, msg, line, source):
        log.warning(colorize('jsconsole(): %s line %d: %s' % (source, line, msg), RED))

    # Выполнение js-скрипта
    def js(self, script):
        log.debug('js(): evalute %s' % colorize(script))
        result = self.mainFrame().evaluateJavaScript(script).toString()
        log.debug('js(): result %s' % colorize(result))
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
        self.loop.exec_()                           # ждем пока досасется страница
        self.jquerify()                             # подгружаем jQuery

    # Сохранение высосанных данных (например картинок)
    # Данные берутся из кеша (для этого его и поправили) по url'у
    def save(self, url):
        name = SAVE_PATH + '/' + QFileInfo(QUrl(url).path()).fileName()
        log.info('save(): path %s' % colorize(name))
        file = QFile(name)
        cached = self.cache.data(QUrl(url)).readAll()
        if file.open(QIODevice.WriteOnly):
            file.write(cached)
        file.close()
        return name

    # Получение картинки, сохраненной в кеше
    def image(self, url):
        cached = self.cache.data(QUrl(url))
        img = QImage()
        img.loadFromData(cached.readAll())
        return img

    # Показ отладочного окна
    def show(self):
        self.shown = True
        self.view = QWebView()
        self.view.setPage(self)
        self.view.show()