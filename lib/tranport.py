# -*- coding: utf-8 -*-

import	cgi, os, sys, time, string

LIBRARY_DIR = r"/home/smirnov/MyTests/CGI/lib/"
sys.path.insert(0, LIBRARY_DIR)
CONFIG = None

import	dbtools
import	session
import	cglob

CDB_DESC = cglob.get_CDB_DESC('ZZZ')	#"host=127.0.0.1 dbname=contracts port=5432 user=smirnov"

USER =		None
SUBSYS =	None
CONFIG =	None
DRWT = 		None	# Описатеть БД worktime
DRCNTR =	None	# Описатеть БД contracts

def	perror (tit = None, txt = None):
	if not tit:	tit = ''
	print	"<div class='error'><b>%s</b> %s</div>" % (str(tit), str(txt))

def	get_auto (regnum, device_id, is_work):	## device_id
	global	DRCNTR, COUNT
	if not DRCNTR:	DRCNTR = dbtools.dbtools(CDB_DESC)
	query = "SELECT * FROM vtransports WHERE device_id = %d;" % device_id
	adict = DRCNTR.get_dict(query)
	return	adict
	'''
	print "<td>", #device_id,
	if adict:
#		for k in adict.keys():
#			if adict[k]:	print k, adict[k], ";"
		print adict['bm_ssys'], adict['ttname'], adict['oname']	#['rname'],
		if COUNT ['ssys'].has_key(adict['bm_ssys']):
			COUNT ['ssys'][adict['bm_ssys']] += 1
		else:	COUNT ['ssys'][adict['bm_ssys']] = 1
	else:
		COUNT ['isnt'] += 1
		print "adict", adict	# query,
	print "</td>"
	'''

COUNT = {}
def	init_COUNT ():
	global	COUNT
	COUNT ['line'] = 0
	COUNT ['isnt'] = 0
	COUNT ['isntS'] = 0
#	COUNT ['is_org'] = 0
	COUNT ['is_work'] = 0
	COUNT ['is_wtm'] = 0
	COUNT ['ssys'] = {}
	COUNT ['ssysS'] = {}
#	COUNT ['get_auto'] = 0

def	mond_status (SS, request):
	""" Справка по работоспособности ТС за прошедший месяц	"""
	global	DRWT, DRCNTR, COUNT
	if not DRWT:	DRWT = dbtools.dbtools(CONFIG.get('dbNames', 'worktime'))
	if not DRCNTR:	DRCNTR = dbtools.dbtools(CDB_DESC)

	col_order = [	#'id_auto',	#'month', 'is_work', 'work_time', # 'code', 'imei',
		'id', 'device_id', 'is_work', 'work_time', 'regnum',#'regnumber',
	#	'where_set',
		'where_mod', ]
	col_name = {'is_work': "W", 'work_time': "T", 'regnum': "Гос. No", 'regnumber': "+++", 'where_mod': "Изменен", 'where_set': "Создан",}
	res = DRWT.get_table("nav_work_time w, nav2regnum a", "a.id = id_auto")
#	print "nav_work_time w, nav2regnum a", res[0]
	print "<div class='box' style='min-height: 400px; max-height: 600px; overflow: auto;'>"
	print "<table id='nav_work_time' width=100%><thead style='position: relative; width: inherit'><tr>"

	col_index = []
	for js in col_order:
		col_index.append(res[0].index(js))
		if col_name.has_key(js):
			print "<th>", col_name[js], "</th>",
		else:	print "<th>", js.upper(), "</th>",
	print "<th>gosnum</th><th>НАЛИЧИЕ</th></tr></thead><tbody>"
	lenr = 0
	init_COUNT()
	for r in res[1]:
		if not lenr:	lenr = len(r)
	#	adict = get_auto (r[res[0].index('regnum')], r[res[0].index('device_id')], r[res[0].index('is_work')])
		qutrns = "SELECT * FROM vtransports WHERE device_id = %d;" % r[res[0].index('device_id')]	#device_id
		adict = DRCNTR.get_dict(qutrns)
		if adict:
	#		print "<tr>"	# align='center'>"
			if adict['gosnum'] == r[res[0].index('regnum')]:
				if r[res[0].index('is_work')]:
					print "<tr class='line' id='%d' bgcolor='#bbffbb'>" % r[res[0].index('device_id')]
				else:	print "<tr class='line' id='%d' title='Нет данных!'>" % r[res[0].index('device_id')]
			else:	print "<tr class='line' id='%d' bgcolor='ffffaa' title='Изменен Гос. No'>"  % r[res[0].index('device_id')]
		else:	print "<tr class='line' bgcolor='#ffcccc' title='Отсутствует в справочной БД'>"
