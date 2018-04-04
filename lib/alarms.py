#!/usr/bin/python
# -*- coding: utf-8 -*-

import	sys, os, time

LIBRARY_DIR = r"/home/smirnov/MyTests/CGI/lib/"         # Путь к рабочей директории (библиотеке)
sys.path.insert(0, LIBRARY_DIR)

import	dicts
import	cglob
import	session
import	dbtools

'''
	id | id_bid | bm_btype | bm_bstat | id_org | id_contr | message | tm_creat | tm_alarm | tm_close | who_close | rem | bname | obname
'''

RBBTYPE =	None	# Буфер хранения результата запроса к 'bid_type'
RBBSTAT =	None	# Буфер хранения результата запроса к 'bid_stat'

def	get_sbid_type (idb, bm_btype, span = None):
	""" Читать (показать) Тип заявки письма	"""
	global	RBBTYPE
	
	if not RBBTYPE:	RBBTYPE = idb.get_table('bid_type', 'code > 0')
	ibm_btype = int (bm_btype)
	if not span:	span = 'bfgrey'
	if RBBTYPE:
		for r in RBBTYPE[1]:
			if r[0] == ibm_btype:	return	"<span class='%s'>%s</span>" % (span, r[1])
	return	"QQQ"

def	get_sbid_stat (idb, bm_bstat, tm_alarm = None, slen = None):
	""" Читать (показать) статус заявки письма	"""
	global	RBBSTAT
	if not RBBSTAT:	RBBSTAT = idb.get_table('bid_stat', 'code >= 0 ORDER BY code')
	if not (bm_bstat and int (bm_bstat) > 0):	return	"<span class='bferr'>%s</span>" % RBBSTAT[1][0][2]
	ibm_bstat = int (bm_bstat)
	if RBBSTAT:
		sss = []
		for r in RBBSTAT[1]:
#			print	r[2]
			if r[0] & ibm_bstat:	sss.append(r[2])
		if sss:
			sout = "; ".join(sss)
			if slen:	sout = sout[:slen] +'...'	
	#		sout = "DDD %d" % int(tm_alarm - time.time())
			if tm_alarm > time.time():
				return	"<span class='bfinf'>%s</span>" % sout	
			else:	return	"<span class='bferr'>%s</span>" % sout
	return	"QQQ"

def	alist(SS, idb, request):
	global	RBBTYPE

	print	"<div style='background-color: #eef; border: thin solid #778; padding: 0px;'>"
	tm_current = int (time.time())
#	res = idb.get_table ('valarms', "id > 0 ORDER BY id_bid, tm_alarm DESC")
	slike_org = ''
	sqqq = ''
	butt_all = ''
	if request.has_key('like_org') and request['like_org'].strip() != '':
		slike_org = request['like_org'].strip()
		sqqq = "obname LIKE '%%%s%%' AND tm_alarm < %d GROUP BY id_org, obname ORDER BY tma ;" % (slike_org, tm_current)
		res = idb.get_table ('valarms', "obname LIKE '%%%s%%' AND tm_alarm < %d GROUP BY id_org, obname ORDER BY tma ;" % (slike_org, tm_current), "id_org, min(tm_alarm) AS tma, obname")
	elif request.has_key('id_org') and request['id_org'].isdigit() and int(request['id_org']) > 0:
		print "<input name='id_org' type='hidden' value='%s' />" % request['id_org']
		butt_all = """<td align=right><input class='butt' type='button' onclick="document.myForm.id_org.value=''; document.myForm.like_org.value=''; set_shadow('view_alarms');" value='Все' /></td>"""
		dorg = idb.get_dict("SELECT * FROM organizations WHERE id_org = %d" % int(request['id_org']))
		slike_org = dorg['bname']
		res = idb.get_table ('valarms', "id_org = %d GROUP BY id_org, obname ORDER BY tma " % int(request['id_org']), "id_org, min(tm_alarm) AS tma, obname")
	else:
		res = idb.get_table ('valarms', "tm_alarm < %d GROUP BY id_org, obname ORDER BY tma ;" % tm_current, "id_org, min(tm_alarm) AS tma, obname")
	if not RBBTYPE:	RBBTYPE = idb.get_table('bid_type', 'code > 0')
	print	"""<div class='box' style='background-color: #dde;'><table width=100%><tr onclick="$('#id_body').addClass('mark');"><td width=20% class='tit'>Список событий</td>"""
	print	"<td align='center'>Организация:<input type='text' name='like_org' value='%s' /></td>" % slike_org
	print	"<td align='center'>Заявка:"
	if request.has_key('set_btype') and request['set_btype'].isdigit():
		iset_btype = int (request['set_btype'])
	else:	iset_btype = 0
	cglob.out_select('set_btype', RBBTYPE, ['code', 'bname'], key = iset_btype, sopt = """ onchange="set_shadow('view_alarms');" """, sfirst=' ')
	print	"</td>"
	if butt_all:
		print butt_all
	else:	print	"""<td align=right><input id='sss' class='butt' type='button' title='Help' onclick="win_helps('bids.html');" value='?'></td>"""
	print	"""<td align=right><img onclick="set_shadow('view_alarms');" title="Обновить" src="../img/reload3.png"></td></tr></table></div>"""
	if not res:
		print "<span class='tit bferr'> &nbsp; &nbsp; Событий по шаблону Организация: [%s] не найдено.</span><br>%s" % (slike_org, sqqq)
		return
	fis_alarm = 0
	cdict = res[0]
	print	"<table width=100% border=0 cellpadding=2 cellspacing=0><tr><th colspan=2>Наименование организации</th><th>Тип заявки</th><th>Действие</th></tr>"
	for r in res[1]:
		if iset_btype:
			jres = idb.get_table ('valarms', "id_org = %d AND bm_btype = %d ORDER BY id_bid, bm_bstat DESC" % (r[cdict.index('id_org')], iset_btype))
		else:	jres = idb.get_table ('valarms', "id_org = %d ORDER BY id_bid, bm_bstat DESC" % r[cdict.index('id_org')])
		if not jres:	continue
		jcdict = jres[0]
