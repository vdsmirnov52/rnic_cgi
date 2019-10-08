# -*- coding: utf-8 -*-

import	 sys, os, time, string

LIBRARY_DIR = r"/home/smirnov/MyTests/CGI/lib/"
sys.path.insert(0, LIBRARY_DIR)

import	dbtools
import	session
import	cglob
import	dicts

RES_YN =	(['cod', 'name'], [(0,'Да'),(1, 'Нет')])
RES_YNC =	(['cod', 'name'], [(0,'Да'),(1, 'Нет'),(2,'Сегодня')])
RES_NDS =	(['cod', 'name'], [(0,'без НДС'),(1, 'с НДС')])
RES_BIDS =	(['cod', 'name'], [(0,'Откр'),(1, 'Закр'),(2, 'Все')])
RES_STTS =	(['cod', 'name'], [(1024+2048,'Отмена'),(1024, 'Блокировать'), (4096, 'Блок. E-mail'),(2048, 'Удалить')])	# Стаус ТС
RES_TABS =	[['cod', 'name'], [('vcontracts','Договора и Контракты'),('vorganizations', 'Данные по Организациям'),
		('wtransports', 'Транспорт в работе'),
		('vtransports', 'Транспорт'), ('voatts', 'Оборудование'),
		('vbids', "Список Заявок"),
		('vpersons', "Список контактов"),
		('vmail_to', "Список отправки почты"),
		('varms', 'АРМ Авторизация'), ('vhistory', 'История измененмй БД')
		],
		]
DICT_TABS =	dicts.CONTRCT
SFDATE =	dicts.SFDATE
DAYS =	10	### WWW Сколько дней нет данных от машин

CDB_DESC = cglob.get_CDB_DESC('ZZZ')

def	out_tform (SS, tname, pkname, idrow, title = None, stat = None, reqst = None):
	butts = {
	'edit_tabl':	"""<input type='button' class='butt' value='Изменить' onclick="set_shadow('edit_tabl&id_tabl=%s');">""",
	'view_tabl':	"""<input type='button' class='butt' value='Смотреть' onclick="set_shadow('view_tabl&id_tabl=%s');">""",
	'save_tabl':	"""<input type='button' class='butt' value='Сохранить изменения' onclick="set_shadow('save_tabl&id_tabl=%s');">""" % idrow, 
	'view_org':	"""<input type='button' class='butt' value='к Организации' onclick="set_shadow('view_org&id_org=%d');">""",
	'view_evnt':	"""<input type='button' class='butt' value='к Событиям' onclick="set_shadow('view_alarms&id_org=%d');" />""",
	}
	if not (tname and pkname and idrow):
		perror ("out_tform", ", ".join ([tname, pkname, idrow]))
		return
	idb = dbtools.dbtools (CDB_DESC)	#"host=127.0.0.1 dbname=contracts port=5432 user=smirnov")
	print "QQQ", pkname, idrow
	res = idb.get_table (tname, '%s = %s' % (pkname, idrow))
	if not res:
		perror ('out_tform get_table', ", ".join ([tname, pkname, idrow]))
		return
	form_tit = tname
	order = is_update = None
	cdict = res[0]
	row = res[1][0]
	if tname == 'vcontracts':	return	out_vcontracts(SS, idb, row, cdict, stat)
	if tname == 'vorganizations':	return	out_vorganizations (SS, idb, row, cdict, stat, reqst)
	thead = None
	butt_tabl = []
	if DICT_TABS.has_key(tname):
		dtbl = DICT_TABS[tname]
		if dtbl.has_key('form_tit'):	form_tit = dtbl['form_tit']
		if dtbl.has_key('thead'):	thead = dtbl['thead']
		if dtbl.has_key('order'):	order = dtbl['order']
		if 'id_org' in cdict and row[cdict.index('id_org')]:
			if tname == 'vbids' and is_valarms (idb, row[cdict.index('id_org')]):
				butt_tabl.append (butts['view_evnt'] % row[cdict.index('id_org')])
			butt_tabl.append (butts['view_org'] % row[cdict.index('id_org')])
		if stat and stat == 'edit':
			if dtbl.has_key('update'):	is_update = dtbl['update'].keys()
			butt_tabl.append (butts['view_tabl'] % str(row[cdict.index(dtbl['key'])]))
		else:	butt_tabl.append (butts['edit_tabl'] % str(row[cdict.index(dtbl['key'])]))
	else:	print res
	cglob.out_headform(form_tit, sright = ' '.join(butt_tabl))
	print	"<div style='background-color: #dde; border: thin solid #778;'><div style='min-height: 408px; width: 880px; padding: 6px;'>"
#	print	tname, order, dtbl.keys()
	if not order:	order = res[0]

	print	"<table id='%s_row' width=100%%>" % tname
	for cnm in order:
		if cnm == 'rem':
			colname = 'Примечание'
		elif cnm == 'bm_ssys':
			colname = 'Подсистема'
		elif cnm == 'id_mail':
			colname = 'Уведомление'
		elif thead and thead.has_key(cnm):
			colname = thead[cnm]
		else:	colname = cnm.upper()
		if row[res[0].index(cnm)]:
			if cnm in SFDATE:
				val = cglob.out_sfdate(row[res[0].index(cnm)])
			else:	val = row[res[0].index(cnm)]
		else:	val = ''
		print	"<tr class='hei'><td width=194px align='right'>%s:</td><td id='%s'>" % (colname, cnm),
		if cnm == 'ctype':
			print	"<b>", get_sctype(idb, val), "</b>",
		elif cnm == 'bm_ssys':
			print	"<b>", get_subsystems(idb, val), "</b>",
		elif cnm == 'bm_options':
			print	"<b>", get_options_att(idb, val), "</b>",
		elif cnm == 'id_mail':
			print	"<b>", get_mail_to (idb, val), "</b>",
		elif cnm == 'bm_bstat':
			print	"<b>", get_sbid_stat (idb, val, row[res[0].index('tm_alarm')], fix_bstat = row[res[0].index('fix_bstat')]), "</b>",
		elif cnm == 'bm_status':
			if stat == 'edit' and is_update and cnm in is_update:
				print "Блокировать или Удалить ТС "
				cglob.out_select('bm_status', RES_STTS, key = row[res[0].index('bm_status')], sfirst=" ")
			else:	print	"<b>", get_bm_status(idb, val), "</b>",
		elif cnm[:3] == 'tm_' and val:
			print	"<b>", time.strftime('%d-%m-%Y', time.localtime(val)), "</b>",
		else:
			if stat == 'edit' and is_update and cnm in is_update:
				ppp = []
				opt = dtbl['update'][cnm]
				if opt[:2] == 't:':
					print "<textarea name='%s' maxlength=%s rows=1 cols=80>%s</textarea>" % (cnm, opt[2:], val)
				else:
					if opt[:2] == 's:':
						if int(opt[2:]) > 32:	ppp.append ("size=32")
						ppp.append ('maxlength=%s' % opt[2:])
					elif opt[0] == 'd':
						ppp.append ("size=10 class='date'")
					if ppp:	sopt = ' '.join(ppp)
					else:	sopt = ''
					print	"<b><input type='text' name='%s' value='%s' %s></b>" % (cnm, val, sopt)
			else:	print	"<b>", val, "</b>",
		print	"</td></tr>"
	if tname in ["vtransports", "wtransports"]:
		print "<tr><td align='right'>Информация о приборе</td><td><hr></td></tr>"
		datt = idb.get_dict ("SELECT * FROM atts WHERE autos = %d" % row[res[0].index('id_ts')])
		if datt:
			print "<tr><td align='right'>%s:</td><td><b>" % 'id_att'.upper(), datt['id_att'], "</b></td></tr>"
			print "<tr><td align='right'>%s:</td><td><b>" % 'device_id'.upper(),
			if datt['device_id'] != row[res[0].index('device_id')]:
				print "<span class='bferr'> Транспорт ", row[res[0].index('device_id')], " != </span>"
			print datt['device_id'], "</b></td></tr>"
			print "<tr><td align='right'>%s:</td><td><b>" % 'transport_id'.upper()
			if datt['transport_id'] != row[res[0].index('transport_id')]:
				print "<span class='bferr'> Транспорт ", row[res[0].index('transport_id')], " != </span>"
			print datt['transport_id'], "</b></td></tr>"
			for c in ['modele', 'uin', 'sim_1', 'sim_2', 'last_date']:
				if datt[c]:
					print "<tr><td align='right'>%s:</td><td><b>" % c.upper(), datt[c], "</b></td></tr>"
		else:	 print "<tr><td align='right'>&nbsp;</td><td><span class='bferr'> Отсутствует прибор для ТС (id_ts: %d) </span></td></tr>" % row[res[0].index('id_ts')]
	if stat == 'update':
		print	"""<tr><td></td><td><input type='button' class='butt' value=' Обновить ' onclick="set_shadow('update&table=%s');" /></td></tr>""" % tname
	if stat == 'addnew':
		print	"""<tr><td></td><td><input type='button' class='butt' value=' Сохранить ' onclick="set_shadow('insert&table=%s');" /></td></tr>""" % tname
	print	"</table>"
#	print	"<div id='is_result' style='text-align: center;'>%s</div>" % stat
	print	"</div>"
	print	"<div style='min-height: 30px;  text-align: center;'>"
	if stat and  stat == 'edit':	print	butts['save_tabl']	#contr, butt_save_as_new
	print	"</div>"
	print	"<div id='wform_result' style='min-height: 30px;  text-align: center;'>%s</div>" % stat
	print	"</div><!-- wform out_tform	-->"	############################################

def	get_bm_status (idb, jbm):
	""" Читать статусы ТС	"""
	if not jbm:	return	jbm
	res = idb.get_table ('ts_status', "code > 0 ORDER BY code")
	if not res:	return	"ERROR"
	stt_list = []
	for r in res[1]:
		if r[0] & jbm:
			if r[0] < 1024:
				stt_list.append(r[1])
			else:	stt_list.append("<span class='bferr'>%s</span>" % r[1])
	if stt_list:	return	"; ".join(stt_list)
	else:		return	"SSS"

