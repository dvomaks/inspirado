# -*- coding: utf-8 -*-

from opencv.cv import *
from picker import Picker
from browser import Browser
from transformer import Transformer, TransformError
from analyzer import Analyzer
from base import getlog, colorize, RED, GREEN, YELLOW


log = getlog('wmstream')

class Implem(Picker):

    def picup(self):
        browser.show()
        browser.get('http://wmstream.ru/')
        print 'GET PAGE'
        browser.sleep(1000)
        print 'GET CAPTCHA'
        captcha = browser.js('$("#wmbonus_form_captcha img")[0].src')
        browser.sleep(1000)

        t.load('orig', browser.image(captcha))
        t.show()
        browser.save(captcha, '/home/polzuka/inspirado/symbols/first')

        t.resizeby('resize', t['orig'], 4, 4)
        t.grayscale('grayscale', t['resize'], 2)
        t.binarize('binarize', t['grayscale'], 200, CV_THRESH_BINARY)

        radius = 3
        kernel = cvCreateStructuringElementEx(radius * 2 + 1, radius * 2 + 1, radius, radius, CV_SHAPE_ELLIPSE)
        
        t.morphology('morphology', t['binarize'], 1, 1, kernel)
        try:
            t.breakSplit('breaksplit', t['morphology'], 0.2)
        except TransformError:
            print 'ololo'
            
        t.normolize('origsplit', 'breaksplit', 20, 30)
        sl = t.slice('origsplit')
        a = Analyzer(20, 30, '0123456789')
        a.load('/home/polzuka/inspirado/fann.data')
        code = a.captcha(sl)
        print code

        print 'GET CLICK'
        
        browser.js('$("#frm_vallet").mousedown()')
        browser.js('$("#frm_vallet").mouseup()')
        browser.js('$("#frm_vallet").click()')
        browser.sleep(1000)
        browser.js('$("#frm_vallet").val("%s")' % data['purse'])

        browser.js('$("#frm_captcha").mousedown()')
        browser.js('$("#frm_captcha").mouseup()')
        browser.js('$("#frm_captcha").click()')

        for i in xrange(5):
            browser.js('$("#frm_captcha").keydown()')
            browser.js('$("#frm_captcha").keyup()')
            browser.js('$("#frm_captcha").keypress()')

        browser.js('$("#frm_captcha").val("%s")' % code)
        print 2
        browser.js('$("#btn_bonus").click()')
        print 3
        

        #t.show()
        #t.saveSymbols('origsplit', '/home/polzuka/inspirado/symbols', '%02d' % i)

def preparing(b, t, a, l, d):
    b.show()
    for i in xrange(30):
        b.get('http://wmstream.ru/')
        captcha = b.js('$("#wmbonus_form_captcha img")[0].src')
        b.save(captcha, '/home/polzuka/inspirado/captcha/picture%02d' % i)
        t = Transformer()
        t.load('orig', b.image(captcha))

        #t.save(t['orig'], '/home/polzuka/inspirado/captcha/picture%02d' % i)
        t.resizeby('resize', t['orig'], 4, 4)
        t.grayscale('grayscale', t['resize'], 2)
        t.binarize('binarize', t['grayscale'], 200, CV_THRESH_BINARY)

        radius = 3
        kernel = cvCreateStructuringElementEx(radius * 2 + 1, radius * 2 + 1, radius, radius, CV_SHAPE_ELLIPSE)
        
        t.morphology('morphology', t['binarize'], 1, 1, kernel)
        try:
            t.breakSplit('breaksplit', t['morphology'], 0.2)
        except TransformError:
            print 'ololo'
            continue
        t.normolize('origsplit', 'breaksplit', 20, 30)
        #t.show()
        t.saveSymbols('origsplit', '/home/polzuka/inspirado/symbols', '%02d' % i)
        del t


if __name__ == '__main__':
    