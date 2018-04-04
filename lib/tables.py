# -*- coding: utf-8 -*-

import	 time, string, sys

LIBRARY_DIR = r"/home/smirnov/MyTests/CGI/lib/"
sys.path.insert(0, LIBRARY_DIR)

dict_tabs = {
	'rusers': {	'title': "Список пользователей",
		'order': ['login', 'uname', 'ufam', 'bm_ssys', 'bm_role'],	# Default == dbtools.desc результат запроса к <table name>
		'thead': {'login': 'Login', 'uname': 'Имя', 'ufam': 'Фамилия', 'bm_ssys': 'Подсистемы', 'bm_role': 'Роли'},
		'key': 'user_id',		# Default == order[0]
		'functs': {'mark': "mark", 'ordbycol': "ordbycol"},
		},
	'subsystem': {	'title': "Доступные подсистемы",
		'order': ['label', 'ssname'],
		'thead': {'label': "Метка", 'ssname': "Название подсистемы"},
		'functs': {'mark': "mark",},
		},
	}

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
	jline = 0
	for r in res[1]:
		if jline % 2:
			bgcolor = "bgcolor=#ddddee"
		else:	bgcolor = ""
		jline += 1
		if type(r[ixkey]) == type(1):	# IntType:
			print "<tr id='%05d' class='line' %s>" % (r[ixkey], bgcolor)
		else:	print "<tr id='%s' class='line' %s>" % (r[ixkey], bgcolor)
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
	import	rusers
	tnames = ['rusers', 'subsystem', 'roles', 'rfunc']
	print "<table width=100%><tr style='vertical-align: top;'>"	# valign='top'>"
	for tname in tnames:
		print	"<td><div class='box'><table width=100%><tr><td><span class='tit'>",
		if dict_tabs.has_key(tname) and dict_tabs[tname].has_key('title'):
			dtbl = dict_tabs[tname]
			print	dict_tabs[tname]['title'],
		else:
			dtbl = None
			print	tname,
		print	 """</span></td><td align='right'><input type='button' class='butt' value=' ADD ' title='Добавить запись' onclick="add_row('%s');" /></td></tr></table><div class='box'>""" % tname
		res = rusers.get_table (tname)
		print res[0]
		if res:
			out_table (tname, res, dtbl)
		else:	cglob.wdgerror("out_users", obj=SS.objpkl)
		print	"</div></div></td>"
	print "</tr></table>"
	cglob.ppobj(USER)