#		print jcdict
		sonclick = "win_open('view', '&shstat=mark_row&idrow=%05d&pkname=id_org&set_table=vorganizations&table=vorganizations');" % r[cdict.index('id_org')]
		if jres[1][0][jcdict.index('message')]:
			stitle = "title='%s'" % jres[1][0][jcdict.index('message')]
		else:	stitle = ''
		if len(jres[1]) == 1 and not jres[1][0][jres[0].index('bm_bstat')]:	#jres:
			if (tm_current - r[cdict.index('tma')]) > 0:
				fis_alarm += 1
				bg = 'bferr'
			else:	bg = 'bfinf'
			print	"""<tr class='hei' bgcolor='#fea'><td colspan=2 class='line' onclick="%s" %s>""" % (sonclick, stitle)
			print	"<span class='bfgrey'>", r[cdict.index('obname')], "</span>",
			print	"</td><td>", get_sbid_type (idb, jres[1][0][jres[0].index('bm_btype')], 'bferr'), "</td><td nowrap>",
			print	"""<input type='text' class='date %s' value='%s' title='Отложить' name='date:%05d' /><input type='button' class='butt' value='O' title='Отложить'
				onclick="set_shadow('udate_alarms&defer=Y&id_row=%05d');" />""" % (
				bg, time.strftime('%d-%m-%Y', time.localtime (r[cdict.index('tma')])), jres[1][0][0], jres[1][0][0]), "</td></tr>"
		else:
			print	"""<tr class='hei' bgcolor='#fda'><td colspan=2 class='line' onclick="%s" %s>""" % (sonclick, stitle)
			print	"<span class='bfgrey'>", r[cdict.index('obname')], "</span>",
			print	"</td><td>", get_sbid_type (idb, jres[1][0][jres[0].index('bm_btype')], 'bfinf'), jres[1][0][0]
			print	"""</td><td><input type='button' class='butt' value='Все Исполнено' onclick="set_shadow('udate_alarms&all_done=Y&id_row=%05d');" /></td></tr>""" % jres[1][0][0]
			jcdict = jres[0]
			obm_btype = 0
			for jr in jres[1]:
				if not obm_btype:	obm_btype = jr[jcdict.index('bm_btype')]
				if obm_btype != jr[jcdict.index('bm_btype')]:	# Несколько заявок у одной организации
					obm_btype = jr[jcdict.index('bm_btype')]
					print	"""<tr class='hei' bgcolor='#fea'><td colspan=2 class='line bfligt' onclick="%s" title='%s'>""" % (sonclick, jr[jcdict.index('message')]), jr[jcdict.index('obname')]
					bg = 'bferr' if (tm_current > jr[jcdict.index('tm_alarm')]) else 'bfinf'
					print	"</td><td><span class='%s'>" % bg, jr[jcdict.index('bname')], '</span></td><td>',
					if jr[jcdict.index('bm_bstat')]:
						print	"""<input type='button' class='butt' value='Все Исполнено' onclick="set_shadow('udate_alarms&all_done=Y&id_row=%05d&');" />""" % jr[jcdict.index('id')]
					else:
						print	"""<input type='text' class='date %s' value='%s' title='Отложить' name='date:%05d' /><input type='button' class='butt' value='O' title='Отложить'
							onclick="set_shadow('udate_alarms&defer=Y&id_row=%05d');" />""" % (bg, time.strftime('%d-%m-%Y', time.localtime (jr[jcdict.index('tm_alarm')])),
							jr[jcdict.index('id')], jr[jcdict.index('id')])
						
					'''	
					j = 0
					for s in jr:
						print j, jcdict[j], s, '<br>'
						j += 1
					'''
					print	"""</td></tr>"""
					if not jr[jcdict.index('bm_bstat')]:	continue
				if (tm_current - jr[jcdict.index('tm_alarm')]) > 0:
					fis_alarm += 1
					bg = 'bferr'
				else:	bg = 'bfinf'
				print	"<tr class='hei' bgcolor='#fed'><td width=2%></td><td>", get_sbid_stat (idb, jr[jcdict.index('bm_bstat')], jr[jcdict.index('tm_alarm')])
				print	"</td><td nowrap> c: ", time.strftime("%d-%m-%Y", time.localtime (jr[jcdict.index('tm_creat')])), "исполнение до:"
				print	"""<input type='text' class='date %s' value='%s' title='Отложить' name='date:%05d' /><input type='button' class='butt' value='O' title='Отложить'
					onclick="set_shadow('udate_alarms&defer=Y&id_row=%05d');" />""" % (
					bg,  time.strftime("%d-%m-%Y", time.localtime (jr[jcdict.index('tm_alarm')])), jr[0], jr[0]), #jr[jcdict.index('bm_btype')]
				print	"""</td><td><input type='button' class='butt' value='Исполнено' onclick="set_shadow('udate_alarms&done=Y&id_row=%05d');" />""" % jr[0]
		#		print	"<tr class='hei'><td></td><td>", jr[jcdict.index('message')], "</td><td class='%s'>" % bg,  time.strftime('%d-%m-%Y', time.localtime (jr[jcdict.index('tm_alarm')])),
				print	"</td></tr>"
	print	"</table></div>"
	print	"Организаций:<span class='bfinf'>", len(res[1]), "</span>, &nbsp; Событий:<span class='bfinf'>", fis_alarm, "</span>"
