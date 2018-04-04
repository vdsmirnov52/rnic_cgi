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

def	get_vnav2gnum (ddb, swhere = None):	# Читать из vms_ws.vnav2gnum 
	if not swhere:
		swhere = ''
	query = "SELECT * FROM vnav2gnum %s" % swhere
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
		values.append ("('%s', '%s', %d, %d, %s, %s)" % (r[0], r[1], r[2], r[3], isnone(r[4]), isnone(r[5])))
	query = "INSERT INTO nav2regnum (%s) VALUES %s" % (rnames, ','.join(values))
	#print query
	ddb.qexecute(query)

def	check_new_nav (dbwtm, rows):
	for r in rows:
		code, imei, rid, device_id = r[:4]
		print	code, imei, rid, device_id
		break
	
def	get_infor_work_time (ddb, lgnum, stmb, stme):
	if not stmb:	stmb = time.strftime("%Y-%m-%d 00:00:00", time.localtime(time.time()))
	if not stme:	stme = time.strftime("%Y-%m-%d 23:59:59", time.localtime(time.time()))
#	print "get_infor_work_time", stmb, stme
	print 'tbeg, "%s"' % stmb
	print 'tend, "%s"' % stme
	for snum in lgnum:	#desp['param1']:
		query = "SELECT * FROM vnav2gnum WHERE regnum = '%s' OR regnumber = '%s'" % (snum, snum)
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

desp = {}
bases = {
	'vms_ws': 'host=10.40.25.176 dbname=vms_ws port=5432 user=vms',
#	'vms_ws': 'host=212.193.103.9 dbname=vms_ws port=5432 user=vms',
#	'vtst': 'host=10.40.25.180 dbname=vms_ws port=5432 user=vms',
	'wtm': 'host=127.0.0.1 dbname=worktime port=5432 user=smirnov',
	'contr': 'host=127.0.0.1 dbname=contracts port=5432 user=smirnov'}

def	outhelp():
	print """
	-t	Контроль соединений с БД
	-c	Поиск новых ТС (навигаторов)
	-o	Очистить и обновить список машин (nav2regnum)
	-w	Проверить vn2regnum и маркировать Стат.ТС |= 1C в contracts transports
	-b	Блокировать  машины в БД contracts при исключении их в vms_ws
	-d	Удалить машины в БД contracts при исключении их в vms_ws
	"""
#	-x	Путь к файлу списка машин в формате XML
#	-f	Путь к файлу списка машин в формате CSV (utf-8)

dbcontr = None

def	update_atts (device_id, last_date):
	global	dbcontr
	if not dbcontr:		dbcontr = dbtools.dbtools (bases['contr'], 0)
	query = "UPDATE atts SET last_date = '%s', bm_wtime = bm_wtime | 512 WHERE device_id = %d;" % (last_date, device_id)
#	print query
	return	dbcontr.qexecute(query)

def	check_nddatacacheentry ():
	""" Проверить кто сегодня стучался в "nddatacacheentry" 	"""
	sdate = time.strftime("%Y-%m-%d", time.localtime(time.time()))
