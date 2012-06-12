# -*- coding: utf-8 -*-

from opencv.cv import *
from picker import Picker
from browser import Browser
from transformer import Transformer, TransformError
from analyzer import Analyzer
from base import getlog, colorize, RED, GREEN


class Implem(Picker):

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
        b = Browser()
        a = Analyzer(20, 30, '123456789')

        symbolqty = 5

        a.load('/home/polzuka/inspirado/nets/wmtake.ann')
        b.show()
        b.get('http://wmtake.ru/m.base/bonus.php')

        while(True):
            captcha = b.js('$("#scode-pic img")[0].src')
            #b.save(captcha, '/home/polzuka/inspirado/captcha/wmtake/%02d.gif' % i)

            t = Transformer('orig', b.image(captcha))
            t.resizeby('resize', t['orig'], 2, 2)
            t.grayscale('grayscale', t['resize'], 2)
            t.binarize('binarize', t['grayscale'], 150, CV_THRESH_BINARY_INV)

            t.contourSplit('breaksplit', t['binarize'], 0.001)
            if len(t.symbols) != symbolqty:
                b.get('http://wmtake.ru/m.base/bonus.php')
                continue

            t.normolize('origsplit', 'breaksplit', 20, 30)
            symbols = t.slice('origsplit')
            code = a.captcha(symbols)
            del t
            print code

            b.js("$('#scode').val('%s')" % code)
            b.js("$('#purse').val('%s')" % self.info['purse'])
            b.js("$('div.news_box div.bn p').click()")
            b.sleep(7000)

            if b.js("$('#mess-exec:visible').length"):
                break

            b.js("$('#mess-exec p').click()")
