#!/usr/bin/python
# -*- coding: utf-8 -*-

import	os, sys, time

LIBRARY_DIR = r"/home/smirnov/MyTests/CGI/lib/"

import	dbtools

idbusr = None
sdbusr = "host=127.0.0.1 dbname=rusers port=5432 user=smirnov"

def	check_user (login, passwd):
	global	idbusr
	if not (login.strip() and passwd.strip()):	return
	if not idbusr:	idbusr = dbtools.dbtools(sdbusr)
	query = "SELECT * FROM rusers WHERE login = '%s' AND passwd = '%s'" % (login.strip(), passwd.strip())
	dusr = idbusr.get_dict(query)
	if dusr:
		del(dusr['login'])
		del(dusr['passwd'])
	return	dusr

def	get_roles(USER, code_ssys = 15):
	""" Читать Роли пользователя	"""
	global	idbusr
	if not idbusr:	idbusr = dbtools.dbtools(sdbusr)
#	query = "SELECT * FROM roles WHERE code & %d > 0 AND bm_ssys & %d >0;" % (USER['bm_role'], code_ssys)
	query = "SELECT * FROM roles WHERE bm_ssys & %d >0;" % code_ssys
	rows = idbusr.get_rows(query)
	if rows:
		return	idbusr.desc, rows

def	get_ssystems(USER):
	""" Читать Подсистемы пользователя	"""
	global	idbusr
	if not idbusr:	idbusr = dbtools.dbtools(sdbusr)
#	query = "SELECT * FROM subsystem WHERE code & %d > 0 ORDER BY ssname;" % USER['bm_ssys']
	query = "SELECT * FROM subsystem WHERE code & 6 > 0 ORDER BY ssname;"	# % USER['bm_ssys']
	rows = idbusr.get_rows(query)
	if rows:
		return	idbusr.desc, rows

def	get_table (tname, swhere = None, cols = None):
	""" Читать таблицу из БД rusers	"""
	global	idbusr
	if not idbusr:	idbusr = dbtools.dbtools(sdbusr)
	if not cols:	cols = '*'
	if swhere:
		query = "SELECT %s FROM %s WHERE %s;" % (cols, tname, swhere)
	else:	query = "SELECT %s FROM %s;" % (cols, tname)
	rows = idbusr.get_rows(query)
	if rows:
		return	idbusr.desc, rows

def	get_func_allowed(USER, role):	#SS):
	""" Читать список разрешенных пользователю функций	"""
	global	idbusr
	if USER and USER['bm_role']:
		if role and role['bm_func']:
			if not idbusr:	idbusr = dbtools.dbtools(sdbusr)
			query = "SELECT label FROM rfunc WHERE bm_role & %d > 0 AND code & %d > 0" % (USER['bm_role'], role['bm_func'])
			rows = idbusr.get_rows(query)
			funcs = []
			for r in rows:	funcs.append(r[0])
			return	funcs

import	cglob

dict_tabs = {
	'rusers': {	'title': "Список пользователей", 'titrow': "Пользователь",
		'order': ['login', 'uname', 'ufam', 'bm_ssys', 'bm_role'],	# Default == dbtools.desc результат запроса к <table name>
		'thead': {'login': 'Login', 'uname': 'Имя', 'ufam': 'Фамилия', 'bm_ssys': 'Подсистемы', 'bm_role': 'Роли'},
		'key': 'user_id',		# Default == order[0]
		'functs': {'mark': "mark", 'ordbycol': "ordbycol"},
		},
	'subsystem': {	'title': "Доступные подсистемы", 'titrow': "Подсистема",
		'order': ['label', 'ssname'],
		'thead': {'label': "Метка", 'ssname': "Название подсистемы"},
		'functs': {'mark': "mark",},
		},
	}
def	insert_row(request):
	insert_row(request)
# 	 'table': 'subsystem', 'label': 'aa', 'shstat': 'insert', 'ssname': 'aa'
	if request.has_key('table') and dict_tabs.has_key(request['table']):
		tname = request['table']
		dtbl = dict_tabs[tname]
		
def	out_tform (tname, pkname, idrow, stat = 'view', title = None):
	if dict_tabs.has_key(tname):
		dtbl = dict_tabs[tname]
		if not stat == 'addnew':
			if idrow.isdigit():
				res = get_table(tname, "%s = %s" % (pkname, idrow))
			else:	res = get_table(tname, "%s = '%s'" % (pkname, idrow))
			if not res:	return
			row = res[1][0]
		else:	res = (dtbl['order'], ) 
		if not title:
			if  dtbl.has_key('titrow'):	title = dtbl['titrow']
			else:	title = "%s %s" % (tname.upper(), stat)
		
