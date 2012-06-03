# -*- coding: utf-8 -*-

def implement(browser, transformer, analyzer, log, data):
    browser.show()
    browser.get('http://wmstream.ru/') 
    captcha = browser.js('$("#wmbonus_form_captcha img")[0].src')
    #code = analyzer(tarnsformer(captcha))
    code = '1234'
    browser.js('$("#frm_vallet").val("%s")' % data['purse'])
    browser.js('$("input:eq(2)").click()')
    browser.js('$("frm_captcha").val("%s")' % code)
    browser.save(captcha)
    
