# -*- coding: utf-8 -*-

from sys import argv, exit
from PyQt4.QtGui import QApplication
from base import getData, getLog, colorize, RED, GREEN

log = getLog('picker')

class Picker(QApplication):
	
	def __init__(self, argv):
		QApplication.__init__(self, [])
		self.args = getData(argv)

	def pickup(self):
		


if __name__ == '__main__':
	picker = Picker(argv)
	picker.pickup()
	exit(picker.exec_())