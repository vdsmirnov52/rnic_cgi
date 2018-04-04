#!/usr/bin/python
# -*- coding: utf-8 -*-

import  cgi, os, sys
import	psycopg2, psycopg2.extensions
import	time

print "Content-Type: text/html; charset=utf-8\n"


LIBRARY_DIR = r"/home/smirnov/MyTests/CGI/lib/"		# Путь к рабочей директории (библиотеке)
sys.path.insert(0, LIBRARY_DIR)

import	cglob
import	session
import	dbtools
import	dicts

CDB_DESC = cglob.get_CDB_DESC('ZZZ')

def	set_sysoptions (SS, request):
	""" Выбор подсистемы, Выбор Роли	"""
	import	rusers
	if request.has_key('sssystem') and request['sssystem'] != '':
		oname = 'subsystem'
		res = rusers.get_table('subsystem', 'code = %s' % request['sssystem'])
	elif request.has_key('setrole') and request['setrole'] != '':
		oname = 'role'
		res = rusers.get_table('roles', 'code = %s' % request['setrole'])
	else:
		print "set_sysoptions request:", request
		return
	if res:
		sss = {}
		for k in res[0]:	sss[k] = res[1][0][res[0].index(k)]
		SS.set_obj(oname, sss)
		print "~eval|document.myForm.submit();"
	else:	print "set_sysoptions res:", res

def	find_device2org (SS, request):
	idb = dbtools.dbtools (CDB_DESC)
	if request.has_key('idrow') and request['idrow'].isdigit():
		sss = "device_id = <b>%s</b>" % request['idrow']
		query = "SELECT * FROM transports WHERE device_id = %s" % request['idrow']
		res = idb.get_table('vtransports', "device_id = %s" % request['idrow'])
		if res:
			d = res[0]
			if len(res[1]) > 1:
				ltxt = ["<pre class='mbody' style='padding: 5px'>"]
				for r in res[1]:
					ltxt.append ("%s\t%s\t%s\t%s\n" % (r[d.index('gosnum')], r[d.index('marka')], r[d.index('oname')], r[d.index('rname')]))
				ltxt.append('</pre>')
				cglob.out_widget('wbox', "find_device2org", txt = ' '.join(ltxt), sright = sss)
			else:
				import  conract
				conract.out_tform (SS, 'vorganizations', 'id_org', res[1][0][d.index('id_org')])	#, reqst = request)
				edit_device_rem(request)
		else:
			cglob.out_widget('wbox', "find_device2org", txt = "<div class='mark' style='padding: 8px'><b>Устройство отсутствует в Базе данных!<br/></b>&nbsp;&nbsp; %s </div>" % CDB_DESC, sright = sss)
	else:	cglob.out_widget('wbox', "find_device2org", txt = str(request), sright = 'find_device2org', obj = SS.objpkl)

def	edit_device_rem(request, rem = None):
	Y = 10+	int(request['Y'])
	X = 1100	#int(request['X'])
	idb = dbtools.dbtools("host=127.0.0.1 dbname=worktime port=5432 user=smirnov")
	query = "SELECT w.*, n.regnum, n.device_id FROM work_statistic w LEFT JOIN nav2regnum n ON w.device_id = n.device_id WHERE w.device_id = %s" % request['idrow'] 
#	query = "SELECT * FROM work_statistic WHERE device_id=%s" % request['idrow']
	row = idb.get_dict(query)
	srem = regnum = ''
	if row and row['rem']:		srem = row['rem']
	if row and row['regnum']:	regnum = row['regnum']
	sdate = time.strftime(" %d.%m.%Y", time.localtime(time.time()))
	print """~warnn|<div class='wbox' style='background-color: #ded; top: %dpx; left: %dpx;'> <table width=100%% cellpadding=2 cellspacing=0>
	<tr bgcolor=#ccccee><td class='tit'>&nbsp;Примечание: %s</td>
	<td align='right'>
	<input type='button' class='butt' value='+Date' onclick="document.myForm.rem.value += '%s'" />
	<input type='button' class='butt' value='Сохранить' title='Сохранить Примечание' onclick="if (document.myForm.rem.value != '') set_shadow('save_device_rem&device_id=%s');" /></td>
	<td align='right'><img onclick="$('#warnn').html('')" src='../img/error24.png' /></td></tr>
	<tr valign='top'><td colspan=3 align='right'><textarea cols='40' rows='1' maxlength='256' name='rem'>%s</textarea></td></tr>
	</table></div>""" % (
			Y, X, regnum, sdate, request['idrow'], srem)
	print "</div>"

def	mark_row (SS, request):
	ssystem = SS.get_key('subsystem')
#	func_allowed = get_func_allowed(ssystem['code'], SS.get_key('USER')) 
	if ssystem:
		if ssystem['label'] == 'RUSERS':
			import	rusers
			rusers.out_tform (request['table'], request['pkname'], request['idrow'])
		elif ssystem['label'] == 'CONTRCT':
			import	conract
			conract.out_tform (SS, request['table'], request['pkname'], request['idrow'])
		elif ssystem['label'] == 'WORK_TS':
			if request.has_key('shstat'):
				if request['shstat'] == 'mark_row' and request.has_key('table') and request['table'] == 'work_tts':
					find_device2org (SS, request)	#&pkname=device_id&idrow=
				else:	cglob.wdgwarnn("'shstat: [%s]!');" % request ['shstat'], str(request), obj = SS.objpkl)
		else:	cglob.wdgerror('Отсуттвует описание подсистемы', obj = SS.objpkl)

def	add_row (SS, request, ssystem):
	""" Добавить нового пользлвателя	"""
	if ssystem and ssystem['label'] == 'RUSERS':
		import	rusers
		rusers.out_tform (request['table'], None, None, 'addnew')

def	clear (SS, shstat):
	""" Завершение работы пользователя	"""
	SS.del_key('subsystem')
	SS.del_key('role')
	SS.del_key('func_allowed')
	if shstat == 'exit':	SS.del_key('USER')
#	SS.stop()
	print "~eval|document.myForm.submit();"

def	insert_row (SS, request):
	ssystem = SS.get_key('subsystem')
	if ssystem:
		if ssystem['label'] == 'RUSERS':
			import	rusers
			print	"~is_result|"
			print	"rusers.insert_row(request)"
		elif ssystem['label'] == 'CONTRCT':
			import	conract
			print	"CONTRCT", request
	else:
		print	"insert_row", ssystem['label']

def	set_region(idb, SS, request):
	""" Сохранить выбранный район	"""
	if request.has_key('region') and int(request['region']) > 0 and request.has_key('id_org') and int(request['id_org']) > 0:
		query = "UPDATE organizations SET region = %s WHERE id_org = %s;" % (request['region'], request['id_org'])
		if idb.qexecute(query):
			row = idb.get_dict("SELECT * FROM region WHERE id = %s" % request['region'])
			print	"~region|<b>%s</b>" % row['rname']
			return	"set_region", "id_org: %s, rname: '%s'" % (request['id_org'], row['rname'])
		else:	print	"<span class='bferr'>", query, "</span>"
	else:	print	"set_region", request
'''
def	set_bm_cstat (idb, SS, request):
	""" Установить (изменить) текуший статус Договора (контракта)	"""
	if request.has_key('bm_cstat') and int(request['bm_cstat']) > 0 and request.has_key('id_contr') and int(request['id_contr']) > 0:	
		query = "UPDATE contracts SET bm_cstat = %s WHERE id_contr = %s;" % (request['bm_cstat'], request['id_contr'])
		if idb.qexecute(query):
			row = idb.get_dict("SELECT * FROM cont_stat WHERE code = %s;" % request['bm_cstat'])
			print	"~bm_cstat|<span class='bfinf'>", row['sname'], "</span>"
			return	"set_bm_cstat", "текуший статус Договора sname: '%s'" % row['sname']
		else:	print	"<span class='bferr'>", query, "</span>"
	print	"set_bm_cstat", request
'''
def	set_bm_ssys (idb, SS, request):
	""" Установить (изменить) подсистему РНИЦ <bm_ssys>	"""
	if request.has_key('bm_ssys') and int(request['bm_ssys']) > 0 and request.has_key('id_contr') and int(request['id_contr']) > 0:
		query = "UPDATE contracts SET bm_ssys = %s WHERE id_contr = %s; UPDATE organizations SET bm_ssys = bm_ssys | %s WHERE id_org = (SELECT id_org FROM contracts WHERE id_contr = %s)" % (
			request['bm_ssys'], request['id_contr'], request['bm_ssys'], request['id_contr'])
	#	query = "UPDATE contracts SET bm_ssys = %s WHERE id_contr = %s;" % (request['bm_ssys'], request['id_contr'])
		if idb.qexecute(query):
			row = idb.get_dict("SELECT * FROM subsys WHERE code = %s;" % request['bm_ssys'])
			print	"~bm_ssys|<span class='bfgrey'>", row['ssname'], "</span>"
			return	"set_bm_ssys", "тип подсистемы РНИЦ ssname: '%s'" % row['ssname']
	else:	"set_bm_ssys", request

