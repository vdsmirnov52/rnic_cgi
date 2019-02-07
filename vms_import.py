#!/usr/bin/python -u
# -*- coding: utf-8 -*-
"""	Утилита crontab	vms_import.py
	Сбор данных о состоянию работоспособности ТС в БД vms_ws 
"""
import  os, sys, time, getopt

LIBRARY_DIR = r"/home/smirnov/pylib"	# Путь к рабочей директории (библиотеке)
sys.path.insert(0, LIBRARY_DIR)
import  dbtools


bases = {
	'vms_ws': 'host=10.40.25.176 dbname=vms_ws port=5432 user=vms',
	'wtm': 'host=127.0.0.1 dbname=worktime port=5432 user=smirnov',
	'contt': 'host=127.0.0.1 dbname=contr_tst port=5432 user=smirnov',
	'contr': 'host=127.0.0.1 dbname=contracts port=5432 user=smirnov',
	}

def	pdict(jdct):		### Print Dictionary
	for k in jdct.keys():
		if jdct[k]:	print "[", k, jdct[k], "]",
	print

def	prow (r, d = None):	### Print Lists | Cortege
	try:
		if d:
			for k in d:	print "%s: %s\t" % (k, str(r[d.index(k)])) ,
		else:
			for c in r:	print "\t", c,
		print
	except:	print "EXCEPT: prow", k

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

def	chk_subsystem ():
	""" Проверка создания новых подсистем ('subsystem') в БВ 'vms_ws'.	"""
	res_c = DB_cont.get_table ('subsys', 'code > 0', cols='pnc_labl, code')
	dict_cntr = {}
	max_code = 0
	for r in res_c[1]:
		pnc_labl, code = r
		dict_cntr[pnc_labl] = code
		if code > max_code:	max_code = code
#	print "max_code", max_code
#	res_vss = DB_vms.get_table('subsystem', 'isdeleted=0 ORDER BY code', cols='code, description')
	res_vss = DB_vms.get_table('subsystem', cols='code, description')
	dict_vms = {}
	for r in res_vss[1]:
		code, description = r
		dict_vms[code] = description
	keys_vms = dict_vms.keys()
	keys_cntr = dict_cntr.keys()
	for k in keys_cntr:	# поиск ключа
		if k in keys_vms:
			del(dict_vms[k])
			del(dict_cntr[k])
	if dict_cntr:		# поиск совпадений в наименовании ключа 
		for kcnt in dict_cntr.keys():
		#	print kcnt, dict_cntr[kcnt]
			keys_vms = dict_vms.keys()
			for kvms in keys_vms:
				if kcnt in kvms:
					del(dict_vms[kvms])
					break
	if dict_vms:
		print	"New subsystem:"
		for kvms in dict_vms.keys():
			print "\t'%s',\t'%s'" % (kvms, dict_vms[kvms])
		print "    'subsys' max code =", max_code
	else:	print "\tchk_subsystem: Ok"

#####################################################
"""-- Выборка всех доступных групп ТС
SELECT t.id, t.changeddatetime, t.createddatetime, tg.description, t.regnum FROM transport t left join transportgroup tg on tg.id=t.group_id WHERE t.isdeleted=0 and (not t.group_id is null) order by tg.description, t.regnum;

-- Владельци ТС (type=1 - организации, type=2 - Диспетчер)
SELECT name FROM rightsowner WHERE type=1;
SELECT * FROM rightsowner WHERE type=1;
"""
###
'''
--	SELECT t.regnum, t.garagenum, tg.description, tt.code AS marka, tt.description AS modele, t.contractnumber, co.inn, co.contactname, co.name, ss.code AS sscode, br.description AS rname
--	LEFT JOIN transportgroup tg ON tg.id = group_id
'''
"""
	SELECT t.regnum, t.garagenum, tt.code AS marka, tt.description AS modele, t.contractnumber, co.inn, co.contactname, co.name, ss.code AS sscode, br.description AS rname
	FROM transport t
	LEFT JOIN transporttype tt ON tt.id = t.transporttype_id
	LEFT JOIN contractor co ON co.id = t.owner_id
	LEFT JOIN subsystem ss ON ss.id = t.subsystem_id
	LEFT JOIN buildingregion br ON br.id = t.region_id
	LIMIT 111;
"""
#	ИП Гаголкин В.А. E754EX152 АВ37152 АВ62652 АВ64352 АВ65452 АВ65652 АВ66952 АВ67052 АТ13752 АТ16452 АТ16552 В982ЕУ152 Е755ЕХ152 Е802ХТ52 К844НТ152 К845НТ152 М230СС152 М250СС152 Т406МС52
#	ИНН:	524400147474

def	chk_transport ():
	query = """SELECT ss.code, t.id, t.regnum, nd.id as dev_id, nd.code as dev_code, ndd.createddatetime, t.createdby_id, --(extract(epoch FROM ndd.createddatetime)) as epoch,
		t.changeddatetime as t_changedt, t.createddatetime as t_createdt
	FROM transport t
	inner join subsystem ss on ss.id=t.subsystem_id
	inner join abstracttransportlink atl on atl.transport_id=t.id AND atl.isdeleted = 0 AND atl.enddate IS NULL
	inner join transport2devicelink t2d on t2d.id=atl.id
	inner join navigationdevice nd on nd.id=t2d.device_id
	left join nddatacacheentry nddc on nddc.deviceid=nd.id
	left join nddata ndd on ndd.id=nddc.lastdata_id
	WHERE t.isdeleted=0
	and (t.discarddate is null or t.discarddate<='08.08.2016 12:00:00')
	and not t.subsystem_id is null
	and (atl.begindate<='%s 12:00:00' or atl.begindate is null)
	and (atl.enddate>='%s 12:00:00' or atl.enddate is null)
	ORDER BY id --	LIMIT 111;
	"""
	sdate = time.strftime("%d.%m.%Y", time.localtime(time.time()))