#		for j in range(lenr):
#			if res[0][j] in col_order:
#				print "<td>", r[j], "</td>",
		for j in col_index:
			print "<td>", r[j], "</td>",
		if r[res[0].index('is_work')]:
			COUNT ['is_work'] += 1
		elif r[res[0].index('work_time')] > 0:
			COUNT ['is_wtm'] += 1
		COUNT['line'] += 1 
		print "<td>"
		if adict:
			print adict['gosnum'], "</td><td>", adict['ttname'], adict['oname']	#['rname'],
			if r[res[0].index('is_work')]:
				if COUNT ['ssys'].has_key(adict['bm_ssys']):
					COUNT ['ssys'][adict['bm_ssys']] += 1
				else:	COUNT ['ssys'][adict['bm_ssys']] = 1
			else:
				if COUNT ['ssysS'].has_key(adict['bm_ssys']):
					COUNT ['ssysS'][adict['bm_ssys']] += 1
				else:	COUNT ['ssysS'][adict['bm_ssys']] = 1
		else:
			if r[res[0].index('is_work')]:
				COUNT ['isnt'] += 1
			else:	COUNT ['isntS'] += 1
			print "</td><td>",	#"adict", adict	# query,
		print "</td>"
		print "</tr>"
	print "</tbody></table>", "</div>"
	print	"### mond_status", COUNT['line']
	print """<script language='JavaScript'>
		$('#nav_work_time tr.line').hover (function () { $('#nav_work_time tr').removeClass('mark'); $(this).addClass('mark'); $('#shadow').text('')})
			.click (function (e) { $('#nav_work_time tr').removeClass('mark'); $(this).addClass('mark');
			$.ajax ({data: 'shstat=mark_row&table=work_tts&pkname=device_id&idrow=' +$(this).get(0).id +'&X=' +e.clientX +'&Y=' +e.clientY +'&' +$('form').serialize() }); });
		</script>"""

DSSYS =	{}

def	get_subsys (code, cname):
	global	DRCNTR, DSSYS
	if not DRCNTR:	DRCNTR = dbtools.dbtools(CDB_DESC)
	if not DSSYS:
		res = DRCNTR.get_table('subsys', "code > 0 ORDER BY code")
		DSSYS['d'] = res[0]
		for r in res[1]:	DSSYS[r[0]] = r
	if DSSYS.has_key(code) and cname in DSSYS['d']:
		return	DSSYS[code][DSSYS['d'].index(cname)]
	else:	return	str(code)

