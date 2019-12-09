#!/usr/bin/python -u
# -*- coding: utf-8 -*-
""" Утилита crontab.
	Обновление списков ТС для ретрансляции данных в БД receiver
"""
import  os, sys, time

LIBRARY_DIR = r"/home/smirnov/MyTests/CGI/lib/"
sys.path.insert(0, LIBRARY_DIR)

import  dbtools

YELLOW = '\x1b[1;33m'
GREEN =  '\x1b[0;32m'
RED =    '\x1b[0;31m'
NC =     '\x1b[0m'

flag_clear_double = False

def	get_doule_id_ts (dbcntr):
	""" Читать дублированные ссылки transports.id_ts > atts.autos	"""
	rlist = []
	query = "SELECT c.*, t.* FROM vcount_autos c, transports t WHERE count > 1 AND autos = t.id_ts;"
#	['autos', 'count', 'id_ts', 'garnum', 'gosnum', 'marka', 'modele', 'vin', 'year', 'ptsnumber', 'ptsdate', 'registrationnumber', 'registrationdate', 'bm_ssys', 'id_att', 'id_tgroup', 'region', 'id_org', 'ts_type', 'rem', 'transport_id', 'device_id', 'bm_status', 'id_mail', 'transporttype_id', 'devicetype_id', 'category_id', 'yearofcar', 'vinnumber', 'bm_options']
	print YELLOW, "Дублированные ссылки transports.id_ts > atts.autos"
	try:
		rows = dbcntr.get_rows (query)
		d = dbcntr.desc
		for r in rows:
			print "\t", r[d.index('id_ts')], r[d.index('count')], r[d.index('gosnum')], r[d.index('id_org')]
			rlist.append(r[d.index('id_ts')])
	except:
		print YELLOW, "\texcept:", NC, query
	print	NC
	if flag_clear_double:	return	clear_doule_id_ts (dbcntr, rlist)
	return	rlist

def	clear_doule_id_ts (dbcntr, ignore_id_ts):
	""" Почистить дублированные ссылки transports.id_ts > atts.autos. Почистить ignore_id_ts	"""
	rlist = []
	print " Почистить дублированные ссылки transports.id_ts > atts.autos"
	for jt in ignore_id_ts:
		try:
			query = "SELECT id_att, last_date, autos FROM atts WHERE autos = %s ORDER BY id_att;" % jt
			rows = dbcntr.get_rows (query)
			if len(rows) == 1:	continue
			id_att, last_date, autos = rows[0]
			if not last_date:
				jqu = "DELETE FROM atts WHERE id_att = %s" % id_att
				print YELLOW, jqu, NC, dbcntr.qexecute(jqu)
				continue
			gid_att, glast_date, gautos = rows[1]
		#	print [id_att, last_date, autos], [gid_att, glast_date, gautos]
			if glast_date and glast_date > last_date and gid_att > id_att:
				jqu = "DELETE FROM atts WHERE id_att = %s" % id_att
				print "\t", YELLOW, jqu, NC, dbcntr.qexecute(jqu)
				continue
			rlist.append(jt)
		except:	rlist.append(jt)
	return	rlist

def     update_recv_ts ():
	""" Обновить список ТС	""", "#"*33
	dbcntr = dbtools.dbtools('host=127.0.0.1 dbname=contracts port=5432 user=smirnov')
	dbi = dbtools.dbtools('host=127.0.0.1 dbname=receiver port=5432 user=smirnov')

	ignore_id_ts = get_doule_id_ts (dbcntr)
#	ignore_id_ts = clear_doule_id_ts (dbcntr, ignore_id_ts)
	if ignore_id_ts:	print YELLOW, "ignore_id_ts:", NC, ignore_id_ts
#	return
	
	query = "SELECT id_org, inn, bm_ssys, stat FROM org_desc WHERE bm_ssys & (131072+128+64+2) > 0"
	rows = dbi.get_rows (query)
	list_org = []
	for r in rows:
		id_org, inn, bm_ssys, stat = r
		if bm_ssys == 131072 and stat == 0:	continue
		list_org.append(id_org)
#	print	"list_org:", list_org

	query = "SELECT id_ts, gosnum, marka, a.device_id, inn, uin, o.bm_ssys, t.bm_status FROM transports t, organizations o, atts a WHERE o.id_org IN (%s) AND t.id_org = o.id_org AND id_ts = autos ORDER BY o.id_org;" % str(list_org)[1:-1]
	
