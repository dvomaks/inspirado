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

log = getlog('smswebmoney')

class Implem(Picker):

    def init(self):
        self.site = 'smswebmoney'
        self.symqty = 4
        self.symsize = (20, 30)
        self.charset = '23456789ABCDEFGHIJKMNPRSTUVWXYZ'


    def collect(self):
        b = Browser()

        for i in xrange(200):
            log.info('LOAD PAGE WITH CAPTCHA')
            b.get('http://sms-webmoney.ru/')
            captcha = 'http://sms-webmoney.ru/img.php'
            b.save(captcha, CAPTCHA_PATH + self.site + '/%02d.png' % i)

            t = Transformer()
            t.load('orig', b.image(captcha))
            t.resizeby('resize', t['orig'], 3, 3)
            t.grayscale('grayscale', t['resize'], 2)
            t.binarize('binarize', t['grayscale'], 200, CV_THRESH_BINARY_INV)

            radius = 2
            kernel = cvCreateStructuringElementEx(radius * 2 + 1, radius * 2 + 1, radius, radius, CV_SHAPE_ELLIPSE)
            
            t.morphology('morphology', t['binarize'], 0, 1, kernel)
            t.contourSplit('breaksplit', t['morphology'], 0.01)

            if len(t.symbols) != self.symqty:
                log.debug(colorize('INCORRECT SYMBOL NUMBER', RED))
                continue

            t.normolize('origsplit', 'breaksplit', self.symsize)
            t.savesymbols('origsplit', SYMBOLS_PATH + self.site, '%02d' % i)
            del t


    def analyze(self):
        a = Analyzer(self.site, self.symsize, self.charset)
        a.prepare()
        a.train()
        self.quit()


    def pickup(self):

        # создаем браузер, которым будем ходить по wmtake.ru
        b = Browser()
        # создаем анализатор, которым будем распознавать капчу
        a = Analyzer(self.site, self.symsize, self.charset)

        a.load()
        b.show()

        while(True):
            log.debug('LOADING PAGE WITH WM BONUS')
            b.get('http://exchangecity.ru/?cmd=bonus')
            log.debug('SAVING CAPTCHA')
            captcha = 'http://exchangecity.ru/include/anti_robot.php'
            #b.save(captcha, '/home/polzuka/inspirado/captcha/wmtake/%02d.gif' % i)

            log.debug('CAPTCHA TRANSFORMING')
            t = Transformer('orig', b.image(captcha))
            t.resizeby('resize', t['orig'], 2, 2)
            t.grayscale('grayscale', t['resize'], 2)
            t.binarize('binarize', t['grayscale'], 200, CV_THRESH_BINARY_INV)

            t.contourSplit('breaksplit', t['binarize'], 0.001)
            if len(t.symbols) != self.symqty:
                log.debug(colorize('INCORRECT SYMBOL NUMBER', RED))
                continue

            t.normolize('origsplit', 'breaksplit', self.symsize)
            symbols = t.slice('origsplit')
            log.debug('RECOGNITION CAPTCHA')
            code = a.captcha(symbols)
            log.debug('ANALYZE RESULT: %s' % colorize(code))
            del t
            print code

            log.debug('FILLING FIELDS')
            b.js("$('input[name = img]').val('%s')" % code)
            b.js("$('input[name = WALLET_BONUS]').val('R%s')" % self.purse)
            b.js("$('input[name = get_bonus]').click()")
            b.sleep(1)

            if not b.js("$('font.textbl:contains(Вы получили бонус в размере)').length"):
                log.debug('FINISH')
                break

            log.debug('INCORRECT CAPCTHA RECOGNITION')

        self.quit()


if __name__ == '__main__':
    implem = Implem()
    #implem.startcollect()
    implem.startanalyze()
    #implem.startpickup('168625933467')
    sys.exit(implem.exec_())