def	set_ctype (idb, SS, request):
	""" Установить (изменить) тип Договора (контракта) <ctype>	"""
	if request.has_key('ctype') and int(request['ctype']) > 0 and request.has_key('id_contr') and request['id_contr'].isdigit():
		iid_contr = int(request['id_contr'])
		if iid_contr > 0:
			query = "UPDATE contracts SET ctype = %s WHERE id_contr = %s;" % (request['ctype'], request['id_contr'])
			if idb.qexecute(query):
				row = idb.get_dict("SELECT * FROM cont_type WHERE cod = %s;" % request['ctype'])
				print	"~ctype|<span class='bfgrey'>", row['tname'], "</span>"
				return	"set_ctype", "тип Договора sname: '%s'" % row['tname']
		elif iid_contr == 0:
			res =  idb.get_table('cont_stat', 'code > 0 AND (bm_type & %s) > 0 ORDER BY code' % request['ctype'])
			print "~bm_cstat| "	#, request['ctype'], res[0]
			cglob.out_select('bm_cstat', res, ['code', 'sname'])
	else:	"set_ctype", request

def	update_stable (idb, SS, request):
	if request.has_key ('stable'):	# and request.has_key('npkey'):
		if request['stable'] == 'vorganizations' and request.has_key('id_org') and request['id_org'].isdigit() and int(request['id_org']) > 0:
			pdict = dicts.CONTRCT['vorganizations']
			messg = 'Изменение Организации'
			npkey = 'id_org'
			ipkey = int(request['id_org'])
		elif request['stable'] == 'vcontracts' and request.has_key('id_contr') and request['id_contr'].isdigit() and int(request['id_contr']) > 0:
			pdict = dicts.CONTRCT['vcontracts']
			messg = 'Изменение Договора'
			npkey = 'id_contr'
			ipkey = int(request['id_contr'])
		else:
			cglob.wdgwarnn('update_stable %s' % request['stable'].upper(), 'DEBUG', obj = request)
			return
#		print	request.keys()
		drow = idb.get_dict("SELECT * FROM %s  WHERE %s = %d;" % (request['stable'], npkey, ipkey))
		if not drow:
			print	"<span class='bferr'> Отсутствует организация %s </span>" % request['id_org']
			return
		sset = []
		dcols = pdict['update']
		rrr = cglob.diff_d2r (dcols.keys(), drow, request)
	#	print 'diff_d2r', rrr
		if not rrr:
			print	"<span class='bfinf'>%s.</span> <span class='bferr'>Изменнений нет!</span>" % messg
			return
		for k in rrr.keys():
			if k == 'inn':
				if not rrr[k].isdigit():
					print	"""<span class='bferr'>ИНН это число 10 или 12 знаков!</span>"""
					return
				elif not len(rrr[k]) in [10, 12]:
					print	"<span class='bferr'>Неверное колличество симполов в ИНН!</span>"
					return
				else:
					dr = idb.get_dict('SELECT inn, bname, rname FROM vorganizations WHERE inn = %s;' % rrr[k])
					if dr:
						print	"""<span class='bferr'>ИНН %s принадлежит "%s" </span><br />""" % (request['inn'], dr['bname']), dr['inn'], dr['rname']
						return
			if rrr.has_key('cnum'):	
				dr = idb.get_dict("SELECT * FROM vcontracts WHERE cnum = '%s';" % request['cnum'])
				if dr:
					print	"""<span class='bferr'>Договор № %s уже существует!" </span><br />"""  % request['cnum'], dr['cnum'], 'от', dr['cdate'], dr['bname']
					return
			sset.append ("%s = '%s'" % (k, cglob.ptext(rrr[k])))
		'''
		for k in dcols.keys():
			if request.has_key(k):
				if k == 'inn' and int(request[k]) != drow['inn']:
					if not len(request[k]) in [10, 12]:
						print	"<span class='bferr'>Неверное колличество симполов в ИНН!</span>"
						return
					dr = idb.get_dict('SELECT inn, bname, rname FROM vorganizations WHERE inn = %s;' % request[k])
					if dr:
						print	"""<span class='bferr'>ИНН %s принадлежит "%s" </span><br />""" % (request['inn'], dr['bname']), dr['inn'], dr['rname']
						return
			#	print k, dcols[k], sset, "<br>"
				if dcols[k][0] == 's': 
					ss = cglob.ptext(request[k])
					if not ss or ss != 'None':
					#	if dcols[cn][1] == ':':
						if not drow[k] or drow[k].strip() != ss:
							sset.append ("%s='%s'" % (k, ss))
				elif dcols[k][0] == 'd':
					sdate = cglob.sfdate(request[k])
					if sdate and str(drow[k]) != sdate:
						sset.append ("%s='%s'" % (k, sdate))
				elif dcols[k][0] == 'i':
					ss = request[k]
					if not ss.isdigit():
						print	"<span class='bferr'> Ошибка формата данных.</span> %s = %s" % (k, dcols[k])
					elif drow[k] != int(ss):
						sset.append ("%s = %s" % (k, ss)) 
		'''
		if sset:
			query = "UPDATE %s SET %s WHERE %s = %d;" % (request['stable'][1:], ', '.join(sset),  npkey, ipkey)
			if idb.qexecute(query):
				print	"<span class='bfinf'>", messg, "выполнено УСПЕШНО.</span>"
				return	messg, "%s: %d SET [%s]" % (npkey, ipkey, "; ".join(sset))
			else:	print	"<span class='bferr'>", messg, "ОШИБКА</span><br />", query
	#	else:	print	"<span class='bfinf'>", messg, "Изменнений нет!</span>"
	#	print	drow
	else:	cglob.wdgwarnn('update_stable', 'DEBUG', obj = request)

def	save_tabl (idb, SS, request, dtable):
	if dtable.has_key('update'):
		set_table = request['set_table']
		if set_table[:2] == 'vo':	set_table = set_table[2:]
		elif set_table[0] == 'w':	set_table = set_table[1:]
		elif set_table[0] == 'v':	set_table = set_table[1:]
		swhere = "%s = %s" % (dtable['key'], request['id_tabl'])

		drow = idb.get_dict("SELECT * FROM %s  WHERE %s;" % (set_table, swhere))
		lset = cglob.diff_update (dtable['update'], drow, request)
	#	print lset, dtable['update']
	#	return
		if lset:
			messg = "Измененме в %s " % set_table.upper()
			query = "UPDATE %s SET %s WHERE %s" % (set_table, ", ".join(lset), swhere)
			if idb.qexecute(query):
				print   "<span class='bfinf'>", messg, "выполнено УСПЕШНО.</span>"
				return	messg, query	#"%s: %d SET [%s]" % (npkey, ipkey, "; ".join(sset))
			else:	print   "<span class='bferr'>", messg, "ОШИБКА</span><br />", query
		print "<span class='bfinf'>Нет изменения в данных.</span>"
	else:	print	"save_tabl", request

def	save_new (idb, SS, request):
	""" Создание (сохранение) новой записи в request['stable']	"""
	if request.has_key ('stable') and request.has_key('npkey'):
		if request['stable'] == 'vcontracts' and request.has_key('id_org') and request['id_org'].isdigit() and int(request['id_org']) > 0:
			pdict = dicts.CONTRCT['vcontracts']
			messg = 'Создание нового Договора'
		elif request['stable'] == 'vorganizations':
			pdict = dicts.CONTRCT['vorganizations']
			messg = 'Создание новой Организации'
		elif request['stable'] == 'add_acts':
			pdict = dicts.CONTRCT['add_acts']
			messg = 'Создание нового АКТа'
		elif request['stable'] == 'add_consents':
			pdict = dicts.CONTRCT['add_consents']
			messg = 'Создание нового АКТа'
		else:
			cglob.wdgwarnn('save_new', 'DEBUG', obj = request)
			return
		if request.has_key('inn'):
			dr = idb.get_dict('SELECT inn, bname, rname FROM vorganizations WHERE inn = %s;' % request['inn'])
			if dr:
				print	"""<span class='bferr'>ИНН %s принадлежит "%s" </span><br />""" % (request['inn'], dr['bname']), dr['inn'], dr['rname']
				return
		elif request.has_key('cnum'):
			dr = idb.get_dict("SELECT * FROM vcontracts WHERE cnum = '%s';" % request['cnum'])
			if dr:
				print	"""<span class='bferr'>Договор № %s уже существует!" </span><br />"""  % request['cnum'], dr 
				return
		nams = []
		vals = []
		for k in pdict['update'].keys():	#pdict['order']:
			if request.has_key(k) and request[k].strip():
				nams.append(k)
				vals.append("'%s'" % cglob.ptext(request[k]))
		if not nams:
			print	"<span class='bferr'> Нет данных! </span><br />", request
			return
		query = "INSERT INTO %s (%s) VALUES (%s); SELECT max(%s) FROM %s;" % (request['stable'][1:], ', '.join(nams), ', '.join(vals), request['npkey'], request['stable'][1:])
		dr = idb.get_dict(query)
		if dr:
			if request['stable'] == 'vcontracts':
				query = "UPDATE organizations SET bm_ssys = bm_ssys | (SELECT bm_ssys FROM contracts WHERE id_contr = %d)  WHERE id_org = %s;" % (dr['max'], request['id_org'])
				request[request['npkey']] = str(dr['max'])
				idb.qexecute(query)
			print	"<span class='bfinf'>", messg, "УСПЕШНО</span>", dr	# DEBUG
			return  messg, "%s: %d [%s]" % (request['npkey'], dr['max'], "; ".join(nv2lsnv(nams, vals)))
		else:	"<span class='bferr'>", messg, "ОШИБКА</span><br />", query
	else:	cglob.wdgwarnn('save_new', 'DEBUG', obj = request)