#	print query % (sdate, sdate)
	rows = DB_vms.get_rows (query % (sdate, sdate))
	if not rows:	return	False
	d = DB_vms.desc
	print d, len(rows)
	for r in rows:
		if "ПП ЦДС" in r[d.index('code')]:	continue
		if "ПП НПАП" in r[d.index('code')]:	continue
		transport_id = r[d.index('id')]
		device_id = r[d.index('dev_id')]
	#	drans = DB_cont.get_table('transports', "transport_id=%d AND device_id=%d" % (transport_id, device_id))
	#	drans = DB_cont.get_table('transports', "transport_id=%d OR device_id=%d" % (transport_id, device_id))
	#	drans = DB_cont.get_table('transports t LEFT JOIN atts a ON t.id_att=a.id_att', "t.device_id=%d" % (device_id))
	#	drans = DB_cont.get_table('transports', "device_id=%d" % (device_id))
		drans = DB_cont.get_table('atts', "device_id=%d" % (device_id))
	#	if "Тестирование" in r[d.index('code')]:	continue
		if not drans:
			print "Not\t",
			prow(r)
	#		for c in r:	print c,
	#		print ""
		elif len(drans[1]) > 1:
			#	autos, mark, modele, uin, last_date, transport_id, device_id
			print len(drans[1]), "#"*11, drans[0]
			for jr in drans[1]:
				for c in jr:	print c,
				print "\tid_att:", jr[drans[0].index('id_att')], r[d.index('code')]
			if drans[1][0][1:] == drans[1][1][1:]:	print "ZZZ", #"id_att", jr[d.index('id_att')]
		else:
			pass
		#	print drans

def	chk_lastdate ():
	sql = """SELECT nd.id, nd.imei, nd.code, ndd.createddatetime
	FROM navigationdevice nd
	INNER JOIN nddatacacheentry nddc on nddc.deviceid=nd.id
	INNER JOIN nddata ndd on ndd.id=nddc.lastdata_id
	WHERE nd.isdeleted=0 ;"""
	rows = DB_vms.get_rows (sql)
	if not rows:	return	False
	d = DB_vms.desc
	print "chk_lastdate", d
	for r in rows:
		sdate = str(r[d.index('createddatetime')])[:19]
	#	qupd = "UPDATE atts SET last_date = '%s' WHERE uin='%s' OR uin='%s';" % (sdate, r[d.index('imei')], r[d.index('code')])
		qupd = "UPDATE atts SET last_date = '%s' WHERE device_id = %d;" % (sdate, r[d.index('id')])
		if not DB_cont.qexecute(qupd):
			print qupd
	#	print r[d.index('id')], '\t', qupd

def	get_id_tgroup (tgname):
	""" Читать id_tgroup по Наменованию. При отсутствии - добавить Группу ТС	"""
	try:
		if tgname and tgname.strip():
			dr = DB_cont.get_dict ("SELECT * FROM ts_groups WHERE tgname = '%s'" % tgname.strip())
			if dr:
				return dr['id_tgroup']
			else:
				q = "INSERT INTO ts_groups (tgname) VALUES ('%s'); SELECT max(id_tgroup)  FROM ts_groups;"  % tgname.strip()
				dr = DB_cont.get_dict (q)
				return dr['max']
	except:	print "EXCEPT: get_id_tgroup", tgname
	return 0

