#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
"""

import	os, sys, time, getopt
import math

r_major = 6378137.0
r_minor = 6356752.3142

def	xm2lon (xm):
	""" xm Меркатор -> долготу	"""
	return	math.degrees(xm/r_major)

def	lon2mx (lon):
	""" долготу -> Меркатор	"""
	return	r_major*math.radians(lon)

def	lat2my (lat):
	""" широту -> Меркатор EPSG:900913	"""
	if lat > 89.5:	lat = 89.5
	if lat < -89.5:	lat = -89.5
	rLat = math.radians(lat)
	return 	r_major*math.log(math.tan(math.pi/4+rLat/2))

def	ym2lat (ym):
	""" ym Меркатор EPSG:900913 -> широту	"""
	return	math.degrees(2.0*math.atan(math.exp(ym/r_major)) - math.pi/2)

def	LatLongToMerc(lon, lat):
	""" Пересчет координат из широты/долготы в проекцию Меркатора/WGS84 EPSG:3857	"""
	if lat > 89.5:		lat = 89.5
	if lat < -89.5:		lat = -89.5
 
	rLat = math.radians(lat)
	rLong = math.radians(lon)
 
	a = 6378137.0
	b = 6356752.3142
	f = (a-b)/a
	e = math.sqrt(2*f-f**2)
	x = a*rLong
	y = a*math.log(math.tan(math.pi/4+rLat/2)*((1-e*math.sin(rLat))/(1+e*math.sin(rLat)))**(e/2))
	return {'x':x,'y':y}

def	LatLongToSpherMerc(lon, lat):
	""" Пересчет координат из широты/долготы в проекцию "Сферического Меркатора" EPSG:900913	"""
	if lat > 89.5:		lat = 89.5
	if lat < -89.5:		lat = -89.5
 
	rLat = math.radians(lat)
	rLong = math.radians(lon)
 
	a = 6378137.0
	x = a*rLong
	y = a*math.log(math.tan(math.pi/4+rLat/2))
	return {'x':x,'y':y}

res = LatLongToMerc(37.617778,55.751667)
print res['x'], res['y'], res 

res = LatLongToSpherMerc(37.617778,55.751667)
print res['x'], res['y'], res

LIBRARY_DIR = r"/home/smirnov/pylib"	# Путь к рабочей директории (библиотеке)
sys.path.insert(0, LIBRARY_DIR)
import  dbtools

"""
	POINT		(4552706.45 7536377.61)
	LINESTRING	(4926700.47 7618779.43, ...)
	POLYGON		((4736226.56 7576338.28, ..., 4736226.56 7576338.28))
	MULTIPOLYGON	(((4928466.2 7541926.4, ..., 4928466.2 7541926.4)),((4929658.14 7543369.16, ..., 4929658.14 7543369.16)))

	boundary = 'administrative', admin_level, way_area
	highway
"""
bases = {
	'vms_ws': 'host=10.40.25.176 dbname=vms_ws port=5432 user=vms',
	'wtm': 'host=127.0.0.1 dbname=worktime port=5432 user=smirnov',
	'gis': 'host=127.0.0.1 dbname=gis port=5432 user=smirnov',
	'contr': 'host=127.0.0.1 dbname=contracts port=5432 user=smirnov',
	}
def	test_db ():
	print 'Test DB connect:'
	for key in bases:
		print "\t", key, "\t=", bases[key], '\t>',
		ddb = dbtools.dbtools (bases[key], 0)
		if not ddb.last_error:  print 'OK'

def	outTable (ddb, table, where = None, cols = None, limit = 11):
	if not where:
		swwhere = "osm_id > 0 LIMIT %d" % limit
	else:	swwhere = " %s LIMIT %d" % (where, limit)
	if 'planet_osm_point' == table:
		cols = 'osm_id, power, name, ref, point(way) AS way'
	#	cols = 'osm_id, power, name, ref, ST_AsText(way) AS point'	#(way)'
	else:
		cols = 'osm_id, name,  ST_AsText(way) AS way'
#	print swwhere
	print "outTable:", table, "\t%s" % swwhere, cols
#	return
#	res = ddb.get_table ('planet_osm_polygon', " \"addr:housenumber\" IS NOT NULL LIMIT 1111")
	res = ddb.get_table (table, swwhere, cols)
	if res:
		d = res[0]
		for r in res[1]:
			for k in d:
				if r[d.index(k)]:
					if k == 'way':
						print '\t', k, ':', r[d.index(k)][:64], len (r[d.index(k)]),
					elif  k == 'point' and 'planet_osm_point' == table:
						lon, lat = r[d.index(k)][1:-1].split(',')
						print lon, lat, xm2lon(float(lon)), ym2lat(float(lat)), lat2my(ym2lat(float(lat))),
					#	print LatLongToMerc(lon, lat)
					else:	print '\t', k, ':', r[d.index(k)],
			print

def	HouseCount (ddb, street, house = None):
	if house and house != '':
		query = "SELECT COUNT(house.*) FROM planet_osm_polygon AS house WHERE \"addr:street\" ILIKE '%%%s%%' AND \"addr:housenumber\" ILIKE '%%%s%%'" % (street, house)
	else:	query = "SELECT COUNT(house.*) FROM planet_osm_polygon AS house WHERE \"addr:street\" ILIKE '%%%s%%'" % street
	row = ddb.get_row (query)
	print 'HouseCount', row

def	StreetCount (ddb, street):
	query = "SELECT COUNT(*) FROM planet_osm_line WHERE highway <> '' AND name ILIKE '%%%s%%'" % street
	row = ddb.get_row (query)
	print 'StreetCount', row

if __name__ == "__main__":
	test_db ()
	ddbgis = dbtools.dbtools (bases['gis'], 1)
	StreetCount (ddbgis, 'Гага')
#	HouseCount (ddbgis, 'а', '')
#	outTable (ddbgis, 'planet_osm_polygon', "way NOT LIKE '010300002031BF%'")	#'"addr:housenumber" IS NOT NULL')
#	outTable (ddbgis, 'planet_osm_polygon', '"addr:housenumber" IS NOT NULL ORDER BY way_area')
#	outTable (ddbgis, 'planet_osm_line', 'name IS NOT NULL ORDER BY way_area')
#	outTable (ddbgis, 'planet_osm_roads')
	outTable (ddbgis, 'planet_osm_polygon', 'admin_level IS NOT NULL')
	outTable (ddbgis, 'planet_osm_point', "power != 'tower'")
