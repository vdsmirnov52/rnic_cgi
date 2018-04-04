#!/usr/bin/python -u
# -*- coding: utf-8 -*-

#	Формированме задания (session) 
#	и сбор данных о работе транспортных средств

#	transport.id (regnum, regnumber) ->	abstracttransportlink.transport_id
#	abstracttransportlink.id ->		transport2devicelink.id
#						transport2statuslink.id ->	journaldispatcher.statuslink_id
#						transport2kindlink.id
#						abstractwaybill.transport_id ->	waybilldanger.id
#					
#						deviceparametercalibration.id
#	transport2devicelink.device_id ->	navigationdevice.id	(code, imei)

#	create VIEW vatnum AS select at.id, t.regnum, t.regnumber FROM transport t, abstracttransportlink at WHERE t.id = at.transport_id;
#	create VIEW vt2datnum AS select c.*, v.regnum, v.regnumber FROM transport2devicelink c, vatnum v WHERE c.id = v.id;
#	create VIEW vnav2gnum AS select code, imei, v.* FROM navigationdevice n, vt2datnum v WHERE n.id = v.device_id;

#	infor_work_time(IN deviceid text, IN dtb timestamp without time zone, IN dte timestamp without time zone, OUT work_time real)
#	select * FROM infor_work_time('4304175091', '2016-01-01'::timestamp, '2016-01-31'::timestamp);

import	os, time, sys
import	getopt

LIBRARY_DIR = r"/home/smirnov/pylib"          # Путь к рабочей директории (библиотеке)
sys.path.insert(0, LIBRARY_DIR)
import	dbtools

from xml.dom import minidom

def	get_fxml (fname = None):
	dres = {}
	if not fname:
		fname = 'copyright-0.xml'
	doc = minidom.parse(fname)
	for j in range(5):
		nname = 'param%d' % j
		dres[nname] = []
		ilist = doc.getElementsByTagName(nname)
		if ilist:
			for s in ilist:
				x = s.toxml()
				xs = x.split('>')
				if xs[1]:
					xt = xs[1].split('<')
					dres[nname].append(xt[0])
		else:	pass
	return	dres

def	get_file_1C (fname):
	lautos = []
	if not os.path.isfile(fname):
		print "Файл %s отсутствует!"
		return
	f = open (fname, 'r')
	sfs = f.read()
	fs = sfs.split('\n')
	if 'tbeg' in fs[0]:
		stbeg = fs[0].split('"')[1]
	if 'tend' in fs[1]:
		stend = fs[1].split('"')[1]
	print YELLOW, "get_file_1C:\t", stbeg, stend, NC
	for s in fs[2:]:
		if not s.strip():	continue
		lautos.append (s.strip()[1:-1])
	return stbeg, stend, lautos

def	check_xml (ddb, desp = None):
	lres = []
	dtb = dte = None	#time.strftime("%Y-%m-%d", time.localtime(time.time()))
	if not ddb:
		return	'not DataBase descriptor.'
	if  ddb.last_error:
		return	ddb.last_error
	if not desp:
		return	'not XML descriptor.'
	if not desp['param1']:
		return  'not GosNumbers'
#	print	"check_xml", "#"*22
	if desp['param2']:
		dtb =  desp['param2'][0].replace('T', ' ')
	else:	pass
	if desp['param3']:
		dte =  desp['param3'][0].replace('T', ' ')
	else:	pass
#	print	 desp['param2'],  desp['param3'], dtb, dte
	'''
	get_infor_work_time (ddb, desp['param1'], dtb, dte)	#'2015-12-01', '2016-01-01')
	'''
"""
CREATE VIEW vvv AS SELECT at.id, t.regnum, t.regnumber, at.begindate, at.enddate, c.device_id, n.code, n.imei
   FROM transport t
   JOIN abstracttransportlink at ON t.id = at.transport_id AND at.isdeleted = 0 AND at.isdeleted = 0 AND at.enddate IS NULL
   JOIN transport2devicelink c ON c.id = at.id
   JOIN navigationdevice n ON n.id = c.device_id;
"""