def	chk_auto (rn, id_ts = None):
	""" Проверить наличие машины. При необходтмости добавить или обновит информацию о ней	"""
	d, r = rn
	INN = id_org = region = bm_ssys = None
	if not r[d.index('inn')]:	# tgroup ИНН: НПАП№1 - 5257002665,	МП ЦДС - 5260126942
		if r[d.index('tgroup')] == "НПАП№1":			INN = 5257002665
		elif r[d.index('sscode')] == "ПП ЦДС (тестовая)":	INN = 5260126942
		else:	pass
		#	for c in r:	print "\t", c,
		#	print
	elif r[d.index('inn')].isdigit():	INN = int(r[d.index('inn')])

	if INN:
		dro = DB_cont.get_dict ("SELECT * FROM organizations WHERE inn = %d" % INN)
		if dro:
			id_org = dro['id_org']
			region = dro['region']
			bm_ssys = dro['bm_ssys']
		else:
			print RED, "NOT organizations", NC, 'INN:', INN, 'id_ts:', id_ts
			return
	
	id_tgroup = get_id_tgroup (r[d.index('tgroup')])
	cols = []
	mark = None
	if id_ts:
		mark = 'Id TS'
		jres = DB_cont.get_table ('transports', "id_ts = %d" % id_ts)
		if jres:
			jr = jres[1][0]
			jd = jres[0]
			if id_org:
				if jr[jd.index('id_org')] != id_org:		cols.append('id_org=%d' % id_org)
				'''
				if dro['bm_ssys'] == 1:
					bm_ssys = 1
				elif dro['bm_ssys'] > 1:
					bm_ssys = 0xfffffffe & dro['bm_ssys']
				else:	bm_ssys = 0
				'''
				if bm_ssys and ( not jr[jd.index('bm_ssys')] or jr[jd.index('bm_ssys')] == 0):	cols.append('bm_ssys=%d' % bm_ssys)
				if region and jr[jd.index('region')] != region:		cols.append('region=%d' % region)

			if r[d.index('regnum')].strip() != jr[jd.index('gosnum')]:	cols.append("gosnum = '%s'" % r[d.index('regnum')].strip())
			if r[d.index('tmarka')].strip() != jr[jd.index('marka')]:	cols.append("marka='%s'" % r[d.index('tmarka')].strip())
			if r[d.index('tmodele')].strip() != jr[jd.index('modele')]:	cols.append("modele='%s'" % r[d.index('tmodele')].strip())
			if id_tgroup and id_tgroup != jr[jd.index('id_tgroup')]:	cols.append('id_tgroup=%d' % id_tgroup)
			if r[d.index('id')] != jr[jd.index('device_id')]:		cols.append('device_id=%d' % r[d.index('id')])
			if r[d.index('transport_id')] != jr[jd.index('transport_id')]:	cols.append('transport_id=%d' % r[d.index('transport_id')])
			'''
			if r[d.index('regnum')] and r[d.index('regnum')].strip():	cols.append("gosnum='%s'" % r[d.index('regnum')].strip())
			if r[d.index('tmarka')] and r[d.index('tmarka')].strip():	cols.append("marka='%s'" % r[d.index('tmarka')].strip())
			if r[d.index('tmodele')] and r[d.index('tmodele')].strip():	cols.append("modele='%s'" % r[d.index('tmodele')].strip())
			if id_tgroup and id_tgroup != jr[jd.index('id_tgroup')]:	cols.append('id_tgroup=%d' % id_tgroup)
			if r[d.index('id')]:		cols.append('device_id=%d' % r[d.index('id')])
			if r[d.index('transport_id')]:	cols.append('transport_id=%d' % r[d.index('transport_id')])
		#	if r[d.index('transport_id')]:	cols.append('transport_id=%d' % r[d.index('t2d_id')])
			query = "UPDATE transports SET %s WHERE id_ts = %d;" % (", ".join(cols), id_ts)
			if not DB_cont.qexecute(query):
				print "\t", query
		return id_ts
			'''
	else:	#return 0
		mark = r[d.index('regnum')].strip()
		jres = DB_cont.get_table ('transports', "gosnum = '%s'" % r[d.index('regnum')].strip())
		if not jres:
			print	YELLOW, "Not TS:", r[d.index('regnum')], NC, 'id_org', id_org, region, id_tgroup
		elif len(jres[1]) > 1:
			print	RED, "Doubla TS:", r[d.index('regnum')], NC, 'id_org', id_org, region, id_tgroup
		else:
			jd = jres[0]
			jr = jres[1][0]
			id_ts = jr[jd.index('id_ts')]

			if r[d.index('tmarka')].strip() != jr[jd.index('marka')]:	cols.append("marka='%s'" % r[d.index('tmarka')].strip())
			if r[d.index('tmodele')].strip() != jr[jd.index('modele')]:	cols.append("modele='%s'" % r[d.index('tmodele')].strip())
			if id_tgroup and id_tgroup != jr[jd.index('id_tgroup')]:	cols.append('id_tgroup=%d' % id_tgroup)
			if r[d.index('id')] != jr[jd.index('device_id')]:		cols.append('device_id=%d' % r[d.index('id')])
			if r[d.index('transport_id')] != jr[jd.index('transport_id')]:	cols.append('transport_id=%d' % r[d.index('transport_id')])
	if id_ts and cols:
		query = "UPDATE transports SET %s WHERE id_ts = %d;" % (", ".join(cols), id_ts)
		print YELLOW, mark, NC, query, DB_cont.qexecute(query)
	return id_ts

def	insert_transport(r, d, id_org, region, id_tgroup, bm_ssys, print_only = False):
		drt = DB_cont.get_dict("SELECT id_ts, device_id, transport_id FROM transports WHERE gosnum = '%s'" % r[d.index('regnum')])
		if drt:
			if not (drt['device_id'] == r[d.index('id')] and drt['transport_id'] == r[d.index('transport_id')]):
				www = DB_cont.get_dict("SELECT id_ts, gosnum FROM transports WHERE device_id = %d AND transport_id = %d" % (r[d.index('id')], r[d.index('transport_id')]))
				if www:		print RED, "Double device_id AND transport_id", NC, www, r[d.index('id')], r[d.index('transport_id')]

				query = "UPDATE transports SET device_id = %d, transport_id = %d WHERE id_ts = %d;" % (r[d.index('id')], r[d.index('transport_id')], drt['id_ts'])
				print YELLOW, query, NC, DB_cont.qexecute(query)
			return drt['id_ts']
		'''
		drt = DB_cont.get_dict("SELECT id_ts FROM transports WHERE device_id = %d AND transport_id = %d" % (r[d.index('id')], r[d.index('transport_id')]))
		if drt:		return drt['id_ts']
		'''
		
	#	id_ts, garnum, gosnum, marka, modele, vin, year, pts, pts_date, sregistr, sreg_date, bm_ssys, id_att, id_tgroup, region, id_org, ts_type, rem, transport_id, device_id, bm_status
		cnm = ['device_id', 'transport_id', 'id_tgroup']
		val = [str(r[d.index('id')]), str(r[d.index('transport_id')]), str(id_tgroup)]
		if id_org:
			cnm.append('id_org')
			val.append(str(id_org))
			if region:
				cnm.append('region')
				val.append(str(region))
		if r[d.index('regnum')]:
			cnm.append('gosnum')
			val.append("'%s'" % r[d.index('regnum')])
		if r[d.index('tmarka')]:
			cnm.append('marka')
			val.append("'%s'" % r[d.index('tmarka')])
		if r[d.index('tmodele')]:
			cnm.append('modele')
			val.append("'%s'" % r[d.index('tmodele')])
		if bm_ssys:
			cnm.append('bm_ssys')
			val.append(str(bm_ssys))
		query = "INSERT INTO transports (%s, bm_status) VALUES (%s, 64); SELECT max(id_ts) FROM transports" % (", ".join(cnm), ", ".join(val))
		if not id_org:
			print RED, 'id_org:', id_org, NC, query
			return	0
		if print_only:
			drt = None
		else:	drt = DB_cont.get_dict(query)
		print YELLOW, query, NC, drt
		if drt:
			return drt['max']
		else:	return 0
			
	
