#!/usr/bin/python -u
# -*- coding: utf-8 -*-
"""     Демон vms_getdd.py

	nohup /home/smirnov/MyTests/CGI/vms_getdd.py > /home/smirnov/MyTests/log/vms_getdd.log &

	- Читать данные nddata_20YYMM из БД vms_ws -> contracts
	- Если receiver.recv_ts('inn') > 0	Писать данные в receiver last_pos, data_pos
	- Обновляет список машин в receiver.recv_ts
"""
import	os, sys, time

LIBRARY_DIR = r"/home/smirnov/pylib"    # Путь к рабочей директории (библиотеке)
sys.path.insert(0, LIBRARY_DIR)
import  dbtools
bases = {
	'vms_ws': 'host=10.40.25.176 dbname=vms_ws port=5432 user=vms',
	'recvr': 'host=127.0.0.1 dbname=receiver port=5432 user=smirnov',
	'contr': 'host=127.0.0.1 dbname=contracts port=5432 user=smirnov',
	}

def	get_racv_list ():
	""" Читать (обновить) с список device_id для ТС	"""
	dev_list = []
	res = RECVR.get_table('recv_ts', 'inn > 0', cols='device_id')
	if not res:	return
	for r in res[1]:
		if r[0]:	dev_list.append(int(r[0]))
	return	dev_list

def	clear_old_data (dtime = 24*3600):
	""" Удалить устаревшие навигационные данные в БД receiver 	"""
	tmin = int(time.time()) - dtime
	query = "DELETE FROM data_pos WHERE t < %d; DELETE FROM data_prms WHERE t < %d;" % (tmin, tmin)
	print	"\t", query, RECVR.qexecute(query)

def	test ():
	print "Читать данные nddata_20YYMM из БД vms_ws -> contracts"
	dres = {}
	for key in bases:
		print key, "\t=", bases[key], '\t>',
		ddb = dbtools.dbtools (bases[key], 0)
		if not ddb.last_error:
			print 'OK'
			dres[key] = True
		else:	dres[key] = False
	print
	return	dres

def	get_nddata (tname, last_id):
#	print 'get_nddata\t', tname, last_id

	ftime = '%Y-%m-%d %H:%M:%S'
	intm = int(time.time())
	if not last_id:
		print 'get_nddata\t', tname, time.strftime(ftime, time.localtime(intm))
#	print "time.time", intm, 'last_id', last_id, type(last_id)
	'''
	if last_id  and	last_id > 0:
		swhere = "id > %s AND createddatetime > '%s' ORDER BY id" % (last_id, time.strftime(ftime, time.localtime(intm -3600)))
	else:	swhere = "createddatetime > '%s' ORDER BY id" % time.strftime(ftime, time.localtime(intm -600))
	'''
	if last_id  and	last_id > 0:
		swhere = "id > %s AND createddatetime > '%s' ORDER BY createddatetime, id" % (last_id, time.strftime(ftime, time.localtime(intm -3600)))
	else:	swhere = "createddatetime > '%s' ORDER BY createddatetime, id" % time.strftime(ftime, time.localtime(intm -600))

	vms_ws = dbtools.dbtools (bases['vms_ws'])
	res = vms_ws.get_table(tname, swhere)
	if not res:	return
	d = res[0]
	max_id = 0
	j = 0
	for r in res[1]:
		rid = r[d.index('id')]
		devid = r[d.index('deviceid')]
		if not (devid in recvr_dev_list):	continue

		sdate = str(r[d.index('createddatetime')])[:19]
		sstm = time.strptime(sdate[:19], ftime)	
		intm = int(time.mktime(sstm))
	#	print sdate[:19], sstm, time.mktime(sstm)
	#	print rid, r[d.index('lat')], r[d.index('lon')], r[d.index('deviceid')], r[d.index('gpssatcount')], r[d.index('direction')], r[d.index('speed')]
		gpssatcount = direction = 0
		if r[d.index('direction')]:	direction = r[d.index('direction')]
		if r[d.index('gpssatcount')]:	gpssatcount = r[d.index('gpssatcount')]
		query = "UPDATE last_pos SET x = %s, y = %s, t = %s, cr = %s, sp = %s, st = %s WHERE ida = %s AND idd = '%s'" % (
				r[d.index('lon')], r[d.index('lat')], intm, direction, r[d.index('speed')], gpssatcount, devid, devid)
		if not RECVR.qexecute(query):
			query = "INSERT INTO last_pos (ida, idd, x, y, t, cr, sp, st) VALUES (%d, '%d', %s, %s, %s, %s, %s, %s);" % (devid, devid, r[d.index('lon')], r[d.index('lat')], intm, direction, r[d.index('speed')], gpssatcount)
			print query, RECVR.qexecute
		'''##########
		if RECVR.qexecute ("DELETE FROM last_pos WHERE ida =%d;" % devid):
			RECVR.qexecute ("INSERT INTO last_pos (ida, idd, x, y, t, cr, sp, st) VALUES (%d, '%d', %s, %s, %s, %s, %s, %s);" % (
						devid, devid, r[d.index('lon')], r[d.index('lat')], intm, direction, r[d.index('speed')], gpssatcount))
		querys = [
			"DELETE FROM last_pos WHERE ida = %d OR idd = '%s';" % (devid, devid),
			"INSERT INTO last_pos (ida, idd, x, y, t, cr, sp, st) VALUES (%d, '%d', %s, %s, %s, %s, %s, %s);" % (devid, devid, r[d.index('lon')], r[d.index('lat')], intm, direction, r[d.index('speed')], gpssatcount),
	#		"INSERT INTO data_pos (ida, idd, x, y, t, cr, sp, st) VALUES (%d, '%d', %s, %s, %s, %s, %s, %s);" % (devid, devid, r[d.index('lon')], r[d.index('lat')], intm, direction, r[d.index('speed')], gpssatcount),
			]
		if not RECVR.qexecute ("\n".join(querys)):	print querys
		'''############
		if rid > max_id:	max_id = rid
		j += 1
	print "\tlen(res[1]): %d, j: %d, max_id: %d" % (len(res[1]), j, max_id)
	return	max_id