def	get_vnav2gnum (ddb, swhere = None):	# Читать из vms_ws.vnav2gnum 
	if not swhere:
		swhere = ''
#	query = "SELECT * FROM vnav2gnum %s" % swhere
	query = "SELECT code, imei, id, device_id, regnum, regnumber FROM vvv %s" % swhere
	print	query
	rows = ddb.get_rows(query)
	return	rows

def	isnone(v):
	if not v:
		return 'NULL'
	else:	return "'%s'" % v

def	insert2wtm (ddb, rows):		# Писать code, imei, id, device_id, regnum, regnumber в worktime.nav2regnum
	rnames = "code, imei, id, device_id, regnum, regnumber"
	values = []
	for r in rows:
	#	print r, 
		try:
			values.append ("('%s', '%s', %d, %d, %s, %s)" % (r[0], r[1], r[2], r[3], isnone(r[4]), isnone(r[5])))
		except:
			print "except:", r[0], r[1], r[2], r[3], isnone(r[4]), isnone(r[5])
	query = "INSERT INTO nav2regnum (%s) VALUES %s" % (rnames, ','.join(values))
	#print query
	ddb.qexecute(query)

def	check_new_nav (dbwtm, rows):
	j = 0
		# ['id', 'regnum', 'regnumber', 'begindate', 'enddate', 'device_id', 'code', 'imei']
	#rnames = "code, imei, id, device_id, regnum, regnumber"
	cp_cols = ['id', 'device_id', 'code', 'imei', 'regnum', 'regnumber']
	d, rows = dbvms.get_table ('vvv')	#, [swhere], [cols])
	print d, len(rows), ',\t'.join(cp_cols)
#	print ">\t", ',\t'.join(cp_cols)
	for r in rows:
	#	for c in r:	print c,
	#	print ''
		rid = r[d.index('id')]
		regnumber = isnone(r[d.index('regnumber')])
		regnum = isnone(r[d.index('regnum')])
		device_id = r[d.index('device_id')]
		code = r[d.index('code')]
		imei = r[d.index('imei')]
		vals = []
	#	for k in cp_cols:	vals.append (isnone(r[d.index(k)]))
	#	print ">\t", ', '.join(vals)
		
	#	print "%d\t'%s'\t%d\t'%s'\t'%s'" % (rid, regnum, device_id, code, imei)
		res = dbwtm.get_table('nav2regnum', swhere = "regnum=%s" % regnum)	#, cols = ','.join(cp_cols))
	#	res = dbwtm.get_table('nav2regnum', swhere = "id=%d" % rid)
		if res:
			jd = res[0]
			jrows = res[1]
			jvals = []
			queries = []
			for jr in jrows:
				if jr[jd.index('stat')] <= 0:	continue
				queries.append ("UPDATE nav2regnum SET stat = -stat WHERE id=%d" % jr[jd.index('id')])
				if  r[d.index('id')] != jr[jd.index('id')]:
					row = dbwtm.get_row("SELECT * FROM nav2regnum WHERE id=%d" % r[d.index('id')])
					if row:
						lset = []
						for k in cp_cols:
							lset.append ("%s = %s" % (k, isnone(r[d.index(k)])))
						queries.append ("UPDATE nav2regnum SET %s WHERE id=%d" % (', '.join(lset), r[d.index('id')]))
					else:
						for k in cp_cols:	jvals.append (isnone(r[d.index(k)]))
		#				print "\t", ',\t'.join(jvals)
						queries.append ("INSERT INTO nav2regnum (%s) VALUES (%s)" % (', '.join(cp_cols), ', '.join(jvals)))
			if queries and len(queries) >1:
			#	if not dbwtm.qexecute ('; '.join(queries)):
				print ";\t".join(queries), dbwtm.qexecute ('; '.join(queries))
		'''
					break
		j += 1
		if j > 11:		break
		'''

def	get_infor_work_time (ddb, lgnum, stmb, stme):
	if not stmb:	stmb = time.strftime("%Y-%m-%d 00:00:00", time.localtime(time.time()))
	if not stme:	stme = time.strftime("%Y-%m-%d 23:59:59", time.localtime(time.time()))
