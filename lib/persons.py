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
'''
 family   | character varying(32)  | Фамилия
 names    | character varying(32)  | Имя Отчество
 phones   | character varying(32)  |
 email    | character varying(64)  |
 post     | character varying(32)  | Должность
 rem      | character varying(256)
'''
CDB_DESC = cglob.get_CDB_DESC('ZZZ')

class	persons:
	idb = None
	def	__init__(self, debug = 0):
		self.idb =  dbtools.dbtools(CDB_DESC, debug)	#"host=127.0.0.1 dbname=contracts port=5432 user=smirnov", debug)
		if debug:	print "__init__ DEBUG"

	def	insert (self, SS, request):
		""" Добавить контакт	"""
		pdict = dicts.CONTRCT['persons']
	#	print	"insert_persons", request, pdict
		nams = []
		vals = []
		for k in pdict['order']:
			if request.has_key(k) and request[k].strip():
				nams.append(k)
				vals.append("'%s'" % cglob.ptext(request[k]))	#.strip())
		print	"~wform_result|"
		if nams:
			query = "INSERT INTO persons (%s) VALUES (%s);" % (', '.join(nams), ', '.join(vals))
			xnams = []
			xvals = []
			for k in ['id_contr', 'id_org']:
				if request.has_key(k) and int(request[k]) > 0:
					xnams.append(k)
					xvals.append(request[k])
			if xnams:
				query = "%s INSERT INTO person2x (%s, id_persn) VALUES (%s, (SELECT max(id_persn) FROM persons));" % (query, ', '.join(xnams), ', '.join(xvals))
			if self.idb.qexecute(query):
				print	"Ok!", self.save_history (SS, "Добавить контакт", ', '.join(vals), request)
				return	True
			else:	print	query
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

	def	update (self, SS, request):
		""" Изменить контакт	"""
		print	"~wform_result|"
		if request.has_key('id_persn') and int(request['id_persn']) > 0:
			pdict = dicts.CONTRCT['persons']
			sset = []
			for k in pdict['order']:
				if request.has_key(k) and request[k].strip():
					sset.append("%s = '%s'" % (k, cglob.ptext(request[k])))	#.strip()))
			if sset:
				query = "UPDATE persons SET %s WHERE id_persn = %s;" %(', '.join(sset), request['id_persn'])
			if self.idb.qexecute(query):
				print	"Ok!",  self.save_history (SS, "Изменить контакт id_persn: %s" % request['id_persn'], ', '.join(sset), request)
				return	True
			else:	print	query
		else:	print	"UPDATE: Нет Данных!"

	def	delete (self, SS, request):
		""" Удалить контакт	"""
		print	"~wform_result|"
		if request.has_key('id_persn') and int(request['id_persn']) > 0:
			query = "DELETE FROM persons WHERE id_persn = %s; DELETE FROM person2x WHERE id_persn = %s;" % (request['id_persn'], request['id_persn'])
			if self.idb.qexecute(query):
				print	"Ok!", self.save_history (SS, "Удалить контакт id_persn: %s" % request['id_persn'], query, request)
				return	True
			else:	print	query
		else:	print	"DELETE: Нет Данных!"
	
	def	outform (self, SS, request, referer):
		left = 220
		top = 380
		iddom = 'wform_result'
		id_persn = int(request['id_persn'])
		id_contr = int(request['id_contr'])
		id_org = int(request['id_org'])
		if (id_contr + id_org + id_persn) == 0:
			print	"~error|<div class='error'>Не достаточно данных!</div>"
		#	return
		if int(request['id_persn']) > 0:
			idb = dbtools.dbtools (CDB_DESC)	#"host=127.0.0.1 dbname=contracts port=5432 user=smirnov")
			tit = "Изменить контакт"
			sfamily = snames = sphones = semail = spost = srem = ""
			res = idb.get_table ("persons", "id_persn = %s;" % request['id_persn'])
			if res:
				d = res[0]
				r = res[1][0]
				if r[d.index('family')]:	sfamily = r[d.index('family')]
				if r[d.index('names')]:	snames = r[d.index('names')]
				if r[d.index('phones')]:	sphones = r[d.index('phones')]
				if r[d.index('email')]:	semail = r[d.index('email')]
				if r[d.index('post')]:	spost = r[d.index('post')]
				if r[d.index('rem')]:	srem = r[d.index('rem')]
			sright = """<td align='right'>
				<input type='button' class='butt' value='Сохранить изменения' onclick="set_shadow('update&table=persons&id_persn=%d&id_contr=%d&id_org=%d');" />
				<input type='button' class='butt' value='Удалить' onclick="if (confirm ('Удалить контакт?')) {set_shadow('delete&table=persons&id_persn=%d'); }" /></td>
				""" % (id_persn, id_contr, id_org, id_persn)
		else:
			tit = "Новый контакт"
			sfamily = snames = sphones = semail = spost = srem = ''
			sright = """<td align='right'>
				<input type='button' class='butt' value='Добавить контакт' onclick="set_shadow('insert&table=persons&id_persn=%d&id_contr=%d&id_org=%d');" /></td>
				""" % (id_persn, id_contr, id_org)
		bgcolor = '#aab'
		print	"""~%s|<div id='%s' style='top: %dpx; left: %dpx; position: absolute; padding: 1px; margin: 1px; text-align: left;
			min-width: 600px; border: thin solid #668; background-color: #efe;'>""" % (iddom, iddom, top, left)
		print	"""<div style='padding: 1px; margin: 0px; border: thin solid #668; background-color: %s;'><table width=100%% cellpadding=2 cellspacing=0><tr>
			<td class='tit'>&nbsp;%s</td>%s<td align='right'><img onclick="$('#%s').html('')" src='../img/delt2.png' /></td></tr></table></div>""" % (bgcolor, tit, sright, iddom)
		print	"<table width=100% cellpadding=2 cellspacing=0>"
		print	"<tr><td align='right'>Фамилия:</td><td><input type='text' size=10 name='family' value='%s' maxlength=32 /> И.О.:<input type='text' name='names' value='%s' maxlength=32 />" % (
			sfamily, snames)
		print	"<tr><td align='right'>Ph:</td><td><input type='text' size=10 name='phones' value='%s' maxlength=32 /> E-mail:<input type='text' name='email' value='%s' maxlength=64 size=44 />" % (
			sphones, semail)
		print	"<tr><td align='right'>Долж.:</td><td><input type='text' size=10 name='post' value='%s' maxlength=32 /> Прим.:<input type='text' name='rem' value='%s' maxlength=255 size=44 />" % (
			spost, srem)
		print	"</table></div>"

if __name__ == '__main__':
	print	"Test "
	person = persons(1)
	person.update(None, None)
