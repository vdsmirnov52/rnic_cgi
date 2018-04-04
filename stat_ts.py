#!/usr/bin/python
# -*- coding: utf-8 -*-
"""	Утилита crontab	"stat_ts.py"
	7 0 1 * *       /home/smirnov/MyTests/CGI/stat_ts.py > /home/smirnov/MyTests/log/stat_ts.py.log
	Сбор данных для формирования ежемесячного отчета работоспособности ТС (Транспорт)
"""
import  os, sys, time,  getopt

LIBRARY_DIR = r"/home/smirnov/pylib"	# Путь к рабочей директории (библиотеке)
sys.path.insert(0, LIBRARY_DIR)
import  dbtools

fcsv_name = r"/tmp/health_status_TC.csv"
bases = {
	'vms_ws': 'host=10.40.25.176 dbname=vms_ws port=5432 user=vms',
	'wtm': 'host=127.0.0.1 dbname=worktime port=5432 user=smirnov',
	'contt': 'host=127.0.0.1 dbname=contr_tst port=5432 user=smirnov',
	'contr': 'host=127.0.0.1 dbname=contracts port=5432 user=smirnov',
	}

list_sformat = ['%d.%m.%Y', '%Y.%m.%d', '%d.%m.%Y', '%d.%m.%y', '%m.%d.%y']
def	sfdate (sdate, jfs = 0):
	""" Преобразовать строку даты в формат записи в БД	"""
	if not sdate.strip():	return
	ts = None
	sdate = sdate.strip().replace(' ', '.').replace('/', '.').replace('-', '.').replace(',', '.').replace(':', '.')
	try:
		ts = time.strptime(sdate, list_sformat[jfs])
	except ValueError:
		jfs += 1
		if jfs < len(list_sformat):	return	sfdate (sdate, jfs)
	finally:
		if ts:	return	time.strftime(list_sformat[0], ts)

DB_vms =	None
DB_wtm =	None
DB_cont =	None

def	calc_atts (ddb):
	global	DB_cont
	print ddb
	DB_cont = dbtools.dbtools (ddb)
	last_month = DB_cont.get_dict ("SELECT * FROM stat_ts_month ORDER BY when_count DESC LIMIT 1")
	if last_month:
		try:
			y,m,d = str(last_month['when_count']).split('-')
		except:
			print "\texcept: calc_atts", last_month['when_count']
			return
		yar = int(y)
		month = int(m)
		if month == 12:
			month = 1
			yar += 1
		else:	month += 1
	else:	
		yar = 2015
		month = 1
	cref = ['when_formed', 'bm_ssys', 'last_day', 'all_time', 'into_system']
	while 1:
	#	query = "SELECT * FROM ref_ts_stat WHERE when_formed < '1.%d.%d' LIMIT 16;" % (month, yar)
	#	print query
		res = DB_cont.get_table('ref_ts_stat', "when_formed = '1.%02d.%d' ORDER BY bm_ssys;" % (month, yar))
		if not res:
			print "\tНет данных на 1.%02d.%d" % (month, yar)
			break
		print "\tДобавить данные на 1.%02d.%d" % (month, yar)
		d = res[0]
		cols = []
		vals = []
		for r in res[1]:
			if r[d.index('bm_ssys')] > 0 and r[d.index('bm_ssys')] < 8192:
				cols.append("c_%d" % r[d.index('bm_ssys')])
				vals.append("'{%d, %d, %d}'" % (r[d.index('last_day')], r[d.index('all_time')], r[d.index('into_system')]))
			elif r[d.index('bm_ssys')] > 4096:
				cols.append("c_all")
				vals.append("'{%d, %d, %d}'" % (r[d.index('last_day')], r[d.index('all_time')], r[d.index('into_system')]))
		if cols:
			cols.append("when_count")
			vals.append("'%s'" % str(r[d.index('when_formed')]))
			query = "INSERT INTO stat_ts_month (%s) VALUES (%s)" % (",".join(cols), ",".join(vals))
			if not DB_cont.qexecute(query):
				print query
		if month == 12:
			month = 1
			yar += 1
		else:	month += 1
	#	if yar == 2018:	break

def	outhelp():
	print """
	Утилита crontab
        Сбор данных для формирования отчета 'Справка по состоянию работоспособности ТС '
	-h	Справка
	-t	Контроль соединений с БД %s
	-d	Отладка на БД %s
	""" % (bases['contr'], bases['contt'])
DEBUG =	False

if __name__ == "__main__":
	FL_help = False
	FL_test = False
	try:
		optlist, args = getopt.getopt(sys.argv[1:], 'htd')
		for o in optlist:
			if o[0] == '-h':	FL_help = True
			if o[0] == '-d':	DEBUG = True
			if o[0] == '-t':	FL_test = True

		if FL_test:
			for key in bases:
				print key, "\t=", bases[key], '\t>',
				ddb = dbtools.dbtools (bases[key], 0)
				if not ddb.last_error:	print 'OK'
		elif FL_help:	outhelp()
		else:
			if DEBUG:
				calc_atts (bases['contt'])
			else:	calc_atts (bases['contr'])
			print "##### DEBUG:", DEBUG, args
	except:
		exc_type, exc_value = sys.exc_info()[:2]
		print "EXCEPT:", exc_type, exc_value