def	get_mail_to (idb, id_mail):
	""" Читать Уведомление	"""
	if not id_mail:	return	""
	dres = idb.get_dict("SELECT * FROM mail_to WHERE id_mail = %d" % id_mail)
	if not dres:	return	"ERROR"
	if not dres['date_ack']:
		return	"Отправлено: %s" % cglob.out_sfdate(dres['date_send'])
	else:	return	"Отправлено: %s, есть ответ: %s" % (cglob.out_sfdate(dres['date_send']), cglob.out_sfdate(dres['date_ack']))

def	out_vorganizations (SS, idb, row, cdict, stat = None, request = None):
	""" Показвть данные по Организации	"""
	global	RBBTYPE

	iid_org = row[cdict.index('id_org')]
	butts = {
	'edit_org':	"""<input type='button' class='butt' value='Изменить' onclick="set_shadow('edit_org&id_org=%s');">""",	# % iid_org,
	'view_org':	"""<input type='button' class='butt' value='Смотреть' onclick="set_shadow('view_org&id_org=%s');">""",	# % iid_org,
	'view_contr':	"""<input type='button' class='butt' value='к Договору' onclick="set_shadow('view_contr&id_contr=%s');">""",
	'update':	"""<input type='button' class='butt' value='Сохранить изменения' onclick="set_shadow('update&stable=vorganizations&id_org=%d');">""",	# % iid_org
	'save_new':	"""<input type='button' class='butt' value='Сохранить новую организацию' onclick="check_form_org();" />""",	#set_shadow('save_new');">""",
	'view_evnt':    """<input type='button' class='butt mark' value='к Событиям' onclick="set_shadow('view_alarms&id_org=%d');" />""",
	}
	count_valarms = is_valarms (idb, iid_org)
	list_butts = []
	if count_valarms:	list_butts.append (butts['view_evnt'] % iid_org)
	if request and request.has_key('id_contr'):
		list_butts.append (butts['view_contr'] % request['id_contr'])
		id_contr = request['id_contr']
		if stat and stat == 'edit':
			list_butts.append (butts['view_org'] % ("%s&id_contr=%s" % (str(iid_org), request['id_contr'])))
		else:	list_butts.append (butts['edit_org'] % ("%s&id_contr=%s" % (str(iid_org), request['id_contr'])))
	else:
		id_contr = None
		if stat and stat == 'edit':
			list_butts.append (butts['view_org'] % iid_org)
		else:	list_butts.append (butts['edit_org'] % iid_org)
		view_contr = ''
	if stat != 'new':	cglob.out_headform('Данные по Организации', sright = " ".join(list_butts))

	USER = SS.get_key('USER')
	print	"<div style='background-color: #dde; border: thin solid #778;'>"	###, USER, USER['bm_role']
	print	"<div style='min-height: 408px; width: 878px; padding: 6px;'>"
	print	"<table id='organization_row' width=100%%>"	# % iid_org
	print	"<tr><td width=194px align='right'>Метка организации:</td><td>"
	if stat:
		if stat == 'edit':
			slabel = row[cdict.index('label')]
		else:	slabel = ''
		print	"<input type='text' name='label' maxlength=32 value='%s' /></td></tr>" % slabel
	else:
		is_arms = "role:", USER['bm_role']
		if USER['bm_role'] & 4:	# Admin
			res = idb.get_table('arms', 'id_org=%d' % iid_org)
			if res:
				is_arms = """<span id='arm_info' class='bfinf'> АРМов %d.</span> <input type='button' class='butt' value='Показать' onclick="set_shadow('arm_alist&id_org=%s');" />""" % (len(res[1]), iid_org)
			else:	is_arms = "<span id='arm_info' class='bferr'>Нет АРМов </span>"
			arm_butt = """<input type='button' class='butt' value='Создать новый' onclick="set_shadow('arm_new&id_org=%s');" />"""  % iid_org
		else:	arm_butt = "###"
		print	"<b>%s</b> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; АРМы: %s &nbsp; <span id='arm_info' class='bfinf'> %s</span></td></tr>" % (
				row[cdict.index('label')], is_arms, arm_butt)
	print	"<tr class='hei'><td width=194px align='right'>Краткое Наименоване:</td><td>"
	if stat:
		if stat == 'edit':
			sbname = row[cdict.index('bname')]
		else:	sbname = ''
		print	"<input type='text' name='bname' size=72 maxlength=128 value='%s' /></td></tr>" % sbname
	else:	print	"<b>%s</b></td></tr>" % row[cdict.index('bname')]
	print	"<tr class='hei'><td width=194px align='right'>Полное Наименоване:</td>"
	if stat:
		if stat == 'edit':
			sfname = row[cdict.index('fname')]	#.srtip()
		else:	sfname = ''
		print	"<td valign='bottom'><textarea name='fname' maxlength=256 rows=1 cols=80>%s</textarea></td></tr>" % sfname
	else:	print	"<td><b>%s</b></td></tr>" % row[cdict.index('fname')]
	print	"<tr><td width=194px align='right'>ИНН:</td><td><b>"
	sinn = ''
	if row[cdict.index('inn')]:	sinn = row[cdict.index('inn')]
	if stat in ['new', 'edit']:
		print	"<input type='text' name='inn' size=10 maxlength=12 value='%s' onkeyup='return intKey(this);' /></b>" % sinn
	else:	print sinn, "</b>"	#, stat
	############################	Район:
	print 	" &nbsp; Район:<span id='region' class='bfinf'>"
	if stat or not row[cdict.index('rname')]:
		RREGION = idb.get_table ('region', "id > 0 ORDER BY rname")
		if RREGION:
			if iid_org:
				ssopt = """onchange="if (confirm ('Сохранить выбранный район?')) { set_shadow('set_region&id_org=%d');}" """ % iid_org
				cglob.out_select('region', RREGION, ['id', 'rname'], key = row[cdict.index('region')], sopt = ssopt)
			else:	cglob.out_select('region', RREGION, ['id', 'rname'], key = row[cdict.index('region')])
	else:	print	row[cdict.index('rname')]
	print	"</span>"
	############################	Подситемы:
	if stat not in ['new', 'edit']:
		print	" &nbsp; Подситемы:<span id='bm_ssys' class='bfinf'>"
		if row[cdict.index('bm_ssys')]:
			bm_ssys = get_subsystems(idb, row[cdict.index('bm_ssys')])
		else:	bm_ssys = ''
		print   "%s</span>" % bm_ssys

#	else:	print	"%s</td></tr>" % sinn	#row[cdict.index('inn')]
	print	"</td></tr>"
	'''	WWW
	print	"<tr><td width=194px align='right'>Район:</td><td id='region'>"
	if stat or not row[cdict.index('rname')]:
	#	ssopt = """onchange="if (confirm ('Сохранить выбранный район?')) { alert('ZZZ '+ document.myForm.region.value); set_shadow('set_region&id_org=%d');}" """ % iid_org
		RREGION = idb.get_table ('region', "id > 0 ORDER BY rname")
		if RREGION:
			if iid_org:
				ssopt = """onchange="if (confirm ('Сохранить выбранный район?')) { set_shadow('set_region&id_org=%d');}" """ % iid_org
				cglob.out_select('region', RREGION, ['id', 'rname'], key = row[cdict.index('region')], sopt = ssopt)
			else:	cglob.out_select('region', RREGION, ['id', 'rname'], key = row[cdict.index('region')])
	else:	print	"<b>%s</b>"  % row[cdict.index('rname')] #	rname
	print	"</td></tr>"
	'''
	if stat != 'new':
		print	"<tr class='hei'><td width=194px align='right'>Контакты:</td><td>%s</td></tr>" % get_persons(idb, 0, iid_org)
		print	"</td></tr>"
		print	"<tr class='hei'><td width=194px align='right'>Договора:</td><td>", out_contrlist (idb, iid_org)	#, butts['view_contr'])
		print	"</td></tr>"
		'''	WWW
		print	"<tr><td width=194px align='right'>Договор на подситему:</td><td id='bm_ssys'>"
		if row[cdict.index('bm_ssys')]:
			bm_ssys = get_subsystems(idb, row[cdict.index('bm_ssys')])	#, 'ssname')
		else:	bm_ssys = ''
		print	"<b>%s</b>" % bm_ssys
		print	"</td></tr>"
		'''
		print	"<tr class='hei'><td width=194px align='right'>Входящие заявки письма:</td><td>"
		if not RBBTYPE:	RBBTYPE = idb.get_table ('bid_type', 'code > 0')
		cglob.out_select('bid_type', RBBTYPE, ['code', 'bname'])
		print	" &nbsp; № <input type='text' size=6 maxlength=16 name='bid_num' > от:<input type='text' class='date' name='bid_create' />"
		print	"""<input type='button' class='butt' value='Сохранить' title='Сохранить заявку (письмо)'
			onclick="if (check_new_bid()) {set_shadow('new_bid&id_org=%d'); }" >""" % iid_org
		print	"<div id='bids' style='max-height: 160px; overflow: auto;'>%s</div>" % get_bids(idb, iid_org)
		print	"</td></tr>"
	if not stat in ['new', 'edit']:
		shead, ress = out_transports(idb, iid_org, row[cdict.index('region')], row[cdict.index('bl_mail')])
		print	"<tr class='hei'><td width=194px align='right' rowspan='2'>Машины:</td><td>", shead, "</td></tr>"
		print   "<tr><td>", ress
		print	"</td></tr>"
	else:
		print	"<tr class='hei'><td width=194px align='right'>Машины:</td><td>Отправлять уведомления об отсутсвии данных:"
	#	print row[cdict.index('bl_mail')]
		cglob.out_select('bl_mail', RES_YN, key = row[cdict.index('bl_mail')])
		print	"</td></tr>"
	print	"<tr class='hei'><td width=194px align='right'>Примечание:</td><td valign='bottom' class='bfgrey'>"
	srem = ''
	if row[cdict.index('rem')]:	srem = row[cdict.index('rem')].strip()
	if stat:
		print	"<textarea name='rem' maxlength=256 rows=1 cols=80>%s</textarea>" % srem	#row[cdict.index('rem')]
	else:	print	srem	#row[cdict.index('rem')]
	print	"</td></tr>"
	print	"</table>"
	print	"</div>"
	print	"<div style='min-height: 30px;  text-align: center;'>"
	if stat == 'edit':	print	butts['update'] % iid_org	#, butts['save_new']
	if stat == 'new':	print	butts['save_new']
	print	"</div>"
	print	"<div id='wform_result' style='min-height: 30px;  text-align: center;'>%s</div>" % stat
	if stat != 'new':	print	"</div><!-- wform out_vorganizations	-->"	############################################