def	check_yullik (r, d):
	cols_nd = ['operator1_id', 'operator2_id', 'icc_id1', 'icc_id2', 'devicetype_id',]
	cols_ts = ['transporttype_id', 'yearofcar', 'category_id', 'vinnumber', 'ptsnumber', 'ptsdate', 'registrationdate', 'registrationnumber',]

	query = 'SELECT * FROM transports WHERE bm_status > 0 AND transport_id = %d;' % r[d.index('transport_id')]
	dct_ts = DB_cont.get_dict (query)
	if not dct_ts:		return
	ss_nd = []
	ss_ts = []
	querys = []
	if r[d.index('yearofcar')] and len (r[d.index('yearofcar')]) > 4:
		print "ZZZ\t", r[d.index('regnum')], 'yearofcar:"%s"' % r[d.index('yearofcar')]
		return
		'''
		for k in d:
			if not r[d.index(k)]:	continue
			print k,"\t'%s'" % r[d.index(k)]
			return
		'''
	for c in cols_ts:
		if r[d.index(c)] and dct_ts[c] != r[d.index(c)]:	#	not dct_ts[c] or (r[d.index(c)] and dct_ts[c] != r[d.index(c)]):
			ss_ts.append("%s = '%s'" % (c, r[d.index(c)]))
	#	else:	print '\t', c, dct_ts[c], r[d.index(c)]
	if ss_ts:
		querys.append("UPDATE transports SET %s WHERE transport_id = %d;" % (', '.join(ss_ts), r[d.index('transport_id')]))

	query = 'SELECT * FROM atts WHERE device_id = %d;' % r[d.index('id')]
	dct_att = DB_cont.get_dict (query)
	if not dct_att:
		print "Not device in 'atts'.", query
	else:
		for c in cols_nd:
			if r[d.index(c)] and dct_att[c] != r[d.index(c)]:
				ss_nd.append("%s = '%s'" % (c, r[d.index(c)]))
		if ss_nd:
			querys.append("UPDATE atts SET %s  WHERE device_id = %d;" % (', '.join(ss_nd), r[d.index('id')]))

	if querys:
		query = '\n'.join(querys)
		if not DB_cont.qexecute(query):
			print query

def	chk_atts ():
	sql = """SELECT nd.id, imei, nd.code, nd.name, nd.phone, nd.phone2, 
	nd.operator1_id, nd.operator2_id, nd.icc_id1, nd.icc_id2, nd.devicetype_id,	--yu
	nt.description as marka, t2d.id as t2d_id, atl.transport_id, t.regnum, t.garagenum, t.contractnumber,
	t.transporttype_id, t.yearofcar, t.category_id, t.vinnumber, t.ptsnumber, t.ptsdate, t.registrationdate, t.registrationnumber, --yu
        tt.code AS tmarka, tt.description AS tmodele, 
        co.inn, 
        ss.code AS sscode, tg.code AS tgroup
        FROM navigationdevice nd
        INNER JOIN transport2devicelink t2d on t2d.device_id=nd.id
        INNER JOIN abstracttransportlink atl on atl.id=t2d.id AND atl.isdeleted = 0 AND atl.enddate IS NULL
        INNER JOIN transport t on atl.transport_id=t.id
        INNER JOIN subsystem ss ON ss.id = t.subsystem_id
        INNER JOIN transporttype tt ON tt.id = t.transporttype_id
        INNER JOIN navigationdevicetype nt ON nt.id = nd.devicetype_id
        LEFT JOIN transportgroup tg ON tg.id = t.group_id
        LEFT JOIN contractor co ON co.id = t.owner_id
        WHERE nd.isdeleted=0
	ORDER BY nd.id
	"""
	
	rows = DB_vms.get_rows (sql)
	if not rows:	return	False
	d = DB_vms.desc
#	print d
#	att2nav = {'mark': 'marka', 'modele': 'name', 'sim_1': 'phone', 'sim_2': 'phone2'}
	new_atts = []
	new_ts = []
	j = 0
	for r in rows:
		ratts = check_atts_double (r, d)
		if not ratts:
			new_atts.append(r)
			continue
		elif len (ratts) > 1:
			print RED, "Double ATTS", NC, "chk_atts device_id:", r[d.index('id')], r[d.index('regnum')]
		#	for jr in ratts:	prow (jr)
			continue
		j += 1
		jr = ratts[0]	# jres[1][0]
		jd = DB_cont.desc
		id_ts = chk_auto ((d, r), jr[jd.index('autos')])
		cols = []
		for k in att2nav.keys():
			if r[d.index(att2nav[k])] and r[d.index(att2nav[k])].strip():	cols.append("%s='%s'" % (k, r[d.index(att2nav[k])]))
		if id_ts:			cols.append('autos=%d' % id_ts)