def	nv2lsnv (nams, vals):
	""" Собрать два списка nams, vals в список строк ["nams1: vals1", ...]	"""
	res = []
	for s in map(None, nams, map(str, vals)):
		res.append (": ".join(s))
	return	res

def	save_history (idb, SS, res, request = None):
	""" Сохранить историю изменений в 'history'.	"""
	user = SS.get_key('USER')
	print	"~shadow|save_history"	#, res
	swho_name = "%s %s" % (user['uname'], user['ufam'])
	slabel = cglob.ptext(str(res[0]))
	smessge = cglob.ptext(str(res[1]))
	sid_contr = sid_org = 'NULL'
	if request:
		if request.has_key('id_contr') and request['id_contr'].isdigit():	sid_contr = request['id_contr']
		if request.has_key('id_org') and request['id_org'].isdigit():		sid_org = request['id_org']
	query = "INSERT INTO history (who_id, who_name, label, messge, id_contr, id_org) VALUES (%d, '%s', '%s', '%s', %s, %s);" % (user['user_id'], swho_name, slabel, smessge, sid_contr, sid_org)
	return	idb.qexecute(query)

def	isset_org (idb, request):
	""" Показать доп. информацию по выбранной организации	"""
	if request.has_key('id_org') and request['id_org'].isdigit() and int(request['id_org']) > 0:
		iid_org = int(request['id_org'])
		query = "SELECT bname, fname, rname FROM vorganizations WHERE id_org = %d;" % iid_org
		dr = idb.get_dict(query)
		if dr:
			import	conract
			print	"~org_fname|", dr['fname']
			print	"~org_persons|", conract.get_persons(idb, 0, iid_org)
			if dr['rname']:		print	"~org_rname|", dr['rname']
	else:	print	request

def	find_org (idb, request):
	""" DEBUG Выбор организации	"""
	if request.has_key('org_name') and len(request['org_name']) > 4:
#		idb = dbtools.dbtools (CDB_DESC)
		label = request['org_name']
		slike = "LIKE '%%%s%%'" % label.replace(' ',"%")
		query = "SELECT id_org, bname, fname, rname FROM vorganizations WHERE bname %s OR fname %s LIMIT 120;" % (slike, slike)
		rows = idb.get_rows(query)
		if rows:
			#	<tr class='line' onclick="$('#persons tr').removeClass('mark'); $(this).addClass('mark');" ondblclick="out_person(0,25,16);" >
			print 	"<div style='top: 50px; left: 230px; position: absolute; padding: 4px; margin: 4px; min-width: 500px; border: thin solid #668; background-color: #efe; max-height: 200px; overflow: auto;'>"
			print	"<table width=100% id='find_org' cellpadding=2 cellspacing=0>"
			for r in rows:
				print	"""<tr class="line" onclick="$('#find_org tr').removeClass('mark'); $(this).addClass('mark');" ondblclick="
				document.myForm.id_org.value=%d; document.myForm.org_name.value='%s';
				$('#wform_result').html(''); set_shadow('isset_org') ">""" % (r[0], r[1].replace('"', ""))	#, "r[2]")
				print	"<td align='left'>", r[0], r[1], "</td></tr>"
			print	"</table>"
			print	"</div> <!-- cglob.out_widget	-->"
		'''
		import	compaire
		query = "SELECT id_org, bname, fname FROM organizations;" 
		rows = idb.get_rows(query)
		if rows:
			cmp0 = compaire.genshingle(compaire.canonize(label))
			j = 0
			for r in rows:
				r1 = r2 = 0.0
				if j > 5:	break
				if r[1]:
					cmp1 = compaire.genshingle(compaire.canonize(r[1]))
					r1 = compaire.compaire(cmp0, cmp1)
				if r1 > 2:
					print	r1, r[1], "<br />"
					j += 1
				if r[2]:
					cmp2 = compaire.genshingle(compaire.canonize(r[2]))
					r2 = compaire.compaire(cmp0, cmp2)
				if r1 > 90.0 or r2 > 90.0:
					print r1, r2, " => \t[%s]\t[%s]<br />" % (r[1], r[2])
		'''
	else:	print	"<span class='bferr'> Маловато данных id_org </span>"

def	test_compaire(idb, request):
	import	compaire
	print	"<pre>"
	ooo = request['org_name']
	for ch in request['org_name']:
		if ch != '\xd0':
			print ch,
	print ""
#	print ooo, ooo.upper()
	Rcann = compaire.genshingle (compaire.canonize (request['org_name']))
	print	'Rcann', Rcann
	if request.has_key('id_org'):
		query = "SELECT id_org, bname FROM organizations WHERE id_org = %s;" % request['id_org']
		dr = idb.get_dict(query)
		DBrow = compaire.genshingle (compaire.canonize (dr['bname']))
		print	'DBrow', DBrow
		print compaire.compaire (Rcann, DBrow)
	print	"</pre>"

def	save_as_new_contr (SS, request):
	""" Сохранить Договор (контракт) как новый	"""
	if not request.has_key('id_contr'):	return
	print "~wform_result|"	#, "save_as_new_contr".upper()
	idb = dbtools.dbtools (CDB_DESC)
	query = "SELECT * FROM contracts WHERE id_contr = %s;" % request['id_contr']
	dr = idb.get_dict(query)
	res = cglob.diff_d2r (['cnum', 'cdate', 'period_valid'], dr, request)
	if not (res and res.has_key('cnum') and res.has_key('cdate') and res.has_key('period_valid')):
		print	"<span class='bferr'>Необходимо изменить Номер, Дату и Срок действия договора!</span><br />", "№: %s, &nbsp; Дата: %s, &nbsp; Срок действия: %s " % (
			dr['cnum'], dr['cdate'], dr['period_valid'])
		return
#	print	"diff_d2r", cglob.diff_d2r (['cnum', 'cdate'], dr, request)
	ddr = idb.get_dict("SELECT * FROM contracts WHERE cnum = '%s'" % res['cnum'])
	if ddr:
		print	"<span class='bferr'>Договор (контракт) № %s от %s уже существует!</span>" % (ddr['cnum'], ddr['cdate'])
		return
	col_names = ['cnum', 'cdate', 'period_valid', 'is_valid', 'id_org', 'bm_ssys', 'csumma', 'is_nds', 'is_fix', 'ctype', 'is_paid', 'pfix', 'ref_docx', 'rem']
	scol = []
	sval = []
	res['rem'] = "Из № %s от %s Создан новый Договор" % (dr['cnum'], dr['cdate'])
	for cn in col_names:
		if cn in ['cnum', 'cdate', 'period_valid'] and res.has_key(cn):
			scol.append(cn)
			sval.append("'%s'" % res[cn])
		elif res.has_key(cn):
			scol.append(cn)
			sval.append("'%s'" % res[cn])
		elif dr[cn]:
			scol.append(cn)
			sval.append("'%s'" % dr[cn])
	query = "INSERT INTO contracts (%s) VALUES (%s);" % (', '.join(scol), ', '.join(sval))
#	print	query
	if idb.qexecute(query):
		messg = "Создан новый Договор (контракт) № %s от %s.</span>" % (res['cnum'], res['cdate'])
		print	"<span class='bfinf'>УСПЕШНО", messg
		return	messg, "%s" % "; ".join(nv2lsnv(scol, sval)) 

def	update_add_doc (idb, SS, request):
	if not (request.has_key('stable') and request.has_key('id_doc') and request['id_doc'].isdigit()):
		print	"~wform_result|<span class='bferr'>delete_add_dmc: Отсутствует данные!</span>", request
		return
	if request['stable'] == 'add_acts':
		message = "Изменение AКTа"
		swhere = "WHERE id_act = %s" % request['id_doc']
	elif request['stable'] == 'add_consents':
		message = "Изменение Доп. соглашения"
		swhere = "WHERE id_acon = %s" % request['id_doc']
	else:
		print	"update_add_doc", request
	rdoc = idb.get_dict ("SELECT * FROM %s %s;" % (request['stable'], swhere))
	if not rdoc:	return
	sss = []
	if request.has_key('docteam') and cglob.ptext(request['docteam']) != rdoc['docteam']:
		sss.append("docteam = '%s'" % cglob.ptext(request['docteam']))
	if request.has_key('rem') and cglob.ptext(request['rem']) != rdoc['rem']:
		sss.append("rem = '%s'" % cglob.ptext(request['rem']))
	if request.has_key('docnum') and cglob.ptext(request['docnum']) != rdoc['docnum']:
		sss.append("docnum = '%s'" % cglob.ptext(request['docnum']))
	if request.has_key('docdate') and cglob.sfdate(request['docdate']) != rdoc['docdate']:
		sss.append("docdate = '%s'" % cglob.sfdate(request['docdate']))

	if not sss:
		print	"~eval|alert('Изменения в документе Отсутстуют!');"
		return
	query = "UPDATE %s SET %s %s;" % (request['stable'], ', '.join(sss), swhere)
	if idb.qexecute(query):
		print	"~wform_result|<span class='bfinf'>%s выполнено УСПЕШНО.</span>" % message
		return	message, "[ %s ]" % '; '.join(sss)