#	res = dbvms.get_table ("nddatacacheentry", "lastdata_id >0 AND prevdata_id >0 AND lastupdated > '%s 00:00:00' AND lastupdated < '%s 23:59:59'" % (sdate, sdate))
	res = dbvms.get_table ("nddatacacheentry dc INNER JOIN nddata d ON d.id = lastdata_id", "d.createddatetime > '%s 00:00:00' AND d.createddatetime < '%s 23:59:59'" % (sdate, sdate), "dc.*, d.createddatetime")
	j = 0
	sttm =  time.localtime(time.time())
	tm_year, tm_mon, tm_mday = sttm[:3]
	if res:
		d = res[0]
		print d, time.localtime(time.time()), sttm[:3], tm_year, tm_mon, tm_mday
	#	return	True
	#	tm_mday = 4
		tm_mday -= 1
		for r in res[1]:
			updts = []
			'''
			print j, "\t",
			for c in r:	print "\t", c,
			print "#"
			'''
			qu_get = "SELECT * FROM work_statistic WHERE device_id = %d AND year=%d AND month=%d" % (r[d.index('deviceid')], tm_year, tm_mon)
			jsd = dbwtm.get_dict (qu_get)
			if not jsd:
				query = "INSERT INTO work_statistic (device_id, year, month) VALUES (%d, %d, %d); %s" % (r[d.index('deviceid')], tm_year, tm_mon, qu_get)
				jsd = dbwtm.get_dict (query)
				if not jsd:
					print "\t", query
					continue
		#	tm_mday = j
		#	jbstat = 3 & (jsd['mon_bstat'] >> (2 * tm_mday))
		#	print "%016x" % jsd['mon_bstat'], (2 * tm_mday), (jsd['mon_bstat'] + (1 << (2 * tm_mday))),
			if (3 & (jsd['mon_bstat'] >> (2 * tm_mday))) < 3:
				updts.append('mon_bstat=%d' % (jsd['mon_bstat'] + (1 << (2 * tm_mday))))
		#	print "%016x" % jsd['mon_bstat'],
			updts.append("where_mod='%s'" % str(r[d.index('lastupdated')])[:19])
			updts.append('stat=%d' % (1+j))
		#	print jsd['where_mod'],
		#	print jsd['stat'],
			print jsd['device_id'], r[d.index('lastupdated')],
			query = "UPDATE work_statistic SET %s WHERE device_id = %d AND year=%d AND month=%d" % (", ".join(updts), r[d.index('deviceid')], tm_year, tm_mon)
			print "\t", query, dbwtm.qexecute(query), update_atts (r[d.index('deviceid')], str(r[d.index('lastupdated')])[:19])
			j += 1
		#	if j > 30:	break
		print "len(res[1]):", len(res[1]), j

def	find_in_vms (gosnum):
	""" Поиск активной машины в vms_ws	"""
	query = """select ss.code, t.id, t.regnum, nd.id as dev_id, nd.code as dev_code, t.createdby_id
	from transport t
	left join subsystem ss on ss.id=t.subsystem_id
	inner join abstracttransportlink atl on atl.transport_id=t.id AND atl.isdeleted = 0 AND atl.enddate IS NULL
	inner join transport2devicelink t2d on t2d.id=atl.id
	inner join navigationdevice nd on nd.id=t2d.device_id
	where t.isdeleted=0 
	AND t.contractnumber > ''
	AND t.regnum ='%s'""" % gosnum

	return	dbvms.get_dict (query)

YELLOW ='\x1b[1;33m'
GREEN =	'\x1b[0;32m'
RED =	'\x1b[0;31m'
NC =	'\x1b[0m'
TS_1C =		2
TS_CONTR =	4
TS_WORK =	8
TS_DELETE =	2048
TS_BLOCK =	1024

def	check_ts_contr2vms (FLTS):
	print "Блокировать/Удалить  машины в БД contracts пр исключении их в vms_ws", FLTS
	sttm =  time.localtime(time.time())
	tm_year, tm_mon, tm_mday = sttm[:3]
	dbcontr = dbtools.dbtools (bases['contr'])
#	res = dbcontr.get_table ('transports', "bm_status < 1024 AND gosnum LIKE 'А%' ORDER BY gosnum LIMIT 13")
#	res = dbcontr.get_table ('transports', "bm_status IS NULL OR bm_status < 1024 ORDER BY gosnum LIMIT 11111")
	res = dbcontr.get_table ('wtransports', "amark != 'WialonHost' AND (bm_status IS NULL OR bm_status < 1024)")	# WIALON
	if not res:	return
	j = 0
	res_ln = len(res[1])
	d = res[0]
#	print d
	for r in res[1]:
#		print r[d.index('id_ts')], r[d.index('gosnum')], r[d.index('device_id')], r[d.index('transport_id')], r[d.index('bm_status')]
		rvms = find_in_vms (r[d.index('gosnum')])
		if rvms:
			if not ((rvms['dev_id'] == r[d.index('device_id')]) and (rvms['id'] == r[d.index('transport_id')])):
				print YELLOW, r[d.index('gosnum')]
				for k in ['device_id', 'gosnum', 'id_ts', 'transport_id']:
					print "\t%s:" % k, r[d.index(k)],
				print NC
				for k in rvms.keys():
					print "\t%s:" % k, rvms[k],
				print ""
			else:
				j += 1
			#	print GREEN, r[d.index('gosnum')], NC
		else:
			print YELLOW, r[d.index('gosnum')], "\tid_org:", r[d.index('id_org')], NC
			if r[d.index('bm_status')]:
				query = "UPDATE transports SET bm_status = bm_status | %d WHERE id_ts = %d;" % (TS_BLOCK, r[d.index('id_ts')])
			else:	query = "UPDATE transports SET bm_status = %d WHERE id_ts = %d;" % (TS_BLOCK, r[d.index('id_ts')])
			rq = dbcontr.qexecute (query)
			if not rq:
				print RED, "\t",  query, NC
			else:
				query = "SELECT * FROM work_statistic WHERe DEVICE_ID = (SELECT device_id FROM nav2regnum WHERE regnum = '%s') and year = %d AND month = %d" % (r[d.index('gosnum')], tm_year, tm_mon)
	#			query = "UPDATE nav2regnum SET stat = 0 WHERE regnum = '%s'" % r[d.index('gosnum')]
				print YELLOW, query, dbwtm.qexecute(query), NC
	print	"res_ln:", res_ln, "\tis active:", j