"""
131072+64+2
      2 | СМУ ПП  | Система мониторинга и управления пассажирскими перевозками
      4 | СМУ ША  | Система мониторинга и управления школьными автобусами
      8 | СМ ЖКХ  | Система мониторинга транспортных средств жилищно-коммунального хозяйства
     64 | ЖКХ-М   | ЖКХ-Мусоровозы(Экология)
    128 | СМП     | Скорая помощь
  16384 | СХ      | Сельское хозяйство
  32768 | ЛХ      | Лесное хозяйство
 131072 | ДТ-НН   | Дорожная техника - Нижний Новгород
 262144 | ДТ-НО   | Дорожная техника - Нижегородская область

"""
def     update_recv_ts ():
	""" Обновить список ТС	"""
	dbcntr = dbtools.dbtools('host=127.0.0.1 dbname=contracts port=5432 user=smirnov')
	dbi = dbtools.dbtools('host=127.0.0.1 dbname=receiver port=5432 user=smirnov')
	
	query = "SELECT id_org, inn, bm_ssys, stat FROM org_desc WHERE bm_ssys & (131072+128+64+2) > 0"
	rows = dbi.get_rows (query)
	list_org = []
	for r in rows:
		id_org, inn, bm_ssys, stat = r
		if bm_ssys == 131072 and stat == 0:	continue
		list_org.append(id_org)
#	print	"list_org:", list_org

#	query = "SELECT id_ts, gosnum, marka, a.device_id, inn, uin, o.bm_ssys FROM transports t, organizations o, atts a WHERE o.id_org IN (%s) AND t.id_org = o.id_org AND id_ts = autos ORDER BY o.id_org;" % str(list_org)[1:-1]
	query = "SELECT id_ts, gosnum, marka, a.device_id, inn, uin, o.bm_ssys FROM transports t, organizations o, atts a WHERE o.id_org IN (%s) AND %s ORDER BY o.id_org;" % (
		str(list_org)[1:-1], " AND ".join(["bm_status < 1024", "t.id_org = o.id_org", "id_ts = autos"]))