def	delete_add_doc (idb, SS, request):
	""" Удаление Доп. соглашений или АКТов	"""
	if not (request.has_key('stable') and request.has_key('id_doc') and request['id_doc'].isdigit()):
		print	"~wform_result|<span class='bferr'>delete_add_dmc: Отсутствует данные!</span>", request
		return
	if request['stable'] == 'add_acts':
		message	= "Удаление AКTа"
		query = "DELETE FROM add_acts WHERE id_act = %s" % request['id_doc']
	elif request['stable'] == 'add_consents':
		message = "Удаление Доп. соглашения"
		query = "DELETE FROM add_consents WHERE id_acon = %s" % request['id_doc']
	else:
		print	"delete_add_doc", request
		return
	if idb.qexecute(query):
		print   "~wform_result|<span class='bfinf'>%s выполнено УСПЕШНО.</span>" % message
		return	message, str(request)

def	out_add_doc (idb, SS, request):
	""" Показать форму для создания Доп. соглашений или АКТов	"""
	if not (request.has_key('id_contr') and request['id_contr'].isdigit()):
		print	"<span class='bferr'>Отсутствует id_contr!</span>", request['id_contr']
		return
	iid_contr = int(request['id_contr'])
	sdocnum = sdocdate = sdocteam = srem = ''
	tit = ''
	if idb:
		print	request
		if request['stable'] == 'add_acts':
			label = 'act'
			query = 'SELECT * FROM %s WHERE id_act=%s' % (request['stable'], request['id_doc'])
			tit = "AКT"
		if request['stable'] == 'add_consents':
			label = 'consent'
			query = 'SELECT * FROM %s WHERE id_acon=%s' % (request['stable'], request['id_doc'])
			tit = "Доп. соглашение"
		rdoc = idb.get_dict (query)
		if rdoc:
			if rdoc['docnum']:	sdocnum = rdoc['docnum']
			if rdoc['docdate']:	sdocdate = cglob.out_sfdate (rdoc['docdate'])
			if rdoc['docteam']:	sdocteam = rdoc['docteam']
			if rdoc['rem']:	srem = rdoc['rem']
		else:	return
		sright = """<td align='right'>
			<input type='button' class='butt' value='Изменить %s' onclick="set_shadow('update_add_doc&stable=add_%ss&id_doc=%s');" />
			<input type='button' class='butt' value=' Удалить ' onclick="set_shadow('delete_add_doc&stable=add_%ss&id_doc=%s');" />
			</td>""" % (
				tit, label, request['id_doc'], label, request['id_doc'])
	else:
		label = request['shstat'][1 +len('new_create'):]
		if label == 'consent':	tit = "Доп. соглашение"
		elif label == 'act':	tit = "AКT"
		else:
			print	"<span class='bferr'>Непорнятно что создаем</span><br />", label, request
			return
		sright = """<td align='right'><input type='button' class='butt' value='Сохранить %s'
			onclick="if (check_form_add_doc()) {set_shadow('save_new_doc&stable=add_%ss&id_contr=%d');}" /></td>""" % (tit, label, iid_contr)
	prn_div_tit (tit, sright)
	print	"<table width=100% >"
	print	"""<tr><td align='right'>Номер:</td><td><input type='text' name='docnum' size='10' maxlength=16 value='%s' />
		&nbsp; от: <input type='text' name='docdate' class='date' value='%s' /></td></tr>""" % (
		sdocnum, sdocdate)	# disabled
	print	"<tr><td align='right'>Тема:</td><td><input type='text' name='docteam' size='64' maxlength=128 value='%s' /></td></tr>" % sdocteam
	print	"<tr><td align='right'>Суть:</td><td><textarea name='rem' maxlength=256 rows=1 cols=80>%s </textarea></td></tr>" % srem
	print	"</table>"
#	print	"oit_create_new", request, label
	print	"</div>"

def	save_new_doc (idb, SS, request):
	""" Сохранить Доп. соглашение или АКТ	"""
	iid_contr = iid_org = 0
	if request.has_key ('stable'):
		if request.has_key('id_org') and request['id_org'].isdigit() and int(request['id_org']) > 0:
			iid_org = int(request['id_org'])
		if request.has_key('id_contr') and request['id_contr'].isdigit() and int(request['id_contr']) > 0:
			iid_contr = int(request['id_contr'])
		if not (iid_org and iid_contr):
			cglob.wdgwarnn('save_new_doc', 'DEBUG id_org: %d; id_contr: %d' % (iid_org, iid_contr), obj = request)
			return
		if request['stable'] == 'add_acts':
			qsel = "SELECT max(id_act) FROM add_acts"
			messg = 'Создание нового АКТа'
		elif request['stable'] == 'add_consents':
			qsel = "SELECT max(id_acon) FROM add_consents"
			messg = 'Создание нового Доп. соглашения'
		else:
			cglob.wdgwarnn('save_new_doc', 'DEBUG stable: "%s"' % request['stable'], obj = request)
			return
		if not (request.has_key('docnum') and request['docnum'].strip()):
			cglob.wdgerror('Ошибка:', 'Отсутствует номер документа!', obj = request)
			return
		if not (request.has_key('docdate') and cglob.sfdate(request['docdate'])):
			cglob.wdgerror('Ошибка:', 'В формате даты документа [%s]!' % request['docdate'], obj = request)
			return
		nams = ['id_org', 'id_contr', 'docnum', 'docdate']
		vals = [str(iid_org), str(iid_contr), "'%s'" % request['docnum'].strip(), "'%s'" % cglob.sfdate(request['docdate'])]
		for k in ['docteam', 'rem']:
			if request.has_key(k):
				nams.append(k)
				vals.append("'%s'" % cglob.ptext(request[k]))
		query = "INSERT INTO %s (%s) VALUES (%s); UPDATE contracts SET %s = (%s);" % (request['stable'], ', '.join(nams), ', '.join(vals), request['stable'], qsel)
	#	print	query
		if idb.qexecute (query):
			print	"~wform_result|<span class='bfinf'>", messg, 'УСПЕШНО.</span>'
			return  messg, "%s" % "; ".join(nv2lsnv(nams, vals))
	else:	cglob.wdgwarnn('save_new_doc', 'DEBUG', obj = request)
'''
   256 |       6 | Выполнен
   512 |       7 | Закрыт
  4096 |       9 | Завершен
 65536 |       1 | Удален
 70400
'''

def	out_bm_cstat (idb, SS, request):
	""" Показать форму для изменения Состояния договора	"""
	if not (request.has_key('id_contr') and request['id_contr'].isdigit()):
		print	"<span class='bferr'>Отсутствует id_contr!</span>", request['id_contr']
		return
	iid_contr = int(request['id_contr'])
	dr = idb.get_dict("SELECT * FROM contracts WHERE id_contr = %d;" % iid_contr)
	if not dr:	return
	if not dr['ctype']:
		print	"<span class='bferr'>Отсутствует Тип Договора (контракта)!</span>"
		return
	res =  idb.get_table('cont_stat', 'code > 0 AND (bm_type & %d) > 0 ORDER BY code' % dr['ctype'])
	rdict = res[0]
	
	if dr['bm_cstat'] and (dr['bm_cstat'] & 70400):	#69888):	# Выполнен | Завершен | Удален	69632
		if dr['bm_cstat'] & 4096:
			sst = 'Завершен'
		elif dr['bm_cstat'] & 512:
			sst = 'Закрыт'
		elif dr['bm_cstat'] & 256:
			sst = 'Выполнен'
		else:	sst = 'Удален'
		'''
		sd_close = """<td>%s: <input id='date_close' type='text' name='date_close' value='%s' class='date' /> </td>""" % (sst, cglob.out_sfdate (dr['date_close']))
		'''
		if dr['date_close']:
			sd_close = """<td>%s:<b> %s </b></td>""" % (sst, cglob.out_sfdate (dr['date_close']))
		else:	sd_close = """<td>%s: <input id='date_close' type='text' name='date_close' value='%s' class='date' /> </td>""" % (sst, cglob.out_sfdate (dr['date_close']))
	else:	sd_close = ''
	sright = sd_close + """<td align='right'><input type='button' class='butt' value='Сохранить изменения' onclick="set_shadow('update&save_bm_cstat=Y&id_contr=%d');" /></td>""" % iid_contr
	prn_div_tit ("Состояние договора", sright)
	print	"<table width=100% >"
	j = 0
	for r in res[1]:
		if dr['bm_cstat'] < 32:
			xcode = dr['bm_cstat']
		else:	xcode = 32
	#	if r[rdict.index('code')] < (dr['bm_cstat']) and not (r[rdict.index('code')] & dr['bm_cstat']) :	continue
		if r[rdict.index('code')] < xcode and not (r[rdict.index('code')] & dr['bm_cstat']) :	continue
		sdisabl = scheck = ''
		if not (j % 4):	print "<tr>",
		if r[rdict.index('code')] & dr['bm_cstat']:
			scheck = 'checked'
			if r[rdict.index('code')] != 2048:	# 2048 Приостановлен
				ssname = "<span class='bfinf'>%s</span>" % r[rdict.index('sname')]
				sdisabl = 'disabled'
			else:	ssname = "<span class='bferr'>%s</span>" % r[rdict.index('sname')]
		else:	ssname = "<span class='bfgrey'>%s</span>" % r[rdict.index('sname')]
	#	if r[rdict.index('code')] < (dr['bm_cstat']):	sdisabl = 'disabled'
		print	"<td><label><input type='checkbox' name='cstat:%05d' %s %s>%s</label></td>" % (r[rdict.index('code')], scheck, sdisabl, ssname)	# r[rdict.index('sname')])
		j += 1
		if not (j % 4):	print "</tr>"
	print	"</table>"
	print	"</div>"

