# -*- coding: utf-8 -*-

import os
import re
from pyfann import libfann
from opencv.highgui import cvLoadImage, CV_LOAD_IMAGE_GRAYSCALE
from settings import SYMBOL_FILTER, SYMBOLS_PATH, NETS_PATH,TRAINS_PATH
from base import getlog, colorize, RED, GREEN


log = getlog('anayzer')


# Нейронная сеть для распознавния капчи
class Analyzer():

    # implemname - имя реализации
    # picsize - размер картинки, содержащей один символ (x, y)
    # charset - строка, содержащая все символы, встречающиеся в капче
    def __init__(self, implemname, picsize, charset):
        self.implemname = implemname
        self.charset = charset
        self.input = picsize[0] * picsize[1]
        self.output = len(charset)
        self.hidden = self.input / 3
        self.layers = 3

        self.desiredError = 0.00006
        self.maxEpochs = 50000
        self.epochsBetweenReports = 1000

        self.ann = libfann.neural_net()
        self.ann.create_sparse_array(self.layers, (self.input, self.hidden, self.output))
        self.ann.set_activation_function_hidden(libfann.SIGMOID_SYMMETRIC_STEPWISE)
        self.ann.set_activation_function_output(libfann.SIGMOID_SYMMETRIC_STEPWISE)

        log.info('init(): implemname: %s, size: %sx%s, charset: %s, input: %s, hidden: %s, output: %s' % 
                 colorize((implemname, picsize[0], picsize[1], charset, self.input, self.hidden, self.output)))
 

    def getdata(self, img):
        log.debug('getdata(): size: %sx%s' % colorize((img.width, img.height)))
        data = []
        for x in range(img.width):
            for y in range(img.height):
                data.append(1 if img[y, x] > 0 else 0)
        '''
        for i in xrange(img.height):
            print data[i * img.width : (i + 1) * img.width]
        print
        '''
        return data
    

    # создание файла для обучения нейронной сети
    def prepare(self):
        trainpath = TRAINS_PATH + self.implemname + '.trn'
        symbolpath = SYMBOLS_PATH + self.implemname
        log.info('prepare(): trainpath: %s, symbolpath: %s' % colorize((trainpath, symbolpath)))

        trainfile = open(trainpath, 'w')

        filter = re.compile(SYMBOL_FILTER)
        symbols = []
        for name in os.listdir(symbolpath):
            if filter.match(name):
                symbols.append(name)

        trainfile.write('%d %d %d\n' % (len(symbols), self.input, self.output))


        for name in symbols:
            img = cvLoadImage(SYMBOLS_PATH + self.implemname + '/' + name, CV_LOAD_IMAGE_GRAYSCALE)
            data = self.getdata(img)
            trainfile.write('%s\n' % ' '.join(map(str, data)))

            c = name[0]
            n = self.charset.index(c)
            trainfile.write('-1 ' * n + '1' + ' -1' * (self.output - n - 1) + '\n')

        trainfile.close()


    # обучение нейронной сети на основе обучаещего файла
    def train(self):
        print 'satrt'
        trainpath = TRAINS_PATH + self.implemname + '.trn'
        netpath = NETS_PATH + self.implemname + '.ann'
        log.info('prepare(): trainpath: %s, netpath: %s' % colorize((trainpath, netpath)))

        self.ann.train_on_file(trainpath, self.maxEpochs, self.epochsBetweenReports, self.desiredError)
        self.ann.save(netpath)
        print 'satrt'


    def load(self, filename):
        self.ann.create_from_file(filename)
        log.info('load(): from: %s' % colorize(filename))


    def symbol(self, data):
        distr = self.ann.run(data)
        i = distr.index(max(distr))
        smb = self.charset[i]
        log.debug('symbol(): distr: %s' % map(lambda el: round(el, 2), distr))
        return smb


    def captcha(self, symbols):
        result = ''
        for smb in symbols:
            data = self.getdata(smb)
            result += self.symbol(data)
        log.info('captcha(): result: %s' % colorize(result))
        return result



if __name__ == '__main__':
    a = Analyzer(20, 30, '123456789')
    a.prepare('wmtake.trn', '/home/polzuka/inspirado/symbols/wmtake')
    a.train('wmtake.trn')
    a.load('/home/polzuka/inspirado/wmtake.ann')
    
    img = cvLoadImage('/home/polzuka/inspirado/symbols/wmtake/4_19.png', CV_LOAD_IMAGE_GRAYSCALE)
    print a.symbol(a.getdata(img))
    img = cvLoadImage('/home/polzuka/inspirado/symbols/wmtake/9_15.png', CV_LOAD_IMAGE_GRAYSCALE)
    print a.symbol(a.getdata(img))