def	out_vcontracts (SS, idb, row, cdict, stat = None, iid_org = None):
	""" Показвть данные по договору (контракту)	"""
	if not iid_org:
		iid_org = row[cdict.index('id_org')]
	iid_contr = row[cdict.index('id_contr')]
	butts = {
#	'view_org':	"""<input type='button' class='butt' value='к Организации' onclick="set_shadow('view_org&id_org=%d&id_contr=%d');">""" % (iid_org, iid_contr),
	'view_org':	"""<input type='button' class='butt' value='к Организации' onclick="set_shadow('view_org&id_contr=%d');">""" % (iid_contr),
	'edit_contr':	"""<input type='button' class='butt' value='Изменить' onclick="set_shadow('edit_contr&id_contr=%d');" />""",
	'view_contr':	"""<input type='button' class='butt' value='Смотреть' onclick="set_shadow('view_contr&id_contr=%d');" />""",
	'save_new':	"""<input type='button' class='butt' value='Сохранить новый договор' onclick="check_form_contr();" />""",
	'save_as_new':	"""<input type='button' class='butt' value='Сохранить как новый' onclick="set_shadow('save_as_new_contr&id_contr=%d');">""" % iid_contr,
	'update':	"""<input type='button' class='butt' value='Сохранить изменения' onclick="set_shadow('update&stable=vcontracts&id_contr=%d');">""" % iid_contr,
	}

	if stat != 'new':
		if stat and stat == 'edit':
			butt_contr = butts['view_contr'] % iid_contr
		else:	butt_contr = butts['edit_contr'] % iid_contr
#		cglob.out_headform('Договор (контракт)', sright = " ".join([butts['view_org'], butt_contr]))
		cglob.out_headform('Договор (контракт)', sright = " ".join(["id:%d" % iid_org, butts['view_org'], butt_contr]))
	print	"<div style='background-color: #dde; border: thin solid #778;'>"
	print	"<div style='min-height: 408px; width: 878px; padding: 6px;'>"
	print	"<fieldset id='id_contr:%d' class='hidd'><input name='id_org' type='hidden' value='%d' /><table id='contract_row' width=100%%>" % (iid_contr, iid_org)
	if stat == 'new' and iid_org:
		dr_org = idb.get_dict("SELECT * FROM vorganizations WHERE id_org = %d;" % iid_org)
	else:	dr_org = None
	if row[cdict.index('fname')]:
		oname = row[cdict.index('fname')]
	elif row[cdict.index('bname')]:
		oname = row[cdict.index('bname')]
	elif row[cdict.index('label')]:
		oname = row[cdict.index('label')]
	else:	oname = ''
	print	"<tr class='hei'><td width=194px align='right'>Наименоване организации:</td><td id='find_org'>"
	if stat == 'new' or not oname:
		if dr_org and dr_org['bname']:
			bname = dr_org['bname']
		else:	bname = ''
#		print	"iid_org", iid_org
		print	"<input type='text' name='org_name' size=48 maxlength=64 value='%s' />" % bname
		print	"""<input type='button' class='butt' value='Искать' onclick="set_shadow('find_org');" title='Искать Организацию' />"""
		print	"""<input class="butt" type="button" value="Создать" onclick="win_open('new_org', '');" title="Новая Организация" />"""
	else:	print	"<b>%s</b>" % oname
	print	"</td></tr>"
	if stat == 'new':
		if dr_org and dr_org['fname']:
			fname = dr_org['fname']
		else:	fname = ' &nbsp; '
		print	"<tr class='hei'><td width=194px> &nbsp; </td><td id='org_fname' class='bfgrey'>%s</td></tr>" % fname
	print	"<tr class='hei'><td width=194px align='right'>№ Договора (контракта):</td><td>"
	cnum = cdate = ''
	if not stat or stat == 'edit':
		if row[cdict.index('cnum')]:		cnum = row[cdict.index('cnum')]
		if row[cdict.index('cdate')]:		cdate = cglob.out_sfdate(row[cdict.index('cdate')])	#str(row[cdict.index('cdate')])
	if stat == 'edit' or stat == 'new':
		print	"""<input type='text' name='cnum' value='%s' /> от <input id='create' class='date' type='text' name='cdate' value='%s' />""" % (cnum, cdate)
	else:
		print	"<b>%s</b> от <b>%s</b>" % (cnum, cdate)
	print	"</td></tr>"
	print	"<tr><td width=194px align='right'>Тип Договора (контракта):</td><td id='ctype'>"
	if stat or not row[cdict.index('ctype')]:
		set_ctype (idb, row[cdict.index('ctype')], iid_contr)
	else:	print	"<b>%s</b>" % get_sctype(idb, row[cdict.index('ctype')],2)
	print	"</td></tr>"
	print	"<tr><td width=194px align='right'>Договор на подситему:</td><td id='bm_ssys'>"
	if stat or not row[cdict.index('bm_ssys')]:
		set_subsystem (idb, row[cdict.index('bm_ssys')], iid_contr)
	else:	print	"<b>%s</b>" % get_subsystems(idb, row[cdict.index('bm_ssys')], 'ssname')

	print	"</td></tr>"
	print	"<tr><td width=194px align='right'>Срок действия:</td><td>"
	if stat:
		print	"<input td='period' type='text' name='period_valid' value='%s' class='date' /> &nbsp; действует/НЕТ: " % cglob.out_sfdate (row[cdict.index('period_valid')])
		cglob.out_select('is_valid', RES_YN, key = row[cdict.index('is_valid')])
	else:
		print	"<b>%s</b> &nbsp; действует/НЕТ: <span id='is_valid' class='bfgrey'>" % cglob.out_sfdate (row[cdict.index('period_valid')])
		if row[cdict.index('is_valid')] in [0,1]:
			print	RES_YN[1][row[cdict.index('is_valid')]][1]
		else:	print	 str(row[cdict.index('is_valid')])
	print	"</span></td></tr>"
	print	"""<tr><td width=194px align='right'>Состояние договора:</td><td class='line' id='bm_cstat' onclick="$(this).addClass('mark'); $('#add_doc tr').removeClass('mark');"
		ondblclick="out_bm_cstat(%d);">""" % iid_contr
	print	get_cont_stat(idb, row[cdict.index('bm_cstat')], 1)
	"""
	if row[cdict.index('date_close')]:
		print cglob.out_sfdate(row[cdict.index('date_close')])
	elif row[cdict.index('bm_cstat')] & 4096:
	#	print	"<br />bm_cstat", row[cdict.index('bm_cstat')]
		print "<input td='date_close' type='text' name='date_close' value='%s' class='date' />" % cglob.out_sfdate (row[cdict.index('date_close')])
	"""
	'''
	if not row[cdict.index('bm_cstat')] or stat:
		set_cont_stat(idb, row[cdict.index('bm_cstat')], row[cdict.index('ctype')], iid_contr)
	else:
		print	get_cont_stat(idb, row[cdict.index('bm_cstat')], 1)
	'''
	print	"</td></tr>"
	print	"<tr><td width=194px align='right'>Сумма договора:</td><td>"
	if row[cdict.index('csumma')] and row[cdict.index('csumma')] > 0:
		csumma = str(row[cdict.index('csumma')])
	else:	csumma = ''
	if stat:
		print	"<input type='text' name='csumma' value='%s'  onkeyup='return intKey(this);' /> руб &nbsp; НДС:" % csumma
		cglob.out_select('is_nds', RES_NDS, key = row[cdict.index('is_nds')])
	else:
		print	"<div style='width:200px; text-align: right;'><b>%s</b> руб &nbsp; %s  </div>" % (cglob.strub(row[cdict.index('csumma')]),  RES_NDS[1][row[cdict.index('is_nds')]][1])
#		print   " НДС: %s </div>" % RES_NDS[1][row[cdict.index('is_nds')]][1]
		
	print	"</td></tr>"
	if row[cdict.index('rname')]:
		rname = row[cdict.index('rname')]
	elif dr_org and dr_org['rname']:
		rname = dr_org['rname']
	else:	rname = ''
	print	"<tr><td width=194px align='right'>Район:</td><td id='org_rname' class='bfgrey'>%s</td></tr>" % rname
	if stat == 'new':
		print	"<tr class='hei'><td width=194px align='right'>Контакты:</td><td id='org_persons' > &nbsp; </td></tr>"
	else:	print	"<tr class='hei'><td width=194px align='right'>Контакты:</td><td >%s</td></tr>" % get_persons(idb, iid_contr, iid_org)
	if stat != 'new':	# get_add_doc
		print	"<tr class='hei'><td width=194px align='right'>Доп. соглашения:</td><td id='add_consents'> %s </td></tr>" % (get_add_doc(idb, iid_contr, 'add_consents', row[cdict.index('add_consents')]))
		print	"<tr class='hei'><td width=194px align='right'>Наличие актов:</td><td id='add_acts'> %s </td></tr>" % (get_add_doc(idb, iid_contr, 'add_acts', row[cdict.index('add_acts')]))
		
	print	"<tr class='hei'><td width=194px align='right'>Примечание:</td><td valign='bottom' class='bfgrey'>"
	srem = ''
	if row[cdict.index('rem')]:	srem = row[cdict.index('rem')].strip()
	if stat:
		print	"<textarea name='rem' maxlength=256 rows=1 cols=80>%s</textarea>" % srem	#row[cdict.index('rem')]
	else:	print	srem	#row[cdict.index('rem')]
	print	"</table></fieldset>"
	print	"</div>"
	print	"<div style='min-height: 30px;  text-align: center;'>"
	if stat == 'edit':	print	butts['update'], butts['save_as_new']
	if stat == 'new':	print	butts['save_new']
#	print	"""<input type='button' class='butt' value='DEBUG' onclick="win_open('view', '');" />"""
	print	"</div>"
	print	"<div id='wform_result' style='min-height: 30px;  text-align: center;'>%s</div>" % stat
	if stat != 'new':	print	"</div><!-- wform out_vcontracts	-->"	############################################