#	print query
	rows = dbcntr.get_rows (query)
	if not rows:
		print query
		return
	for r in rows:
		id_ts, gosnum, marka, device_id, inn, uin, bm_ssys = r
		if marka:
			marka = "'%s'" % marka
		else:	marka = 'NULL'
		if not device_id:
			print "\tNot device_id", id_ts, gosnum, marka, "inn:", inn, "uin:", uin, "bm_ssys:", bm_ssys
			continue
		if device_id < 0:
		#	print type(uin)
			uin = uin.strip()
		#	print "WWW\t", id_ts, gosnum, marka, device_id, inn, uin, bm_ssys
		#	rw = dbi.get_row ("SELECT gosnum, device_id, inn FROM recv_ts WHERE gosnum = '%s' OR device_id = %s;" % (gosnum, uin))
			query = "SELECT gosnum, device_id, inn FROM recv_ts WHERE gosnum = '%s' OR device_id = %s;" % (gosnum, uin)
			rw = dbi.get_row (query)
			if dbi.last_error:
		#		for s in dbi.last_error:	print s,
				print ">\t", query
			if rw:
				g, d, i = rw
				if gosnum == g and uin == d and inn == i:	
					print "Wialon\t", id_ts, gosnum, marka, device_id, inn
				
			else:
				print ">\tuin [%s]" % uin, ord(uin[-1])
				if bm_ssys == 131072:	# Уборка снега
					query = "INSERT INTO recv_ts (idd, inn, gosnum, marka, device_id, stat_ts) VALUES ('idd%s', %s, '%s', %s, %s, 0)" % (uin, inn, gosnum, marka, uin)
				else:	query = "INSERT INTO recv_ts (idd, inn, gosnum, marka, device_id, stat_ts) VALUES ('%s', %s, '%s', %s, %s, 0)" % ((device_id *-1), inn, gosnum, marka, uin)
				print "Wialon\t", query, dbi.qexecute (query)
		#	print rw
			continue		### 20181211
		
		rr = dbi.get_row ("SELECT gosnum, device_id, inn FROM recv_ts WHERE gosnum = '%s' OR device_id = %s" % (gosnum, device_id))
		if dbi.last_error:	print ">\t '%s', '%s'" % (gosnum, device_id)
		if rr:
			g, d, i = rr
			if device_id < 0 and gosnum == g :		continue
			if gosnum == g and device_id == d and inn == i: continue
			print g, d, i, '!=\t',
			query = "DELETE FROM recv_ts WHERE gosnum = '%s' OR device_id = %s" % (gosnum, device_id)
			print query, dbi.qexecute (query)
	#	else:
		query = "INSERT INTO recv_ts (idd, inn, gosnum, marka, device_id, stat_ts) VALUES ('idd%s', %s, '%s', %s, %s, 0)" % (device_id, inn, gosnum, marka, device_id)
		print query, dbi.qexecute (query)
	#	print id_ts, gosnum, marka, device_id, inn, '<br>'
	print "UPDATE org_desc SET count_ts",   dbi.qexecute ("UPDATE org_desc SET count_ts = (SELECT count(*) FROM recv_ts WHERE org_desc.inn = recv_ts.inn);")

RECVR =	None
#CONTR =	None
#VMSWS =	None
recvr_dev_list = None

def	main ():
	global	RECVR, recvr_dev_list

	last_id = None
	try:
		RECVR =	dbtools.dbtools(bases['recvr'])
		recvr_dev_list = get_racv_list ()
		update_recv_ts ()
		print "len recvr_dev_list", len(recvr_dev_list)
		if RECVR and recvr_dev_list:
			j = 0
			while True:
				last_id = get_nddata (time.strftime('nddata_%Y%m', time.localtime(time.time())), last_id)
				j += 1
				if j > 276:
					j = 0
					clear_old_data (24*3600)
					update_recv_ts ()
					recvr_dev_list = get_racv_list ()
					time.sleep(11)
				else:	time.sleep(3)
			#	if j > 11:	break
		os._exit(0)
	except:
		exc_type, exc_value = sys.exc_info()[:2]
		print "main:", exc_type, exc_value
		os._exit(-1)
	
if __name__ == "__main__":
	print 'Start:', sys.argv, time.strftime('\t%T', time.localtime(time.time()))
	'''
	update_recv_ts ()
	'''
	while True:
		try:
			pid = os.fork()
			if pid > 0:     # PARENT
				pre_fork = 'PARENT'
				print pre_fork, "os.waitpid"
				os.waitpid(pid, 0)
			elif pid == 0:
				pre_fork = 'CHILD'
				main ()
			else:
				pre_fork = 'ERROR'

			print pre_fork, pid
			time.sleep(50)
		except  KeyboardInterrupt:
			print "KeyboardInterrupt"
			break
		except:
			print "#"*22
		print	test()
