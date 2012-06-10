# -*- coding: utf-8 -*-

from opencv.cv import *
from transformer import TransformError

def implement(browser, transformer, analyzer, log, data):
    browser.show()
    browser.get('http://wmstream.ru/') 
    captcha = browser.js('$("#wmbonus_form_captcha img")[0].src')
    #code = analyzer(tarnsformer(captcha))
    code = '1234'
    browser.js('$("#frm_vallet").val("%s")' % data['purse'])
    browser.js('$("input:eq(2)").click()')
    browser.js('$("frm_captcha").val("%s")' % code)

    transformer.load('orig', browser.image(captcha))
    transformer.show()
    browser.save(captcha)

def preparing(b, t, a, l, d):
    b.show()
    for i in xrange(30):
        b.get('http://wmstream.ru/')
        captcha = b.js('$("#wmbonus_form_captcha img")[0].src')
        b.save(captcha, '/home/polzuka/inspirado/captcha/picture%02d' % i)
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