def	check_vn2regnum ():
	print """ Проверить vn2regnum и маркировать Стат.ТС |= 1C в contracts transports	"""
	# create view vn2regnum AS SELECT w.*, a.regnum,a.regnumber, a.device_id FROM nav_work_time w, nav2regnum a WHERE w.id_auto = a.id ORDER BY w.id_auto;
	rows = dbwtm.get_rows("SELECT device_id, is_work, regnum FROM vn2regnum")
	new_autos = []
	if rows:
		dbcontr = dbtools.dbtools (bases['contr'])
		for r in rows:
			querys = []
			device_id, is_work, regnum = r
			query = "SELECT gosnum, device_id, bm_status FROM transports WHERE device_id = %d" % device_id
			rss = dbcontr.get_rows(query)
			if not rss:
			#	print query
				new_autos.append (r)
			else:
				ln_rss = len(rss)
				if is_work:
					bm_status = 14
				else:	bm_status = 6
				if ln_rss == 1:
					querys.append("UPDATE transports SET bm_status = bm_status | %d  WHERE device_id = %d" % (bm_status, device_id))
				else:
				#	print ">>\t", regnum, device_id, is_work, bm_status
					for rs in rss:
						jgosnum, jdevice_id, jbm_status = rs
				#		print "\t", jgosnum, jdevice_id, jbm_status
						if not jbm_status:	jbm_status = 0
						if regnum == jgosnum:
							jstatus = (bm_status | jbm_status)
						else:
							jstatus = (0xfffff0 & jbm_status) | TS_BLOCK
						querys.append("UPDATE transports SET bm_status = %d  WHERE device_id = %d AND gosnum = '%s'" % (jstatus, device_id, jgosnum))
			if querys:
				if not dbcontr.qexecute (";\n".join(querys)):
					print ";\n".join(querys)

		print "Len rows", len(rows)
	
		if new_autos:
			list_regnum = []
			print "new_autos in vn2regnum:\n\tregnum   device_id is_work "	# \t is_work \t is_work"
			for r in new_autos:
				device_id, is_work, regnum = r
				print "\t", regnum, device_id, is_work, "\t",
				vres = find_in_vms (regnum)
		#		print "vres\t", vres['regnum'], vres['dev_id'], vres['id']
				jstatus = TS_1C + TS_CONTR
				if is_work > 0:		jstatus += TS_WORK
				if vres:
					if vres['dev_id'] == device_id:
						qsel = "SELECT * FROM transports WHERE gosnum = '%s'" % regnum
						tsd =  dbcontr.get_dict (qsel)
						if tsd:
							query = "UPDATE transports SET bm_status = %d, device_id = %d  WHERE gosnum = '%s'" % (jstatus, device_id, regnum)
							print query, dbcontr.qexecute (query)
						else:
							list_regnum.append(regnum)
							print YELLOW, regnum, "is not in", NC, qsel
					#	else:	print YELLOW, "vres\t(", vres['regnum'], vres['dev_id'], ") is not in", NC, qsel
						continue
					else:
						print YELLOW, "vms_ws is", vres['regnum'], vres['dev_id'], NC,
						qsel = "SELECT * FROM transports WHERE device_id = %d AND gosnum = '%s'" % (vres['dev_id'], regnum)
					#	print "2"*11, qsel
						tsd =  dbcontr.get_dict (qsel)
						if tsd:
							query = "UPDATE transports SET bm_status = %d WHERE device_id = %d AND gosnum = '%s';" % (jstatus, vres['dev_id'], regnum)
							print query, dbcontr.qexecute (query)
						else:
							list_regnum.append(regnum)
							print YELLOW, "is not in", NC, qsel
						continue
					print "#"*22, "vres\t", vres['regnum'], vres['dev_id'], vres['id']
			print "Len new_autos", len(new_autos)
			if list_regnum:
				print YELLOW, "Машин нет в системе 'Информационная поддержка работы РНИЦ'", NC
				print "\t('%s')" % "','".join(list_regnum)
	else:	return "Not Rows!"