#	print query
	rows = dbcntr.get_rows (query)
	if not rows:
		print query
		return
	for r in rows:
		id_ts, gosnum, marka, device_id, inn, uin, bm_ssys, bm_status = r
		if marka:
			marka = "'%s'" % marka
		else:	marka = 'NULL'
		if not device_id:
			print YELLOW, "\tNot device_id", NC, id_ts, gosnum, marka, "inn:", inn, "uin:", uin, "bm_ssys:", bm_ssys
			continue

		if bm_status > 1023:
			if dbi.get_row("SELECT gosnum, device_id, inn FROM recv_ts WHERE gosnum = '%s'" % gosnum):
				query = "DELETE FROM recv_ts WHERE gosnum = '%s'" % gosnum
				print YELLOW, "\tbm_status % d" % bm_status, NC, query, dbi.qexecute (query)
			continue

		if id_ts in ignore_id_ts:
			print YELLOW, "\tid_ts", NC, id_ts, "in ignore_id_ts", gosnum, device_id
			continue

		if device_id < 0:	# Wialon
			query ="SELECT gosnum, device_id, inn FROM recv_ts WHERE gosnum = '%s' OR device_id = %s" % (gosnum, uin)
			rws = dbi.get_rows (query)
			if rws:
				if len(rws) > 1:
					print YELLOW, "\tNumber of records %s in query" % len(rws), NC, query
					continue
				g, d, i = rws[0]
				if gosnum == g and inn == i and uin == str(d):	continue
				query = "DELETE FROM recv_ts WHERE gosnum = '%s' OR device_id = %s;" % (gosnum, uin)
				print "Wialon\t", query, dbi.qexecute (query)
				continue
			
			if bm_ssys == 131072:	# Уборка снега
				query = "INSERT INTO recv_ts (idd, inn, gosnum, marka, device_id, stat_ts) VALUES ('idd%s', %s, '%s', %s, %s, 0)" % (uin, inn, gosnum, marka, uin)
			else:	query = "INSERT INTO recv_ts (idd, inn, gosnum, marka, device_id, stat_ts) VALUES ('%s', %s, '%s', %s, %s, 0)" % ((device_id *-1), inn, gosnum, marka, uin)
			print "Wialon\t", query, dbi.qexecute (query)
			continue		### 20181211
		
		query ="SELECT gosnum, device_id, inn FROM recv_ts WHERE gosnum = '%s' OR device_id = %s" % (gosnum, device_id)
		rrs = dbi.get_rows (query)
		if rrs:
			if len(rrs) > 1:
				print YELLOW, "\tNumber of records %s in query" % len(rrs), NC, query
				continue
			g, d, i = rrs[0]
			if device_id < 0 and gosnum == g :		continue
			if gosnum == g and device_id == d and inn == i: continue
			'''
			if id_ts in ignore_id_ts:
				print YELLOW, "\tid_ts", NC, id_ts, "in ignore_id_ts", gosnum, device_id
				continue
			'''
			print id_ts, ' >\t', gosnum, device_id, inn, uin, "\t>", g, d, i
			query = "DELETE FROM recv_ts WHERE gosnum = '%s' OR device_id = %s" % (gosnum, device_id)
			print "\t", query, dbi.qexecute (query)

		query = "INSERT INTO recv_ts (idd, inn, gosnum, marka, device_id, stat_ts) VALUES ('idd%s', %s, '%s', %s, %s, 0)" % (device_id, inn, gosnum, marka, device_id)
		print "\t", query, dbi.qexecute (query)

	print "UPDATE org_desc SET count_ts",   dbi.qexecute ("UPDATE org_desc SET count_ts = (SELECT count(*) FROM recv_ts WHERE org_desc.inn = recv_ts.inn);")

shelp = """\tУтилита crontab.
        Обновление списков ТС для ретрансляции данных в БД receiver
                ./update_recv_ts.py [clear]
                clear - Почистить дублированные ссылки transports.id_ts > atts.autos. Почистить ignore_id_ts
        """
if __name__ == "__main__":
	if len(sys.argv) > 1:
		print sys.argv
		if sys.argv[1] == 'clear':
			flag_clear_double = True
			update_recv_ts ()
		else:	print shelp
	else:
		update_recv_ts ()
