#!/usr/bin/python
# -*- coding: utf-8 -*-

import	sys, os
import	time

LIBRARY_DIR = r"/home/smirnov/MyTests/CGI/lib/"         # Путь к рабочей директории (библиотеке)
sys.path.insert(0, LIBRARY_DIR)

import	dicts
import	cglob
import	session
import	dbtools

CDB_DESC = cglob.get_CDB_DESC('ZZZ')

def	gen_passwd (ln = 8):
	import	string,	random
	token = "".join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for x in range(ln))
	return	token

class arms ():
	iddom = 'wform_result'
	left = 220
	top = 380
	idb = None
	def	__init__(self, debug = 0):
		self.idb =  dbtools.dbtools(CDB_DESC, debug)
		if debug:	print "__init__ DEBUG"
	'''
	id_org   | integer                | 
	id_bid   | integer                | 
	id_contr | integer                | 
	login    | character varying(32)  | 
	passwd   | character varying(32)  | 
	family   | character varying(32)  | 
	pname    | character varying(32)  | 
	post     | character varying(32)  | 
	phones   | character varying(64)  | 
	emails   | character varying(128) | 
	url      | character varying(128) | 
	tm_creat | integer                | 
	tm_send  | integer                | 
	who_send | integer                | 
	ps       | character varying(256) | 
	rem      | character varying(256) | 
	'''

	def	insert (self, SS, request):
		pdict = dicts.CONTRCT['varms']
		if request.has_key('id_org') and request['id_org'].isdigit():
			sid_org = request['id_org']
		elif not (request.has_key('login') or request.has_key('passwd') or request.has_key('family') or request.has_key('pname')):
			print "~error|<div class='error'> ARMS INSERN", request, "</div>"
		else:
			print "~error|<div class='error'>Нет дрнных!</div>"
			return
		"""
		print	"insert_arms", request, pdict
		"""
		nams = ['id_org']
		vals = [sid_org]
		if request.has_key('id_bid') and request['id_bid'].isdigit():
			nams.append('id_bid')
			vals.append(request['id_bid'])
		if request.has_key('id_contr') and request['id_contr'].isdigit():
			nams.append('id_contr')
			vals.append(request['id_contr'])

		for k in pdict['update'].keys():
			if request.has_key(k) and request[k].strip():
				nams.append(k)
				vals.append("'%s'" % cglob.ptext(request[k]))	#.strip())
		print	"~wform_result|"
		if nams:
			query = "INSERT INTO arms (%s) VALUES (%s);" % (', '.join(nams), ', '.join(vals))
			xnams = []
			xvals = []
			for k in ['id_contr', 'id_org']:
				if request.has_key(k) and int(request[k]) > 0:
					xnams.append(k)
					xvals.append(request[k])
			'''
			if xnams:
				query = "%s INSERT INTO person2x (%s, id_persn) VALUES (%s, (SELECT max(id_persn) FROM arms));" % (query, ', '.join(xnams), ', '.join(xvals))
			'''
			if self.idb.qexecute(query):
				print	"Ok!", self.save_history (SS, "Добавить АРМ", ', '.join(vals), request)
				return	True
			else:	print	query
			print query
		else:	print	"INSERT: Нет Данных!"

	def	save_history (self, SS, label, messge, request):
		user = SS.get_key('USER')
		swho_name = "%s %s" % (user['uname'], user['ufam'])
		sid_contr = sid_org = 'NULL'
		if request.has_key('id_contr') and request['id_contr'].isdigit():	sid_contr = request['id_contr']
		if request.has_key('id_org') and request['id_org'].isdigit():		sid_org = request['id_org']
		query = "INSERT INTO history (who_id, who_name, label, messge, id_contr, id_org) VALUES (%d, '%s', '%s', '%s', %s, %s);" % (user['user_id'], swho_name,
			cglob.ptext(label), cglob.ptext(messge), sid_contr, sid_org)
		return	self.idb.qexecute(query)

	def	alist (self, SS, request):
		print "alist".upper()
		tit = "Список АРМов"
		sright = """<td align='right'>
			<input type='button' class='butt' value='Добавить АРМ' onclick="set_shadow('arm_insert&table=arms&id_arm=%d&id_contr=%d&id_org=%d');" /></td>
			"""# % (iid_arm, iid_contr, iid_org)
		bgcolor = '#aab'
		print	"""~%s|<div id='%s' style='top: %dpx; left: %dpx; position: absolute; padding: 1px; margin: 1px; text-align: left;
			min-width: 600px; border: thin solid #668; background-color: #efe;'>""" % (self.iddom, self.iddom, self.top, self.left)
		print	"""<div style='padding: 1px; margin: 0px; border: thin solid #668; background-color: %s;'><table width=100%% cellpadding=2 cellspacing=0><tr>
			<td class='tit'>&nbsp;%s</td>%s<td align='right'><img onclick="$('#%s').html('')" src='../img/delt2.png' /></td></tr></table></div>""" % (bgcolor, tit, sright, self.iddom)
		iid_org = int(request['id_org'])
		res = self.idb.get_table('arms', 'id_org=%d ORDER BY family' % iid_org)
		if res:
			print	"<div style='padding: 2px;'><table id='varms_%05d' width=100%% cellpadding=4 cellspacing=0>" % iid_org
			d = res[0]
			for r in res[1]:
				print """<tr id='%05d' class='line' onclick="$('#varms_%05d tr').removeClass('mark'); $(this).addClass('mark'); set_shadow('arm_blank&id_arm=%d');">""" % (
					r[d.index('id_arm')], iid_org, r[d.index('id_arm')])
				print "<td>", r[d.index('login')], "<td>", r[d.index('passwd')]
				print "<td>", r[d.index('family')], r[d.index('pname')], r[d.index('post')]
				print "<td>", r[d.index('phones')]
			#	print r
			print	"</table></div>"
		else:	print "Пусто</div>"

	'''
	def	update (self, SS, request):
		print "~error|<div class='error'>UPDATE</div>"

	def	delete (self, SS, request):
		print "~error|<div class='error'>DELETE</div>"
	'''
	def	outform (self, SS, request, referer):
		""" Показать форму регистрации АРМ	"""
		print "outform", request, referer
		iid_contr = iid_arm = 0 
		if request.has_key('id_contr'):		iid_contr = int(request['id_contr'])
		if request.has_key('id_arm'):		iid_arm = int(request['id_arm'])
		iid_org = int(request['id_org'])
		if (iid_contr + iid_arm + iid_org) == 0:
			print "~error|<div class='error'>Не достаточно данных!</div>"
			return
		sfamily = spname = sphones = semail = spost = srem = slogin = ""
		spasswd = gen_passwd ()
		if iid_arm > 0:
			tit = "Изменить АРМ"
			sfamily = spname = sphones = semail = spost = srem = ""
			res = self.idb.get_table ("arms", "id_arm = %s;" % request['id_arm'])
			if res:
				d = res[0]
				r = res[1][0]
				if r[d.index('sn_bid')]:
					sn_bid = r[d.index('sn_bid')]
				else:	sn_bid = ' '
				if r[d.index('login')]:	slogin = r[d.index('login')]
				if r[d.index('passwd')]:	spasswd = r[d.index('passwd')]
				if r[d.index('family')]:	sfamily = r[d.index('family')]
				if r[d.index('pname')]:		spname = r[d.index('pname')]
				if r[d.index('phones')]:	sphones = r[d.index('phones')]
				if r[d.index('email')]:	semail = r[d.index('email')]
				if r[d.index('post')]:	spost = r[d.index('post')]
				if r[d.index('rem')]:	srem = r[d.index('rem')]
			sright = """<td align='right'>
				<input type='button' class='butt' value='Сохранить изменения' onclick="set_shadow('arm_update&table=arms&id_arm=%d&id_contr=%d&id_org=%d');" />
				<input type='button' class='butt' value='Удалить' onclick="if (confirm ('Удалить АРМ?')) {set_shadow('arm_delete&table=arms&id_arm=%d'); }" /></td>
				""" % (iid_arm, iid_contr, iid_org, id_arm)
			ssn_bid = "<td>Заявка: <b>%s</b></td>" % sn_bid
		else:
			tit = "Новый АРМ"
			ssn_bid = "<td>Заявка: <input type='text' size=10 name='sn_bid' value='%s' maxlength=32 /></td>" % ""
			sright = """<td align='right'>
			<input type='button' class='butt' value='Добавить АРМ' onclick="set_shadow('arm_insert&table=arms&id_arm=%d&id_contr=%d&id_org=%d');" /></td>
			""" % (iid_arm, iid_contr, iid_org)
		bgcolor = '#aab'
		print	"""~%s|<div id='%s' style='top: %dpx; left: %dpx; position: absolute; padding: 1px; margin: 1px; text-align: left;
			min-width: 600px; border: thin solid #668; background-color: #efe;'>""" % (self.iddom, self.iddom, self.top, self.left)
		print	"""<div style='padding: 1px; margin: 0px; border: thin solid #668; background-color: %s;'><table width=100%% cellpadding=2 cellspacing=0><tr>
			<td class='tit'>&nbsp;%s</td>%s%s<td align='right'><img onclick="$('#%s').html('')" src='../img/delt2.png' /></td></tr></table></div>""" % (bgcolor, tit, ssn_bid, sright, self.iddom)
		print	"<table width=100% cellpadding=2 cellspacing=0>"
		print	"""<tr><td align='right'>Логин:</td><td><input type='text' size=12 name='login' value='%s' maxlength=32 /> Пароль: <input type='text' size=12 name='passwd' value='%s' maxlength=32 />
			""" % (slogin, spasswd)
		#	&nbsp;&nbsp;&nbsp; Ph: <input type='text' size=16 name='phones' value='%s' maxlength=32 />""" % (slogin, spasswd, sphones)
		print	"""<tr><td align='right'>Фамилия:</td><td><input type='text' size=12 name='family' value='%s' maxlength=32 /> &nbsp;&nbsp;&nbsp; И.О.: <input type='text' size=12 name='pname' value='%s' maxlength=32 />
			&nbsp;&nbsp;&nbsp; Долж.: <input type='text' size=10 name='post' value='%s' maxlength=32 />""" % (sfamily, spname, spost)
		print	"<tr><td align='right'>Ph:</td><td><input type='text' size=12 name='phones' value='%s' maxlength=32 />  &nbsp; E-mail: <input type='text' name='email' value='%s' maxlength=64 size=44 />" % (
			sphones, semail)
		'''
		print	"<tr><td align='right'>Долж.:</td><td><input type='text' size=10 name='post' value='%s' maxlength=32 /> Прим.:<input type='text' name='rem' value='%s' maxlength=255 size=44 />" % (
			spost, srem)
		'''
		print	"</table></div>"

