#!/usr/bin/python
# -*- coding: utf-8 -*-
"""	Утилита 
"""
import  os, sys, time,  getopt
import	glob
#from	subprocess import Popen, PIPE

LIBRARY_DIR = r"/home/smirnov/pylib"	# Путь к рабочей директории (библиотеке)
sys.path.insert(0, LIBRARY_DIR)
import  dbtools

bases = {
	'vms_ws': 'host=10.40.25.176 dbname=vms_ws port=5432 user=vms',
	'vms_ts': 'host=212.193.103.28 dbname=vms_ws port=5432 user=vms',
	'contr': 'host=127.0.0.1 dbname=contracts port=5432 user=smirnov',
	}

DB_vms =	None

def	check_nddata (ndd_name, dev_id):
	global	DB_vms
	print YELLOW
	if DEBUG:
		DB_vms = dbtools.dbtools (bases['vms_ts'], 0)
		print 'DEBUG:\t', bases['vms_ts'], ndd_name, NC
	else:
		print 'VMS_WS:\t', bases['vms_ws'], ndd_name, NC
		DB_vms = dbtools.dbtools (bases['vms_ws'], 0)

	count_rows = DB_vms.get_row ("SELECT count(*) FROM %s WHERE deviceid = %s LIMIT 2" % (ndd_name, dev_id))
	print 'count_rows:\t',
	if count_rows:
		print count_rows
		return	count_rows[0]
	else:
		print count_rows, DB_vms.last_error[1]
		return	-1

def	parse_data_file (fname, ndd_name, sdeviceid, fl_create_nddata = True):
	global	DB_vms
	print 'parse_data_file:\t', fname
	if not os.path.isfile(fname):
		print "Isn't file", fname
		return

	fl_data = False
	fout_name = r"/tmp/%s-%s.sql" % (ndd_name, sdeviceid)
	try:
		f = open (fname, 'r')
		fout = open (fout_name, 'w+')
		print >> fout, "-- %s %s %s" % (ndd_name, sdeviceid, time.strftime("%d.%m.%Y %T", time.localtime(time.time())))
		s = 'f.readline()'
		qnddata = []
		d = []
		j = 0
#		print "ZZZZZZZZZZZZZZZZ", fl_create_nddata
		while s:
			s = f.readline()
			ss = s.strip()
			if not ss:		continue
			if '--' == ss[:2]:	continue
			if 'SET' == ss[:3]:	continue
			if 'COPY' == ss[:4]:
				fl_data = True
				d_append = False
				for c in ss.split(' '):
					if c[:1] == '(':
						d.append(c[1:-1])
						d_append = True
					elif  c[-1:] == ')':
						d.append(c[:-1])
						break
					elif d_append:
						d.append(c[:-1])
			#	print 'd_append', d
				continue
			if '\.' == ss[:2]:
				fl_data = False
				continue
			if fl_data:
				sss = ss.split('\t')
				if sdeviceid == sss[3]:
					cnm = []
					cvl = [] 
				#	print ss
					for c in d:
						if sss[d.index(c)] == '\N':	continue
						cnm.append(c)
						cvl.append(sss[d.index(c)])
					qs = "INSERT INTO %s (%s) VALUES ('%s');" % (ndd_name, ', '.join(cnm), "', '".join(cvl))
					print >> fout, qs
				#	print >> fout, ss
			else:
				qnddata.append(ss)
				
#			j += 1
			if j > 20: break
			
		fout.close()
		if fl_create_nddata:
			query = '\n'.join(qnddata)
			print YELLOW, 'CREATE TABLE %s >>>' % ndd_name
			if not DB_vms.qexecute(query):
				print query, DB_vms.last_error[1]
				return
			print NC
		fin = open (fout_name, 'r')
		print YELLOW, 'INSERT INTO %s >>>' % ndd_name
		qs = 'fin.readline()'
		while qs:
			qs = fin.readline()
			if 'INSERT INTO' in qs:
				if not DB_vms.qexecute(qs):
					print '\t', DB_vms.last_error[1]	#query
					break
		print NC
	#	print '\n'*2
	except:
		exc_type, exc_value = sys.exc_info()[:2]
		print "EXCEPT:", exc_type, exc_value

YELLOW ='\x1b[1;33m'
NC =	'\x1b[0m'

def	outhelp():
	print """Утилита 
        Загрузка данных из архива nddata_20YYMM.sql БД data_path: %s
	-h	Справка
	-t	Контроль соединений с БД 
	-m	Маска поиска файлов (год, месяц) в /arhive_path/nddata_parts/nddat_*
	-d	Отладка на БД (%s), иначе Работа (%s)
	-i	Иденнтификатор прибора (целое число)
	""" % (data_path, bases['vms_ts'], bases['vms_ws'])

DEBUG =		False
DEVICE_ID =	183370927
ndd_name =	'nddata_201506'
data_path =	r'/home/smirnov/_DBMS/nddata_parts/'
data_mask =	None	#'201506'

if __name__ == "__main__":
	FL_help = False
	FL_test = False
	try:
		optlist, args = getopt.getopt(sys.argv[1:], 'htdm:i:')
		for o in optlist:
			if o[0] == '-h':	FL_help = True
			if o[0] == '-d':	DEBUG = True
			if o[0] == '-t':	FL_test = True
			if o[0] == '-m':	data_mask = o[1]
			if o[0] == '-i':	deviceid = o[1]

		if FL_test:
			for key in bases:
				print key, "\t=", bases[key], '\t>',
				ddb = dbtools.dbtools (bases[key], 0)
				if not ddb.last_error:	print 'OK'
		if data_mask:
			if not (deviceid and deviceid.isdigit()):
				deviceid = str (DEVICE_ID)
				DEBUG = True
			
			sss = '%snddata_%s*' % (data_path, data_mask)
			print 'Find data files:\t', sss
			names = glob.glob(sss)
			for fname in names:
				ndd_name = os.path.split(fname)[1].split('.')[0]
				r = check_nddata (ndd_name, deviceid)
			#	print "RRRRRRRRRRRRRRR", r
				if r > 0:	continue
				if r == 0:
					fl_create_nddata = False
				else:	fl_create_nddata = True	
				print fname, fname[-3:], ndd_name
				if fname[-3:] == '.gz':
					scmd = '/bin/gunzip %s' % fname
					print scmd
					r = os.system(scmd)
					if r != 0:
						print 'Error:', r, '\t', scmd
					fname = fname[:-3]
			#	deviceid = str (DEVICE_ID)
				parse_data_file (fname, ndd_name, deviceid, fl_create_nddata)
		elif FL_help:	outhelp()
		else:
			check_nddata (ndd_name, str(DEVICE_ID))
			print "##### DEBUG:", DEBUG, args
	except:
		exc_type, exc_value = sys.exc_info()[:2]
		print "EXCEPT:", exc_type, exc_value