def	view_COUNT ():
	global	DRCNTR, DRWT,	COUNT
	if not COUNT:
		print "COUNT:", COUNT
		return
	res = DRCNTR.get_table('subsys', "code > 0 ORDER BY code")
	print "<div class='box' style='width: 400px'>"
	print "Всего по договорам:<b> %d</b>, работали более 4х часов<b> %d</b> менее <b> %d</b>." % (COUNT ['line'], COUNT ['is_work'], COUNT ['is_wtm'])
	print "<table width=100%><tr><th>Подсистема</th><th>Не ездили</th><th>Работают</th><th>Всего</th></tr>"
	summW= summS = sum0 = sumS0 = 0
	for r in res[1]:
		code = r[res[0].index('code')]
		if COUNT['ssys'].has_key(code) or COUNT['ssysS'].has_key(code):
			print	"<tr><td>", r[res[0].index('rnc_name')], "</td>",
			summL = 0
			if COUNT['ssysS'].has_key(code):
				summS += COUNT['ssysS'][code]
				summL += COUNT['ssysS'][code]
				print	"<td align='right'>", COUNT['ssysS'][code], "</td>"
			else:	print	"<td align='right'> - </td>"
			if COUNT['ssys'].has_key(code):
				summW+= COUNT['ssys'][code]
				summL += COUNT['ssys'][code]
				print	"<td align='right'>", COUNT['ssys'][code], "</td>"
			else:	print	"<td align='right'> - </td>"
			print	"<td align='right'>", summL, "</td></tr>"
	if COUNT['ssys'].has_key(0) or COUNT['ssysS'].has_key(0):
		print	"<tr bgcolor='#ffaaaa'><td>", "Неизвестная подсистема", "</td>"
		summL = 0
		if COUNT['ssysS'].has_key(0):
			summS += COUNT['ssysS'][0]
			summL += COUNT['ssysS'][0]
			print	"<td align='right'>", COUNT['ssysS'][0], "</td>"
		else:	print	"<td align='right'> - </td>"
		if COUNT['ssys'].has_key(0):
			summW += COUNT['ssys'][0]
			summL += COUNT['ssys'][0]
			print	"<td align='right'>", COUNT['ssys'][0],"</td>"
		else:	print	"<td align='right'> - </td>"
		print	"<td align='right'>", summL, "</td></tr>"
	print	"<tr bgcolor='#ffaaaa'><td>Отсутствуют в БД <b>contracts</b></td>"
	print	"<td align='right'>", COUNT['isntS'], "</td><td align='right'>", COUNT['isnt'], "</td><td align='right'>", (COUNT['isntS']+COUNT['isnt']), "</td></tr>"
	print	"<tr><td><b>", "Всего ", "</b></td><td align='right'><b>", summS, "</b></td><td align='right'><b>", summW, "</b></td><td align='right'><b>", (summW+summS), "</b></td></tr>"
	print	"</table></div>"

def	viev_stat_ts_month (fl_contr = False):
	global	DRCNTR
#	fl_contr = True
	jc_ignore = [64, 1024, 512, 256]
	if fl_contr:
		jc_ignore.append(2048)
		jc_ignore.append(4096)
	if not DRCNTR:	DRCNTR = dbtools.dbtools(CDB_DESC)
	res = DRCNTR.get_table('stat_ts_month', "id > 0 ORDER BY when_count DESC")
	if not res:
		print "viev_stat_ts_month DRCNTR.get_table('stat_ts_month')", CDB_DESC
		return
	print "<div class='box'>"	#style='width: 00px'>"
	d = res[0]
	th_2 = []
	print d
	print "<table width=100%><tr><th rowspan=2>Дата</th>"
	jc = d.index('c_all')
	if fl_contr:		print "<th>Нет подситемы</th><th>Нет в БД</th>"
	for c in d[jc:]:
		if c == 'c_all':
			print "<th colspan=3>Всего</th>"
			th_2.append("<th>сутки</th><th>всего</th><th>в сис</th>")
		elif int(c[2:]) in jc_ignore:	continue
		else:
			print "<th colspan=3>%s</th>" % get_subsys (int(c[2:]), 'label')
	#		th_2.append("<th>1</th><th>2</th><th>3</th>")
			th_2.append("<th>сутки</th><th>всего</th><th>в сис</th>")
	#	print "<th colspan=3>%s</th>" % c
	print "</tr>"
	print "".join(th_2), "</tr>"
	for r in res[1]:
		print "<tr><td>", str (r[1]), "</td>"
		if fl_contr:
			print "<td align='right'>", r[d.index('what_calc')], "</td><td align='right'>", r[d.index('c_unknown')], "</td>"
		for jr in range (jc, len(d)):
			if jr > jc and int (d[jr][2:]) in jc_ignore:	continue
			if not r[jr]:	print "<td align='right' colspan=3>-</td>"
			else:
				for jx in r[jr]:	print "<td align='right'>", jx, "</td>",
	#	print "<td align='right'>", r[jr], "</td>",
		print "</rt>"
	print	"</table></div>"

def	work_statistic (SS, request):
	global	DRWT
	if not DRWT:	DRWT = dbtools.dbtools(CONFIG.get('dbNames', 'worktime'))
	sttm =  time.localtime(time.time())
	tm_year, tm_mon, tm_mday = sttm[:3]
