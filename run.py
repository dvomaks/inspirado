# -*- coding: utf-8 -*-

import sys
import signal
from PyQt4.QtCore import QProcess, QTimer
from PyQt4.QtGui import QApplication
from PyQt4.QtNetwork import QNetworkProxy
from psycopg2 import connect
from psycopg2.extras import DictCursor
from base import parse, newnym
from settings import IMPLEM_PATH, PG_HOST, PG_USER, PG_DB, PG_PASSWORD


def run():
    connstr = "host='%s' dbname='%s' user='%s' password='%s'" % (PG_HOST, PG_DB, PG_USER, PG_PASSWORD)
    conn = connect(connstr)
    cursor = conn.cursor(cursor_factory=DictCursor)
    cursor.execute("SELECT pid, bl FROM purse WHERE type = 'R'")
    purses = cursor.fetchall()
    cursor.execute("SELECT implem FROM site")
    sites = cursor.fetchall()

    for purse in purses:    
        print '*** ', purse
        #if purse['pid'] in ['113879698282', '379498666155'] :
        #if purse['pid'] in ['113879698282'] :
        #    continue
        for site in sites:
            print '* ', site
            #site = dict({'implem': 'iptest'})
            process = QProcess()
            print 'start'
            result = process.execute(IMPLEM_PATH, [site['implem'], purse['pid']])
            print 'finishwith result = ', result
        
        newnym()
    QApplication.exit()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    QTimer.singleShot(0, run)
    app = QApplication([])
    sys.exit(app.exec_())