def	out_contrlist (idb, id_org):	#, sbuttn):
	""" Показвть список договоров (контрактов)     """
	sbutt = """<input type='button' class='butt' value='Добавить Договор' onclick="win_open('new_contr', '&id_org=%d');" title='Новый' />""" % id_org
	res = idb.get_table ('vcontracts', "id_org = %d ORDER BY cdate DESC" % id_org)
	if not res:
		return	"<span class='bferr'>Нет договоров</span>%s" % sbutt
	cdict = res[0]
	sss = ["<table id='contracts' width=100% cellspacing=0>"]
	for r in res[1]:
		id_contr = r[cdict.index('id_contr')]
		scdate = cglob.out_sfdate (r[cdict.index('cdate')])
		if not scdate:	scdate = "<span class='bferr'>Даты НЕТ!</span>"
		sss.append ("""<tr class='line' onclick="$('#contracts tr').removeClass('mark'); $(this).addClass('mark'); $('#bm_cstat').removeClass('mark');
			$('#bids tr').removeClass('mark'); $('#wform_result').html('');" ondblclick="set_shadow('view_contr&id_contr=%d');">""" % id_contr)
		sss.append ("<td align='right' width=28%%><b>%s</b> от <b>%s</b></td>" % (r[cdict.index('cnum')], scdate))	# cglob.out_sfdate (r[cdict.index('cdate')])))
		sss.append ("<td> &nbsp; до <b>%s</b></td>" % cglob.out_sfdate (r[cdict.index('period_valid')]))
		if r[cdict.index('is_valid')]:
			is_valid = RES_YN[1][r[cdict.index('is_valid')]][1]
		else:	is_valid = ''	#"ZZZ"
	#	sss.append ("<td> дейст: <b>%s</b></td>" % is_valid)	#RES_YN[1][r[cdict.index('is_valid')]][1])	# r[cdict.index('period_valid')]))
		sss.append ("<td> тип: <b>%s</b></td>" % get_sctype (idb, r[cdict.index('ctype')]))
		sss.append ("<td> сис: <b>%s</b></td>" % get_subsystems (idb, r[cdict.index('bm_ssys')]))
	#	sss.append ("<td> сост: <b>%s</b></td>" % get_cont_stat (idb, r[cdict.index('bm_cstat')]))
		sss.append ("<td><b>%s</b></td>" % get_cont_stat (idb, r[cdict.index('bm_cstat')]))
		sss.append ('</tr>')
	sss.append ('</table>')
	sss.append (sbutt)
#		sss.append ("<b>%s</b> от <b>%s</b> &nbsp; %s" % (r[dct.index('cnum')], r[dct.index('cdate')], sbuttn % r[dct.index('id_contr')],))
	return	"\n".join(sss)

def	get_add_doc (idb, iid_contr, tname, isrow = None):
	""" Показать Доп. соглашения или Наличие актов	"""
	if tname == 'add_acts':
		sbutt =	"""<input type='button' class='butt' value='Создать новый АКТ' onclick="set_shadow('create_new_act&id_contr=%d');">""" % iid_contr
	elif  tname == 'add_consents':
		sbutt = """<input type='button' class='butt' value='Создать новое Доп. соглашение' onclick="set_shadow('create_new_consent&id_contr=%d');">""" % iid_contr
	else:	return	"get_add_doc tname: %s" % tname
	if not isrow:	return	sbutt
	res = idb.get_table (tname, 'id_contr = %d ORDER BY docdate' % iid_contr)
	if not res:	return	sbutt
	cdict = res[0]
	sss = ["<table id='add_doc' width=99% cellspacing=0>"]
	for r in res[1]:
		sss.append ("""<tr class='line' onclick="$('#add_doc tr').removeClass('mark'); $(this).addClass('mark'); $('#bm_cstat').removeClass('mark');"
			ondblclick="set_shadow('out_add_doc&id_contr=%d&stable=%s&id_doc=%d');">
			<td align='right' width=6%%><b> %s </b></td><td width=18%%> &nbsp; от:<b> %s </b></td><td class='bfgrey'>%s</td></tr>""" % (iid_contr, tname, r[0],
			r[cdict.index('docnum')], cglob.out_sfdate (r[cdict.index('docdate')]), r[cdict.index('docteam')]))
	sss.append ("</table>")
	sss.append (sbutt)
	return	"\n".join(sss)

def	get_sbid_type (idb, bm_btype):
	""" Читать (показать) Тип заявки письма	"""
	global	RBBTYPE
	
	if not RBBTYPE:	RBBTYPE = idb.get_table ('bid_type', 'code > 0')
	ibm_btype = int (bm_btype)
	if RBBTYPE:
		for r in RBBTYPE[1]:
			if r[0] == ibm_btype:	return	"<span class='bfgrey'>%s</span>" % r[1]
	return	"QQQ"

def	get_sbid_stat (idb, bm_bstat, tm_alarm = None, slen = None, fix_bstat = 0):
	""" Читать (показать) статус заявки письма	"""
	global	RBBSTAT
	if not RBBSTAT:	RBBSTAT = idb.get_table ('bid_stat', 'code >= 0 ORDER BY code')
	if not (bm_bstat and int (bm_bstat) > 0):	#	return  "<span class='bferr'>%s</span>" % RBBSTAT[1][0][2]
		if fix_bstat & 32768:
			return	"<span class='bfinf'>Ометка [Все ОК]</span>"
		else:	return	"<span class='bferr'>%s</span>" % RBBSTAT[1][0][2]
	ibm_bstat = int (bm_bstat)
	if RBBSTAT:
		sss = []
		for r in RBBSTAT[1]:
			if r[0] & ibm_bstat:	sss.append (r[2])
		if sss:
			sout = "; ".join(sss)
			if slen:
				sout = sout.decode('utf-8')[:slen].encode('utf-8') +'...'
			if (fix_bstat & bm_bstat) or tm_alarm > time.time():
				return	"<span class='bfinf'>%s</span>" % sout	
			else:	return	"<span class='bferr'>%s</span>" % sout
	return	"QQQ"

def	is_valarms (idb, id_org):
	""" Проверить Список событий valarms	"""
	res = idb.get_table ('valarms', "id_org = %d" % id_org, 'count(*)')
	if res:		return	res[1][0][0]

def	get_bids(idb, id_org):
	""" Читать (показать) Входящие заявки письма	"""
	iid_org	= int (id_org)
#	res = idb.get_table ('bids', 'id_org = %s AND tm_close IS NULL ORDER BY biddate, bid_num' % iid_org)	# Скрыть ИСПОЛНЕНО
#	res = idb.get_table ('bids', 'id_org = %s ORDER BY biddate DESC' % iid_org)
	res = idb.get_table ('bids', 'id_org = %s ORDER BY tm_close DESC, tm_creat DESC LIMIT 5' % iid_org)
	if not  res:	return	""
	cdict = res[0]
	sss = ["<table id='bids' width=100% cellspacing=0>"]
	for r in res[1]:
	#	srem = "%d" % ((int(time.time()) - r[cdict.index('tm_alarm')])/3600)
		dth = - ((int(time.time()) - r[cdict.index('tm_alarm')])/3600)
		if r[cdict.index('bm_bstat')] and (r[cdict.index('bm_bstat')] & r[cdict.index('fix_bstat')]) == r[cdict.index('bm_bstat')]:
			srem = "<span class='bfinf'>ИСПОЛНЕНО</span>" 
		elif r[cdict.index('fix_bstat')] & 32768:
		#	srem = "<span class='bfinf'>Все ОК</span>"
			srem = "<span class='bferr'>???</span>"
		elif dth < -24:	# задержка
			srem = "<span class='bferr'>%d дн.</span>" % (-dth/24)
		elif dth < 0:
			srem = "<span class='bferr'>%d ч.</span>" % -dth
		else:	srem = "<span class='bfinf'>%d ч.</span>" % dth
		'''
		if 32768 & r[cdict.index('fix_bstat')]:
			sbid_stat = "<span class='bfinf'>Исполнено</span>"
		else:
		'''
		sbid_stat =  get_sbid_stat (idb, r[cdict.index('bm_bstat')], r[cdict.index('tm_alarm')], 22, fix_bstat=r[cdict.index('fix_bstat')])
		sss.append ("""<tr class='line' onclick="$('#bids tr').removeClass('mark'); $(this).addClass('mark'); $('#contracts tr').removeClass('mark');
			$('#persons tr').removeClass('mark'); $('#wform_result').html('');" ondblclick="set_shadow('out_fbid&id_org=%d&id_bid=%d');">""" % (iid_org, r[cdict.index('id_bid')]))
		sss.append ("<td align='right' class='bfgrey'>%s</td><td>&nbsp;<span class='bfgrey'>%s</span></td><td>%s</td><td>%s</td><td>%s</td></tr>" % (
			r[cdict.index('bid_num')], time.strftime("%d.%m.%y", time.localtime(r[cdict.index('tm_creat')])),
			get_sbid_type (idb, r[cdict.index('bm_btype')]), sbid_stat, srem ))	# get_sbid_stat (idb, r[cdict.index('bm_bstat')], r[cdict.index('tm_alarm')], 45), srem ))
	if sss:	
		sss.append ("</table>")
		return	"\n".join(sss)
	return	str(res)

