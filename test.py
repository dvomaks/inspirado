# -*- coding: utf-8 -*-

from opencv.cv import *
from opencv.highgui import *

i = cvLoadImage('captcha.jpg', CV_8UC1)
r = cvCreateImage(cvGetSize(i), IPL_DEPTH_8U, 1)
cvThreshold(i, r, 100, 255, CV_THRESH_BINARY_INV);

m = cvGetMat(r)
treshold = 8
split = []

prev = 0
for y in xrange(m.cols):
	s = 0
	for x in xrange(m.rows):
		s += 1 if m[x][y] > 0 else 0

	curr = 1 if s > treshold else 0
	if prev != curr:
		split.append(y)

	prev = curr
print split

if len(split) % 2 != 0:
	slit.append(m.cols - 1)

'''
for i in xrange(1, len(split) - 1):
	split.insert(i * 2, split[i * 2 - 1])
'''

print split

res = []
for i in xrange(0, len(split), 2):
	res.append((split[i], split[i + 1]))

print res
print m.cols, m.rows

for bound in res:
	p1 = (bound[0] + 2, 2)
	p2 = (bound[1] - 2, m.rows - 2)
	white = (255, 255, 255)
	cvRectangle(r, p1, p2, white)



cvNamedWindow( 'test', 1 )
cvShowImage( 'test', r)

cvWaitKey(0)