def	save_bm_cstat (idb, SS, request):
	""" Сохранить изменения Состояние договора <bm_cstat>	"""
	if not (request.has_key('id_contr') and request['id_contr'].isdigit()):
		print	"<span class='bferr'>Отсутствует id_contr!</span>", request['id_contr']
		return
	iid_contr = int(request['id_contr'])
	dr = idb.get_dict("SELECT * FROM contracts WHERE id_contr = %d;" % iid_contr)
	if not dr:	return
	icstat = 0
	for l in request:
		if 'cstat:' in l:
			icstat += int (l[6:])
	if icstat == dr['bm_cstat']:
		print	"<span class='bferr'>Отсутствуют изменения Состояние договора!</span>"
		return
	if (dr['bm_cstat'] & 2048) and not (icstat & 2048):	# 2048 Приостановлен
		dr['bm_cstat'] ^= 2048
	icstat |= dr['bm_cstat']
	if icstat & 70400:	# Закрыт 69888:	# Выполнен   69632:	# Завершен | Удален
		if request.has_key('date_close') and request['date_close'].strip():
			query = "UPDATE contracts SET bm_cstat = %d, is_valid = 1, date_close = '%s' WHERE id_contr = %d;" % (icstat,  cglob.sfdate(request['date_close'].strip()), iid_contr)
		else:	query = "UPDATE contracts SET bm_cstat = %d, is_valid = 1 WHERE id_contr = %d;" % (icstat, iid_contr)
		sis_valid = 'Нет'
	elif icstat & 1216:	# подписан | есть оригинал | исполняется
		query = "UPDATE contracts SET bm_cstat = %d, is_valid = 0 WHERE id_contr = %d;" % (icstat, iid_contr)
		sis_valid = 'Да'
	else:
		query = "UPDATE contracts SET bm_cstat = %d WHERE id_contr = %d;" % (icstat, iid_contr)
		sis_valid = None
	#query = "UPDATE contracts SET bm_cstat = %d WHERE id_contr = %d; SELECT * FROM contracts WHERE id_contr = %d;" % (icstat, iid_contr, iid_contr)
	print	query, "<br />"
	if idb.qexecute(query):
		import	conract
		sctypes = conract.get_cont_stat (idb, icstat, 1)
		print	"<span class='bfinf'> Состояние договора УСПЕШНО изменено.</span>"	#, sctypes
		print	"~bm_cstat|", sctypes, "~eval|$('#bm_cstat').removeClass('mark');"
		if sis_valid:
			print	"~is_valid| %s" % sis_valid
		return	"Изменено Состояние договора.", sctypes

def	prn_div_tit (stit, sright = '', left = 220, top = 380, iddom = 'wform_result', bgcolor = '#aab'):
	print	"""~%s|
		<div id='%s' style='top: %dpx; left: %dpx; position: absolute; padding: 1px; margin: 1px; text-align: left; min-width: 600px; border: thin solid #668; background-color: #efe;'>
		<div style='padding: 1px; margin: 0px; border: thin solid #668; background-color: %s;'><table width=100%% cellpadding=2 cellspacing=0><tr>
		<td class='tit'>&nbsp;%s</td>%s<td align='right'><img onclick="$('#%s').html('')" src='../img/delt2.png' /></td></tr></table></div>
		""" % (iddom, iddom, top, left, bgcolor, stit, sright, iddom)

#	Входящие заявки письма
#	'bid_create': '20-06-2016', 'bid_type': '4', 'shstat': 'new_bid', 'this': 'ajax', 'fform': 'new_widow', 'bid_num': '1234'

def	create_new_bid (idb, SS, request):
	""" Добавление новой Заявки (письма)	"""
	print "~wform_result|"
	stm = time.strptime(cglob.sfdate(request['bid_create']), "%Y-%m-%d")
	tm_creat = int (time.mktime(stm))
	dtt = idb.get_dict ("SELECT * FROM bid_type WHERE code = %s;" % request['bid_type'])
	if not dtt:	return
	tm_alarm = tm_creat +dtt['dtm']
	message = "Заявка на %s" % dtt['bname']
	query = """INSERT INTO bids (bid_num, bm_btype, id_org, tm_creat, tm_alarm) VALUES ('%s', %s, %s, %d, %d);
		INSERT INTO alarms (id_bid, bm_btype, id_org, tm_creat, tm_alarm, message) VALUES ((SELECT max(id_bid) FROM bids), %s, %s, %d, %d, '%s');""" % (
		request['bid_num'].strip(), request['bid_type'], request['id_org'], tm_creat, tm_alarm,
		request['bid_type'], request['id_org'], tm_creat, tm_alarm, message)
	if idb.qexecute(query):
		print	"<span class='bfinf'>%s УСПЕШНО зарегтстрирована.</span>" % message
		import	conract
		sctypes = conract.get_bids(idb, request['id_org'])
		print	"~bids|", sctypes, "~eval| document.myForm.bid_type.value=''; document.myForm.bid_num.value='';"
		return	"Добавлена Заявка (письмо)", message

def	done_bid (idb, SS, request):
	""" Заявка Исполнена [Все Ок]	"""
	print	"done_bid", request
	if not (request.has_key('id_bid') and request['id_bid'].isdigit()):
		print	"<span class='bferr'>Отсутствует id_bid!</span>", request
		return
	dr = idb.get_dict("SELECT * FROM vbids WHERE id_bid = %s" % request['id_bid'])
	request['id_org'] = str(dr['id_org'])
	if not dr:
		print	"<span class='bferr'>Заявка (письмо) Отсутствует!</span> id_bid:", request['id_bid']
		return
	dtt = idb.get_dict ("SELECT * FROM bid_type WHERE code = %d;" % dr['bm_btype'])
	message = "Заявка на %s" % dtt['bname']
	query = "UPDATE bids SET fix_bstat = (SELECT sum(code) FROM bid_stat WHERE (bm_btype & %d > 0)), tm_close=%d WHERE id_bid = %s; DELETE FROM alarms WHERE id_bid = %s;" % (
			dr['bm_btype'], int(time.time()), request['id_bid'], request['id_bid'])
	print "~wform_result|"
#	print	query
	if idb.qexecute(query):
		message = "<span class='bfinf'>%s УСПЕШНО исполнена.</span>" % message
		print message
		import	conract
		sctypes = conract.get_bids(idb, dr['id_org'])
		print	"~bids|", sctypes, "~eval| document.myForm.bid_type.value=''; document.myForm.bid_num.value='';"
		return	"Заявка ID: %s Исполнена" % request['id_bid'], message

def	update_bid (idb, SS, request):
	""" Изменение Заявки (письма)	"""
#	print	"update_bid", request
	if not (request.has_key('id_bid') and request['id_bid'].isdigit()):
		print	"<span class='bferr'>Отсутствует id_bid!</span>", request
		return
	dr = idb.get_dict("SELECT * FROM vbids WHERE id_bid = %s;" % request['id_bid'])
	if not dr:
		print	"<span class='bferr'>Заявка (письмо) Отсутствует!</span> id_bid:", request['id_bid']
		return
	sss = []
	if request.has_key('rem') and cglob.ptext(request['rem']) != dr['rem']:
		sss.append ("rem = '%s'" % cglob.ptext(request['rem']))
	qalarm = []
	ssmess = []
	ibm_bstat = 0
	if dr.has_key('bm_bstat'):
		old_bm_bstat = dr['bm_bstat']
	else:	old_bm_bstat = 0
	for k in request.keys():
		if 'bm_bstat:' in k:
			cod_bstat = int(k[len('bm_bstat:'):])
			ibm_bstat += cod_bstat
	#		print	"\n(old_bm_bstat & cod_bstat)", old_bm_bstat, cod_bstat, (old_bm_bstat & cod_bstat)
			if not qalarm:
				if not old_bm_bstat:
					qalarm.append("DELETE FROM alarms WHERE id_bid=%d;" % dr['id_bid'])
			if (old_bm_bstat & cod_bstat) == 0:	# New cod_bstat
			#	qalarm.append("DELETE FROM alarms WHERE bm_bstat & %d >0 AND  id_bid=%d;" % (dr['bm_bstat'], dr['id_bid']))
				dst = idb.get_dict ("SELECT * FROM bid_stat WHERE code = %d;" % cod_bstat)
				if not dst:
					print	"Not bm_bstat:", cod_bstat
					return
				tm_creat = int(time.time())
				tm_alarm = tm_creat +dst['dtm']
				if dr['rem']:
					message = dr['rem']
				else:	message = 'type: "%s", stat: "%s"' % (dr['bname'], dst['sname'])
				ssmess.append (message)
				qalarm.append ("INSERT INTO alarms (id_bid, bm_btype, bm_bstat, id_org, tm_creat, tm_alarm, message) VALUES (%d, %d, %d, %d, %d, %d, '%s');" % (
					dr['id_bid'], dr['bm_btype'], cod_bstat, dr['id_org'], tm_creat, tm_alarm, message))
	if old_bm_bstat != ibm_bstat:
		sss.append ("bm_bstat = %d" % ibm_bstat)
	if not sss:
		print	"~eval| alert('Отсутствуют изменения в данных!');"
		return
	qalarm[:0] = ["UPDATE bids SET %s WHERE id_bid = %s;" % (', '.join(sss), request['id_bid'])]