def	get_persons(idb, id_contr, id_org):
	""" Показать контакты	"""
	sbutt = """<input type='button' class='butt' value='Добавить в контакты' onclick="out_person(%d,%d, 0);" />""" % (id_contr, id_org)
	res = idb.get_table ('persons', "id_persn IN (SELECT id_persn FROM person2x WHERE id_contr=%d OR id_org=%d) ORDER BY family;" % (id_contr, id_org))
	arms = idb.get_table ('arms', 'id_org=%d' % id_org)
	
	if not res and not arms:	return	sbutt
	sss = ["<table id='persons' width=99% cellspacing=0>"]
	if res:
		cdict = res[0]
		for row in res[1]:
			phones = '_'*10 
			family = ''
			email = '_'*20
			post = srem = ''
			if row[cdict.index('phones')]:	phones = row[cdict.index('phones')]
			if row[cdict.index('family')]:	family = row[cdict.index('family')]
			if row[cdict.index('email')]:	email = row[cdict.index('email')]
			if row[cdict.index('post')]:	post = row[cdict.index('post')]
			if row[cdict.index('rem')]:
				if post:	srem = "title='%s %s'" % (post, row[cdict.index('rem')])
				else:		srem = "title='%s'" % row[cdict.index('rem')]
			sss.append ("""<tr class='line' onclick="$('#persons tr').removeClass('mark'); $(this).addClass('mark'); $('#bm_cstat').removeClass('mark'); $('#add_doc tr').removeClass('mark');
				$('#bids tr').removeClass('mark'); $('#wform_result').html('');" ondblclick="out_person(%d,%d,%d);" %s>""" % (id_contr, id_org, row[cdict.index('id_persn')], srem))
			sss.append ("""<td><b>%s %s</b> %s</td><td>т.<b>%s</b> </td><td><i class="fa fa-envelope-o" aria-hidden="true"></i> <b>%s</b></td></td>""" % (family, row[cdict.index('names')], post, phones, email))
	if arms:	# ARMS ['id_arm', 'id_org', 'id_bid', 'id_contr', 'login', 'passwd', 'family', 'pname', 'post', 'phones', 'emails', 'url', 'tm_creat', 'tm_send', 'who_send', 'ps', 'rem', 'dt_creat', 'sn_bid']
		ad = arms[0]
		for ar in arms[1]: 
			family = pname = post = ''
			if ar[ad.index('family')]:	family = ar[ad.index('family')]
			if ar[ad.index('pname')]:	pname = ar[ad.index('pname')]
			if ar[ad.index('post')]:	post = ar[ad.index('post')]
			sss.append ("""<tr class='line bfinf'><td class='bfinf'>%s %s</td><td colspan=2>%s<td>""" % ( pname, family, post ))
	sss.append ("</table>")
	if id_contr or id_org:
		sss.append (sbutt)
	return "\n".join(sss)

RCSTAT =	None	# Буфер хранения результата запроса к 'cont_cstat'	состояние договора
RCTYPE =	None	# Буфер хранения результата запроса к 'cont_type'	тип договора
RSUBSYS =	None	# Буфер хранения результата запроса к 'subsys'
ROPTATT	=	None	# Буфер хранения - дополнительные опции приборов АТТ
RREGION =	None	# Буфер хранения результата запроса к 'region'
RBBTYPE =	None	# Буфер хранения результата запроса к 'bid_type'
RBBSTAT =	None	# Буфер хранения результата запроса к 'bid_stat'

def	get_cont_stat (idb, bm_cstat, fl_all = None):
	""" Читать текуший статус Договора (контракта) <bm_cstat>	"""
	global	RCSTAT

	ibm_cstat = int(bm_cstat)
	if not RCSTAT:	RCSTAT = idb.get_table ('cont_stat', 'bm_type > 0 ORDER BY code')
	if RCSTAT:
		sss = []
		for r in RCSTAT[1]:
			if (ibm_cstat & r[0]):
				if not (ibm_cstat & 1568):	# Закрыт +	1056): Исполняется | Оплачен
					sss.append ("<span class='bferr'>%s</span>" % r[2])
				elif r[0] < 32 or r[0] == 2048:	# 2048 Приостановлен
					sss.append ("<span class='bferr'>%s</span>" % r[2])
				else:	sss.append ("<span class='bfinf'>%s</span>" % r[2])
		if sss:
			if fl_all:
				return	" + ".join(sss)
			return	sss[len(sss) -1]
		else:	return	"<span class='bferr'>%s</span>" % RCSTAT[1][0][2]
		'''
			if ibm_cstat == r[0]:	break
		if r[0] < 16:
			return	"<span class='bferr'>%s</span>" % r[2]
		else:	return  "<span class='bfinf'>%s</span>" % r[2]
		'''
	return	'ZZZ'
'''
def	set_cont_stat (idb, bm_cstat, ctype, id_contr):
	""" Установить (изменить) текуший статус Договора (контракта) <bm_cstat>	"""
	global	RCSTAT

	if not ctype:	ctype = 1
#	RCSTAT = idb.get_table ('cont_stat', 'bm_type & %d > 0 ORDER BY code' % ctype)
	RCSTAT = idb.get_table ('cont_stat', 'code > %d AND bm_type & %d > 0 ORDER BY code' % (int(bm_cstat/4), ctype))
	return	cglob.out_select('bm_cstat', RCSTAT, ['code', 'sname'], key=bm_cstat, sopt = """onchange="set_shadow('set_bm_cstat&id_contr=%d');" """ % id_contr)
'''
def	get_sctype (idb, ctype, fs = None):
	""" Читать тип Договора (контракта) <ctype>
	fs != None	- читать полное наименование	"""
	global	RCTYPE

	if not ctype:	return	''
	ictype = int(ctype)
	if not RCTYPE:	RCTYPE = idb.get_table ('cont_type')
	if RCTYPE:
		ss = []
		for r in RCTYPE[1]:
			if r[0] & ictype:
				if fs:	ss.append (r[2])
				else:	ss.append (r[1])
		sctype = "/".join(ss)
	return	sctype

def	set_ctype (idb, ctype, id_contr):
	""" Установить (изменить) тип Договора (контракта) <ctype>	"""
	global	RCTYPE

	if ctype:	ictype = int(ctype)
	else:		ictype = 0
	RCTYPE = idb.get_table ('cont_type')
	return	cglob.out_select('ctype', RCTYPE, ['cod', 'tname'], ictype, sopt = """onchange="set_shadow('set_ctype&id_contr=%d');" """ % id_contr)

def	set_subsystem (idb, bm_ssys, id_contr):
	""" Установить (изменить) подсистему РНИЦ <bm_ssys>	"""
	global	RSUBSYS

	if bm_ssys:	ibm_ssys = int(bm_ssys)
	else:		ibm_ssys = 0
	RSUBSYS = idb.get_table ('subsys', 'code > 0 ORDER BY code')
	return	cglob.out_select('bm_ssys', RSUBSYS, ['code', 'ssname'], key=ibm_ssys, sopt = """onchange="set_shadow('set_bm_ssys&id_contr=%d');" """ % id_contr)

def	get_subsystems (idb, bm_ssys, fs = None):
	""" Читать наименование подсистем <subsys>
	fs    - наименование поля (label, ssname, pnc_labl, rnc_name) для отображения
		по умолчарию label	"""
	global	RSUBSYS
	if not bm_ssys:	return	''
	ibm_ssys = int(bm_ssys)
	if not ibm_ssys:	return "ZZZ"
	if not RSUBSYS:	RSUBSYS = idb.get_table ('subsys', 'code >= 0 ORDER BY code')
	if RSUBSYS:
		ss = []
		ds = RSUBSYS[0]
	#	if not fs or (not fs in ds):		fs = 'label'
		if not fs in ds:	fs = 'label'
		for r in RSUBSYS[1]:
			if r[0] & ibm_ssys:
				ss.append (r[ds.index(fs)])
		sbm_ssys = " / ".join(ss)
	return	sbm_ssys

def	get_options_att(idb, bm_options, fs = None):
	""" Дополнительные опции приборов АТТ	"""
	global	ROPTATT
	if not bm_options:	return	'None'
	ibm_options = int(bm_options)
	if not ROPTATT: ROPTATT = idb.get_table ('options_att')
	if ROPTATT:
		ss = []
		ds = ROPTATT[0]
		if not fs in ds:	fs = 'oname'
		for r in ROPTATT[1]:
			if r[0] & ibm_options:
				ss.append (r[ds.index(fs)])
		if ss:	return	" / ".join(ss)
	return	"QQQ"
#	update transports SET id_org = 459 WHERE bm_ssys = 4096;
#	update transports SET gosnum = garnum  WHERE gosnum LIKE '19913035%';

def	td_gosnum (idb, gosnum):
	""" Визуализация gosnum	"""
	query =	"SELECT t.gosnum, a.last_date FROM transports t LEFT JOIN atts AS a ON t.device_id = a.device_id WHERE gosnum = '%s' ORDER BY a.last_date DESC" % gosnum
	row = idb.get_dict(query)
	if row:
		if not row['last_date']:
			return 0, "<td bgcolor=#ff9999 title='Данных не поступало'><b>%s</b></td>" % gosnum
		else:
			ttms = time.mktime(time.strptime(str(row['last_date'])[:16], "%Y-%m-%d %H:%M"))
			dtm = int(time.time() - ttms)
			if dtm < 5*86400:
				return dtm, "<td bgcolor=#bbeebb title='%s'><b>%s</b></td>" % (time.strftime("%H:%M %d.%m.%y", time.localtime(ttms)), gosnum)
			elif dtm > 30*86400:
				return dtm, "<td bgcolor=#ffbbaa title='%s'><b>%s</b></td>" % (time.strftime("%H:%M %d.%m.%y", time.localtime(ttms)), gosnum)
			else:	return dtm, "<td bgcolor=#eeeebb title='%s'><b>%s</b></td>" % (time.strftime("%H:%M %d.%m.%y", time.localtime(ttms)), gosnum)
	else:	return -1, "<td bgcolor=#ffffff title='Нет навигатора'><b>%s</b></td>" % gosnum

def	out_transports(idb, iid_org, id_reg = 0, bl_mail = None):
	""" Показвть список транспрота	"""
	sbutt_add = """<input type='button' class='butt' value='Добавить Машины' onclick="win_open('transport', '&stat=add&id_org=%d');" title='Новый' />""" % iid_org
	sbutt_find = """<input type='button' class='butt' value='Найти Машины' onclick="win_open('transport', '&stat=find&id_org=%d');" title='Новый' />""" % iid_org
	res = idb.get_table ('vtransports', "id_org = %d ORDER BY region, gosnum" % iid_org)
	ress = "ZZZ"
	shead = "shead".upper()
	dtm_ndata = dtm_natt = dtm_nd10 = 0
	if res:
		sss = ["<div style='max-height: 140px; overflow: auto;'><table border=0 cellpadding=2 cellspacing=0><tr>"]
		di = res[0]
	#	jreg = 0
		j = 0
		for r in res[1]:
	#		if id_reg != r[di.index('region')]:		jreg = r[di.index('region')]
			if r[di.index('bm_status')] >= 2048 and r[di.index('bm_status')] < 4096:	continue	# IS DELETED
			if j and not j % 8:	sss.append ("</tr>\n<tr>")
			j += 1
			
			if r[di.index('bm_status')] >= 4096:		# Is E-mail BLOCKED 
				sss.append ("<td bgcolor=#bbbbff title='%s'><b>%s</b></td>" % ("Блок. E-mail", r[di.index('gosnum')]))
				continue
			elif r[di.index('bm_status')] >= 1024:		# Is BLOCKED
				sss.append ("<td bgcolor=#cccccc title='%s'><b>%s</b></td>" % ("Блокирована", r[di.index('gosnum')]))
				continue
			dtm, std = td_gosnum (idb, r[di.index('gosnum')])
			sss.append (std)
			if dtm < 0:		dtm_natt += 1
			elif dtm == 0:		dtm_ndata += 1	# нет данных
			elif dtm > DAYS*86400:	dtm_nd10 += 1
		sss.append ("</tr></table></div>")
		ress = ''.join(sss)
	
		shead = ["<span class='bfinf'>Всего: %d.</span> " %j]
		if dtm_nd10 > 0 or dtm_ndata > 0:
#			shead += "<span class='bferr'>Нет данных %d дней от %d машин (%d/%d).</span> " % (days, dtm_nd10, dtm_ndata, dtm_natt)
			shead.append ("<span class='bferr' title=' Нет данных %d дней %d маш.\n Данных не поступало %d маш.\n Нет навигаторов %d маш.'>Нет данных.</span> " % (DAYS, dtm_nd10, dtm_ndata, dtm_natt))
			if not bl_mail:
				shead.append (check_mail_to (idb, iid_org, DAYS))
			else:	shead.append ("<span class='bfgrey'>Уведомления БЛОКИРОВАНЫ</span>")
		return	" ".join(shead), ress
	else:	return	" &nbsp; ".join (["<span class='bferr'>Нет машин</span>", sbutt_add, sbutt_find]), ""

def	check_mail_to (idb, iid_org, days):
	""" Отправить Уведомление об отсутствии данных от машин	"""
	res = idb.get_dict("SELECT *, EXTRACT(EPOCH FROM date_send) AS dsek FROM vmail_to WHERE id_org = %d ORDER BY date_send DESC LIMIT 1" % iid_org)
	if res:
	#	ustr = """<span class='bfinf line' onclick="$('# ALL ???').removeClass('mark'); $(this).addClass('mark'); set_shadow('view_mail_to&id_mail=%d')">Уведомление от: %s.</span> """ % (res['id_mail'], time.strftime('%d-%m-%y', time.localtime(res['dsek'])))
		ustr = """<span class='bfinf line' onclick="$(this).addClass('mark'); set_shadow('view_mail_to&id_mail=%d')">Уведомление от: %s.</span> """ % (res['id_mail'], time.strftime('%d-%m-%y', time.localtime(res['dsek'])))
		if res['date_ack']:
			ustr += "<span id='is_ack' class='bfinf'>Ответ от: %s</span> " % cglob.out_sfdate(res['date_ack'], "%d-%m-%y")
		else:	ustr += """<span id='is_ack' class='bfinf'><input type='button' class='butt' value='Пришел ответ' 
				onclick="if (confirm ('Пришел ответ на Уведомление?')) {set_shadow('get_ack&id_org=%d&id_mail=%d');}" /></span>""" % (iid_org, res['id_mail'])
		if time.time() -res['dsek'] < days*86400:	### DEBUG
			return 	ustr
		else:	return	"""%s <input type='button' class='butt' value='Повторить Уведомление' onclick="if (confirm ('Повторить Уведомление?')) {set_shadow('send_mail_to&id_org=%d');}" />""" % (ustr, iid_org)
	else:
		return	"""<input type='button' class='butt' value='Отправить Уведомление' onclick="if (confirm ('Отправить Уведомление?')) {set_shadow('send_mail_to&id_org=%d');}" />""" % iid_org

finds_mail_list = {}
control_sdate = time.strftime("%Y-%m-%d", time.localtime(time.time() -DAYS*86400))

def	finds_mail (idb, id_org):
	""" Поиск отправленной ранее почты	"""
	global	finds_mail_list
	query = "SELECT a.id_org, a.id_mail, a.date_send, a.date_ack FROM mail_to AS a WHERE a.id_mail IN (SELECT b.id_mail FROM mail_to AS b WHERE b.id_org = a.id_org ORDER BY b.date_send DESC LIMIT 1) ORDER BY a.id_org DESC, a.id_mail DESC;"
	if not finds_mail_list:
		rows = idb.get_rows(query)
		for r in rows:
			finds_mail_list[r[0]] = r[2:]
	if id_org in finds_mail_list.keys():
		jstate = cglob.out_sfdate (str (finds_mail_list[id_org][0]), "%Y-%m-%d")
		tits = ["Отпр.: %s" % cglob.out_sfdate (str (finds_mail_list[id_org][0]))]
		if finds_mail_list[id_org][1]:
			tits.append(" ответ: %s" % cglob.out_sfdate (str(finds_mail_list[id_org][1])))
			src = "mail_open.svg"
		elif control_sdate > jstate:
			src = "mail_noop.svg"
		else:	src = "mail.svg"
	#	src += str (finds_mail_list[id_org][0])
		return "<img src='../img/%s' title='%s'>" % (src, ",".join(tits))
		return "Y", finds_mail_list[id_org]
	else:	return "&nbsp;"

def	out_table (SS, idb, tname, res, dtbl = None):
	""" Показать таблицу <tname> по результату чтения <res>
	dtbl != None	- описание параметров отображения	"""
	corder = SS.get_key('orderby')
	if corder:
		ssorder = corder.split()
		if len(ssorder) == 2:
			imark = '<i class="fa fa-arrow-up" aria-hidden="true"></i> '	#"<img src='../img/toggle-up.png'>"
		else:	imark = '<i class="fa fa-arrow-down" aria-hidden="true"></i> '	#"<img src='../img/toggle-down.png'>"
		corder = ssorder[0]
	else:
		imark = ''
		ssorder = "XXX"
#	print	"out_table:", tname, corder, ssorder	#SS.get_key('orderby')
#	cglob.ppobj(SS.objpkl)
	if not dtbl:	dtbl = {}
	if not dtbl.has_key('order'):	dtbl['order'] = res[0]
	if not dtbl.has_key('thead'):	dtbl['thead'] = {}
	if dtbl.has_key('key') and dtbl['key']:
		pkname = dtbl['key']
	else:	pkname = dtbl['order'][0]
	ixkey = res[0].index(pkname)
#	cglob.ppobj(dtbl)
	print "<div id='div_table' style=' height: 430px; overflow: auto;'><table id='%s' width=100%%>" % tname
	ixcols = []
	print "<thead style='width: 100%; position: inherit; top: 10px;' ><tr>"
	for cnm in dtbl['order']:
		ixcols.append (res[0].index(cnm))
		if cnm == 'rem':
			if corder == cnm:
				print "<th id='rem' style='width: 20%%'>%sПримечания</th>" % imark,
			else:	print "<th id='rem' style='width: 20%'>Примечания</th>",
		elif cnm == 'rname':
			if corder == cnm:
				print "<th id='rname' style='width: 12%%'>%sРайон</th>" % imark,
			else:	print "<th id='rname' style='width: 12%'>Район</th>",
		elif cnm == 'bm_ssys':
			if corder == cnm:
				print "<th id='bm_ssys'>%sПодсистема</th>" % imark,
			else:	print "<th id='bm_ssys'>Подсистема</th>",
		else:
			if dtbl['thead'].has_key(cnm):
				colname = dtbl['thead'][cnm]
			else:	colname = cnm.upper()
			if corder == cnm:
				print "<th id='%s'>%s%s</th>" % (cnm, imark, colname) ,
			else:	print "<th id='%s'>%s</th>" % (cnm, colname) ,
	print "</tr>"
	print "</thead>"
	print "<tbody>"
	dr = res[0]
	if res[1]:
		jline = 0
		for r in res[1]:
			if jline % 2:
				bgcolor = "bgcolor=#ddddee"
			else:	bgcolor = ""
			jline += 1
			if type(r[ixkey]) == type(1):	# IntType:
				print "<tr id='%05d' class='line' %s>" % (r[ixkey], bgcolor)
			else:	print "<tr id='%s' class='line' %s>" % (r[ixkey], bgcolor)
			for j in ixcols:	# Форматы колонок таблиц: "<td> содержимое колонки </td>"
				if dr[j] == 'bl_mail':
					if r[j] > 0:
						print "<td><img src='../img/mail_block.svg' title='Блокировка'></td>",
					else:	print "<td>", finds_mail (idb, r[dr.index('id_org')]),"</td>",
					continue
				if dr[j] == 'id_mail':
					if r[j] > 0:
						print "<td>", finds_mail (idb, r[dr.index('id_org')]),"</td>",
					else:	print "<td>&nbsp;</td>",
					continue
				if dr[j] == 'bm_wtime':
					wt_mask = 2**DAYS -1	# 0x03ff
					if r[dr.index('bm_wtime')]:
						jwt = wt_mask & r[dr.index('bm_wtime')]
					else:	jwt = 0
					jwts = []
				#	jwts.append(str(jwt))
					if jwt == wt_mask:	jwts.append("<img src='../img/pix_gw.gif' width='%d' height='11'>" % (11*DAYS))
					else:
						for j in xrange(DAYS,0,-1):
							if jwt == 0:
								jwts.append("<img src='../img/pix_mg.gif' width='%d' height='11'>" % (11*j))
								break
							if jwt & 512:
								jwts.append("<img src='../img/pix_gw.gif' width='11' height='11'>")
							else:	jwts.append("<img src='../img/pix_gr.gif' width='11' height='11'>")
							jwt = int(jwt*2) & wt_mask
					print "<td align='center'>%s</td>" % ''.join(jwts)
					continue
				if dr[j] == 'who_name':
					if r[j]:
						whos = r[j].split()
						if len(whos) == 1:
							sout = whos[0]
						if len(whos) == 2:
							sout = '%s.%s' % (whos[0].decode('utf-8')[:1].encode('utf-8'), whos[1])
						elif len(whos) == 3:
							sout = '%s.%s.%s' % (whos[0].decode('utf-8')[:1].encode('utf-8'), whos[1].decode('utf-8')[:1].encode('utf-8'), whos[2])
					else:	sout = 'NOT' 
					print "<td '>%s</td>" % sout
					continue

				if dr[j] == 'bid':	# заявка на Сервисные работы tm_creat
					bid_tm_creat, sout = check_bid (idb, r, dr)
					print "<td '>%s</td>" % sout
					continue
				if dr[j] == 'tm_creat':
					if 'bid' in dr: 
						if bid_tm_creat:
							sout = time.strftime('%d-%m-%y', time.localtime(bid_tm_creat))
						else:	sout = ''
						print "<td '>%s</td>" % sout
						continue
				
				if r[j] != None:
					if dr[j] == 'ctype':		sout = get_sctype (idb, r[j])
					elif dr[j] == 'bm_ssys':	sout = get_subsystems (idb, r[j])
					elif dr[j] == 'bm_cstat':	sout = get_cont_stat (idb, r[j])
					elif dr[j] == 'bm_bstat':	sout = get_sbid_stat (idb, r[j], r[dr.index('tm_alarm')], fix_bstat = r[dr.index('fix_bstat')])
					elif dr[j] == 'bm_status':	sout = outtd_bm_status(r[j])		# Статус ТС
					elif dr[j] in dicts.SFDATE:	sout = cglob.out_sfdate(r[j], '%d-%m-%y')
					elif dr[j] in SFDATE:		sout = cglob.out_sfdate(r[j])
					elif dr[j][:3] == 'tm_' and r[j]:
						sout = time.strftime('%d-%m-%y', time.localtime(r[j]))
					elif dr[j] == 'logdate':
						jsss = str(r[j])
						sout = jsss[2:19]
					else:	sout = r[j]
				else:	sout = ''	#dr[j]	#''
				print "<td>", sout, "</td>",
			print	"</tr>"
	print "</tbody>"
	print "</table></div>"
	if dtbl.has_key('functs'):
		print	"<script language='JavaScript'>"
		if dtbl['functs'].has_key('mark'):
			print	"""$('#%s tr.line').hover (function () { $('#%s tr').removeClass('mark'); $(this).addClass('mark'); $('#shadow').text('')})
			.click (function (e) { $('#%s tr').removeClass('mark'); $(this).addClass('mark');
			$.ajax ({data: 'shstat=mark_row&table=%s&pkname=%s&idrow=' +$(this).get(0).id +'&X=' +e.clientX +'&Y=' +e.clientY +'&' +$('form').serialize() }); });""" % (
					tname, tname, tname, tname, pkname)
		for cnm in dtbl['order']:
			print "$('#%s').dblclick	(function () {set_order('%s')});" % (cnm, cnm)
		print	"</script>"