#	print "get_infor_work_time", stmb, stme
	print 'tbeg, "%s"' % stmb
	print 'tend, "%s"' % stme
	for snum in lgnum:	#desp['param1']:
	#	query = "SELECT * FROM vnav2gnum WHERE regnum = '%s' OR regnumber = '%s'" % (snum, snum)
		query = "SELECT * FROM vvv WHERE regnum = '%s' OR regnumber = '%s'" % (snum, snum)
		drow = ddb.get_dict (query)
		if drow:
			query = "select * FROM infor_work_8_time('%s', '%s'::timestamp, '%s'::timestamp);" % (drow['device_id'], stmb, stme)
			drtw = ddb.get_dict (query)
			if drtw['work_time'] > 4:
				is_active = True
			else:	is_active = False
			print	'"%s", %s' % (snum.encode('utf-8'), is_active)	#, drow['device_id'], is_active)
			time.sleep(180)
		#	break;
		else:
			print	'"%s", None' % snum.encode('utf-8')	#, drow['device_id'])

def	check_wtransports (device_id):
	row = dbcntr.get_row ('select gosnum, device_id, bm_wtime FROM wtransports WHERE device_id = %d;' % device_id)
	if row:
		gosnum, device_id, bm_wtime = row
		if bm_wtime == 1023:
			return	5.55
	return	0.0

def	get_next_auto (dbwtm, dbvms):	# id_auto | month | is_work | work_time | where_set
	dsess = dbwtm.get_dict ("SELECT * FROM session_opt LIMIT 1")
	qsmark = []
	if not dsess:
		print  RED, "NOT SELECT * FROM session_opt", NC
		return

#	query =	"SELECT a.id, a.device_id, a.regnum, s.* FROM nav2regnum a LEFT JOIN nav_work_time s ON a.id = s.id_auto WHERE a.stat >0 ORDER BY a.id LIMIT 1;"
	query = "SELECT id, device_id, regnum FROM nav2regnum WHERE id > %d AND stat = 1 ORDER BY id LIMIT 1" % dsess['id_auto_last']
	rn = dbwtm.get_row (query)
	
	wtmod = time.strftime("%Y-%m-%d %T", time.localtime(time.time()))
	if rn:
		aid, device_id, regnum = rn
		print regnum, "\t",
		drtw = None
		work_time = check_wtransports (device_id)
		if work_time == 0.0:
			query = "select * FROM infor_work_8_time('%s', '%s'::timestamp, '%s'::timestamp);" % (device_id, dsess['tmbeg'], dsess['tmend'])
		#	print query
			drtw = dbvms.get_dict (query)
			if drtw:	work_time = drtw['work_time']
		if work_time or drtw:
			print work_time
			if work_time > 4:
				qsmark.append("UPDATE nav2regnum SET stat = 2, where_mod = '%s' WHERE id = %d" % (wtmod, aid))
				qsmark.append("INSERT INTO nav_work_time (id_auto, month, is_work, work_time, where_set) VALUES (%d, %d, 1, %f, '%s')" % (
					aid, dsess['month'], work_time, wtmod))
			else:
				qsmark.append("UPDATE nav2regnum SET stat = 3, where_mod = '%s' WHERE id = %d" % (wtmod, aid))
				qsmark.append("INSERT INTO nav_work_time (id_auto, month, is_work, work_time, where_set) VALUES (%d, %d, 0, %f, '%s')" % (
					aid, dsess['month'], work_time, wtmod))
		else:	qsmark.append("UPDATE nav2regnum SET stat = -1, where_mod = '%s' WHERE id = %d" % (wtmod, aid))
		qsmark.append ("UPDATE session_opt SET id_auto_last = %d" % aid)
		query = ';\n'.join(qsmark)
		###	03.05.2017
		dbwtm.qexecute("DELETE FROM nav_work_time WHERE id_auto = %d;" % aid)
		dbwtm.qexecute (query)
		return	aid
	elif str(dsess['tmend']) > wtmod:	# Повторное сканирование машин
		query = "select a.id, a.device_id, a.regnum, s.where_set, s.work_time FROM nav2regnum a, nav_work_time s WHERE a.id = s.id_auto AND s.is_work = 0 ORDER BY s.where_set LIMIT 1"
	#	query = "select id, device_id, where_mod FROM nav2regnum WHERE stat = 3 ORDER BY where_mod LIMIT 1"
		rn = dbwtm.get_row (query)
		if rn:
			aid, device_id, regnum, where_set, dw_time = rn
			tmbeg = "%s 00:00:00" % str(where_set)[:10]
			query = "select * FROM infor_work_8_time('%s', '%s'::timestamp, '%s'::timestamp);" % (device_id, tmbeg, dsess['tmend'])
			print regnum, "\t",	#query,
			drtw = dbvms.get_dict (query)
			if drtw:
				work_time = drtw['work_time'] + float(dw_time)
			#	print drtw, work_time
				if work_time > 4:
					print "YYY", work_time
					qsmark.append("UPDATE nav2regnum SET stat = 2, where_mod = '%s' WHERE id = %d" % (wtmod, aid))
					qsmark.append("UPDATE nav_work_time SET is_work = 1, work_time = %f, where_set = '%s' WHERE id_auto = %d;" % (work_time, wtmod, aid))
				else:
					print "NNN", aid
					qsmark.append ("UPDATE nav2regnum SET where_mod = '%s' WHERE id = %d" % (wtmod, aid))
					qsmark.append ("UPDATE nav_work_time SET work_time = %f, where_set = '%s' WHERE id_auto = %d;" % (work_time, wtmod, aid))
		#		print	qsmark
				qsmark.append ("UPDATE session_opt SET id_auto_last = %d" % aid) ### ???
				query = ';\n'.join(qsmark)
				if dbwtm.qexecute (query):	return aid
	#	print "### "*11
	else:	print  "NOT", query