#	print	sss, "qalarm", '\n'.join(qalarm)
	if idb.qexecute('\n'.join(qalarm)):
		print "~wform_result|"
		print	"<span class='bfinf'>Изменения в '%s' УСПЕШНО выполнены." % dr['bname']
		import	conract
		sctypes	= conract.get_bids(idb, dr['id_org'])
		print	"~bids|", sctypes
		return	"Изменена Заявка '%s'" % dr['bname'], "; ".join(ssmess)

def	delete_bid (idb, SS, request):
	""" Удаление Заявки (письма) 	"""
#	print	"delete_bid", request
	if not (request.has_key('id_bid') and request['id_bid'].isdigit()):
		print	"<span class='bferr'>Отсутствует id_bid!</span>", request
		return
	dr = idb.get_dict("SELECT * FROM vbids WHERE id_bid = %s;" % request['id_bid'])
	if not dr:
		print	"<span class='bferr'>Заявка (письмо) Отсутствует!</span> id_bid:", request['id_bid']
		return
	message = "Заявка (письмо) № %s от %s '%s'" % (dr['bid_num'], time.strftime("%d-%m-%Y", time.localtime(dr['tm_creat'])), dr['bname'])
	query = "DELETE FROM bids WHERE id_bid=%s; DELETE FROM alarms WHERE id_bid=%s;" % (request['id_bid'], request['id_bid'])
	if idb.qexecute(query):
		print "~wform_result|"
		print	"<span class='bfinf'>%s УСПЕШНО удалена.</span>" % message
		import	conract
		sctypes = conract.get_bids(idb, dr['id_org'])
		print	"~bids|", sctypes
		return	"Удалена Заявка (письмо)", message

def	out_fbid (idb, SS, request):
	""" Показать форму для изменения Состояния заявки письма	"""
#	print	"out_fbid", request
	if not (request.has_key('id_bid') and request['id_bid'].isdigit()):
		print	"<span class='bferr'>Отсутствует id_bid!</span>", request
		return
	iid_bid = int(request['id_bid'])
	dr = idb.get_dict("SELECT * FROM vbids WHERE id_bid = %d;" % iid_bid)
	if not dr:	return
#	res =  idb.get_table('bid_stat', 'code > 0 AND (bm_btype & %d) > 0 ORDER BY code' % dr['bm_btype'])
	res =  idb.get_table('bid_stat', 'bm_btype > 0 AND (bm_btype & %d) > 0 ORDER BY code' % dr['bm_btype'])
	rdict = res[0]
	prn_div_tit (dr['bname'], """<td align='right'><input type='button' class='butt' value='Сохранить' onclick="set_shadow('update_bid&id_bid=%d');" title='Сохранить изменения'
		/><input type='button' class='butt' value='Все Ок' onclick="if (confirm ('Заявка Исполнена полностью?')) {set_shadow('done_bid&id_bid=%d'); }" title='Заявка Исполнена полностью'
		/><input type='button' class='butt' value='Удалить' onclick="if (confirm ('Удалить заявку (письмо)?')) {set_shadow('delete_bid&id_bid=%d'); }" /></td>""" % (iid_bid, iid_bid, iid_bid))
#	print	"request", rdict, dr['fix_bstat']
	print	"<table width=100% >"
	print	"<tr class='hei'><td align='right'> № <span class='bfgrey'>%s</span> от <span class='bfgrey'>%s</span></td><td>" % (dr['bid_num'], time.strftime("%d-%m-%Y", time.localtime(dr['tm_creat'])))
	j = 0
	ok_bstat = 32768
	for r in res[1]:
		icode = r[rdict.index('code')]
		scheck = sdisabl = ''
		if dr['bm_bstat'] & icode:
			if (icode & dr['fix_bstat']) == icode:	# Действие выполнено
				ssname = "<span class='bfligt'>%s</span>" % r[rdict.index('sname')]
			elif (dr['bm_bstat'] < 2*icode) and (dr['tm_alarm'] < time.time()): 
				ssname = "<span class='bferr'>%s</span>" % r[rdict.index('sname')]
			else:	ssname = "<span class='bfinf'>%s</span>" % r[rdict.index('sname')]
			scheck = 'checked'
		elif ok_bstat & dr['fix_bstat']:
			ssname = "<span class='bfligt'>%s</span>" % r[rdict.index('sname')]
		else:	ssname = "<span class='bfgrey'>%s</span>" % r[rdict.index('sname')]
		print	"<label><input type='checkbox' name='bm_bstat:%05d' %s %s>%s</label>;&nbsp;" % (r[rdict.index('code')], scheck, sdisabl, ssname)
		j += 1
		if not (j % 3):	print	"<br />"
	print	"</td></tr>"
	if dr.has_key('rem') and dr['rem']:
		srem = str(dr['rem']).strip()
	else:	srem = ''
	print	"<tr><td align='right'>Примечание:</td><td class='bfgrey'><input type='text' name='rem' value='%s' size=64 maxlength=128 /></td></tr>" % srem
	dtm = (int(time.time()) - dr['tm_alarm'])/3600/24
#	print	"<tr><td align='right'>Исполнение:</td><td class='bfgrey'>", dr['tm_alarm'], dtm, "</td></tr>"
	if ok_bstat & dr['fix_bstat']:
		print	"<tr><td align='right'>Исполнение:</td><td class='bfinf'>%s Все исполнено </td></tr>" % time.strftime("%d-%m-%Y", time.localtime(dr['tm_close']))
	elif dtm < 0:
		print	"<tr><td align='right'>Исполнение:</td><td class='bfgrey'>%s на исполнение %d дней</td></tr>" % (time.strftime("%d-%m-%Y", time.localtime(12*3600 + dr['tm_alarm'])), -dtm) 
	else:	print	"<tr><td align='right'>Исполнение:</td><td class='bferr'>%s задержка %d дней</td></tr>" % (time.strftime("%d-%m-%Y", time.localtime(12*3600 + dr['tm_alarm'])), dtm) 
	print	"</table>"
	print	"</div>"

def	send_mail_to (idb, SS, request):
	print "~shadow|"
	user = SS.objpkl['USER']
	days = 10	### WWW Сколько дней нет данных от машин
	sdtm = time.strftime("%Y-%m-%d %T", time.localtime(time.time() - days*86400))
	swho_name = "%s %s" % (user['uname'], user['ufam'])
	iid_org = int(request['id_org'])
	res = idb.get_table('vpersons',  'id_org = %d' % iid_org)
#	print	user, iid_org
	d = res[0]
	mails = []
	autos = []
	gosnums = []
	mark_mail = False
	for r in res[1]:
		if r[d.index('email')] and r[d.index('email')] not in mails:
			mails.append(r[d.index('email')])
#	mails = ["v.smirnov@rnc52.ru", "vdsmirnov152@yandex.ru",]
	if not mails:
		print "~eval| alert('Нет адресов для отправки E-mail!')"
		return

