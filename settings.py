# -*- coding: utf-8 -*-

import os

JQUERY_LIB = 'jquery-1.7.2.min.js'
INSPIRADO_PATH = os.getcwd()
JQUERY_PATH = INSPIRADO_PATH + '/' + JQUERY_LIB
CACHE_PATH = INSPIRADO_PATH + '/cache/'
CAPTCHA_PATH = INSPIRADO_PATH + '/captcha/'
SYMBOLS_PATH = INSPIRADO_PATH + '/symbols/'
IMPLEM_PATH = INSPIRADO_PATH + '/implem.py'

SYMBOL_FILTER = r'^._[0-9]+\..+'

PG_HOST = 'localhost'
PG_USER = 'polzuka'
PG_DB = 'inspirado'
PG_PASSWORD = 'vol70CM3'

TOR_HOST = '127.0.0.1'
TOR_PORT = 9050