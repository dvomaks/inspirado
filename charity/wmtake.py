# -*- coding: utf-8 -*-

from opencv.cv import *
from picker import Picker
from browser import Browser
from transformer import Transformer, TransformError
from analyzer import Analyzer
from base import getlog, colorize, RED, GREEN, YELLOW

log = getlog('wmtake')

class Implem(Picker):

    size = (20, 30)

    def runup(self):
        b = Browser()
        symbolqty = 5

        for i in xrange(100):
            print i
            b.get('http://wmtake.ru/m.base/bonus.php')
            captcha = b.js('$("#scode-pic img")[0].src')
            b.save(captcha, '/home/polzuka/inspirado/captcha/wmtake/%02d.gif' % i)

            t = Transformer()
            t.load('orig', b.image(captcha))
            t.resizeby('resize', t['orig'], 2, 2)
            t.grayscale('grayscale', t['resize'], 2)
            t.binarize('binarize', t['grayscale'], 150, CV_THRESH_BINARY_INV)

            '''
            radius = 3
            kernel = cvCreateStructuringElementEx(radius * 2 + 1, radius * 2 + 1, radius, radius, CV_SHAPE_ELLIPSE)
            t.morphology('morphology', t['binarize'], 1, 1, kernel)
            '''

            t.contourSplit('breaksplit', t['binarize'], 0.001)
            if len(t.symbols) != symbolqty:
                continue

            t.normolize('origsplit', 'breaksplit', 20, 30)
            t.savesymbols('origsplit', '/home/polzuka/inspirado/symbols/wmtake', '%02d' % i)
            del t


    def pickup(self):

        # создаем браузер, которым будем ходить по wmtake.ru
        b = Browser()
        # сщздаем анализатор, которым будем распознавать капчу
        a = Analyzer(Implem.size, '123456789')

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
            try:
                t = Transformer('orig', b.image(captcha))
                t.resizeby('resize', t['orig'], 2, 2)
                t.grayscale('grayscale', t['resize'], 2)
                t.binarize('binarize', t['grayscale'], 150, CV_THRESH_BINARY_INV)

                t.contourSplit('breaksplit', t['binarize'], 0.001)
                if len(t.symbols) != symbolqty:
                    raise Exception
            except Exception, e:
                log.debug(e)
                log.debug(colorize('INCORRECT SYMBOL NUMBER', RED))
                log.debug('LOADING PAGE WITH WM BONUS')
                b.get('http://wmtake.ru/m.base/bonus.php')
                continue

            t.normolize('origsplit', 'breaksplit', Implem.size)
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
            b.sleep(10)

            if not b.js("$('#mess-exec:visible').length"):
                log.debug('FINISH')
                break

            log.debug('INCORRECT CAPCTHA RECOGNITION')
            log.debug('LOADING PAGE WITH WM BONUS')
            b.js("$('#mess-exec p').click()")

        self.quit()