#	Только с задержками передачт данных	
#	res = idb.get_table('transports t LEFT JOIN atts a ON t.device_id = a.device_id', "id_org = %d AND last_date < '%s' ORDER BY last_date, gosnum" % (iid_org, sdtm), "t.*, a.last_date")
	res = idb.get_table('transports t LEFT JOIN atts a ON t.device_id = a.device_id', "id_org = %d AND (last_date < '%s' OR last_date IS NULL) ORDER BY last_date, gosnum" % (iid_org, sdtm), "t.*, a.last_date")
	d = res[0]
	for r in res[1]:
		if r[d.index('bm_status')] > 1024:	continue	# Is BLOCKED or DELETED
		if r[d.index('last_date')]:
			sdate = str (r[d.index('last_date')])
			ss = "\t%s\t%s %s" % (r[d.index('gosnum')], cglob.out_sfdate(sdate[:10]), sdate[11:])	#r[d.index('last_date')])
		else:	# Нет данных
			ss = "\t%s\t%s" % (r[d.index('gosnum')], "Нет данных")
		autos.append(ss)
		gosnums.append(r[d.index('gosnum')])
	if not autos:
		print "~eval| alert('Все машины передают данные!')"
		return
	'''
	### DEBUG
	print "<pre>", "\n".join(autos), "</pre>"
	return
	print	"DEBUG", mails, autos
	mails = ["d.kuchin@rnc52.ru", "v.smirnov@rnc52.ru", "r.burygin@rnc52.ru" ]
	'''
	import	send_mail
	mark_mail = False
	rsend = send_mail.send_notice(mails, autos)
	print "~wform_result|"
	if rsend == {}:
		print "<span class='bfinf'>Уведомление отправлено!</span>", mails, "<br />"
		mark_mail = True
	elif rsend and type(rsend) == type({}):
		if len(mails) > len(rsend.keys()):
			ark_mail = True
			print "<span class='bfinf'>Уведомление отправлено НЕ ВСЕМ!</span><br />", str(rsend)
		else:
			print "<span class='bferr'>", rsend, "</span>"
			return
	else:	pass
	if mark_mail:
		query = "INSERT INTO mail_to (id_org, who_id, who_name, body, rem) VALUES (%d, %d, '%s', '%s', '%s'); SELECT max(id_mail) FROM mail_to;" % (iid_org, user['user_id'], swho_name, " ".join(gosnums), "; ".join(mails))
		res = idb.get_row(query)
		if res:
			id_mail = res[0]
			if idb.qexecute("UPDATE transports SET id_mail = %d WHERE gosnum IN ('%s')" % (id_mail, "', '".join(gosnums))):
				print "<span class='bfinf'>Изменения в БД выполнены успешно!</span>"
		else:	print "<span class='bferr'>", query, "</span>"

