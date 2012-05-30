# -*- coding: utf-8 -*-

from opencv.cv import *
from opencv.highgui import *

i = cvLoadImage('captcha.jpg', CV_8UC1)
res = cvCreateImage(cvGetSize(i), IPL_DEPTH_8U, 1)
tmp = cvCreateImage(cvGetSize(i), IPL_DEPTH_8U, 1)
cvThreshold(i, res, 100, 255, CV_THRESH_BINARY_INV);
cvCopy(res, tmp)

mat = cvGetMat(res)
treshold = 7
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
storage = cvCreateMemStorage(0)
for bound in bounds:
	sub = cvGetSubRect(res, (bound[0], 0, bound[1] - bound[0], mat.rows))
	tmp = cvCreateImage(cvGetSize(sub), IPL_DEPTH_8U, 1)
	#cvCopy(sub, tmp)
	nb, contours = cvFindContours(sub, storage, sizeof_CvContour, CV_RETR_EXTERNAL, CV_CHAIN_APPROX_SIMPLE)
	cvDrawContours(tmp, contours, white, white, 1)
	cvNamedWindow( 'test%s' % i, 1 )
	cvShowImage( 'test%s' % i, tmp)
	i+= 1

	cvWaitKey(0)





cvNamedWindow( 'test', 1 )
cvShowImage( 'test', res)

cvWaitKey(0)