#	print	"work_statistic", request, tm_year, tm_mon, tm_mday
	if request.has_key ('select_tts'):
		if request['select_tts'] == 'notdata':		# Нет данных
			swhere = 'n.stat > 0 AND w.stat_view IS NULL AND mon_bstat = 0'
		elif request['select_tts'] == 'not_day':	# Нет сегодня
			mday = 1 << 2*(tm_mday -1)
			swhere = 'n.stat > 0 AND w.stat_view IS NULL AND w.where_mod IS NOT NULL AND w.mon_bstat < %d' % mday
		elif request['select_tts'] == 'is_vts':		# Только скрытые
			mday = 1 << 2*(tm_mday -1)
			swhere = 'n.stat > 0 AND w.stat_view > 0'
		else:		# Список ТС по договорам
			swhere = 'n.stat > 0 AND w.where_mod IS NOT NULL'
	else:	swhere = 'n.stat > 0'
	wtm = "AND w.year = %d AND w.month = %d" % (tm_year, tm_mon)
	sorder = 'ORDER BY w.mon_bstat, n.stat'
	scols = 'w.where_mod, n.regnum, n.device_id, n.imei, w.mon_bstat, s.sname, w.rem, w.stat_view'
	stabs = "nav2regnum n LEFT JOIN work_statistic w ON w.device_id = n.device_id LEFT JOIN nav_stat s ON s.id = n.stat"
	res = DRWT.get_table(stabs, ' '.join([swhere, wtm, sorder]), scols)
#	res = DRWT.get_table('work_statistic w LEFT JOIN nav2regnum n ON w.device_id = n.device_id LEFT JOIN nav_stat s ON s.id = n.stat', swhere, scols)

	if not res:
		print "SELECT %s FROM %s WHERE %s;" % (scols, stabs, ' '.join([swhere, wtm, sorder]))
		print "<br /><span class='bferr'>НЕТ данных!</span>"
		return
	d = res[0]
#	print "<hr>work_statistic", res[0]
	print "<div class='box' style='min-width: 1300px; min-height: 400px; max-height: 600px; overflow: auto;'>"
	print "<table id='work_tts' width=100% cellpadding=2 cellspacing=0><tr>"
	for c in d:
		if c == 'mon_bstat':
			for jd in xrange (31):
				if jd+1 == tm_mday:
					print "<td bgcolor='#ff8888'><b>%02d</b></td>" % (jd+1) ,
				else:	print "<th>%02d</th>" % (jd+1) ,
		#	print "<th colspan=31>%s<?th>" % c ,
		elif c == 'stat_view':
			print """<th><input type='button' class='butt' onclick="if (confirm ('Исключить ТС из просмотра?')) {set_shadow ('set_ts_view');}" value='VTS' title='Скрыть/Показать ТС' /></th>"""
		elif c == 'rem':
		#	print "<th>Примечания</th>"
			print "<th width=14%>Примечания</th>"
		else:	print "<th>%s</th>" % c ,
	print "</tr>"
	j = 0
	for r in res[1]:
		j += 1
		if j % 2:	bgcolor = "bgcolor=#fbfbff"
		else:	bgcolor = ""
		js = 0
		print "<tr id='%d' class='line' %s>" % (r[d.index('device_id')], bgcolor) ,
		for v in r:
			if js == d.index('mon_bstat'):
				if v >= 0:
					for jd in xrange (31):
						if jd+1 == tm_mday:
							bgc = "bgcolor='#ffaaaa'"
						else:	bgc = ''
						jv = (v >> 2*jd) & 3
						if not jv:	print "<td %s> </td>" % bgc ,
						elif not bgc:
							if jv < 2:
								print "<td bgcolor='#ffffaa'>%d</td>" % jv ,
							else:	print "<td bgcolor='#aaffff'>%d</td>" % jv ,
						else:	print "<td %s>%s</td>" % (bgc, str(jv)) ,
				else:
					print "<td>..</td>"*31
			elif js == d.index('stat_view'):
				if r[d.index('stat_view')] and r[d.index('stat_view')] > 0:
					print "<td><input type='checkbox' name='ssvw:%d' checked></td>" % r[d.index('device_id')]
				else:	print "<td><input type='checkbox' name='ssvw:%d'></td>" % r[d.index('device_id')]
			elif js == d.index('rem') and not r[js]:
				print "<td> </td>"
			elif js == d.index('where_mod'):
				print "<td>%s</td>" % cglob.out_sfdate (str(v)[:10])
			else:	print "<td>%s</td>" % str(v) ,
			js += 1
		print "</tr>"
	print "</table></div>"
	print "Найдено машин:<b>", len(res[1]), "</b>"
	print """<script language='JavaScript'>
		$('#work_tts tr.line').hover (function () { $('#work_tts tr').removeClass('mark'); $(this).addClass('mark'); $('#shadow').text('')})
			.click (function (e) { $('#work_tts tr').removeClass('mark'); $(this).addClass('mark');
			$.ajax ({data: 'shstat=mark_row&table=work_tts&pkname=device_id&idrow=' +$(this).get(0).id +'&X=' +e.clientX +'&Y=' +e.clientY +'&' +$('form').serialize() }); });
		</script>"""