def	main (SCRIPT_NAME, request, referer):
#	print "~shadow2|"
	try:
		SS = session.session()
		subsystem = SS.get_key('subsystem')
		if subsystem and subsystem['label'] == 'CONTRCT':
			tm_firstalarm = SS.get_key('tm_firstalarm')
			tm_current = int(time.time())
	#		print "~shadow|", tm_firstalarm, tm_current, (tm_firstalarm < tm_current), (tm_firstalarm - tm_current)
			if tm_firstalarm:
				if tm_firstalarm < tm_current:
					print	"~eval| $('#is_alarms').addClass('mark');"
				else:	print	"~eval| $('#is_alarms').removeClass('mark');"
			else:	SS.set_obj('tm_firstalarm', 10 + tm_current)
	#	print "shadow|", request
		if request.has_key ('shstat'):
			shstat = request ['shstat']
	#		print	"~error|~warnn|", os.environ['SERVER_NAME']
			if shstat in ['sssystem', 'setrole']:
				print "~message|"
				set_sysoptions (SS, request)
			elif shstat in ['clear', 'exit']:
				clear (SS, shstat)
			elif shstat == 'mark_row':
				if SS.objpkl.has_key ('win_view') and SS.objpkl['win_view'] == 'on' and request['table'] in ['vcontracts', 'vorganizations']:
					opts = []
					for k in request.keys():
						if k == 'this':	continue
						opts.append("%s=%s" % (k, request[k]))
					print "~eval| win_open('view', '&%s');" % '&'.join(opts) 
				else:
					print "~shadow|", request
					mark_row (SS, request)
			elif shstat == 'send_mail_to':	# Отправить Уведомление об отсутствии данных от машин
				idb = dbtools.dbtools (CDB_DESC)
				send_mail_to (idb, SS, request)
			elif shstat == 'view_alarms':
				sss = []
				for key in ['set_btype', 'like_org', 'id_org']:	# Что передовать alarms
					if request.has_key(key):	sss.append("%s=%s" % (key, request[key]))
				if sss:	print "~eval| win_open('list', 'alarms&%s');" % '&'.join(sss)
				else:	print "~eval| win_open('list', 'alarms');"
				'''
				if request.has_key('set_btype'):
					print "~eval| win_open('list', 'alarms&set_btype=%s');" % request['set_btype']
				else:	print "~eval| win_open('list', 'alarms');"
				'''
			elif shstat == 'udate_alarms':
				print	"~shadow|"
				if request.has_key('id_row') and request['id_row'].isdigit():
					idb = dbtools.dbtools (CDB_DESC)
					import	alarms
					res = alarms.update (idb, SS, request)
					if res:
						if request.has_key('id_org') and request['id_org'].isdigit():
							print "~eval| win_open('list', 'alarms&id_org=%s');" % request['id_org']
						else:	print "~eval| win_open('list', 'alarms');"
				else:	print	request
			elif shstat == 'sset_win_view':		# Показывать в отдельном окне VIEW
				if SS.objpkl.has_key ('win_view') and SS.objpkl['win_view'] == 'on':
					SS.set_obj('win_view', 'off')
					print	"~eval| document.myForm.win_view.value='DIV'"
				else:
					SS.set_obj('win_view', 'on')
					print	"~eval| document.myForm.win_view.value='WIN'"
			elif shstat == 'sset_is_cstat':		# Изменить условие проверки bm_cstat { and | not }
				if SS.objpkl.has_key ('is_cstat') and SS.objpkl['is_cstat'] == 'A':
					SS.set_obj('is_cstat', 'N')
				else:	SS.set_obj('is_cstat', 'A')
				print	"~eval| document.myForm.submit();"
			elif shstat in ['new_bid', 'out_fbid', 'delete_bid', 'update_bid', 'done_bid']:	# Входящие заявки письма
			#	print "~wform_result|"
				print "~shadow|"
				idb = dbtools.dbtools (CDB_DESC)
				res = None
				if shstat == 'new_bid':		res = create_new_bid (idb, SS, request)
				elif shstat == 'out_fbid':	res = out_fbid (idb, SS, request)
				elif shstat == 'delete_bid':	res = delete_bid (idb, SS, request)
				elif shstat == 'update_bid':	res = update_bid (idb, SS, request)
				elif shstat == 'done_bid':	res = done_bid (idb, SS, request)
				else:	print	"<span class='bferr'>", shstat, "</span>", request
				if res:	print	save_history (idb, SS, res, request)
			elif shstat == 'save_as_new_contr':
				print "~shadow|"	#, request
				save_as_new_contr (SS, request)
			elif shstat == 'out_bm_cstat':
				print "~wform_result|"
				idb = dbtools.dbtools (CDB_DESC)
				out_bm_cstat (idb, SS, request)
			elif shstat == 'arm_blank':
			#	print "~shadow|", request
				sss = []
				for key in ['id_arm', 'id_org']: # Что передовать alarms
					if request.has_key(key):        sss.append("%s=%s" % (key, request[key]))
				print "~eval| _win_open('blank', '_arm&%s', 'width=910, height=700, top=100');" % '&'.join(sss)

			elif shstat in ['arm_new', 'arm_insert', 'arm_alist', 'arm_delete', 'arm_blank']:	# or (request.has_key('table') and request['table'] == 'arms' and shstat in ['update', 'insert', 'delete']):
				print "~shadow|" #, request, shstat[4:], "<br>"
				res = None
				import	arms
				arms = arms.arms()
				if shstat[4:] == 'insert':	res = arms.insert(SS, request)
				elif shstat[4:] == 'alist':	res = arms.alist(SS, request)
				elif shstat[4:] == 'delete':	res = arms.delete(SS, request)
				else:				res = arms.outform(SS, request, referer)
				if res:		print "RES", res
			elif shstat == 'out_person' or (shstat in ['update', 'insert', 'delete'] and request.has_key('table') and request['table'] == 'persons'):	# Контакты
				print "~shadow|"	#, request
				res = sss = None
				if request.has_key('id_org'):
					if type (request['id_org']) == type([]):
						request['id_org'] = request['id_org'][0]	#  Вызов из формы "Данные по Организации" request['id_org'] => ['178', '178']
						sss = "set_shadow('view_contr&id_contr=%s');" % request['id_contr']
					else:	sss = "set_shadow('view_org&id_org=%s');" % (request['id_org'])
				import	persons
				person = persons.persons()
				if shstat == 'update':		res = person.update(SS, request)
				elif shstat == 'insert':	res = person.insert(SS, request)
				elif shstat == 'delete':	res = person.delete(SS, request)
				else:				person.outform(SS, request, referer)
				print	"res", res
				if res and sss:	print	"~eval|", sss
			elif shstat in ['create_new_consent', 'create_new_act']:	# Доп. соглашения & Наличие актов
				print "~wform_result|"	#, request
				out_add_doc(None, SS, request)
			elif shstat in ['save_new_doc', 'out_add_doc', 'update_add_doc', 'delete_add_doc']:
				print "~shadow|"
				res = None
				idb = dbtools.dbtools (CDB_DESC)
				if shstat == 'save_new_doc':		res = save_new_doc (idb, SS, request)
				elif shstat == 'out_add_doc':		out_add_doc (idb, SS, request)
				elif shstat == 'update_add_doc':	res = update_add_doc (idb, SS, request)
				elif shstat == 'delete_add_doc':	res = delete_add_doc (idb, SS, request)
				if res:	print save_history (idb, SS, res, request)
		#	elif shstat in ['set_region', 'set_bm_cstat', 'set_ctype', 'set_bm_ssys', 'find_org', 'isset_org', 'save_new', 'update', 'compaire']:
			elif shstat in ['set_region', 'set_ctype', 'set_bm_ssys', 'find_org', 'isset_org', 'save_new', 'update', 'compaire']:
				print "~wform_result|"
				res = None
				idb = dbtools.dbtools (CDB_DESC)	#"host=127.0.0.1 dbname=contracts port=5432 user=smirnov", 1)
				if shstat == 'compaire':	test_compaire (idb, request)
				elif shstat == 'find_org':	find_org (idb, request)
				elif shstat == 'isset_org':	isset_org (idb, request)
				elif shstat == 'set_region':	res = set_region (idb, SS, request)
		#		elif shstat == 'set_bm_cstat':	res = set_bm_cstat (idb, SS, request)
				elif shstat == 'set_ctype':	res = set_ctype (idb, SS, request)
				elif shstat == 'set_bm_ssys':	res = set_bm_ssys (idb, SS, request)
				elif shstat == 'save_new':	res = save_new (idb, SS, request)
				elif shstat == 'update':
					if request.has_key('save_bm_cstat'):
						res = save_bm_cstat(idb, SS, request)
					else:	res = update_stable (idb, SS, request)
				else:	print	"<span class='bferr'>", shstat, "</span>", request
				if res:	print	save_history (idb, SS, res, request)
			
			elif shstat in ['edit_contr', 'view_contr', 'edit_org', 'view_org']:
				print "~shadow|"	#, request
				import	conract
				if shstat == 'edit_contr':	conract.out_tform (SS, 'vcontracts', 'id_contr', request['id_contr'], stat = 'edit')
				elif shstat == 'view_contr':	conract.out_tform (SS, 'vcontracts', 'id_contr', request['id_contr'])
				elif shstat == 'edit_org':	conract.out_tform (SS, 'vorganizations', 'id_org', request['id_org'], stat = 'edit', reqst = request)
				elif shstat == 'view_org':	conract.out_tform (SS, 'vorganizations', 'id_org', request['id_org'], reqst = request)
				else:	cglob.wdgwarnn(shstat, obj = SS.objpkl)
			elif shstat == 'add_row':	# Добавить нового пользлвателя
				print	"~shadow|"	#, request
				add_row (SS, request, SS.get_key('subsystem'))
			elif shstat == 'save_tabl':
			#	print	"~shadow|", request
				if request.has_key('set_table') and request.has_key('id_tabl') and request['set_table'] in dicts.CONTRCT.keys():
					print "~wform_result|"	#, request
					idb = dbtools.dbtools (CDB_DESC)
					res = None
					res = save_tabl(idb, SS, request, dicts.CONTRCT[request['set_table']])
					if res:	print	save_history (idb, SS, res, request)
				else:	out_widget('warnn', shstat, obj = request, iddom = 'warnn')
			elif shstat in ['edit_tabl', 'view_tabl']:
				print "~shadow|", request	# DEBUG
				if shstat == 'edit_tabl':
					sstat = 'edit'
				else:	sstat = None
				import	conract
				pdict = dicts.CONTRCT[request['set_table']]
				conract.out_tform (SS, request['set_table'], pdict['key'], request['id_tabl'], pdict['title'], stat = sstat)
				'''
				out_tform (SS, tname, pkname, idrow, title = None, stat = None, reqst = None)
				cglob.ppobj(pdict)
				cglob.out_widget('warnn', 'edit_tabl', obj = pdict, iddom = 'warnn')
				'''
			elif shstat == 'insert':
				print	"~shadow|"	#, request
				insert_row (SS, request)
			#	cglob.out_widget ('wform', str(request), obj = SS.objpkl)
			elif shstat == 'get_ack':
				if request.has_key('id_mail') and request['id_mail'].isdigit():
					idb = dbtools.dbtools (CDB_DESC)
					query = "UPDATE mail_to SET date_ack='%s' WHERE id_mail=%s" % (time.strftime('%Y-%m-%d', time.localtime(time.time())), request['id_mail'])
					if idb.qexecute(query):
						print "~is_ack|Ответ от: %s" % time.strftime('%d-%m-%y', time.localtime(time.time()))
					else:	print "~shadow|<span class='bferr'>Error:", query, "</span>"
				else:	print "~is_ack|", request['id_org'], request['id_mail']
			elif shstat == 'view_mail_to':
				if request.has_key('id_mail') and request['id_mail'].isdigit():
					iid_mail = int(request['id_mail'])
					idb = dbtools.dbtools (CDB_DESC)
					dmail = idb.get_dict ("SELECT * FROM mail_to  WHERE id_mail=%d" % iid_mail)
					if dmail['date_ack']:
						sbuttons = "<td align='right'>Ответ от: <b>%s</b> &nbsp; " % cglob.out_sfdate(dmail['date_ack'])
					else:	sbuttons = """<td align='right'><input type='button' class='butt' value='Пришел ответ'
						onclick="if (confirm ('Пришел ответ на Уведомление?')) {set_shadow('get_ack&&id_mail=%d');}" />""" % iid_mail
					sbdel = """<input type='button' class='butt' value=' Удалить ' onclick="if (confirm ('Удалить Уведомление?')) {set_shadow('delete_mail_to&stable=mail_to&id_mail=%d');}" />""" % iid_mail
					prn_div_tit ('E-mail', ''.join([sbuttons, sbdel]))
					print "<table width=100%>"
					for c in ['who_name', 'rem', 'body']:
						print "<tr><td width=100px align='right'>"
						if c == 'who_name':	print "Кто отправил:</td><td class='bfgrey'>", dmail['who_name'],
						if c == 'rem':		print "E-mail:</td><td  class='bfgrey'>", dmail['rem'], " &nbsp; от: ", cglob.out_sfdate(dmail['date_send']),
						if c == 'body':		print "Машины:</td><td  class='bfgrey'>", dmail['body'],
						print "</td></tr>"
				#	print dmail
					print "</table></div>"
					print "~eval|$('#is_ack').removeClass('mark');"
				else:	print "~wform_result|", request
			elif shstat == 'set_ts_view':
				print "~shadow|"
				ldid = []
				for n in request.keys():
					if 'ssvw:' in n:
						ldid.append(n[5:])
				if ldid:
					idb = dbtools.dbtools("host=127.0.0.1 dbname=worktime port=5432 user=smirnov")
					if request.has_key('select_tts') and request['select_tts'] in ['contract', 'is_vts']:
						query = "UPDATE work_statistic SET stat_view = NULL; UPDATE work_statistic SET stat_view = 1 WHERE device_id IN (%s)" % ", ".join(ldid)
					else:	query = "UPDATE work_statistic SET stat_view = 1 WHERE device_id IN (%s)" % ", ".join(ldid)
					if not idb.qexecute(query):
						cglob.out_widget('wbox', shstat, txt = "<div class='mark' style='padding: 8px'><b>ERROR: </b>%s<br/>&nbsp;&nbsp; %s </div>" % (str(idb.last_error), query))
					else:
						cglob.out_widget('wbox', shstat, txt = "<div class='green' style='padding: 5px'><b>Навигаторы: </b>%s<br/>&nbsp;&nbsp; исключены из просмотра. </div>" % ", ".join(ldid))
						print "~eval| document.myForm.submit ();"
				else:
					cglob.out_widget('wbox', shstat, txt = "<div class='mark' style='padding: 8px'><b>Нет выбранных навигаторов!  </b><br/>&nbsp;&nbsp; %s </div>" % str(request,))
			elif shstat == 'save_device_rem':
				if request.has_key('rem') and request.has_key('device_id') and request['device_id'].isdigit():
					idb = dbtools.dbtools("host=127.0.0.1 dbname=worktime port=5432 user=smirnov")
					query = "UPDATE work_statistic SET rem='%s' WHERE device_id = %s;" % (request['rem'].strip(), request['device_id'])
					if not idb.qexecute(query):
						cglob.out_widget('wbox', shstat, txt = "<div class='mark' style='padding: 8px'><b>ERROR: </b>%s<br/>&nbsp;&nbsp; %s </div>" % (str(idb.last_error), query))
					else:
						cglob.out_widget('wbox', shstat, txt = "<div class='green' style='padding: 5px'><b>Примечание: </b>%s<br/>&nbsp;&nbsp; успешно сохранено. </div>" % request['rem'].strip())
						print "~eval| document.myForm.submit ();"
			else:
				cglob.wdgwarnn("'Unknown shstat: [%s]!');" % request ['shstat'], str(request), obj = SS.objpkl)
		#		print "~eval|alert ('Unknown shstat: [%s]!');" % request ['shstat']
		else:
			print "~shadow|"
			wdgerror ("Отсутствует request[shstat]",  txt = "request: %s" % str(request), obj = SS.objpkl)
		#	out_widget('warnn', tit = "Отсутствует request[shstat]",  txt = "request: %s" % str(request), obj = SS.objpkl)
		
	except psycopg2.OperationalError:
		exc_type, exc_value = sys.exc_info()[:2]
		print "~eval|alert (\"EXCEPT: ajax Нет доступа к БД:\\n", ddb_map, "\");"
	except:
		exc_type, exc_value = sys.exc_info()[:2]
		print "~error|<span class='error'>EXCEPT:", exc_type, exc_value, "</span>"
	#	print "~eval|alert (\"EXCEPT: ajax.py shstat: ", shstat, "\\n", exc_type, exc_value, "\");"
