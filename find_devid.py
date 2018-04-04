#!/usr/bin/python -u
# -*- coding: utf-8 -*-
"""	Утилита поиска телематических данных в файлах nddata_YYYYMM.sql по deviceid
	и формирования SQL запросов для создание таблиц nddata_YYYYMM (при необходимомти)
	и добавления телематических данных в таблицы nddata_YYYYMM

	./find_devid.py 183370927 nddata_2016*.sql
"""

import	os, sys

LIBRARY_DIR = r"/home/smirnov/pylib"    # Путь к рабочей директории (библиотеке)
sys.path.insert(0, LIBRARY_DIR)
import  dbtools
'''
 public | nddata_201607                            | таблица | vms      | 8192 bytes |
 public | nddata_201608                            | таблица | vms      | 560 kB     |
 public | nddata_201609                            | таблица | vms      | 3272 kB    |
 public | nddata_201610                            | таблица | vms      | 3992 kB    |
'''

def	is_nddate (tname, deviceid):
	vms = dbtools.dbtools('host=10.40.25.176 dbname=vms_ws port=5432 user=vms', 1)
	query = 'SELECT count(*) FROM %s WHERE deviceid = %s' % (tname, deviceid)
#	print query
	r = vms.get_row (query)
	if r:	return r[0]
	elif vms.last_error:
		print vms.last_error[1]
		return -1
	else:	return 0

open_fout = lambda deviceid, dbname:	open ('%d_%s' % (deviceid, dbname), 'w')

def	create_nddata (dbname, deviceid):
	print 'create_nddata', dbname
	fout = open_fout (deviceid, dbname)
	f = open(dbname, 'r')
	is_copy = False
	sl = 'zzz'
	while sl:
		sl = f.readline()
		ssl = sl.strip()
		if not ssl:		continue
		if '--' in ssl[:2]:	continue
		if 'COPY' in ssl[:5]:
			is_copy = True
			print >> fout, ssl
		elif is_copy:
			if str(deviceid) in ssl:
				print >> fout, ssl
			if '\\.' ==  ssl:
				is_copy = False
				print >> fout, ssl
		else:	print >> fout, ssl
	fout.close()


def	create_insert (dbname, deviceid):
	print 'create_insert', dbname, deviceid
	fout = open_fout (deviceid, dbname)
	f = open(dbname, 'r')
	is_copy = False
	sl = 'zzz'
	while sl:
		sl = f.readline()
		ssl = sl.strip()
		if not ssl:	continue
		if 'COPY' in ssl[:5]:
			is_copy = True
			js0 = ssl.find('(')
			js1 = ssl.find(')')
			sinst = 'INSERT INTO %s %s)\n' % (dbname[:-4], ssl[js0:js1])
		#	print ssl, js0, js1
		#	print sinst
		elif is_copy:
			if str(deviceid) in ssl:
				vals = []
				for v in ssl.split('\t'):
					if v == '\\N':
						vals.append("NULL")
					else:	vals.append("'%s'" % v)
				print >> fout, "%s\tVALUES (%s);" % (sinst, ', '.join(vals))
			if '\\.' ==  ssl:
				print ssl, '#'*22
				break
	fout.close()

if __name__ == "__main__":
	if len (sys.argv) > 2:
		deviceid = int(sys.argv[1])
		print 'deviceid:\t', sys.argv[1]
		print 'files:\t', sys.argv[2:]
		for dbname in sys.argv[2:]:
			print '\t', dbname
			res = is_nddate(dbname[:-4], deviceid)
			if res > 0:
				print '\tdeviceid %d есть в БД %s' % (deviceid, dbname), res
			elif res < 0:
				print create_nddata (dbname, deviceid)
			elif res == 0:
				print create_insert (dbname, deviceid)
			else:
				print 'Res:', res
		'''
		create_insert ('nddata_201607.sql', deviceid)
		create_nddata ('nddata_201607.sql', deviceid)
		'''
	else:
		print sys.argv[0], '<deviceid> <nddata_YYYYMM.sql>'
	

