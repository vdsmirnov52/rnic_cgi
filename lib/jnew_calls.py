#!/usr/bin/python -u
# -*- coding: utf-8 -*-

import  os, sys, time
import  time

LIBRARY_DIR = r"/home/smirnov/MyTests/CGI/lib/"
sys.path.insert(0, LIBRARY_DIR)

import	dbtools

head = """<head>
	<META HTTP-EQUIV='Content-Type' CONTENT='text/html; charset=utf-8'>
	<META NAME='Author' CONTENT='V.Smirnov'>
	<title>Журнал приема вызовов</title>
	<link rel='stylesheet' type='text/css' href='/css/style.css'>
	<link rel='stylesheet' type='text/css' href='/css/style03.css'>
	<link rel='stylesheet' type='text/css' href='/css/butt.css'>
	<link rel='stylesheet' type='text/css' href='/css/calendar.css'>
	<script language='JavaScript' src='/jq/jquery.js'></script>
	<script language='JavaScript' src='/js/calendar.js'></script>
	</head>
	"""
mydiv =	"""<script LANGUAGE='JavaScript'>
	var	height = -100 + document.body.scrollHeight;
//	alert ("<div id='body' class='grey' style='width: 1200px; height: "+ height +"px; overflow: auto;'>");
	document.write ("<div id='body' class='grey' style='height: "+ height +"px; overflow: auto;'>");
	/*
	document.write ("Размер окна клиента = [" +document.body.clientWidth +" x "+ document.body.clientHeight +"] ["+
		+document.body.offsetWidth +" x "+ document.body.offsetHeight +"] ["+
		+document.body.scrollWidth +" x "+ document.body.scrollHeight +"]<br>");
	*/
	</script>"""

sform = """<form name='mainForm' action='%s' method='post'>
	<fieldset class='hidd'>
	<input type='hidden' name='this' value='jnew_calls' />
	<input type='hidden' name='where' value='' />
	<input type='hidden' name='order' value='' />
	</fieldset>"""

def	parse_sdate (sdate):
	sdate = sdate.replace('-', ' ')
	sdate = sdate.replace(':', ' ')
	sdate = sdate.replace('/', ' ')
	sdate = sdate.replace('.', ' ')
	sd = sdate.split()
	return '.'.join(sd)

def	out_titl (request):
	sttm = time.localtime (time.time())
	sdate = time.strftime("%d-%m-%y", sttm)
	if request.has_key('date'):
		if sdate == request['date']:
			jhour = sttm[3]
		else:	jhour = 23
		sdate = parse_sdate (request['date'])
	else:
		jhour = sttm[3]	# hour
	if request.has_key('hour'):
		ishour = request['hour']
	else:	ishour = ''
#	print 'jhour', jhour, "[%s]" % ishour
#	for s in sttm:	print s
	print	"<table width=100%><tr><td><b>Журнал приема вызовов</b></td>"
#	print	"<td>Дата: <input type='text' name='date' size=8 value='%s' /></td>" % sdate
	print	"<td><input id='dp_begin' type='text' name='date' size=5 value='%s' maxlength=8 class='date' /><td>" % sdate
	print	"<td>Час: <input type='text' name='hour' size=2 value='%s' />" % ishour
	lbutts = []
	jh = jhour
	for j in xrange(24):
		lbutts.append ("""<input type='button' class='bb' value='%02d' onclick="document.mainForm.hour.value='%02d'; document.mainForm.submit();">""" % (jh, jh))
		jh -= 1
		if jh < 0:	break	#jh = 23	
	print	''.join (lbutts), "</td>"
	print	"""<td align='right'><img title="Reload" alt="Reload" onclick="document.mainForm.submit();" src="/img/reload3.png"></td></tr></table>"""
	### CREATE string WHERE
	jsttm = [0,0,0,0,0,0,0,0,0]
	sdate = sdate.replace('-', ' ') 
	sdate = sdate.replace(':', ' ') 
	sdate = sdate.replace('/', ' ') 
	sdate = sdate.replace('.', ' ') 
	sd = sdate.split()
	if sd[0].isdigit():	jsttm [2] = int(sd[0])
	if sd[1].isdigit():	jsttm [1] = int(sd[1])
	if len (sd) > 2 and sd[2].isdigit():
		if int(sd[2]) < 100:
			jsttm [0] = int(sd[2]) +2000
		else:	jsttm [0] = int(sd[2])
	if ishour.isdigit():
		jsttm [3] = int(ishour)
		if jhour and jhour < jsttm [3]:
		#	jsttm [2] -= 1
			jsttm [3] -= 1	#86400
	else:	jsttm [3] = jhour
	tmin = int (time.mktime(jsttm)) -BTIMER -1
	swhere = "WHERE t_get > %d AND t_get < %d" % (tmin, 3601 +tmin)
