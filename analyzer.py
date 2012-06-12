# -*- coding: utf-8 -*-

import os
import re
from pyfann import libfann
from opencv.highgui import cvLoadImage, CV_LOAD_IMAGE_GRAYSCALE
from settings import SYMBOL_FILTER

class Analyzer():

    def __init__(self, x, y, charset):
        self.charset = charset
        self.inputNum = x * y
        self.outputNum = len(charset)
        self.hiddenNum = self.inputNum / 3
        self.layersNum = 3

        self.desiredError = 0.00006
        self.maxEpochs = 50000
        self.epochsBetweenReports = 1000

        self.ann = libfann.neural_net()
        self.ann.create_sparse_array(self.layersNum, (self.inputNum, self.hiddenNum, self.outputNum))
        self.ann.set_activation_function_hidden(libfann.SIGMOID_SYMMETRIC_STEPWISE)
        self.ann.set_activation_function_output(libfann.SIGMOID_SYMMETRIC_STEPWISE)
 
    def getdata(self, img):
        data = []
        for x in range(img.width):
            for y in range(img.height):
                data.append(1 if img[y, x] > 0 else 0)
        return data
    
    def prepare(self, filename, smbdir):
        f = open(filename, 'w')

        filter = re.compile(SYMBOL_FILTER)
        symbols = []
        for name in os.listdir(smbdir):
            if filter.match(name):
                symbols.append(name)

        f.write('%d %d %d\n' % (len(symbols), self.inputNum, self.outputNum))


        for name in symbols:
            img = cvLoadImage(os.path.join(smbdir, name), CV_LOAD_IMAGE_GRAYSCALE)
            data = self.getdata(img)
            f.write('%s\n' % ' '.join(map(str, data)))

            c = name[0]
            n = self.charset.index(c)
            f.write('-1 ' * n + '1' + ' -1' * (self.outputNum - n - 1) + '\n')

        f.close()

    def train(self, filename):
        self.ann.train_on_file(filename, self.maxEpochs, self.epochsBetweenReports, self.desiredError)
        self.ann.save('/home/polzuka/inspirado/wmtake.ann')

    def load(self, filename):
        self.ann.create_from_file(filename)

    def symbol(self, data):
        distr = self.ann.run(data)
        i = distr.index(max(distr))
        return self.charset[i]

    def captcha(self, symbols):
        result = ''
        for smb in symbols:
            data = self.getdata(smb)
            result += self.symbol(data)
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