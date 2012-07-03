#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from base import getlog, colorize


if __name__ == '__main__':

    log = getlog('implem')

    log.info('%s: %s' % (sys.argv[0], sys.argv[1:]))
    if len(sys.argv) < 3:
        log.info('implem.py: %s' % 'not enought arguments')
        sys.exit()
    

    site, purse = sys.argv[1:]

    exec('from charity.%s import Implem' % site)
    implem = Implem()
    implem.startpickup(purse)
    sys.exit(implem.exec_())