def	ttt_bm_wtime():
	print "Конвертировать bm_wtime"
	dbcontr = dbtools.dbtools (bases['contr'])
	rows = dbcontr.get_rows("SELECT id_att, bm_wtime FROM atts where bm_wtime >0 and bm_wtime <1023 LIMIT 11133")
	if rows:
		for r in rows:
			id_att, bm_wtime = r
			cbm_wtime = 0
			jbm_wtime = bm_wtime
		#	while jbm_wtime:
			for j in range(10, 0, -1):
				if 1 & jbm_wtime:
					cbm_wtime += 2**j
			#		print "%03x %03x," % (jbm_wtime, cbm_wtime) , 2**j, cbm_wtime
				jbm_wtime /= 2
			print "%03x %03x  >>\t" % (bm_wtime, cbm_wtime/2),
			print dbcontr.qexecute ("UPDATE atts SET bm_wtime = %d WHERE id_att = %d;" % (cbm_wtime/2, id_att))
	sys.exit()

if __name__ == "__main__":
	sttmr = time.time()
#	ttt_bm_wtime ()		# "Конвертировать bm_wtime"
#	fxml_name = None
#	file_name = None
#	new_autos = None
	FClear =	False
	Fchnew =	False
	Ftest =		False
	FL_wtmr = 	False
	FLTS_BLOCK =	0
	FLTS_DELETE =	0
	print "Start %i" % os.getpid(), sys.argv, time.strftime("%Y-%m-%d %T", time.localtime(sttmr))
	try:
		optlist, args = getopt.getopt(sys.argv[1:], 'tcobdw')
		dbwtm = dbtools.dbtools (bases['wtm'], 1)
		dbvms = dbtools.dbtools (bases['vms_ws'], 1)
		for o in optlist:
			if o[0] == '-t':	Ftest = True
#			if o[0] == '-x':	fxml_name = o[1]
#			if o[0] == '-f':	file_name = o[1]
			if o[0] == '-b':	FLTS_BLOCK =	1
			if o[0] == '-d':	FLTS_DELETE =	2
			if o[0] == '-c':	Fchnew = True	# Поиск новых ТС (навигаторов)
			if o[0] == '-o':	FClear = True	# Очистить и обновить список машин (nav2regnum)
			if o[0] == '-w':	FL_wtmr = True	# Проверить vn2regnum и маркировать Стат.ТС |= 1C в contracts transports
	
		if FClear:
			print	"\tОчистить и обновить список машин (nav2regnum)"
			print	"\tОТМЕНЕНО"
			'''
			print check_vn2regnum()
			dbwtm.qexecute ("DELETE FROM nav2regnum")
			rows = get_vnav2gnum (dbvms)	#, 'LIMIT 11')
			if rows:
				insert2wtm (dbwtm, rows)
			'''
			sys.exit ()
		if Fchnew:
			print	"\tПоиск новых ТС (навигаторов)"
			rows = get_vnav2gnum (dbvms)
			if rows:
				check_new_nav (dbwtm, rows)
		if Ftest:
			for key in bases:
				print key, "\t=", bases[key], '\t>',
				ddb = dbtools.dbtools (bases[key], 0)
				if not ddb.last_error:	print 'OK'
		elif FL_wtmr:
			check_vn2regnum()

		elif FLTS_BLOCK + FLTS_DELETE:	# Блокировать/Удалить  машины в БД contracts пр исключении их в vms_ws
			check_ts_contr2vms (FLTS_BLOCK + FLTS_DELETE)
		else:
			"""select dc.*, d.createddatetime FROM nddatacacheentry dc INNER JOIN nddata d ON d.id = lastdata_id WHERE d.createddatetime > '2016-11-28 00:00:00' AND d.createddatetime < '2016-11-28 23:59:59';"""
			check_nddatacacheentry ()
			outhelp()
	except	getopt.GetoptError:	outhelp()
#	if new_autos:
#		print "new_autos"
#		for sa in new_autos:	print sa

	print "dt %9.4f" % (sttmr - time.time())