#		if r[d.index('code')]:		cols.append("code='%s'" % r[d.index('code')]) 
		if r[d.index('id')]:		cols.append('device_id=%d' % r[d.index('id')])
		if r[d.index('transport_id')]:	cols.append('transport_id=%d' %  r[d.index('transport_id')])
		query = "UPDATE atts SET %s WHERE uin='%s' OR uin='%s';" % (", ".join (cols), r[d.index('imei')], r[d.index('code')])
	#	if j > 111:	break
		if not DB_cont.qexecute(query):
			print RED, 'Error', NC, query
		
		check_yullik (r, d)
		# Проверить транспорт transports	(garnum, gosnum)
		if r[d.index('regnum')].strip():
			gosnum = r[d.index('regnum')].strip()
		elif r[d.index('garagenum')].strip():
			gosnum = r[d.index('garagenum')].strip()
		else:
			print "Not gosnum:\t",
			prow (r, d)
			continue
		jres = DB_cont.get_table("transports", "gosnum='%s' OR garnum='%s'" % (gosnum, gosnum))
		if not jres:
			new_ts.append(r)
			continue
		jd = jres[0]
		if len(jres[1]) > 1:
			print "Double TS", "gosnum='%s' OR garnum='%s'" % (gosnum, gosnum), "id_ts:", id_ts, "\n\t", jd
			for jr in jres[1]:
				prow (jr)
				if id_ts == jr[jd.index('id_ts')]:
					query = "UPDATE transports SET id_att = (SELECT id_att FROM atts WHERE autos = %d) WHERE id_ts = %d;" % (id_ts, id_ts)
				else:
					query = "DELETE FROM transports WHERE id_ts = %d;" % jr[jd.index('id_ts')]
				print YELLOW, gosnum, query, NC, DB_cont.qexecute(query)
			continue

		bm_status = jres[1][0][jd.index('bm_status')]
		# Наличие договара в БД vms_ws
		if ((bm_status == None) or (bm_status & 4 == 0)) and (r[d.index('contractnumber')] and len(r[d.index('contractnumber')]) > 4):
			if bm_status > 0:
				query = "UPDATE transports SET bm_status = %d WHERE id_ts = %d;" % (4+bm_status, jres[1][0][jd.index('id_ts')])
			else:	query = "UPDATE transports SET bm_status = 4 WHERE id_ts = %d;" % jres[1][0][jd.index('id_ts')]
			print YELLOW, gosnum, NC, '\t', query, DB_cont.qexecute(query)
		elif FL_CBlok and (bm_status > 0 and (bm_status & TS_BLOCK == 0)) and (not r[d.index('contractnumber')] or len(r[d.index('contractnumber')]) < 4):
			# Блокировка ТС по отсутствию договора
			query = "UPDATE transports SET bm_status = %d WHERE id_ts = %d;" % (TS_BLOCK+bm_status, jres[1][0][jd.index('id_ts')])
			print YELLOW, gosnum, NC, '\t', query, DB_cont.qexecute(query)

	#	if j > 222:	break

	print "chk_atts Проверено %d устройств." % j
	'''
	print "new_atts", d
	print "new_atts:"
	for r in new_atts:	prow (r)
	print "new_ts:"
	for r in new_ts:	prow (r)
	return
	'''

	if new_atts:	add_transport (d, new_atts, 'new_atts')
	if new_ts:	add_transport (d, new_ts, 'new_ts')

#	Контроль соответствия transport.id_ts -> atts.autos
"""	SELECT a.*, t.device_id, t.transport_id, id_ts FROM transports t
	INNER JOIN atts a ON a.autos = t.id_ts
	WHERE t.device_id = a.device_id AND t.transport_id = a.transport_id;
"""
att2nav = {'mark': 'marka', 'modele': 'name', 'sim_1': 'phone', 'sim_2': 'phone2', 'code': 'code'}

def	check_atts_double (r, d):	# return	[(row att)[, ]]
	res = []
	vms = (r[d.index('id')], r[d.index('transport_id')])
	ratts = DB_cont.get_rows("SELECT * FROM atts WHERE device_id = %d OR transport_id = %d" % (r[d.index('id')], r[d.index('transport_id')]))
	max_id_att = 0
	if ratts:
		dd = DB_cont.desc
		for jr in ratts:
			att = (jr[dd.index('device_id')], jr[dd.index('transport_id')])
			if vms != att:
	#			print vms, att
	#		if not (r[d.index('id')] == jr[dd.index('device_id')] and r[d.index('transport_id')] == jr[dd.index('transport_id')]):
				query = "DELETE FROM atts WHERE device_id = %d OR transport_id = %d" % (jr[dd.index('device_id')], jr[dd.index('transport_id')])
				print YELLOW, query, NC, DB_cont.qexecute(query)
			else:
				if max_id_att < jr[dd.index('id_att')]:	max_id_att = jr[dd.index('id_att')]
				res.append(jr)
				
	if len(res) > 1:
		if max_id_att > 0:
			query = "DELETE FROM atts WHERE device_id = %d AND transport_id = %d AND id_att < %d;" % (jr[dd.index('device_id')], jr[dd.index('transport_id')], max_id_att)
			print YELLOW, query, NC, DB_cont.qexecute(query)
		else:
			for jr in res:	prow (jr)
	return	res

def	add_transport (d, atts_list, flist = None):
	print "add_transport Len atts_list", len(atts_list), flist, "="*22
	sql = """SELECT t.regnum, t.garagenum, tt.code AS marka, tt.description AS modele, t.contractnumber, co.inn, co.name, ss.code AS sscode, br.description AS rname, t.contractnumber
	FROM transport t
	INNER JOIN subsystem ss ON ss.id = t.subsystem_id
	INNER JOIN transporttype tt ON tt.id = t.transporttype_id
	-- LEFT JOIN transporttype tt ON tt.id = t.transporttype_id
	LEFT JOIN contractor co ON co.id = t.owner_id
	LEFT JOIN buildingregion br ON br.id = t.region_id
	WHERE t.id = %d; """
	dd_vms = None
	dd = None
	fl_exit = False
	lj = 0
	unknown_inn = []
	
