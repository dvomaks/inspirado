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

    def init(self):
        self.site = 'fotocity'
        self.symqty = 5
        self.symsize = (20, 30)
        self.charset = '123456789'


    def pickup(self):

        # создаем браузер, которым будем ходить по wmtake.ru
        b = Browser()
        # сщздаем анализатор, которым будем распознавать капчу
        a = Analyzer('wmtake', self.symsize, self.charset)

        a.load()
        b.show()
        log.debug('LOADING PAGE WITH WM BONUS')
        b.get('http://fotocity.info/m.base/bonus.php')

        while(True):
            log.debug('SAVING CAPTCHA')
            captcha = b.js('$("#scode-pic img")[0].src')
            #b.save(captcha, '/home/polzuka/inspirado/captcha/wmtake/%02d.gif' % i)

            log.debug('CAPTCHA TRANSFORMING')
            try:
                t = Transformer('orig', b.image(captcha))
                t.resizeby('resize', t['orig'], 2, 2)
                t.grayscale('grayscale', t['resize'], 2)
                t.binarize('binarize', t['grayscale'], 150, CV_THRESH_BINARY_INV)

                t.contourSplit('breaksplit', t['binarize'], 0.001)
                if len(t.symbols) != self.symqty:
                    raise Exception
            except Exception, e:
                log.debug(e)
                log.debug(colorize('INCORRECT SYMBOL NUMBER', RED))
                log.debug('LOADING PAGE WITH WM BONUS')
                b.get('http://wmtake.ru/m.base/bonus.php')
                continue

            t.normolize('origsplit', 'breaksplit', self.symsize)
            symbols = t.slice('origsplit')
            log.debug('RECOGNITION CAPTCHA')
            code = a.captcha(symbols)
            log.debug('ANALYZE RESULT: %s' % colorize(code))
            del t
            print code

            log.debug('FILLING FIELDS')
            b.js("$('#scode').val('%s')" % code)
            b.js("$('#purse').val('R%s')" % self.purse)
            b.js("$('div.news_box div.bn p').click()")
            b.sleep(10)

            if not b.js("$('#mess-exec:visible').length"):
                log.debug('FINISH')
                break

            log.debug('INCORRECT CAPCTHA RECOGNITION')
            log.debug('LOADING PAGE WITH WM BONUS')
            b.js("$('#mess-exec p').click()")

        self.quit()


if __name__ == '__main__':
    implem = Implem()
    implem.startpickup('168625933467')
    sys.exit(implem.exec_())