SESSION_DICT = None

def	check_session (dbwtm, tm, stbeg, stend, month = None):
	global	SESSION_DICT

	SESSION_DICT = dbwtm.get_dict ("SELECT * FROM session_opt LIMIT 1")
	ss_stbeg = str(SESSION_DICT['tmbeg'])
	ss_stend = str(SESSION_DICT['tmend'])
	print YELLOW, "SESSION_DICT:", NC
	for key, val in SESSION_DICT.iteritems():	print '\t%s:\t' % str(key), val
	if (ss_stbeg == stbeg and ss_stend >= stend) or (ss_stbeg > stbeg and ss_stend > stend):
		print	YELLOW, "Продолжеие сессии:", NC
		return	True
	else:
		print YELLOW, "check_session:\t", tm, stbeg, stend, month, NC
		return	False
	
def	mark_work_autos (dbwtm, gnums, month, isss_current = True):
	wtmod = time.strftime("%Y-%m-%d %T", time.localtime(time.time()))
	print "mark_work_autos", wtmod, 'isss_current:', isss_current
	month = SESSION_DICT['month']
	new_autos = []
	rdict = []
	jupdate = 0
	for sgn in gnums:
		qqq = None
	#	query = "SELECT * FROM nav2regnum WHERE regnum = '%s' OR regnumber = '%s' ORDER BY device_id DESC" % (sgn, sgn)
		query = "SELECT a.id, a.device_id, a.regnum, a.stat, s.* FROM nav2regnum a LEFT JOIN nav_work_time s ON a.id = s.id_auto WHERE regnum = '%s' OR regnumber = '%s' ORDER BY device_id DESC" % (sgn, sgn)
		row = dbwtm.get_row (query)
		if not rdict:
			rdict = dbwtm.desc
	#		print rdict
		if row:
			if isss_current:
				if row[rdict.index('stat')] == 1:	continue
				if (row[rdict.index('stat')] == 0) or (row[rdict.index('stat')] > 0 and row[rdict.index('month')] and row[rdict.index('month')] != month):
					print row[rdict.index('regnum')], row[rdict.index('stat')], "\t",
					qqq = "UPDATE nav2regnum SET stat = 1, where_mod = '%s' WHERE id = %d" % (wtmod, row[0])
			else:
				qqq = "UPDATE nav2regnum SET stat = 1, where_mod = '%s' WHERE id = %d" % (wtmod, row[0])
			#	dbwtm.qexecute (qqq)
		else:	new_autos.append (sgn)
		if qqq:
			jupdate +=1
			if not dbwtm.qexecute (qqq):
				print RED, "\t", qqq, NC
		#	else:	print ""
	#	if jupdate > 3:	break
	if jupdate > 0:
		dbwtm.qexecute ("UPDATE session_opt SET id_auto_last = 1, tmlast = '%s', jup_work_time = %d;" % (wtmod, int (time.time())))