#	print sd, jsttm, tmin, time.strftime("[ %D %T ]", time.localtime (tmin +BTIMER)), swhere
	return	swhere

BTIMER =	900000000

dtable = {	'number': 'No', 'cnum_total': 'T.No', 't_get': 'Принят', 'g_disp': 'Кем',
		'RPPPS': ['Рз. М. Пр. ПС Сек.', '; ', 'reasn', 'place', 'profile', 'subst', 'sector'],
		'RK': ['Кто', '&nbsp;', 'kto', 'rept'],
		'street': 'Улица', 'housek': ['Дом', ' ', 'house', 'korp'],
		'jflat': ['Кв. П. Э. Код', ', ', 'flat', 'pdzd', 'etj', 'pcod'], 'phone': 'Телефон',
		'fio': ['ФИО', '&nbsp;', 'name', 'name2'], 'asex': ['Лет Пол', '&nbsp;', 'age', 'sex'],
		'reslt': 'Резлт.', 'DS': ['DS', ' ', 'diagn', 'diat'], 'kuda': 'Куда'}
dtorder = ['number', 'cnum_total', 'RPPPS', 't_get', 'g_disp', 'street', 'housek', 'jflat', 'RK', 'phone', 'fio', 'asex', 'reslt', 'DS', 'kuda']

#'t_send', 's_disp', 't_arrl', 'a_disp', 't_done', 'd_disp', 'diagn', 'diat', 'alk', 'reslt', 'kuda', 't_go', 'br_ref', 'smena', 'nbrg', 'pbrg', 'nsbrg', 'doctor', 'ps', 'c_disp', 't_close', '', 'id_ims', 'tm_hosp', 'disp_hosp', 'tm_ps', 'disp_ps', 'tm_trans', 'disp_trans', 't_wait', 't_serv', 't_hosp']

def	out_clist (where = None):
	dboo = dbtools.dbtools("host=localhost dbname=b03 port=5432 user=vds")
#	print "<pre>", 	help (dbtools), "</pre>"
	if not where:	where = ''
	rows = dboo.get_rows ("SELECT * FROM calls_new %s ORDER BY t_get DESC LIMIT 200;" % where)
	rdesc = dboo.desc

	print "<table width=100%><tr>"
	for t in dtorder:	#dtable:
		if isinstance (dtable[t], basestring):
			print "<th>", dtable[t], "</th>",
		elif isinstance (dtable[t], list):
			print "<th>", dtable[t][0], "</th>",
	print "</tr>"

	j = 0
	for r in rows:
		j += 1
		if j % 2:
			print "<tr id='tr%03d' bgcolor='#ffffff'>" % j
		else:	print "<tr id='tr%03d'>" % j
		for t in dtorder:
			if t == 't_get':
				val = time.strftime("%T %d.%m.%Y", time.localtime (BTIMER +r[rdesc.index(t)]))
			elif t in rdesc:
				if r[rdesc.index(t)]:
					val = r[rdesc.index(t)]
				else:	val = '---'
			else:
				if isinstance (dtable[t], list):
					'''
					val = dtable[t][2:]
					'''
					vall = []
					for jv in dtable[t][2:]:
						if r[rdesc.index(jv)]:
							vall.append (str (r[rdesc.index(jv)]))
						else:	vall.append ('-')
				#	val = ', '.join(vall)
					val = dtable[t][1].join(vall)
				else:
					val = dtable[t]
			print "<td>", val, "</td>",
		print "</tr>"
	print "</table>"
	return j

def	main (request, enveron):
	print head, "<body>"
	print sform % enveron['SCRIPT_NAME']
	print "<div id='titl' class='finans'>"
#	print "<pre>", request, "</pre>"
	swhere = out_titl (request)
	'''
#	for k in enveron:	print k, '\t:', enveron[k]
	print "</pre>"
	'''
	print "</div>", mydiv
	jrows = out_clist (swhere)
	print "</div>"
	print "Найдено <b>%d</b> записей." % jrows
	print "</form></body>"

if __name__ == "__main__":
	main ({'this': 'jnew_calls'})