#	print flist, d
	for r in atts_list:
		if not r[d.index('inn')]:
			'''	Игнорируем по отсутствию ИНН	'''
			continue
	#	prow (r, d)
	#	dratt = DB_cont.get_dict("SELECT * FROM atts WHERE device_id = %d" % r[d.index('id')])
	#	print dratt
	#	continue
		qsql = sql % r[d.index('transport_id')]
		jres = DB_vms.get_rows(qsql)
		if not jres:	# отсутствует transport_id
			print "NOT:\t", r[d.index('transport_id')]
			continue
		elif len(jres) > 1:
			print "DB_vms: Double transport_id", len(jres)
			for r in jres:	prow (r)
			continue
		if not dd_vms:	dd_vms = DB_vms.desc

		ratts = check_atts_double (r, d)
		if ratts:
			pass
		#	insert_atts (r, d, fff='WWW')
		elif len (ratts) > 1:
			print "Double ATTS add_transport device_id:", r[d.index('id')]
			for jr in ratts:	prow (jr)
			continue

		id_ts = chk_auto ((d, r))

		for jr in jres:
			dorg = DB_cont.get_dict("SELECT * FROM organizations WHERE inn=%s" % r[d.index('inn')])
			if not dorg:
				'''
				print RED, "Not INN:", NC,
				for c in ['inn', 'imei', 'code', 'name', 'marka', 't2d_id', 'transport_id', 'regnum', 'garagenum', 'contractnumber', 'tmarka', 'tmodele', 'tgroup']:
					print "%s\t" % str(r[d.index(c)]),
				print
				'''
				if not r[d.index('inn')] in unknown_inn:	unknown_inn.append(r[d.index('inn')])
				continue

			if flist and flist == 'new_atts':
				dratt = DB_cont.get_dict("SELECT * FROM atts WHERE device_id = %d" % r[d.index('id')])
			#	dratt = DB_cont.get_dict("SELECT * FROM atts WHERE transport_id = %d" % r[d.index('transport_id')])
				if dratt:
					for j in range(len(d)):		print "\t%s:" % d[j], r[j],
					print "<<"
					continue
				else:
					id_att = insert_atts (r, d, cols=[], vals=[], fff='ZZZ')

			id_tgroup = get_id_tgroup (r[d.index('tgroup')])
		#	autos = insert_transport(r, d, dorg['id_org'], dorg['region'], id_tgroup, dorg['bm_ssys'])	#, True)
		#	id_ts = chk_auto ((d, r))

			if id_ts:
				if flist and flist == 'new_atts':
					id_att = insert_atts (r, d, cols = ["autos"], vals = ["%d" % id_ts], fff='QQQ')
					print "QQQQQQ id_att", id_att
				else:	
					query = "UPDATE atts SET autos= %d WHERE transport_id = %d AND device_id = %d" % (id_ts, r[d.index('transport_id')], r[d.index('id')])
					if not DB_cont.qexecute(query):
						print query
			else:
				print 'add_transport QWER'
				autos = insert_transport(r, d, dorg['id_org'], dorg['region'], id_tgroup, dorg['bm_ssys'])       #, True
				id_att = insert_atts (r, d, cols = ["autos"], vals = ["%d" % autos], fff='autos')
				if autos > 0 and id_att > 0:
					query = "UPDATE transports SET id_att = %d WHERE id_ts = %d" % (id_att, autos)
					print YELLOW, query, NC, DB_cont.qexecute(query)
					query = "UPDATE atts SET autos = %d WHERE id_att = %d" % (autos, id_att)
					print YELLOW, query, NC, DB_cont.qexecute(query)
		#	if lj > 22:	return
			lj += 1
	if unknown_inn:	print RED, "Unknowns INN:", NC, unknown_inn

YELLOW=	'\x1b[1;33m'
GREEN=	'\x1b[0;32m'
RED=	'\x1b[0;31m'
NC=	'\x1b[0m'	# No Colors

def	insert_atts (r, d, cols = [], vals = [], fff = None):
	datt = DB_cont.get_dict ("SELECT * FROM atts WHERE device_id = %d AND transport_id = %d" % (r[d.index('id')], r[d.index('transport_id')]))
	if datt:	return datt['id_att']

	print "insert_atts:\t", fff, 
	for k in att2nav.keys():
		if r[d.index(att2nav[k])] and r[d.index(att2nav[k])].strip():
			cols.append(k)
			vals.append("'%s'" % r[d.index(att2nav[k])])
	query = "INSERT INTO atts (%s, transport_id, device_id) VALUES (%s, %d, %d); SELECT max(id_att) FROM atts;" % (', '.join(cols), ', '.join(vals), r[d.index('transport_id')], r[d.index('id')])
	print YELLOW, query, NC,
	datt = DB_cont.get_dict (query)
	print datt
	if datt:	return	datt['max']
	return	0

def	check_ts_contr2vms (FLTS = None):
	print "Блокировать/Удалить  машины в БД contracts пр исключении их в vms_ws", FLTS
	sttm =  time.localtime(time.time())
	tm_year, tm_mon, tm_mday = sttm[:3]
	dbcontr = dbtools.dbtools (bases['contr'])
	res = dbcontr.get_table ('wtransports', "amark != 'WialonHost' AND (bm_status IS NULL OR (bm_status & 1024 = 0))")	# WIALON
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
			print YELLOW, r[d.index('gosnum')], "\tid_org:", r[d.index('id_org')], NC,
			if r[d.index('bm_status')]:
				query = "UPDATE transports SET bm_status = bm_status | %d WHERE id_ts = %d;" % (TS_BLOCK, r[d.index('id_ts')])
			else:	query = "UPDATE transports SET bm_status = %d WHERE id_ts = %d;" % (TS_BLOCK, r[d.index('id_ts')])
			print query, dbcontr.qexecute (query)
		
	print	"res_ln:", res_ln, "\tis active:", j

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
	return	DB_vms.get_dict (query)

