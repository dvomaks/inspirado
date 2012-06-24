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
        b.show()
        b.get('http://2ip.ru/')
        ip = b.js("$('div.ip big').text()")
        print ip
        self.quit()