#	print	"</div>"

def	update (idb, SS, request):
	try:
		row = idb.get_dict("SELECT * FROM alarms WHERE id = %s" % request['id_row'])
		if not row:	return
		print "~warnn|"
		'''
	#	print	"row", row
		for k in row.keys():
			if type(row[k]) == type(1):	print	k, row[k], "; "
		'''
		if request.has_key('defer'):	# Отложить
			for k in request:
				if k == "date:%s" % request['id_row']:
					stm = time.strptime(cglob.sfdate(request[k]), "%Y-%m-%d")
					tm_xx = int (time.mktime(stm))
		#			print	k, request[k], stm, tm_xx, row['tm_alarm']
					if tm_xx <= row['tm_alarm']:
						print	"~eval| alert('Нет изменений!\\n\\tДата: %s, меньше или равна текущей.');" % request[k]
						return
					else:
						query = "UPDATE alarms SET tm_alarm = %d WHERE id = %s" % (tm_xx, request['id_row'])
						print	query
						if idb.qexecute(query):
							return	"Ok"
		elif request.has_key('done'):	# Исполнено
			query = "UPDATE bids SET fix_bstat = (fix_bstat | %d)  WHERE id_bid = %d; DELETE FROM alarms WHERE id = %d;" % (row['bm_bstat'], row['id_bid'], row['id'])
			if idb.qexecute(query):
				return	"Ok"
		elif request.has_key('all_done'):	# Все Исполнено
			query = "UPDATE bids SET fix_bstat = (fix_bstat | (SELECT sum(bm_bstat) FROM alarms WHERE id_bid = %d)) WHERE id_bid = %d; DELETE FROM alarms WHERE id_bid = %d;" % (
				row['id_bid'], row['id_bid'], row['id_bid'])
			print	"Все Исполнено", query
			if idb.qexecute(query):
				return	"Ok"
		else:
			print	"update:", request
	except:
		exc_type, exc_value = sys.exc_info()[:2]
		print "~error|<span class='error'>EXCEPT ALARM update:", exc_type, exc_value, "</span>"

if __name__ == '__main__':
	print	"Test "
	person = persons(1)
	person.update(None, None)