def	view_session_opt ():
	""" ПОказать session_opt	"""
	global	DRWT
	if not DRWT:	DRWT = dbtools.dbtools(CONFIG.get('dbNames', 'worktime'))
	res = DRWT.get_table ('session_opt')
	print "<div class='box'>"	# style='width: 680px;'>"
	print "<table width=100%><tr>"
	cols =['tmbeg', 'tmend', 'id_auto_last']
	for cnm in cols:	#res[0]:
		print "<th>", cnm.upper(), "</th>",
	print "</tr><tr align='center'>"
	for cnm in cols:
		print "<td>", res[1][0][res[0].index(cnm)], "</td>",
	print "</tr>"
	print "</table>", "</div>"

RES_TTS = (['cod', 'name'], [('list_ts','Список ТС работающих по договорам'),('stat_ts', 'Статистика подключения ТС'), ('work_ts', 'Контроль работающих ТС')])
RES_SETWTS = (['cod', 'name'], [('contract', 'ТС по договорам'), ('notdata', 'Отсутствие данных'), ('not_day', 'Нет сегодня'), ('is_vts', 'Только скрытые')])
def	head_ts (request):
#	print request
#	</form><form name='tsForm' action='/cgi/index.cgi' method='post' enctype='multipart/form-data'>
	print	"""
	<div class='box' style='background-color: #dde;'><table width=100%><tr><td width=35%><span class='tit'> Список ТС работающих по договорам </span></td>
	<td>Инструменты:"""
	tts_key = request['view_tts']
#	if request.has_key('view_tts'):
#	else:	tts_key = 'stat_ts'
	cglob.out_select('view_tts', RES_TTS, key = tts_key, sopt = 'onchange="document.myForm.submit ()"', sfirst = None)
	if tts_key == 'work_ts':
		if not request.has_key ('select_tts'):
			 request['select_tts'] = 'not_day'
		print "&nbsp;ТС:"
		cglob.out_select('select_tts', RES_SETWTS, key = request['select_tts'], sopt = 'onchange="document.myForm.submit ()"')
	print """</td>
	<td align='right'>	Машины от 1С: <span class='bfgrey'><input type='file' name='file_wtscsv' accept='text/csv' /><input class='butt' type='submit' value=' Отправить '></span> </td>
	</tr></table></div>
	"""
def main (SS, conf, request):
	global	USER, SUBSYS, CONFIG
	CONFIG = conf
	import conract
	if not request.has_key('view_tts'):	request['view_tts'] = 'list_ts'
	head_ts (request)
	try:
		'''
		DRWT = dbtools.dbtools(CONFIG.get('dbNames', 'worktime'))
		res = DRWT.get_table("nav_work_time w, nav2regnum a", "a.id = id_auto")
		conract.out_table (SS, DRWT, 'tname', res)
		'''
		print "<table><tr valign='top'><td valign='top'>"
		if request['view_tts'] == 'work_ts':
		#	print "&nbsp; </td><td width='200px'>&nbsp; </td><td>"
			work_statistic (SS, request)
		else:
			if request['view_tts'] == 'stat_ts':	viev_stat_ts_month()
			if request['view_tts'] == 'list_ts':	mond_status (SS, request)
			print "</td><td valign='top'>"
			view_session_opt()
			view_COUNT ()
		print "</td></tr></table>"
	except:
		exc_type, exc_value = sys.exc_info()[:2]
		perror ("EXCEPT transport", " ".join(["<pre>", str(exc_type).replace('<', '# '), str(exc_value), "</pre>"]))
