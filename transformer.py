# -*- coding: utf-8 -*-
import os
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
from base import getlog, colorize, RED, GREEN, YELLOW

log = getlog('transformer')

class TransformError(Exception):
    pass

# преобразование изображений разных форматов друг в друга
def QIm2PIL(qimg):
    buff = QBuffer()
    buff.open(QIODevice.WriteOnly)
    qimg.save(buff, 'BMP')
    fp = StringIO()
    fp.write(buff.data())
    buff.close()
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


# и несколько полезных констант
black = (0, 0, 0)
white = (255, 255, 255)
gray = (100, 100, 100)


# класс - хранилище преобразований изображения
# все изображения хранятся как IplImage
class Transformer(QObject):

    def __init__(self, key=None, src=None):
        QObject.__init__(self)

        # в transforms хранятся преобразования исходного изображения
        self.transforms = OrderedDict()

        # если изображение передается при создании объекта
        if key and src:
            self.load(key, src)
        # 
        self.symbols = []
        self.info = []

    # переопределение []
    def __getitem__(self, key):
        return self.transforms[key]


    def __setitem__(self, key, value):
        self.transforms[key] = value


    # последнее преобразование
    def last(self):
        return self.transforms.values()[-1]


    # применительно только к символам
    def slice(self, srckey):
        res = []
        for smb in self.symbols:
            res.append(smb[srckey])
        return res


    # подгрузка изображения QImage
    def load(self, key, src):
        self.transforms[key] = QIm2Ipl(src)
        log.debug('load(): %s' % colorize(key, YELLOW))


    def save(self, src, path):
        log.debug('save(): %s' % colorize(path, YELLOW))
        cvSaveImage(path, src);


    # подгрузка изображения из path
    def open(self, key, path):
        log.debug('open(): %s from %s' % (colorize(key, YELLOW), colorize(path, YELLOW)))
        self.transforms[key] = cvLoadImage(path)


    # копирование изображения
    def clone(self, key, src):
        log.debug('clone(): %s' % colorize(key, YELLOW))
        self.transforms[key] = cvCloneImage(src)


    # преобразование в оттенки серого
    def grayscale(self, key, src, flags=0):
        log.debug('garyscale(): %s' % colorize(key, YELLOW))
        res = cvCreateImage(cvGetSize(src), src.depth, 1)
        cvConvertImage(src, res, flags)
        self.transforms[key] = res


    # бинаризация по указанному порогу
    def binarize(self, key, src, threshold, method):
        log.debug('binarize(): %s' % colorize(key, YELLOW))
        res = cvCreateImage(cvGetSize(src), IPL_DEPTH_8U, 1)
        cvThreshold(src, res, threshold, 255, method)
        self.transforms[key] = res


    # масштабирование
    def resizeby(self, key, src, scaleX, scaleY, method=1):
        log.debug('resizeby(): %s' % colorize(key, YELLOW))
        res = cvCreateImage((src.width * scaleX, src.height * scaleY), src.depth, src.nChannels)
        cvResize(src, res, method)
        self.transforms[key] = res


    # масштабирование
    def resizeto(self, key, src, resultX, resultY, method=1):
        log.debug('resizeto(): %s' % colorize(key, YELLOW))
        res = cvCreateImage((resultX, resultY), src.depth, src.nChannels)
        cvResize(src, res, method)
        self.transforms[key] = res


    # морфологические преобразования
    # method - тип преобразования: 
    # 0-erode, 1-dilate, 2-CV_MOP_OPEN, 3-CV_MOP_CLOSE, 4-CV_MOP_GRADIENT, 5-CV_MOP_TOPHAT, 6-CV_MOP_BLACKHAT
    def morphology(self, key, src, method, iterations=1, kernel=None):
        log.debug('morphology(): %s' % colorize(key, YELLOW))
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


    # Разделение на символы на основе контурного анализа
    # threshold - пороговое значение отношения площади обрамляющей рамки символа к исходному изображению
    def contourSplit(self, key, src, threshold=0):
        storage = cvCreateMemStorage(0)
        # cvFindContours портит изображение, на котором ищет контуры, поэтому создадим копию
        tmp = cvCloneImage(src)
        # На res нарисуем найденные контуры и прямоугольники, их ограничивающие
        res = cvCreateImage(cvGetSize(src), IPL_DEPTH_8U, 1)
        self.transforms[key] = res

        # Ищем контуры
        num, contours = cvFindContours(tmp, storage, sizeof_CvContour, CV_RETR_EXTERNAL, CV_CHAIN_APPROX_SIMPLE, (0, 0))

        # Контуры в contours хранятся в беспорядке
        # Нам нужно, что бы они шли по порядку слева направо
        messcontours = dict()
        areas = dict()
        for contour in contours.hrange():
            # прямоугольник, ограничивающий контур
            rect = cvBoundingRect(contour)
            pt1 = (rect.x, rect.y)
            pt2 = (rect.x + rect.width, rect.y + rect.height)

            area = rect.width * rect.height
            areas[rect.x] = area

            # рисуем контур и обрамляющую рамку
            cvRectangle(res, pt1, pt2, gray)
            cvDrawContours(res, contour, white, white, 0)

            # получаем область исходного изображения, на которой находится контур
            roi = cvGetSubRect(src, rect)
            # создаем два избражения для области с контуром с учетом каймы в 1 пиксель по краям
            size = (roi.width + 2, roi.height + 2)
            cnt = cvCreateImage(size, IPL_DEPTH_8U, 1)
            tmp = cvCreateImage(size, IPL_DEPTH_8U, 1)
            cvCopyMakeBorder(roi, cnt, (1, 1), 0)
            cvCopyMakeBorder(roi, tmp, (1, 1), 0)
            
            # на полученном изображении еще раз находим контуры (туда могли попасть обрезки других контуров)
            num, conts = cvFindContours(tmp, storage, sizeof_CvContour, CV_RETR_EXTERNAL, CV_CHAIN_APPROX_SIMPLE, (0, 0))
            # все обрезки закрашиваем черным
            for cont in conts.hrange():
                rect = cvBoundingRect(contour)
                if rect.width * rect.height != area:
                    cvDrawContours(cnt, cont, black, black, 0, -1)

            # сохраняем изображение с выделенным контуром
            messcontours[rect.x] = cnt

        # площадь исходного изображения
        srcarea = src.width * src.height * 1.

        for k in sorted(messcontours.iterkeys()):
            # считаем контур символом, если площадь обрамляющего прямоугольника имеет достаточный размер
            if areas[k] / srcarea > threshold:
                self.symbols.append(Transformer(key, Ipl2QIm(messcontours[k])))


            #rect = cvMinAreaRect2(contour)
            #self.info.append((cnt, rect.angle, rect.center, contour))

            


    # разбиение на символы на основе 'узких мест'
    # threshold - пороговое значение в долях
    def breakSplit(self, key, src, threshold=0):
        log.debug('breakSplit(): %s' % colorize(key, YELLOW))
        storage = cvCreateMemStorage(0)
        res = cvCloneImage(src)

        # алгоритм, не поддающийся документированию и сопровождению
        # тем не менее
        leps = []   # переходы
        prev = 0    # предполагаем, что слева пустое пространство (ничего страшного, если это не так)

        # для каждого столбца считаем количество белых пикселей
        for y in xrange(src.cols):
            qty = 0.0
            for x in xrange(src.rows):
                qty += 1 if src[x][y] > 0 else 0

            # если процент белых пикселей в столбце превышает пороговое значение, считаем что там символ
            curr = 1 if qty / src.rows > threshold else 0

            # фиксируем переходы
            if prev != curr:
                leps.append(y)
            prev = curr

        # корректный последний переход
        if len(leps) % 2 != 0:
            leps.append(src.cols - 1)

        boundPairs = [] # границы
        for i in xrange(0, len(leps), 2):
            boundPairs.append((leps[i], leps[i + 1]))

        # отображение рамок 
        for bounds in boundPairs:
            p1 = (bounds[0], 0)
            p2 = (bounds[1], src.rows - 1)   
            cvRectangle(res, p1, p2, gray)
            self.transforms[key] = res

        # разбиение на символы
        for bounds in boundPairs:
            rect = (bounds[0], 0, bounds[1] - bounds[0], src.rows)
            roi = cvGetSubRect(src, rect)
            tmp1 = cvCreateImage(cvGetSize(roi), IPL_DEPTH_8U, 1)
            tmp2 = cvCreateImage(cvGetSize(roi), IPL_DEPTH_8U, 1)
            cvCopy(roi, tmp1)
            cvCopy(roi, tmp2)
            num, contours = cvFindContours(tmp1, storage, sizeof_CvContour, CV_RETR_EXTERNAL, CV_CHAIN_APPROX_SIMPLE, (0, 0))

            if num == 0:
                raise TransformError

            # выбираем самый крупный контур
            saveArea = 0
            for contour in contours.hrange():
                currArea = cvContourArea(contour)
                if currArea > saveArea:
                    saveArea = currArea
                    saveCont = contour

            # и вычленяем его
            rect = cvBoundingRect(saveCont)
            roi = cvGetSubRect(tmp2, rect)
            smb = cvCreateImage(cvGetSize(roi), IPL_DEPTH_8U, 1)
            cvCopy(roi, smb)
            self.symbols.append(Transformer(key, Ipl2QIm(smb)))


    # групповая функция
    # установка стандартных размеров для символов
    def normolize(self, dstkey, srckey, normX, normY):
        log.debug('normolize(): %s' % colorize(srckey, YELLOW))
        for smb in self.symbols:
            img = smb.transforms[srckey]
            size = cvGetSize(img)
            imgX = size.width
            imgY = size.height
            smb.resizeto(dstkey, img, normX, normY)


    # групповая функция
    # сохранение символов
    def savesymbols(self, srckey, smbdir, ser):
        log.debug('saveSymbols(): %s' % colorize(srckey, YELLOW))
        savedir = os.getcwd()
        os.chdir(smbdir)

        i = 0
        for smb in self.symbols:
            img = smb.transforms[srckey]
            self.save(img, '_%d_%s.png' % (i, ser))
            i += 1

        os.chdir(savedir)




    # отображение всех пеобразований
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

        for symbol in self.symbols:
            transformsLayout = QHBoxLayout()
            mainLayout.addLayout(transformsLayout)
            for key, value in symbol.transforms.iteritems():
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
    qimg = QImage('/home/polzuka/inspirado/captcha/wmtake/13.gif')
    t = Transformer('orig', qimg)
    t.resizeby('resize', t['orig'], 3, 3)
    t.grayscale('grayscale', t['resize'], 2)
    t.binarize('binarize', t['grayscale'], 100, CV_THRESH_BINARY_INV)

    radius = 3
    kernel = cvCreateStructuringElementEx(radius * 2 + 1, radius * 2 + 1, radius, radius, CV_SHAPE_ELLIPSE)
    '''
    for i in xrange(7):
        t.morphology('morphology%d' % i, t['binarize'], i, 5, kernel)
    '''
    
    try:
        t.contourSplit('breaksplit', t['binarize'], 0.001)
    except Exception, e:
        print e
    
    t.normolize('origsplit', 'breaksplit', 20, 30)
    #t.savesymbols('origsplit', '/home/polzuka/inspirado/symbols', 1)
    t.show()
    exit(app.exec_())