def	check_bid (idb, r, dr):
	""" Контроль заявки на Сервисные работы	"""
	drow = idb.get_dict("SELECT * FROM bids WHERE id_org = %d AND rem LIKE '%%%s%%' LIMIT 1" % (r[dr.index('id_org')], r[dr.index('gosnum')]))
	if not drow:
		return None, ''
	return	drow['tm_creat'], drow['bid_num']

def	outtd_bm_status(jbm):
	""" Показать Статус ТС	"""
	if jbm == 0:		return	" "
	if jbm & 2048:		return	"<span class='bferr'>Удалена</span>"
	bm_status = {2: "1C", 4: "K", 8: "D", 16: "+C"}
	ls = []
	for k in [2, 4, 8 ,16]:
		if jbm & k:	ls.append (bm_status[k])
	if jbm & 4096:		ls.append ("<span class='bferr'>@</span>")
	if jbm & 1024:		ls.append ("<span class='bferr'>Блк</span>")
	if ls:	return	"; ".join(ls)
	else:	return	str(jbm)

def	ttt(SS, request):
	global	RCSTAT
	global	RCTYPE
	global	RSUBSYS
	global	RREGION

	idb = dbtools.dbtools (CDB_DESC)	#"host=127.0.0.1 dbname=contracts port=5432 user=smirnov", 1)
	where_list = []
	if request:
		if request.has_key('set_table'):
			tname = request['set_table']
		else:	tname = 'vorganizations'	#'vcontracts'
		if request.has_key('where_region') and not tname in ['persons', 'history', 'vhistory']:
			region = int(request['where_region'])
			where_list.append ("region = %d" % region)
		else:	region = None
		if request.has_key('where_subsys') and not tname in ['vpersons', 'vbids', 'vhistory', 'vmail_to']:
			subsys = int(request['where_subsys'])
			if subsys == 0:
				where_list.append ("bm_ssys = 0")
			else:	where_list.append ("bm_ssys & %d > 0" % subsys)
		else:	subsys = None
		if tname == 'wtransports' and request.has_key('where_attmark'):
			where_list.append ("amark = '%s'" % request['where_attmark'])
		if tname == 'wtransports' and request.has_key('where_attwork'):
			if request['where_attwork'] == '0':
				where_list.append ("bm_wtime & 1023 > 0")
			elif request['where_attwork'] == '1':
				where_list.append ("bm_wtime & 1023 = 0")
			elif request['where_attwork'] == '2':
				where_list.append ("bm_wtime & 512 > 0")
		if tname == 'wtransports':
			ts_status = 0
			if request.has_key('where_ts_status_1024'):		ts_status += 1024
			if request.has_key('where_ts_status_2048'):		ts_status += 2048
			if ts_status > 0:
				where_list.append("bm_status & %d = 0" % (3072 ^ ts_status))
			else:	where_list.append("bm_status & 3072 = 0")

		if tname == 'vcontracts' and request.has_key('where_ctype'):
			ctype = int(request['where_ctype'])
			where_list.append ("ctype & %d > 0" % ctype)
		elif tname == 'vbids':
			bid_stat = None
			if request.has_key('where_bid_type'):
				bid_type = int(request['where_bid_type'])
				where_list.append ('bm_btype = %s' % bid_type)
			if request.has_key('where_bid_stat'):
				bid_stat = int(request['where_bid_stat'])
				where_list.append ('bm_bstat & %d > 0' % bid_stat)
			if request.has_key('where_close'):
				where_close = int(request['where_close'])
			else:	where_close = 0
			if where_close == 1:
				where_list.append ('tm_close IS NOT NULL')
			if where_close == 0:
				if not bid_stat or bid_stat != 32768:
					where_list.append ('tm_close IS NULL')
		elif tname == 'vhistory':
			if request.has_key('his_org') and request['his_org'].isdigit():
				where_list.append ('id_org=%s' % request['his_org'])
			if request.has_key('his_contr') and request['his_contr'].isdigit():
				where_list.append ('id_contr=%s' % request['his_contr'])
		else:	ctype = None
	else:
		tname = 'vcontracts'
		subsys = None
		region = None
		ctype = None
	print "<div class='box' style='background-color: #dde;'><table width=100%><tr><td width=14%><span class='tit'>&nbsp; ", DICT_TABS[tname]['title'], "</span>"	#, tname
#	vpersons,  history,  vbids
	where_region = where_subsys = ''
	if tname == 'vhistory':		# HISTORY
		import	rusers
		USER = SS.get_key('USER')
		his_org = his_contr = ''
		if request.has_key('his_org') and request['his_org'].isdigit():
			his_org = request['his_org']
		if request.has_key('his_contr') and request['his_contr'].isdigit():
			his_contr = request['his_contr']
		RUSERS = rusers.get_table('rusers', 'user_id != 2 ORDER BY uname', 'user_id, uname, ufam')
#		print RUSERS[0]
		if request.has_key('his_usid') and request['his_usid'].isdigit():
			his_usid = int(request['his_usid'])
			where_list.append ("who_id = %s" % request['his_usid'])
		else:
			his_usid = 0
	#		his_usid = USER['user_id']	#None
		print "<td>Правил:"
		cglob.out_select('his_usid', RUSERS, key = his_usid, sopt = """ onchange="document.myForm.submit();" """, sfirst = "<option value=''> Все </option>")
		print """
			&nbsp;id_ORG:<input id='his_org' type='text' name='his_org' size=3 value='%s' maxlength=5 />
			&nbsp;id_CONTR:<input id='his_contr' type='text' name='his_contr' size=3 value='%s' maxlength=5 />
			""" % (his_org, his_contr)
		print "</td>"
		if (request.has_key('his_begin')):
			his_begin = request['his_begin']
			where_list.append ("logdate <= '%s 23:59:59'" % cglob.sfdate(his_begin))	
		else:	his_begin = ''
		if (request.has_key('his_end')):
			his_end = request['his_end']
			where_list.append ("logdate > '%s 00:00:00'" % cglob.sfdate(his_end))
		else:	his_end = ''
		print """<td> по: <input id='his_begin' type='text' name='his_begin' size=5 value='%s' maxlength=8 class='date' />
			&nbsp; c: <input id='his_end' type='text' name='his_end' size=5 value='%s' maxlength=8 class='date' /><td>""" % (his_begin, his_end)
