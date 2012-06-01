# -*- coding: utf-8 -*-

from sys import exit
from collections import OrderedDict
from cStringIO import StringIO
from PyQt4.QtCore import QObject, QBuffer, QIODevice
from PyQt4.QtGui import QApplication, QWidget, QImage, QVBoxLayout, QHBoxLayout
from PyQt4.QtGui import QLabel, QPixmap
from opencv.cv import *
from opencv.highgui import *
from opencv import adaptors
from opencv.adaptors import PIL2Ipl
from PIL import Image

# преобразование изображений разных форматов
def QIm2PIL(qimg):
    buffer = QBuffer()
    buffer.open(QIODevice.WriteOnly)
    qimg.save(buffer, 'BMP')
    fp = StringIO()
    fp.write(buffer.data())
    buffer.close()
    fp.seek(0)
    return Image.open(fp)


def PIL2QIm(pilimg):
    fp = StringIO()
    pilimg.save(fp, 'BMP')
    qimg = QImage()
    qimg.loadFromData(fp.getvalue(), 'BMP')
    return qimg


def Ipl2PIL(iplimg):
    mat = cvGetMat(iplimg)
    return adaptors.Ipl2PIL(mat)


def QIm2Ipl(qimg):
    pilimg = QIm2PIL(qimg)
    return PIL2Ipl(pilimg)


def Ipl2QIm(iplimg):
    pilimg = Ipl2PIL(iplimg)
    return PIL2QIm(pilimg)


