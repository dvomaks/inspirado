#! /usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from base import parse

if __name__ == '__main__':
    print 'ololo'
    info = parse(sys.argv)
    exec('from charity.%s import Implem' % info['implem'])
    implem = Implem(info)
    sys.exit(implem.exec_())