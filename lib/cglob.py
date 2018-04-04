#!/usr/bin/python -u
# -*- coding: utf-8 -*-

import	cgi, os, sys, time

CONF_PATHNAME = r"/home/vds/03/oopy/oopy.ini" 

def	get_CDB_DESC(sflag = 'DEBUG'):
	if sflag == 'DEBUG' and os.environ['REMOTE_ADDR'] == '10.10.2.10':
		return	"host=127.0.0.1 dbname=contr_tst port=5432 user=smirnov"
	else:	return	"host=127.0.0.1 dbname=contracts port=5432 user=smirnov"

def	get_config (pathname = CONF_PATHNAME):
	""" Читать файл конфигурации ConfigParser	"""
	if os.access (pathname, os.F_OK):
		import ConfigParser
		config = ConfigParser.ConfigParser()
		config.read (pathname)
		return config
	else:	print 'Отсутствует файл: ', pathname, '<br />'

def     get_theform ():
	""" Читать файл параметры формы cgi.FieldStorage	"""
	theform = cgi.FieldStorage ()
	request = {}
	for field in theform.keys():
		if theform.has_key(field):
			if  type(theform[field]) != type([]):
				request[field] = theform[field].value
			else:   request[field] = theform.getlist(field)
	return  request

def	ppobj (obj = None, level = 0):
	""" Вывод содержимого объекта (obj)	"""
	if not level:	print	"<pre>"
	if type(obj) == dict:
		print "dict {}"
		for key, val in obj.iteritems():
			print	"\t"*level, "%16s :" % key,
			ppobj(val, level+1)
	elif type(obj) == list:
		print "list ()"
		for o in obj:
			print	"\t"*(2 +level),
			ppobj(o, level+1)
	elif type(obj) == tuple:
		print "tuple []"
		for o in obj:	ppobj(o, level+1)
	elif obj:
		print	obj
	else:	pass
	if not level:	print	"</pre>"

def	out_select(sname, res, cols = None, key = None, sopt = None, sfirst = None):
	""" Вывод селектора: <select  name='sname' sopt> ... </select>
	sname	наименования селектора
	res	([наименования полей], [(значения полей данных),(...), ...])
	cols	[наименования полей для отображения] cols[0] - код (при отсутствии cols == res[0])
	key	[выбранное значение]
	sopt	параметры, например: 'onchange="document.myForm.submit ()"'
	sfirst	первая строка "<option value='код'> наименование </option>", если " " - "<option value=''> </option>" 
	"""
#	sopt = """onchange="check_user('ZZZ')" """
	if sopt:
		print   """<select name='%s' class='ssel' %s >""" % (sname, sopt)
	else:	print   """<select name='%s' class='ssel'>""" % sname
#	print	"""<select name='%s' onchange="check_user('ZZZ')">"""
	if not cols:	cols = res[0]
	if sfirst:
		if sfirst == ' ':
			print   "<option value=''> </option>"
		else:	print	sfirst
	elif not key:	print	"<option value=''> </option>"
	dsr = res[0]
	for sr in res[1]:
		if key != None and key == sr[dsr.index(cols[0])]:
			print	"<option value='%s' selected >" % str(sr[dsr.index(cols[0])]),
		else:	print	"<option value='%s'>" % str(sr[dsr.index(cols[0])]),
		for j in range(1, len(cols)):
			print str(sr[dsr.index(cols[j])]),
		print	"</option>"
	print	"</select>"

def	wdgerror(tit = None, txt = None, obj = None, iddom = None):
	if iddom:	_iddom = iddom
	else:		_iddom = 'error'
	out_widget ('error', tit, txt, obj, iddom = _iddom)

def	wdgwarnn(tit = None, txt = None, obj = None, iddom = None):
	if iddom:	_iddom = iddom
	else:		_iddom = 'warnn'
	out_widget ('warnn', tit, txt, obj, iddom = _iddom)

def	out_headform (tit = None, txt = None, sright = None, iddom = None):
	_sright = sright
	_iddom = iddom
	out_widget('wform', tit, txt, sright = _sright, iddom = _iddom,  head = True)

def	out_widget (wclass = 'wbox', tit = None, txt = None, obj = None, sright = None, head = False, iddom = None):
	if not iddom:	iddom = 'widget'
	print	"""~%s|<div class='%s' style='background-color: #a9a;'>""" % (iddom, wclass)
	if tit:
		if wclass == 'error':	bgcolor = "#ee8888"
		elif wclass == 'wbox':	bgcolor = "#bbbbdd"
		elif wclass == 'wform':	bgcolor = "#aaaacc"
		elif wclass == 'warnn':	bgcolor = "#ee8844"
		else:	bgcolor = "#bbbbdd"
		if not sright:	sright = ''
		else:	sright = ''.join(["<td align='right'>", sright, "<td>"])	# ../img/close_btn1.gif	# ../img/delt2.png
		print	"""<div style='padding: 1px; margin: 0px; border: thin solid #668; background-color: %s;'><table width=100%% cellpadding=2 cellspacing=0><tr>
			<td class='tit'>&nbsp;%s</td>%s<td align='right'><img onclick="$('#%s').html('')" src='../img/error24.png' /></td></tr></table></div>""" % (bgcolor, tit, sright, iddom)
	if txt:	print	txt
	if obj:	ppobj(obj)
	if not head:	print	"</div>"

