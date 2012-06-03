# -*- coding: utf-8 -*-

def implement(browser, transformer, analyzer, log, data):
    browser.get('http://kopeyka.org/') 
    #captcha = browser.js('$("input:eq(2)").val()')
    browser.js('$("input:eq(1)").mouseover()')
    browser.js('$("input:eq(1)").val("%s")' % data['purse'])
    browser.js('$("input:eq(2)").click()')
    #browser.save('http://www.wmkopilka.ru/cbimg.php?11210')
    