#	sys.exit()
	return	new_autos

desp = {}
bases = {
	'vms_ws': 'host=10.40.25.176 dbname=vms_ws port=5432 user=vms',
#	'vms_ws': 'host=212.193.103.9 dbname=vms_ws port=5432 user=vms',
#	'vtst': 'host=10.40.25.180 dbname=vms_ws port=5432 user=vms',
	'wtm': 'host=127.0.0.1 dbname=worktime port=5432 user=smirnov',
	'cntr': 'host=127.0.0.1 dbname=contracts port=5432 user=smirnov',
	'b03': 'host=127.0.0.1 dbname=b03 port=5432 user=smirnov'}

def	outhelp():
	print """
	-t	Контроль соединений с БД
	-c	Поиск новых ТС (навигаторов)
	-o	Очистить и обновить список машин (nav2regnum)
	-d	Фиксировать машины удаленный в 1С -df <file.csv> 
	-x	Путь к файлу списка машин в формате XML
	-f	Путь к файлу списка машин в формате CSV (utf-8)
	-w	Обновить список Машин в work_statistic
	-s	Начать новую сессию сбора данных (обновить session_opt)
	"""

YELLOW ='\x1b[1;33m'
RED =	'\x1b[0;31m'
NC =	'\x1b[0m'

def	ch_work_statistic (dbwtm, tm):
	stm = time.localtime(tm)
	year = stm[0]
	mon = stm[1]
	print YELLOW, """ Обновить список Машин в work_statistic
		""", NC, stm, year, mon
	querys = ["DELETE FROM work_statistic WHERE year < %d AND month < %d" % (year, mon)]		# Удалить старьё
#	querys.append ("DELETE FROM work_statistic WHERE device_id NOT IN (SELECT device_id FROM nav2regnum WHERE stat > 0)")	# ???
	querys.append ("INSERT INTO work_statistic (device_id) (SELECT device_id FROM nav2regnum WHERE stat > 0 AND device_id NOT IN (SELECT device_id FROM work_statistic WHERE year = %d AND month=%d))" %  (year, mon))
	querys.append ("UPDATE work_statistic SET year = %d, month=%d WHERE year IS NULL AND month IS NULL;" % (year, mon))
	query = ";\n".join(querys)
	print query, dbwtm.qexecute (query)
	
def	save_session (dbwtm, tm, stbeg, stend, month = None):
	print "save_session\t", tm, stbeg, stend, month
	if stbeg and stend:
		if not month or month > 12:
			smonth = stbeg[5:7]
		else:	smonth = '%d' % month
		query =  "INSERT INTO session_opt (month, tmbeg, tmend, id_auto_last, tmlast) VALUES (%s, '%s', '%s', 0, '%s')" % (
				smonth, stbeg, stend, time.strftime("%Y-%m-%d %T", time.localtime(sttmr)))
	#	print stbeg, stend, month, query
		dbwtm.qexecute (query)

