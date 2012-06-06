# -*- coding: utf-8 -*-

from sys import argv, exit
from PyQt4.QtCore import QTimer
from PyQt4.QtGui import QApplication
from base import getData, getLog, colorize, RED, GREEN
from browser import Browser
from transformer import Transformer

log = getLog('picker')

class Picker(QApplication):
	
	def __init__(self, argv):
		QApplication.__init__(self, [])
		self.args = getData(argv)
		self.browser = Browser(debug=True)
		self.transformer = Transformer()
		self.analyzer = []
		QTimer.singleShot(0, self.pickup)

	def pickup(self):
		log.debug(colorize('pickup started', GREEN))
		s = 'from %s import implement' % self.args['implem']
		log.debug(colorize(s, GREEN))
		exec s
		implement(self.browser, self.transformer, self.analyzer, log, self.args)
		log.debug(colorize('pickup finished', GREEN))
		if not self.browser.shown:
			self.quit()


if __name__ == '__main__':
	picker = Picker(argv)
	exit(picker.exec_())