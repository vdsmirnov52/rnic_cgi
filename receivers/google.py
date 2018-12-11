# -*- coding: koi8-r -*-

from math import *
""" Функции преобразование координат Google Map
"""
BlockSize = 256
nTiles_20 = 524288
bSize_20 = nTiles_20 << 8	# === * 256
bOrigo_20 = bSize_20 >> 1	# === / 2
delta_yg = 0.1777	# Смещение по y для карт /var/www/html/gmaps/yamapng/*
#delta_yg = 0.		# Смещение по y для карт /var/www/html/gmaps/mt/*

def	fname (nx, ny, lev):
	""" Формировать имя графического Блока (файла)
	nx, ny	- координаты Блока
	"""
	d = 1 << (lev-1)
	if nx < 0 or nx > (d-1):
		nx = nx % d
		if nx < 0:
			nx = nx+d
	res = 't'
	for i in range (2,lev+1):
		d = d >> 1
		if ny < d:
			if nx < d:
				res = res + 'q'
			else:
				res = res + 'r'
				nx = nx-d
		else:
			if nx < d:
				res = res + 't'
			else:
				res = res + 's'
				nx = nx-d
			ny = ny-d
	return res

def	g20nx (lon):
	return	int (0.5 + bOrigo_20 + lon * bOrigo_20/180)

def	g20ny (lat):
	lat -= delta_yg
	z = sin ((lat) * pi /180)
	return	int (0.5 + bOrigo_20 -.5 * log ((1+z)/(1-z)) * bOrigo_20/pi)

def	n20gx (X):
	return	180.0 * (X - bOrigo_20) / bOrigo_20

def	n20gy (Y):
	z = pi * (Y - bOrigo_20) / bOrigo_20
	return	delta_yg - (2 * atan(exp(z)) - pi/2) * (180 / pi)
#	return	- (2 * arctan(exp(z)) - pi/2) * (180 / pi)	#from Numeric import *

def	numer ():
	lon = 43.84121
	lat = 56.30354
	""" Отладка
	print "PI", pi
	print 'exp', exp(1)
	print ">>>>>>>>>>> nTiles_20 %d, bSize_20 %d, bOrigo_20 %d<BR>" % (nTiles_20, bSize_20, bOrigo_20)
	
	X = int (bOrigo_20 + lon * bOrigo_20/180)
	z = sin (lat * pi /180)
	Y = int (bOrigo_20 -.5 * log ((1+z)/(1-z)) * bOrigo_20/pi)

	rlon = 180.0 * (X - bOrigo_20) / bOrigo_20
	z = pi * (Y - bOrigo_20) / bOrigo_20
	rlat = - (2 * arctan(exp(z)) - pi/2) * (180 / pi)
	"""
	X = g20nx (lon)
	Y = g20ny (lat)
	print "<br> >>> lon: %f, lat: %f; [X: %d, Y: %d]" % (lon, lat, X, Y)
	print "<br> >>> lon: %f, lat: %f " % (n20gx (X), n20gy (Y))

if __name__ == "__main__":
	nx = 83454051 >> 8
	ny = 41591327 >> 8
	for lev in range (20, 4, -1):
		res = fname (nx, ny, lev)
		print "L:", lev, nx, ny, "\tResult:", res
		nx = nx >> 1
		ny = ny >> 1

	help (Numeric)
	"""
	numer ()
	print "numer OK"
	"""
