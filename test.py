# -*- coding: utf-8 -*-

from opencv.cv import *
from opencv.highgui import *

i = cvLoadImage('captcha.jpg', CV_8UC1)
res = cvCreateImage(cvGetSize(i), IPL_DEPTH_8U, 1)
cvThreshold(i, res, 100, 255, CV_THRESH_BINARY_INV);

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


for bound in bounds:
	p1 = (bound[0], 0)
	p2 = (bound[1], mat.rows - 2)
	white = (255, 255, 255)
	cvRectangle(res, p1, p2, white)



cvNamedWindow( 'test', 1 )
cvShowImage( 'test', res)

cvWaitKey(0)