# хитрый класс
class Transformer(QObject):

    def __init__(self, orig):
        QObject.__init__(self)
        self.transforms = OrderedDict({'ORIG': QIm2Ipl(orig)})
        self.pieces = []
        self.info = []

    # переопределение []
    def __getitem__(self, key):
        return self.transforms[key]

    def __setitem__(self, key, value):
        self.transforms[key] = value

    # подгрузка изображения
    def load(self, key, path):
        self.transforms[key] = cvLoadImage(path)

    # копирование изображения
    def clone(self, key, src):
        self.transforms[key] = cvCloneImage(src)

    # преобразование в оттенки серого
    def grayscale(self, key, src, flags=0):
        res = cvCreateImage(cvGetSize(src), src.depth, 1)
        cvConvertImage(src, res, flags)
        self.transforms[key] = res

    # бинаризация
    def binarize(self, key, src, threshold, method):
        res = cvCreateImage(cvGetSize(src), IPL_DEPTH_8U, 1)
        cvThreshold(src, res, threshold, 255, method)
        self.transforms[key] = res

    # масштабирование
    def resize(self, key, src, scaleX, scaleY, method=1):
        res = cvCreateImage((src.width * scaleX, src.height * scaleY), src.depth, src.nChannels)
        cvResize(src, res, method)
        self.transforms[key] = res

    # морфологические преобразования
    def morphology(self, key, src, method, iterations=1, kernel=None):
        tmp = cvCreateImage(cvGetSize(src), src.depth, src.nChannels)
        if not kernel:
            kernel = cvCreateStructuringElementEx(3, 3, 1, 1, CV_SHAPE_ELLIPSE)
        if method == 0:
            cvErode(src, tmp, kernel, iterations)
            self.transforms[key] = tmp
        elif method == 1:
            cvDilate(src, tmp, kernel, iterations)
            self.transforms[key] = tmp
        elif 2 <= method <= 6:
            res = cvCreateImage(cvGetSize(src), src.depth, src.nChannels)
            cvMorphologyEx(src, res, tmp, kernel, method, iterations)
            self.transforms[key] = res

    # разделение на символы на основе контурноо анализа
    def contourSplit(self, key, src, mode, method, externalColor, internalColor):
        storage = cvCreateMemStorage(0)
        tmp = cvCloneImage(src)
        res = cvCreateImage(cvGetSize(src), IPL_DEPTH_8U, 1)

        num, contours = cvFindContours(tmp, storage, sizeof_CvContour, mode, method, (0, 0))
        cvDrawContours(res, contours, externalColor, internalColor, 1)
        self.transforms[key] = res

        for contour in contours.hrange():
            rect = cvBoundingRect(contour)
            pt1 = (rect.x, rect.y)
            pt2 = (rect.x + rect.width, rect.y + rect.height)
            cvRectangle(res, pt1, pt2, externalColor)
            roi = cvGetSubRect(src, rect)
            cnt = cvCreateImage(cvGetSize(roi), IPL_DEPTH_8U, 1)
            white = (255, 255, 255)
            cvSet(cnt, white)
            cvCopy(roi, cnt)
            self.pieces.append(Transformer(Ipl2QIm(cnt)))
            rect = cvMinAreaRect2(contour)
            self.info.append((cnt, rect.angle, rect.center, contour))

    # разбиение на символы на основе 'узких мест'
    '''
    def breakSplit(self, key, src, threshold):
        storage = cvCreateMemStorage(0)
        tmp = cvCloneImage(src)
        res = cvCreateImage(cvGetSize(src), IPL_DEPTH_8U, 1)
        mat = cvGetMat(res)

        divs = []

        prev = 0
        for y in xrange(mat.cols):
            s = 0
            for x in xrange(mat.rows):
                s += 1 if mat[x][y] > 0 else 0

            curr = 1 if s > treshold else 0
            if prev != curr:
                divs.append(y)
            prev = curr

        if len(divs) % 2 != 0:
            divs.append(mat.cols - 1)

        bounds = []
        for i in xrange(0, len(divs), 2):
            bounds.append((divs[i], divs[i + 1]))

        # Покажем рамки
        white = (255, 255, 255)
        for bound in bounds:
            p1 = (bound[0], 0)
            p2 = (bound[1], mat.rows - 1)   
            cvRectangle(tmp, p1, p2, white)

        cvNamedWindow( 'test', 1 )
        cvShowImage( 'test', tmp)
        i = 0
        
        for bound in bounds:
            sub = cvGetSubRect(res, (bound[0], 0, bound[1] - bound[0], mat.rows))
            tmp = cvCreateImage(cvGetSize(sub), IPL_DEPTH_8U, 1)
            #cvCopy(sub, tmp)
            nb, contours = cvFindContours(sub, storage, sizeof_CvContour, CV_RETR_EXTERNAL, CV_CHAIN_APPROX_SIMPLE)
            cvDrawContours(tmp, contours, white, white, 1)
            cvNamedWindow( 'test%s' % i, 1 )
            cvShowImage( 'test%s' % i, tmp)
            i+= 1

    '''
    def show(self):
        self.view = QWidget()
        mainLayout = QVBoxLayout()
        self.view.setLayout(mainLayout)
        transformsLayout = QHBoxLayout()
        mainLayout.addLayout(transformsLayout)
        for key, value in self.transforms.iteritems():
            transrormLayout = QVBoxLayout()
            transformsLayout.addLayout(transrormLayout)
            header = QLabel(key)
            image = QLabel()
            image.setPixmap(QPixmap.fromImage(Ipl2QIm(value)))
            transrormLayout.addWidget(header)
            transrormLayout.addWidget(image)

        for piece in self.pieces:
            transformsLayout = QHBoxLayout()
            mainLayout.addLayout(transformsLayout)
            for key, value in piece.transforms.iteritems():
                transrormLayout = QVBoxLayout()
                transformsLayout.addLayout(transrormLayout)
                header = QLabel(key)
                image = QLabel()
                image.setPixmap(QPixmap.fromImage(Ipl2QIm(value)))
                transrormLayout.addWidget(header)
                transrormLayout.addWidget(image)

        self.view.show()


if __name__ == '__main__':
    app = QApplication([])
    qimg = QImage('captcha/captcha.jpg')
    t = Transformer(qimg)
    t.resize('resize', t['ORIG'], 4, 4)
    t.grayscale('grayscale', t['resize'], 2)
    t.binarize('binarize', t['grayscale'], 200, CV_THRESH_BINARY)
    radius = 3
    kernel = cvCreateStructuringElementEx(radius * 2 + 1, radius * 2 + 1, radius, radius, CV_SHAPE_ELLIPSE)
    t.morphology('morphology', t['binarize'], 1, 1, kernel)
    white = (255, 255, 255)
    gray = (137, 137, 137)
    t.show()
    exit(app.exec_())