def	blank (SS, idb, request):
	query = "SELECT a.*, o.fname AS oname, c.cnum, b.bid_num FROM arms a LEFT JOIN vorganizations o ON a.id_org = o.id_org LEFT JOIN contracts c ON a.id_contr = c.id_contr LEFT JOIN bids b ON a.id_bid = b.id_bid "
	row = idb.get_row (query +"WHERE id_arm = %s" % request['id_arm'])
	if not row:
		print "blank", request
		return
	d = idb.desc
#	for j in range (len(d)):	print d[j], row[j], "<br>"
#	print d
	print """<center><h2>АО «РНИЦ Нижегородской области»</h2><br /> <h3>Информация для подключения АРМ диспетчера <br />
		к «Региональной навигационно-информационной системе Нижегородской области» (РНИС) </h3><br /><br /></center>"""
	print "<!--div style='align-self: right; border: solid 1px black; background-color: #ffa; padding: 22px'-->"
	print "<div style='align: right; padding: 22px'>"
	print "<table cellpadding=2 cellspacing=2 >"
	print "<tr><td align='right' width=22%%>Наименование организации:</td><td><b>%s</b></td></tr>" % row[d.index('oname')]
	if row[d.index('sn_bid')]:
		ssn_bid = row[d.index('sn_bid')]
	else:	ssn_bid = ""
	print "<tr><td align='right'>№ Заявки на подключению к РНИС:</td><td><b>%s</b></td></tr>" % ssn_bid	#row[d.index('bid_num')]
	if row[d.index('url')]:
		surl = row[d.index('url')]
	else:	surl = "http://monitoring.rnc52.ru/"	#"http://212.193.103.6/"
	print "<tr><td align='right'>WEB интерфейс:</td><td><b>%s</b></td></tr>"  % surl	#row[d.index('url')]
	print "<tr><td align='right'>Логин:</td><td><b>%s</b></td></tr>" % row[d.index('login')]
	print "<tr><td align='right'>Пароль:</td><td><b>%s</b></td></tr>" % row[d.index('passwd')]
	print "</table>"
	print """<br /><br />
	<p><b>Внимание: Данная информация является конфиденциальной. Передача логина/пароля третьим лицам без согласия АО «РНИЦ Нижегородской области» запрещена.	</b></p>
	<p>Будьте внимательны при наборе логина/пароля. При неправильном вводе данных больше 3-х раз, доступ к web-интерфейсу будет заблокирован.
	При необходимости сменить пароль, просьба отправить запрос по электронной почте в свободной форме по адресу «rnic-nn@rnc52.ru».</p>
	<p>Приложение: «Руководство пользователя. «РНИС Нижегородской области». Web-клиент» на 13-ти листах.	</p>
	"""
	print "</div>"
	user = SS.get_key('USER')
#	print user
	sn = user['uname'].split()
	sio = ""
	for s in sn:	sio += s[:2] +"."
	print """<pre><br />
	Пароль выдал:                               %s %s 

	тел.:(831) 261-75-96(97), доб.307
	</pre>""" % (user['ufam'], sio)	#user['uname'])
#	print sn, sio

if __name__ == '__main__':
	print "TEST arms"
	arms =  arms(1)
	arms.outform (None, None, None)