#		his_limit = request['his_limit'] if (request.has_key('his_limit')) else '300'
#		print "<td>Limit: <input id='his_limit' type='text' name='his_limit' size=3 value='%s' maxlength=4 /></td>" % his_limit
	else:
		print "<td>Район:"
		RREGION = idb.get_table ('region', "id >= 0 ORDER BY rname")	#, 'id > 0')
		cglob.out_select('where_region', RREGION, ['id', 'rname'], key = region, sopt = """ onchange="document.myForm.submit();" """, sfirst = "<option value=''> Все </option>")
		print "</td>"
		if tname in ['vcontracts', 'vorganizations', 'vtransports', 'wtransports', 'voatts']:	#, 'wtransports']:
			print "<td>Подсистема:"
			RSUBSYS = idb.get_table ('subsys', 'code >= 0 ORDER BY code')
			ssopt = """ onchange="document.myForm.submit();" """
			cglob.out_select('where_subsys', RSUBSYS, ['code', 'label'], key = subsys, sopt = ssopt, sfirst = "<option value=''> Все </option>")
			print "</td>"
	
	where_gosnum = where_marka = where_uin = ''
	if tname == 'vorganizations':	pass
	elif tname == 'vmail_to':
		if (request.has_key('mail_beg')):
			mail_beg = request['mail_beg']
			where_list.append ("date_send <= '%s'" % cglob.sfdate(mail_beg))
		else:	mail_beg = ''
		if (request.has_key('mail_end')):
			mail_end = request['mail_end']
			where_list.append ("date_send > '%s'" % cglob.sfdate(mail_end))
		else:	mail_end = ''
		# WHERE a.id_mail IN (SELECT b.id_mail FROM mail_to AS b WHERE b.id_org = a.id_org ORDER BY b.date_send DESC LIMIT 1) ORDER BY a.id_org DESC, a.id_mail DESC
		'''
		if not (mail_end and mail_beg):
			dicts.CONTRCT["vmail_to AS a"] = dicts.CONTRCT['vmail_to']
			tname = "vmail_to AS a"
			orderby = ""
			where_list.append ("a.id_mail IN (SELECT b.id_mail FROM mail_to AS b WHERE b.id_org = a.id_org ORDER BY b.date_send DESC LIMIT 1) ORDER BY a.id_org DESC, a.id_mail DESC")
		'''
		print """<td> c: <input id='mail_beg' type='text' name='mail_beg' size=5 value='%s' maxlength=8 class='date' />
			&nbsp; по:: <input id='mail_end' type='text' name='mail_end' size=5 value='%s' maxlength=8 class='date' /><td>""" % (mail_beg, mail_end)
	elif tname == 'vbids':
		print "<td>Тип:"
		if request.has_key('where_bid_type'):
			bid_type = int(request['where_bid_type'])
		else:	bid_type = None
	#	print "bid_type", bid_type
		rtbids = idb.get_table ('bid_type')
		cglob.out_select('where_bid_type', rtbids, ['code', 'bname'], key = bid_type, sopt = """ onchange="document.myForm.submit();" """, sfirst = ' ')
		if not ( bid_type and bid_type > 0):	bid_type = 0x7fff
		print "&nbsp;Статус:"
		rsbids = idb.get_table ('bid_stat', '(bm_btype & %d) > 0 AND code > 0 ORDER BY sname DESC' % bid_type)
		if request.has_key('where_bid_stat'):
			bid_stat = int(request['where_bid_stat'])
		else:	bid_stat = None
		cglob.out_select('where_bid_stat', rsbids, ['code', 'sname'], key = bid_stat, sopt = """ onchange="document.myForm.submit();" """, sfirst = ' ')
#		else:	print "&nbsp;Статус исполнения"
		if request.has_key('where_close'):
			bid_close = int(request['where_close'])
		else:	bid_close = 0 
		cglob.out_select('where_close', RES_BIDS, key = bid_close, sopt = """ onchange="document.myForm.submit();" """)
		print "</td>"
	elif tname == 'vcontracts':
		print "<td>Тип договора:"
		RCTYPE = idb.get_table ('cont_type')
		ssopt = """ onchange="document.myForm.submit();" """
		cglob.out_select('where_ctype', RCTYPE, ['cod', 'label'], key = ctype, sopt = ssopt, sfirst = ' ')
		print "</td>"
		if request.has_key('where_bm_cstat'):
			bm_cstat = int(request['where_bm_cstat'])
		else:	bm_cstat = None
		if bm_cstat:
			if SS.objpkl.has_key('is_cstat') and SS.objpkl['is_cstat'] == "N":
				where_list.append ('bm_cstat & %d = 0' % bm_cstat)
			else:	where_list.append ('bm_cstat & %d > 0' % bm_cstat)
		#	where_list.append ('bm_cstat & %d > 0 AND bm_cstat <= %d' % (bm_cstat, bm_cstat))
		else:	where_list.append ('id_contr > 0 AND bm_cstat < 65536')
		print "<td>Статус:"
		RCSTAT = idb.get_table ('cont_stat', "code >= 0 ORDER BY code")
		cglob.out_select('where_bm_cstat', RCSTAT, ['code', 'sname'], key = bm_cstat, sopt = """ onchange="document.myForm.submit();" """)
		if SS.objpkl.has_key('is_cstat') and SS.objpkl['is_cstat'] == "N":
			print	"""<input name='win_view' type='button' class='butt' value='N' title='Статус NOT' onclick="set_shadow('sset_is_cstat');" />"""
		else:	print	"""<input name='win_view' type='button' class='butt' value='&' title='Статус AND' onclick="set_shadow('sset_is_cstat');" />"""
		print "</td>"
	elif tname in ['vtransports', 'wtransports']:
		if request.has_key('where_gosnum'):
			where_gosnum = request['where_gosnum'].strip()
			where_list.append ("gosnum LIKE '%%%s%%'" % where_gosnum)
		print "<td>Гос.№:"
		print "<input type='text' name='where_gosnum' value='%s' size=6 />" % where_gosnum
		print "</td>"
		if tname == 'vtransports':
			if request.has_key('where_marka'):
				where_marka = request['where_marka'].strip()
				where_list.append ("marka LIKE '%%%s%%'" % where_marka)
			print "<td>Марка:"
			print "<input type='text' name='where_marka' value='%s' size=10 />" % where_marka
		elif tname == 'wtransports':
			print "<td>Прибор:"
			if request.has_key('where_attmark'):
				where_attmark = request ['where_attmark']
			else:	where_attmark = ""
			RCAMARK = idb.get_table ('wtransports', "amark IS NOT NULL ORDER BY mname", "DISTINCT amark, amark AS mname")
			cglob.out_select ('where_attmark', RCAMARK, key = where_attmark, sopt = """ onchange="document.myForm.submit();" """, sfirst = ' ')
			print "<td>Работа:"
			if request.has_key('where_attwork') and request ['where_attwork'].isdigit():
				where_attwork = int(request ['where_attwork'])
			else:	where_attwork = None
			cglob.out_select ('where_attwork', RES_YNC, key = where_attwork, sopt = """ onchange="document.myForm.submit();" """, sfirst = ' ')
	#		print "<td>Стат:"
			if request.has_key('where_ts_status_1024'):
				print """<input type='checkbox' title='Скрыть Блкокированные ТС' name='where_ts_status_1024' checked><b></b>"""
			else:	print """<input type='checkbox' title='Показать Блкокированные ТС' name='where_ts_status_1024'>"""
			if request.has_key('where_ts_status_2048'):
				print """<input type='checkbox' title='Скрыть Удаленные ТС' name='where_ts_status_2048' checked><b></b>"""
			else:	print """<input type='checkbox' title='Показать Удаленные ТС' name='where_ts_status_2048'>"""
			'''
			print request['where_ts_status_1024']
			if request.has_key('where_attstat') and request ['where_attstat'].isdigit():
				where_attstat = int(request ['where_attstat'])
			else:	where_attstat = None
			cglob.out_select ('where_attstat', RES_YN, key = where_attstat, sopt = """ onchange="document.myForm.submit();" """, sfirst = ' ')
			'''
		print "</td>"

	elif tname == 'voatts':	#	VOATTS
		if request.has_key('where_gosnum'):
			where_gosnum = request['where_gosnum'].strip()
			where_list.append ("gosnum LIKE '%%%s%%'" % where_gosnum)
		if request.has_key('where_uin'):
			where_uin = request['where_uin'].strip()
			where_list.append ("uin LIKE '%s%%'" % where_uin)
		print "<td>Гос.№:"
		print "<input type='text' name='where_gosnum' value='%s' size=6 />" % where_gosnum
		print "</td>"
		print "<td>UIN:"
		print "<input type='text' name='where_uin' value='%s' size=10 />" % where_uin
		print "</td>"
	else:	#pass
		print "<td>:", tname.upper(), "</td>"

#	if tname not in ['wtransports', 'vtransports', 'voatts', 'vbids']:
	if tname in ['vcontracts', 'vorganizations', ]:
		print "<td align=right>Создать:"
		print	"""<input type='button' class='butt' value='Договор' onclick="win_open('new_contr', '');" title='Новый' />""",
		print	"""<input type='button' class='butt' value='Организация' onclick="win_open('new_org', '');" title='Новая' />""",
		print '</td>'
	print "<td align='right'>Смотрим:"
#	print 	RES_TABS[2]	#.append(('varms', 'АРМ Авторизация'))	#, ('vhistory', 'История измененмй БД')
	cglob.out_select('set_table', RES_TABS, key = tname, sopt = """ onchange="document.myForm.submit();" """)
	print '</td>'
	print "</tr></table></div>"
	if request.has_key('orderby') and request['orderby'] in DICT_TABS[tname]['order']:
		if SS.get_key('orderby') == request['orderby']:
		#	SS.del_key('orderby')
			SS.set_obj('orderby', "%s DESC" % request['orderby'])
			orderby = " ORDER BY %s DESC" % request['orderby']
		else:
			SS.set_obj('orderby', request['orderby'])
			orderby = " ORDER BY %s" % request['orderby']
	elif DICT_TABS[tname].has_key('orderby'):
		SS.del_key('orderby')
		orderby = " ORDER BY %s" % DICT_TABS[tname]['orderby']
	else:
		orderby = ''
	if where_list:
		wheres = ' AND '.join(where_list) +orderby
	else:
		if orderby:	wheres = '1=1 %s' % orderby
		else:		wheres = None
#	print	"WHEREs:", wheres, orderby
#	print "where_list:", where_list
#	cglob.ppobj (DICT_TABS[tname])
	res = idb.get_table (tname, wheres)
	if res:
#		print res[0], "where_list", where_list
		out_table(SS, idb, tname, res, DICT_TABS[tname])
		print """<span class='bfinf'>найдено %d записей</span>""" % len(res[1])
	else:
		out_table(SS, idb, tname, (idb.desc, None), DICT_TABS[tname])
		print """<span class='bferr'>Данных НЕТ</span> """, tname.upper(), 'WHERE', wheres

def	perror (tit = None, txt = None):
	if not tit:	tit = ''
	print	"<div class='error'><b>%s</b> %s</div>" % (str(tit), str(txt))

def	main (SS, request):
	try:
	#	print "<a href='' onclick=\"window.open ('index.cgi?this=jnew_calls', 'jnew_calls', 'scrollbars=yes').focus(); return false;\"  ><b>Журнал вызовов</b></a>"
	#	print	request
	#	print "<input type='text' class='date'  />"
		ttt(SS, request)
	#	cglob.ppobj(SS.objpkl)
		USER = SS.get_key('USER')
		ssystem = SS.get_key('subsystem')
	except:
		exc_type, exc_value = sys.exc_info()[:2]
		perror ("EXCEPT conract", " ".join(["<pre>", str(exc_type).replace('<', '# '), str(exc_value), "</pre>"]))