def	find_atts (swhere = "id_org=0"):
	""" Поиск навигаторов и ТС в БД vms_ws	"""
	# t.contractnumber
	sql = """SELECT nd.id, nd.imei, nd.code, nd.name, nd.phone, nd.phone2, nt.description as marka, t2d.id as t2d_id, atl.transport_id, t.regnum, co.inn, tt.code AS tmarka, tt.description AS tmodele
	FROM navigationdevice nd
	INNER JOIN transport2devicelink t2d on t2d.device_id=nd.id
	INNER JOIN abstracttransportlink atl on atl.id=t2d.id AND atl.isdeleted = 0 AND atl.enddate IS NULL
	INNER JOIN transport t on atl.transport_id=t.id
	LEFT JOIN transporttype tt ON tt.id = t.transporttype_id
	LEFT JOIN contractor co ON co.id = t.owner_id
	LEFT JOIN navigationdevicetype nt ON nt.id = nd.devicetype_id
	WHERE nd.isdeleted=0 %s;"""

	res = DB_cont.get_table('voatts', swhere, "id_att, autos, uin, sim_1, sim_2, transport_id, device_id, gosnum")
	if not res:
		print "\tfind_atts Нет данных."
		return
	d = res[0]
	print	d
	j = 0
	for r in res[1]:
		if r[d.index('uin')]:	### 27.03.2017
			sand = "AND (imei = '%s' OR nd.code = '%s')" % (r[d.index('uin')], r[d.index('uin')])
		else:	sand = ''
		jdct = DB_vms.get_dict (sql % sand)
		if not jdct:
			print "Not >\t",
			for c in r:	print c, "\t",
			print sand
			continue
#		print r
#		continue
		quers = []
		id_att = r[d.index('id_att')]
		autos = r[d.index('autos')]
		marka = "'%s'" % jdct['marka'][:64]	if (jdct['marka'] and jdct['marka'].strip())	else "NULL"
		name = "'%s'" % jdct['name'][:64]	if (jdct['name'] and jdct['name'].strip())	else "NULL"
		phone = "'%s'" % jdct['phone']		if (jdct['phone'] and jdct['phone'].strip())	else "NULL"
		phone2 = "'%s'" % jdct['phone2']	if (jdct['phone2'] and jdct['phone2'].strip())	else "NULL"
		tmarka = "'%s'" % jdct['tmarka'][:64]	if (jdct['tmarka'] and jdct['tmarka'].strip())	else "NULL"
		tmodele = "'%s'" % jdct['tmodele'][:64]	if (jdct['tmodele'] and jdct['tmodele'].strip())	else "NULL"
		regnum = "'%s'" % jdct['regnum']	if (jdct['regnum'] and jdct['regnum'].strip())	else "NULL"
		quers.append ("UPDATE atts SET mark=%s, modele=%s, sim_1=%s, sim_2=%s, transport_id=%d, device_id=%d WHERE id_att =%d;" % (marka, name, phone, phone2,
                        jdct['transport_id'], jdct['id'], id_att))
		if jdct['inn'] and jdct['inn'] > 0:
		#	pdict (jdct) 
			quers.append ("UPDATE transports SET transport_id=%d, device_id=%d, marka=%s, modele=%s, gosnum=%s, id_org = (SELECT id_org FROM organizations WHERE inn = %s) WHERE id_ts = %d;" % (
				jdct['transport_id'], jdct['id'], tmarka, tmodele, regnum, jdct['inn'], autos))
			#	jdct['t2d_id'], jdct['id'], tmarka, tmodele, regnum, jdct['inn'], autos))
		else:
		#	print "ZZZ", j, jdct['transport_id'], jdct['id'],  autos
			quers.append ("UPDATE transports SET transport_id=%d, device_id=%d, marka=%s, modele=%s, gosnum=%s WHERE id_ts = %d;" % (jdct['transport_id'], jdct['id'], tmarka, tmodele, regnum, autos))
		#	quers.append ("UPDATE transports SET transport_id=%d, device_id=%d, marka=%s, modele=%s, gosnum=%s WHERE id_ts = %d;" % (jdct['t2d_id'], jdct['id'], tmarka, tmodele, regnum, autos))
	#	print "quers", quers
		if not DB_cont.qexecute("\n".join(quers)):
			print "\n".join(quers)
			break
		j += 1
	#	if j > 111:	break
	print	"Len RES:", j

def	check_param(pname):
	global	DB_vms, DB_cont

	if not cparam in check_pnames:
		print "Параметр '%s' отсутствует в Списке:\n\t" % pname, check_pnames
		return
	DB_vms = dbtools.dbtools (bases['vms_ws'])
	if DEBUG:
		print "DEBUG\t",
		DB_cont = dbtools.dbtools (bases['contt'])	# DEBUG
	else:	DB_cont = dbtools.dbtools (bases['contr'])

	print "check_param", pname
	if pname == 'subsystem':	return	chk_subsystem()
	if pname == 'all_ts':		return	chk_transport()
	if pname == 'lastdate':		return	chk_lastdate()
	if pname == 'atts':		return	chk_atts()
	if pname == 'find_org':		return	find_atts ("id_org=0")
	if pname == 'check_org':	return	check_org ()

TS_BLOCK =	1024	

def	check_org ():
	""" Контроль наличия ТС в transports и wtransports	"""
	res = DB_cont.get_table ('organizations', 'inn > 0 ORDER BY id_org')
	print " Контроль ТС в transports и wtransports      "
	if not res:
		print RED, 'Not res', NC
	d = res[0]
	jts = jtsc = 0
	for ro in res[1]:
		id_org = ro[d.index('id_org')]
		rts = DB_cont.get_rows ('SELECT id_ts, gosnum, bm_status, device_id, transport_id FROM vtransports WHERE id_org = %d AND (bm_status & %d) > 0 ORDER BY gosnum, id_ts' % (id_org, 15))	#TS_BLOCK))
		rwts = DB_cont.get_rows ('SELECT id_ts, gosnum, bm_status, device_id, transport_id FROM wtransports WHERE id_org = %d ORDER BY gosnum, id_ts' % id_org)
		countts = len(rts)
		countwts = len(rwts)
		if countts != countwts:
			isdouble = False
			print id_org, ro[d.index('bname')], '\tTS:', countts, 'in Work:', countwts, 'd:', (countwts - countts)
			jw = 0
			for j in xrange(countts):
				if jw >= countwts:	break
				if rts[j] == rwts[jw]:
					id_ts, gosnum, bm_status, device_id, transport_id = rts[j]
					'''
					print '\rT\t', id_ts, gosnum, bm_status, device_id, transport_id, '\t',
					ratt = DB_cont.get_rows('SELECT id_att, autos, device_id, transport_id FROM atts WHERE  autos = %d' % id_ts)
					print ratt, '\n\t',
					'''
					first = 0
					while jw < countwts and rts[j] == rwts[jw]:
						if first == 1:
							print '\rT\t', id_ts, gosnum, bm_status, device_id, transport_id, '\t',
							ratt = DB_cont.get_rows('SELECT id_att, autos, device_id, transport_id FROM atts WHERE  autos = %d' % id_ts)
							print ratt, '\n\t',
							isdouble = True
						if first > 0:
							for c in rwts[jw]:	print c,
							print j, jw, countwts, first, '\n\t',
						first += 1
						jw += 1
			#	else:	jw += 1
			if isdouble:	print
			jtsc += 1
		jts += 1
	#	if jts > 111:	break
	print '#'*11, 'check_org', jts, jtsc

