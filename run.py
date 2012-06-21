# -*- coding: utf-8 -*-

import sys
import signal
from PyQt4.QtCore import QProcess, QTimer
from PyQt4.QtGui import QApplication
from psycopg2 import connect
from psycopg2.extras import DictCursor
from base import parse
from settings import IMPLEM_PATH, HOST, USER, DB, PASSWORD


def run():
    proxy = QNetworkProxy(QNetworkProxy.Socks5Proxy, '127.0.0.1', 9050)
    QNetworkProxy.setApplicationProxy(proxy)
    
    connstr = "host='%s' dbname='%s' user='%s' password='%s'" % (HOST, DB, USER, PASSWORD)
    conn = connect(connstr)
    cursor = conn.cursor(cursor_factory=DictCursor)
    cursor.execute("SELECT pid, bl FROM purse WHERE type = 'R'")
    purses = cursor.fetchall()
    cursor.execute("SELECT implem FROM site")
    sites = cursor.fetchall()

    for purse in purses:
        print '*** ', purse
        for site in sites:
            print '* ', site
            process = QProcess()
            print 'start'
            result = process.execute(IMPLEM_PATH, [site['implem'], purse['pid']])
            print 'finishwith result = ', result

    QApplication.exit()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    QTimer.singleShot(0, run)
    app = QApplication([])
    sys.exit(app.exec_())