list_sformat = ['%Y-%m-%d', '%d-%m-%Y', '%d-%m-%y', '%m-%d-%y', '%m-%d-%Y']
def	sfdate (sdate, jfs = 0):
	""" Преобразовать строку даты в формат записи в БД	"""
	if not sdate.strip():	return
	ts = None
	sdate = sdate.strip().replace(' ', '-').replace('/', '-').replace('.', '-').replace(',', '-').replace(':', '-')
	try:
		ts = time.strptime(sdate, list_sformat[jfs])
	except ValueError:
		jfs += 1
		if jfs < len(list_sformat):	return	sfdate (sdate, jfs)
	finally:
		if ts:	return	time.strftime(list_sformat[0], ts)

def	out_sfdate(date, sformat = None):
	""" Преобразовать формат даты из '%Y-%m-%d' в '%Y-%m-%d'	"""
	if not date:	return	''
	if not sformat:	sformat = '%d-%m-%Y'
	try:
		ts = time.strptime(str(date), '%Y-%m-%d')
		return  time.strftime(sformat, ts)
	except ValueError:	return  ''

def	strub (irub):
	""" Преобразуеи чмсло (int) в строку (например: 1234567 => '1 234 567'	"""
	sss = []
	if type(irub) != type(1):	return	''
	for j in range(4):
		if irub > 1000:
			ooo = irub % 1000
			sss.insert(0, '%03d' % ooo)
			irub /= 1000
		else:
			sss.insert(0, '%d' % irub)
			break
	return	' '.join(sss)
'''
def	ptext (s, mylps = None):
	""" Убрать из строки лишние символы перед записью в БД	"""
	lps = [["'",'"']]
	if not s:	return	''
	s = s.strip()
	if not s:	return	''
	for ps in lps:
		s = s.replace(ps[0], ps[1])
	return	s
'''
def	ptext (ss, mylps = None):
	""" Убрать из строки лишние символы перед записью в БД	"""
	lps = [["'",'"']]
	if not ss:	return	''
	ss = ss.strip()
	if not ss:	return	''
	if mylps:
		if isinstance(mylps[0], (list, tuple)):	# Если список списков
			ls = list(mylps)		# => [mylps, lps] переопределяет lps
			ls.extend(lps)
			lps = ls
		#	lps.extend(mylps)		# => [lps, mylps]
		else:	lps.append(mylps)		# Одиночная подмена
	for p,s in lps:
		ss = ss.replace(p,s)
	return	ss

def	diff_d2r (cols, dct, rqst, ignore = None):
	""" Сравнеие данных пользователя <rqst> с записью в БД <dct>
	cols	- список полей для проверки,
	dct	- dct = idb.get_dict(...),
	rqst	- rqst = request 
	"""
	res = {}
	for c in cols:
		if rqst.has_key(c) and rqst[c].strip():
			if c in ['cdate', 'period_valid']:
				val = sfdate(rqst[c])
			else:	val = rqst[c].strip()
			if str(dct[c]) != val:	#rqst[c].strip():
				res[c] = val	#rqst[c].strip()
	return	res

def	diff_update (update, dct, rqst, ignore = None):
	""" Сравнеие данных пользователя <rqst> с записью в БД <dct>
	update	- dict список полей для проверки и формат данных,
	dct	- dct = idb.get_dict(...),
	rqst	- rqst = request 
	"""
	res = []
	for c in update.keys():
		if not c in dct.keys():		continue
		if rqst.has_key(c) and rqst[c].strip():
			if c in ['cdate', 'period_valid']:
				val = sfdate(rqst[c])
			elif c == 'bm_status':
				if rqst[c].isdigit() and int(rqst[c]) > 0:
					ival = int(rqst[c])
					if ival > 2048 and ival < 4096:	#2048:
						res.append("%s = %d" % (c, 0x3f & dct[c]))
					else:	res.append("%s = %d" % (c, dct[c] | ival))
				continue
			else:	val = rqst[c].strip()
			if update[c][:2] == 's:':	val = val[:int(update[c][2:])]
			if str(dct[c]) != val:	res.append("%s = '%s'" % (c, val))
		elif dct[c] and c != 'bm_status':
			res.append("%s = NULL" % c)
	return	res

if __name__ == "__main__":
	print	out_sfdate('2011-11-22')
	print	"strub:", strub(1234567)
	'''
	res = (['cod', 'name'], [(0,'No'),(1, 'Yes')])
	res = (['cod', 'name'], [('vcontracts','Договора (контракты)'),('vorganizations', 'Данные по Организациям')])
	out_select('sname', res, cols = None, key = 'vorganizations', sopt = None, sfirst = "<option value=''> Все </option>")
	'''
	print	"ptext > [%s]" % ptext(None)
	print	"ptext > [%s]" % ptext("")
	print	"ptext > [%s]" % ptext("'None'")