def	check_vn2regnum ():
	print """ Проверить vn2regnum и маркировать Стат.ТС |= 1C в contracts transports	"""
	# create view vn2regnum AS SELECT w.*, a.regnum,a.regnumber, a.device_id FROM nav_work_time w, nav2regnum a WHERE w.id_auto = a.id ORDER BY w.id_auto;
	dbwtm = dbtools.dbtools (bases['wtm'])
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
						querys.append("UPDATE transports SET bm_status =  %d  WHERE device_id = %d AND gosnum = '%s'" % (jstatus, device_id, jgosnum))
			if querys:
				if not dbcontr.qexecute (";\n".join(querys)):
					print ";\n".join(querys)

		print "Len rows", len(rows)
		if new_autos:
			print "new_autos in vn2regnum:\n\t device_id \t is_work \t is_work"

			for r in new_autos:
				device_id, is_work, regnum = r
				print "\t", regnum, "\t", device_id, "\t", is_work
	else:	return "Not Rows!"

def	outhelp():
	print """
	Утилита crontab
	Сбор данных о состоянию работоспособности ТС в БД vms_ws
	-t	Контроль соединений с БД
	-d	Отладка	(DEBUG = True)
	-w	Проверить vn2regnum и маркировать Стат.ТС |= 1C в contracts transports
	-b	Блокировка ТС по отсутствию договора
	-c 	Контроль данных { %s }
	-h	Справка
	
Контроль дублей в atts -> CREATE VIEW vcount_autos AS SELECT atts.autos, count(atts.id_att) AS count FROM atts WHERE (atts.autos IN ( SELECT vtransports.id_ts FROM vtransports)) GROUP BY atts.autos;
	SELECT c.*, t.* FROM vcount_autos c, transports t WHERE count > 1 AND autos = t.id_ts;

	SELECT * FROM atts WHERE autos IS NULL ;
	UPDATE atts a set autos = (SELECT id_ts FROM transports t WHERE t.device_id = a.device_id AND t.transport_id = a.transport_id) WHERE autos IS NULL;

	SELECT gosnum, t.bm_ssys, t.id_org FROM transports t WHERE t.bm_ssys > 0 AND t.id_org > 0 AND bm_ssys != (SELECT bm_ssys FROM organizations o WHERE o.id_org = t.id_org);
	UPDATE transports t SET bm_ssys = (SELECT bm_ssys FROM organizations o WHERE o.id_org = t.id_org)  WHERE t.bm_ssys > 0 AND t.id_org > 0 AND bm_ssys != (SELECT bm_ssys FROM organizations o WHERE o.id_org = t.id_org);
	""" % ' | '.join(check_pnames)

#QQQ	SELECT * FROM nddatacacheentry WHERE lastdata_id >0 AND prevdata_id >0 AND lastupdated > '2016-11-28 00:00:00' AND lastupdated < '2016-11-28 23:59:59';
#QQQ	UPDATE transports t SET bm_ssys = (SELECT bm_ssys FROM organizations o WHERE t.id_org = o.id_org AND o.bm_ssys >0) WHERE bm_ssys = 0 AND id_org > 0;
#QQQ	ALTER TABLE ONLY transports ADD CONSTRAINT transports_gosnum_key UNIQUE (gosnum);

check_pnames = ['subsystem', 'all_ts', 'lastdate', 'atts', 'find_org', 'check_org']
cparam =	None
DB_vms =	None
DB_cont =	None
DEBUG =		False

if __name__ == "__main__":
	FL_help = False
	FL_test = False
	FL_wtmr = False
	FL_CBlok = False	# Блокировка ТС по отсутствию договора

	sttmr = time.time()
	print "Start %i" % os.getpid(), sys.argv, time.strftime("%Y-%m-%d %T", time.localtime(sttmr))
	try:
		optlist, args = getopt.getopt(sys.argv[1:], 'htbdwc:')
		for o in optlist:
			if o[0] == '-h':	FL_help = True
			if o[0] == '-t':	FL_test = True
			if o[0] == '-b':	FL_CBlok = True
			if o[0] == '-d':	DEBUG = True
			if o[0] == '-c':	cparam = o[1]
			if o[0] == '-w':	FL_wtmr = True

		if FL_test:
			for key in bases:
				print key, "\t=", bases[key], '\t>',
				ddb = dbtools.dbtools (bases[key], 0)
				if not ddb.last_error:	print 'OK'
		elif FL_help:	outhelp()
		elif FL_wtmr:	check_vn2regnum()
		else:
			if cparam:
				check_param (cparam.strip())
			else: 
				print optlist,args
				outhelp()
		if FL_CBlok:	check_ts_contr2vms ()
	except:
		exc_type, exc_value = sys.exc_info()[:2]
		print "EXCEPT:", exc_type, exc_value