def	fix_delete_ts (tslist):
	print """ Фиксировать машины удаленный в 1С -df <file.csv>	"""
	print "len(tslist)", len(tslist)
	d = None
	j = 0
	# Просмотр списка машин (tslist)
	for gnum in tslist:	# Контроль дублирования regnum в таблице nav2regnum
		res = dbwtm.get_table('nav2regnum', "regnum = '%s' ORDER BY id" % gnum)
		if res:
			if not d:	d = res[0]
			lenres = len(res[1])
			if lenres > 1:
			#	print gnum, lenres
				jr = 0
				for r in res[1]:
					jr += 1
					if r[d.index('stat')] <= 0:
						if lenres == 2:	break
						continue
					if jr != lenres: 
						query = "UPDATE nav2regnum SET stat = -stat WHERE id = %d" % r[d.index('id')]
						print "\t", r[d.index('id')], r[d.index('device_id')], r[d.index('stat')], query,
					#	print dbwtm.qexecute(query)
						print ""
				#	else:	print "###\t", r[d.index('id')], r[d.index('device_id')], r[d.index('stat')]
				j += jr -1
		else:
			print gnum, res
	print "###:", j
#	return
	res = dbwtm.get_table('nav2regnum', 'stat > 0 ORDER BY regnum')
	if res:		# Контроль принадлежности regnum списку машин (tslist)
		d = res[0]
		print d
		j = 0
		old_regnum = ''
		old_device_id = 0
		for r in res[1]:
			if r[d.index('regnum')] and old_regnum == r[d.index('regnum')]:
				print "double\t", old_regnum, old_device_id
			else:
				old_regnum = d.index('regnum')
				old_device_id = d.index('device_id')
			if r[d.index('regnum')] not in tslist:
				query = "UPDATE nav2regnum SET stat = -stat WHERE regnum = '%s'" %  r[d.index('regnum')]
				print "\t", r[d.index('regnum')], "\t", r[d.index('where_mod')], r[d.index('stat')], query, "\t",
			#	print dbwtm.qexecute(query)
				print ""
				j += 1
		print len(res[1]), j, (len(res[1]) - j)
	
def	update_session_opt (sttmr):
	stime = time.localtime(sttmr)
	tm_year = stime[0]
	mon = tm_mon = stime[1]

	stmbeg = "%d-%02d-01 00:00:00" % (tm_year, tm_mon)
	if tm_mon == 12:
		tm_year += 1
		tm_mon = 1
	else:	tm_mon += 1
	stmend = "%d-%02d-01 00:00:00" % (tm_year, tm_mon)
	query = "UPDATE session_opt SET month = %d, tmbeg = '%s', tmend = '%s', id_auto_last = 1" % (mon, stmbeg, stmend)
	print YELLOW, query, dbwtm.qexecute(query), NC
#	sys.exit()

if __name__ == "__main__":
	sttmr = time.time()
	fxml_name = None
	file_name = None
	new_autos = None
	FClear = False
	Fchnew = False
	Ftest = False
	Ffixdel = False
	Fchwstat = False
	month = 0