#		cglob.out_widget('wform', title,  head = True)
		cglob.out_headform(title)
		if not dtbl.has_key('order'):	dtbl['order'] = res[0]
		if not dtbl.has_key('thead'):	dtbl['thead'] = {}
		print	"<table id='%s_row' width=100%%>" % tname
		for cnm in dtbl['order']:
			if dtbl['thead'].has_key(cnm):
				colname = dtbl['thead'][cnm]
			else:	colname = cnm.upper()
		#	print	"<tr style='vertical-align: top;'><td width=200px align='right'>%s:</td><td>" % colname,
			print	"<tr><td width=200px align='right'>%s:</td><td>" % colname,
			if stat == 'addnew':
				print	"<input type='text' name='%s' value='' />" % cnm
				if cnm == 'login':
					print	"<tr><td width=200px align='right'>Пароль:</td><td><input type='password' name='passwd' value='' />"
					print	"<tr><td width=200px align='right'>+Пароль:</td><td><input type='password' name='passwd2' value='' />"
			elif stat == 'update':
				print	"<input type='text' name='%s' value='%s' />" % (cnm, row[res[0].index(cnm)])
				if cnm == 'login':
					print	"<tr><td width=200px align='right'>Пароль:</td><td><input type='password' name='passwd' value='' />"
					print	"<tr><td width=200px align='right'>+Пароль:</td><td><input type='password' name='passwd2' value='' />"
			else:
				if 'bm_' in cnm:
					print	str_bitmask (cnm, row[res[0].index(cnm)]) ,
				else:
					print	"<b>", row[res[0].index(cnm)], "</b>",
			print	"</td></tr>"
		if stat == 'update':
			print	"""<tr><td></td><td><input type='button' class='butt' value=' Обновить ' onclick="set_shadow('update&table=%s');" /></td></tr>""" % tname
		if stat == 'addnew':
			print	"""<tr><td></td><td><input type='button' class='butt' value=' Сохранить ' onclick="set_shadow('insert&table=%s');" /></td></tr>""" % tname
		print	"</table>"
		print	"<div id='is_result' style='text-align:center;'>%s</div>" % stat
	#	print	res
		print	"</div><!-- wform -->"

def	str_bitmask(bm_name, bm_val):
	if bm_val == -1:	return	"<b>ВСЕ</b>"
	if bm_name == 'bm_ssys':
		res = get_table('subsystem', 'code & %d > 0' % bm_val, 'ssname AS name')
	elif bm_name == 'bm_role':
		res = get_table('roles', 'code & %d > 0' % bm_val, 'rname AS name')
	elif bm_name == 'bm_func':
		res = get_table('rfunc', 'code & %d > 0' % bm_val, 'fname AS name')
	else:	return	"Нет", bm_name, bm_val
	rr = ["<b>"]
	if res:
		for r in res[1]:
			rr.append("%s<br />" % r[0])
	else:	rr.append("Пусто")
	rr.append("</b>")
	return	"\n".join(rr)

def	out_table (tname, res, dtbl = None):
	if not dtbl:	dtbl = {}
	if not dtbl.has_key('order'):	dtbl['order'] = res[0]
	if not dtbl.has_key('thead'):	dtbl['thead'] = {}
	if dtbl.has_key('key') and dtbl['key']:
		pkname = dtbl['key']
	else:	pkname = dtbl['order'][0]
	ixkey = res[0].index(pkname)
#	cglob.ppobj(dtbl)
	print "<table id='%s' width=100%%><tr>" % tname
	ixcols = []
	for cnm in dtbl['order']:
		ixcols.append(res[0].index(cnm))
		if dtbl['thead'].has_key(cnm):
			colname = dtbl['thead'][cnm]
		else:	colname = cnm.upper()
		print "<th>", colname, "</th>",
	print "</tr>"
	if dtbl.has_key('functs'):
		clline = "class='line'"
	else:	clline = ""
	jline = 0
	for r in res[1]:
		if jline % 2:
			bgcolor = "bgcolor=#ddddee"
		else:	bgcolor = ""
		jline += 1
		if type(r[ixkey]) == type(1):	# IntType:
			print "<tr id='%05d' %s %s>" % (r[ixkey], clline, bgcolor)
		else:	print "<tr id='%s' %s %s>" % (r[ixkey], clline, bgcolor)
		for j in ixcols:
			print "<td>", r[j], "</td>",
		print	"</tr>"
	print "</table>"
	if dtbl.has_key('functs'):
		print	"<script language='JavaScript'>"
		if dtbl['functs'].has_key('mark'):
			print	"""$('#%s tr.line').click (function () { $('#%s tr').removeClass('mark'); $(this).addClass('mark'); $('#shadow').text('')})
				.dblclick (function (e) { $('#%s tr').removeClass('mark'); $(this).addClass('mark');
				$.ajax ({data: 'shstat=mark_row&table=%s&pkname=%s&idrow=' +$(this).get(0).id +'&X=' +e.clientX +'&Y=' +e.clientY +'&' +$('form').serialize() }); });""" % (
					tname, tname, tname, tname, pkname)
		print	"</script>"

def	out_users(SS, USER):
#	import	rusers
	tnames = ['rusers', 'subsystem', 'roles', 'rfunc']
	print "<table width=100%><tr style='vertical-align: top;'>"	# valign='top'>"
	for tname in tnames:
		print	"<td><div class='box'><table width=100% class='bggreys'><tr><td><span class='tit'>",
		if dict_tabs.has_key(tname) and dict_tabs[tname].has_key('title'):
			dtbl = dict_tabs[tname]
			print	dict_tabs[tname]['title'],
		else:
			dtbl = None
			print	tname,
		print	"</span></td><td align='right'>&nbsp;",
		if USER['bm_role'] == -1:
			print	"""<input type='button' class='butt' value=' ADD ' title='Добавить запись' onclick="add_row('%s');" />""" % tname
		print	"</td></tr></table><div class='box'>"
		res = get_table (tname)
		print res[0]
		if res:
			out_table (tname, res, dtbl)
		else:	cglob.wdgerror("out_users", obj=SS.objpkl)
		print	"</div></div></td>"
	print "</tr></table>"
#	cglob.ppobj(USER)
	cglob.ppobj(SS.objpkl)

if __name__ == "__main__":
#	idbusr = dbtools.dbtools(sdbusr)
	USER = {}
	USER['bm_ssys'] = 3
	print	get_ssystems(USER)
	print	check_user('vds', '123')
