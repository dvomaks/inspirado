# -*- coding: utf-8 -*-

import sys
from opencv.cv import *
from PyQt4.QtGui import QApplication
from picker import Picker
from browser import Browser
from transformer import Transformer, TransformError
from analyzer import Analyzer
from base import getlog, colorize, RED, GREEN, YELLOW
from settings import CAPTCHA_PATH, SYMBOLS_PATH

log = getlog('exchangecity')

class Implem(Picker):

    name = 'exchangecity'
    size = (20, 30)


    def collect(self):
        b = Browser()
        symbolqty = 5

        for i in xrange(100):
            log.info('LOAD PAGE WITH CAPTCHA')
            b.get('http://exchangecity.ru/?cmd=bonus')
            captcha = 'http://exchangecity.ru/include/anti_robot.php'
            b.save(captcha, CAPTCHA_PATH + Implem.name + '/%02d.png' % i)

            t = Transformer()
            t.load('orig', b.image(captcha))
            t.resizeby('resize', t['orig'], 2, 2)
            t.grayscale('grayscale', t['resize'], 2)
            t.binarize('binarize', t['grayscale'], 200, CV_THRESH_BINARY_INV)

            '''
            radius = 3
            kernel = cvCreateStructuringElementEx(radius * 2 + 1, radius * 2 + 1, radius, radius, CV_SHAPE_ELLIPSE)
            t.morphology('morphology', t['binarize'], 1, 1, kernel)
            '''

            t.contourSplit('breaksplit', t['binarize'], 0.001)

            if len(t.symbols) != symbolqty:
                log.debug(colorize('INCORRECT SYMBOL NUMBER', RED))
                continue

            t.normolize('origsplit', 'breaksplit', Implem.size)
            t.savesymbols('origsplit', SYMBOLS_PATH + Implem.name, '%02d' % i)
            del t


    def analyze(self):
        raise NotImplementedError('This method is not implemented')


    def pickup(self):

        # создаем браузер, которым будем ходить по wmtake.ru
        b = Browser()
        # создаем анализатор, которым будем распознавать капчу
        a = Analyzer(20, 30, '123456789ABCDEFGHIJKLMNPQRSTUVWXYZ')

        symbolqty = 5

        a.load('/home/polzuka/inspirado/nets/wmtake.ann')
        b.show()
        log.debug('LOADING PAGE WITH WM BONUS')
        b.get('http://wmtake.ru/m.base/bonus.php')

        while(True):
            log.debug('SAVING CAPTCHA')
            captcha = b.js('$("#scode-pic img")[0].src')
            #b.save(captcha, '/home/polzuka/inspirado/captcha/wmtake/%02d.gif' % i)

            log.debug('CAPTCHA TRANSFORMING')
            t = Transformer('orig', b.image(captcha))
            t.resizeby('resize', t['orig'], 2, 2)
            t.grayscale('grayscale', t['resize'], 2)
            t.binarize('binarize', t['grayscale'], 150, CV_THRESH_BINARY_INV)

            t.contourSplit('breaksplit', t['binarize'], 0.001)
            if len(t.symbols) != symbolqty:
                log.debug(colorize('INCORRECT SYMBOL NUMBER', RED))
                log.debug('LOADING PAGE WITH WM BONUS')
                b.get('http://wmtake.ru/m.base/bonus.php')
                continue

            t.normolize('origsplit', 'breaksplit', 20, 30)
            symbols = t.slice('origsplit')
            log.debug('RECOGNITION CAPTCHA')
            code = a.captcha(symbols)
            log.debug('ANALYZE RESULT: %s' % colorize(code))
            del t
            print code

            log.debug('FILLING FIELDS')
            b.js("$('#scode').val('%s')" % code)
            b.js("$('#purse').val('%s')" % self.info['purse'])
            b.js("$('div.news_box div.bn p').click()")
            b.sleep(1000)

            if not b.js("$('#mess-exec:visible').length"):
                log.debug('FINISH')
                break

            log.debug('INCORRECT CAPCTHA RECOGNITION')
            log.debug('LOADING PAGE WITH WM BONUS')
            b.js("$('#mess-exec p').click()")

        self.quit()


if __name__ == '__main__':
    info = dict({'mode': 'collect'})
    implem = Implem(info)
    sys.exit(implem.exec_())