#	month = 2
	print "Start %i" % os.getpid(), sys.argv, time.strftime("%Y-%m-%d %T", time.localtime(sttmr))
	try:
		optlist, args = getopt.getopt(sys.argv[1:], 'stcodwx:f:')
		dbwtm = dbtools.dbtools (bases['wtm'], 1)
		dbvms = dbtools.dbtools (bases['vms_ws'], 1)
		dbcntr = dbtools.dbtools (bases['cntr'])
		for o in optlist:
			if o[0] == '-t':	Ftest = True
			if o[0] == '-x':	fxml_name = o[1]
			if o[0] == '-f':	file_name = o[1]
			if o[0] == '-m':	month = int(o[1])
			if o[0] == '-w':	Fchwstat = True
			if o[0] == '-c':	Fchnew = True
			if o[0] == '-o':	FClear = True
			if o[0] == '-d':	Ffixdel = True
			if o[0] == '-s':	update_session_opt (sttmr)
	
		if FClear:
			print	"\tОТМЕНЕНО"
			dbc = dbtools.dbtools (bases['cntr'])
			query = 'select gosnum, device_id, bm_wtime FROM wtransports WHERE bm_wtime = 1023'
			res = dbc.get_table('wtransports', 'bm_wtime = 1023', cols='gosnum, device_id, bm_wtime')
			print res[0]
			if res:
				for r in res[1]:
					gosnum, device_id, bm_wtime = r
					print gosnum, device_id, bm_wtime
			'''
			print	"\tОчистить и обновить список машин (nav2regnum)"
			query = "select * FROM nav2regnum WHERE stat < 0 ORDER BY stat"
			res = dbwtm.get_table('nav2regnum', "stat < 0 ORDER BY stat", cols='device_id, stat')
			if res:
				dids = {-1: [], -2:[], -3:[]}
				for r in res[1]:
					dids[r[1]].append('%d' % r[0])
				dbcntr = dbtools.dbtools (bases['cntr'], 1)
				for k in dids.keys():
				#	query = "DELETE FROM transports WHERE device_id IN (%s)" % ", ".join(dids[k])
					query = "DELETE FROM atts WHERE device_id IN (%s)" % ", ".join(dids[k])
					print k, query	#", ".join(dids[k])
				#	print dbcntr.qexecute(query)
			'''
			print "#"*22
			'''
			dbwtm.qexecute ("DELETE FROM nav2regnum")
			rows = get_vnav2gnum (dbvms)	#, 'LIMIT 11')
			if rows:
				insert2wtm (dbwtm, rows)
			'''
			sys.exit()
		if Fchnew:
			print	"\tПоиск новых ТС (навигаторов)"
			rows = get_vnav2gnum (dbvms)
			if rows:
				check_new_nav (dbwtm, rows)
			sys.exit()
		if Ftest:
			for key in bases:
				print key, "\t=", bases[key], '\t>',
				ddb = dbtools.dbtools (bases[key], 0)
				if not ddb.last_error:	print 'OK'
		elif Ffixdel:
			if file_name:
				res = get_file_1C (file_name)
				fix_delete_ts(res[2])
			else:
				print "\n\tОтсутствует Путь к файлу от 1С списка машин в формате CSV"
				outhelp()
		elif file_name:
			res = get_file_1C (file_name)
			if res and res[2]:
				stbeg, stend, lautos = res
				isss_current = check_session (dbwtm, sttmr, stbeg, stend, month)
				new_autos = mark_work_autos (dbwtm, lautos, month, isss_current)
			#	print new_autos, isss_current
			#	sys.exit()
				if new_autos:
					swhere = "WHERE regnum IN ('%s')" % "', '".join(new_autos)
					rows = get_vnav2gnum (dbvms, swhere)
					if rows:
						insert2wtm (dbwtm, rows)
						new_autos = mark_work_autos (dbwtm, lautos, month, isss_current)
			#	save_session (dbwtm, sttmr, stbeg, stend, month)
		elif fxml_name:
			desc_xml = get_fxml ()
			if desc_xml['param1']:
				stbeg = desc_xml['param2']
				stend = desc_xml['param2']
				isss_current = check_session (dbwtm, sttmr, desc_xml['param2'], desc_xml['param2'], month)
				new_autos = mark_work_autos (dbwtm, desc_xml['param1'], month, isss_current)
			#	save_session (dbwtm, sttmr, desc_xml['param2'], desc_xml['param2'], month)
		elif month:
			print "WWW"
		elif Fchwstat:	# Обновить список Машин в work_statistic
			ch_work_statistic (dbwtm, sttmr)
		else:
			for j in range(9999):
				jtm = time.time()
				res = get_next_auto (dbwtm, dbvms)
				if not res:	break
				dtm = 9 + int (time.time() - jtm)
				if dtm > 130:	dtm = 130
				jsh = time.strftime("%H", time.localtime(time.time()))
			#	print j, (dtm), "[%s]" % jsh ,
				if jsh in '07 15':
					print YELLOW, "Break:\t", time.strftime("%Y-%m-%d %T", time.localtime(sttmr)), NC
					break
		#		else:	print "??? [%s]" % jsh
				time.sleep (dtm)
			outhelp()
	except	getopt.GetoptError:	outhelp()
	if new_autos:
		print YELLOW, "Not in 'vms_ws' new_autos len:", len(new_autos), NC
		for sa in new_autos:	print "\t", sa
	print "dt %9.4f" % (sttmr - time.time())
