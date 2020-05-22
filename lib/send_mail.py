#!/usr/bin/python -u
# -*- coding: utf-8 -*-

import	smtplib
from	email.mime.multipart import MIMEMultipart
from	email.mime.text import MIMEText
from	email.mime.base import MIMEBase
from	email.utils import COMMASPACE
from	email import Encoders
import	base64

def	send_file (toaddr, files, body = None, subject = None, fromaddr=None):
	if not fromaddr:	fromaddr = "rnic-nn@rnc52.ru"
	if not subject:	subject = "SUBJECT OF THE MAIL"

	msg = MIMEMultipart()
	msg['From'] = fromaddr
	if type(toaddr) == type(""):
		msg['To'] = toaddr
	else:	msg['To'] = COMMASPACE.join(toaddr)
#	'=?utf-8?B?' +base64_encode($subject)
	msg['Subject'] = "=?utf-8?B?" + base64.b64encode(subject)	+"?="
#	msg['Subject'] = "=?UTF-8?B?RndkOiDQodC40YHRgtC10LzRiyDRgNCw0LTQuNC+0YPQv9GA0LDQstC70LU=?="
#	msg['Subject'] = subject
	if not body:	body = "YOUR MESSAGE HERE"
	msg.attach(MIMEText(body, 'plain', 'utf-8'))
	
	# Compose attachment
	for filepath in files:
		basename = os.path.basename(filepath)
	#	print filepath, filepath[-4:]
		if filepath[-4:] in ['html', '.htm']:
			part = MIMEBase("text", "html; charset=utf-8")
		elif filepath[-4:] in ['.csv', '.txt']:
			part = MIMEBase("text", 'plain; charset=utf-8')
		else:	part = MIMEBase('application', "octet-stream")
		part.set_payload(open(filepath,"rb").read() )
		Encoders.encode_base64(part)
		part.add_header('Content-Disposition', 'attachment; filename="%s"' % basename)
		msg.attach(part)

	server = smtplib.SMTP('10.10.2.201', 25)
	server.starttls()
#	server.login(fromaddr, mypass)
	text = msg.as_string()
#	print msg
#	print text
#	return
	rsend = server.sendmail(fromaddr, toaddr, text)
	rquit = server.quit()
#	print "rsend:", rsend, "rquit:", rquit
	return rsend

import	random
def	send_mail (toaddr, files, body = None, subject = None, fromaddr = "rnic-nn@rnc52.ru"):
	if not subject:	subject = "SUBJECT OF THE MAIL"
	if not body:	body = "YOUR MESSAGE HERE"
	boundary = "="*10 + str(int(random.random()*1e20)) +"=="
	msg = []
	msg.append ('Content-Type: multipart/alternative; boundary="%s"' % boundary)
	msg.append ('MIME-Version: 1.0')
	msg.append ('From: %s' % fromaddr)
	if type(toaddr) == type(""):
		msg.append ('To: %s' % toaddr)
	else:	msg.append ('To: %s' % COMMASPACE.join(toaddr))
	msg.append ('Subject: ' + "=?utf-8?B?" + base64.b64encode(subject) + "?=")
	msg.append ('\n--' + boundary)

	msg.append ('Content-Type: text/plain; charset="utf-8"\nMIME-Version: 1.0\nContent-Transfer-Encoding: base64\n')
	msg.append (base64.b64encode(body))
	msg.append ('\n--' + boundary)
	text = "\n".join(msg)
	print text
	server = smtplib.SMTP('10.10.2.201', 25)
	server.starttls()
	rsend = server.sendmail(fromaddr, toaddr, text)
	rquit = server.quit()
	return rsend

def	send_notice (tolist, autos):
	""" Отправка уведомлений об отсутствии данных от ТС	"""
	if not autos:	return
#	print tolist
#	tolist = toaddrs	### DEBUG
	files = [r"/home/smirnov/MyTests/CGI/Bid_for_diaghostics.docx"]
	ssubj = "«РНИЦ Нижегородской области» уведомляет"
	shead = """Уважаемый абонент!\n
	АО «РНИЦ Нижегородской области» уведомляет Вас, что по транспортным средствам
	Вашей организации от оборудования ГЛОНАСС не поступают навигационные данные в
	Региональную навигационно-информационную систему Нижегородской области (РНИС)

	Государственные номера транспортных средств и время последней передачи данных:
	"""
	sbutt = """\n
	Просим Вас сообщить причину отсутствия передачи навигационных данных от указанных
	транспортных средств и сроки возобновления передачи данных.
	В случае, если указанные транспортные средства эксплуатируются, а причина отсутствия
	передачи навигационных данных Вам не известна, просим Вас заполнить заявку на
	проведение диагностических работ (во вложении) и прислать нам подписанную скан-копию данной заявки.
	
	По всем вопросам просим обращаться в техническую поддержку АО «РНИЦ Нижегородской области»
	по тел. (831) 261-75-97 (доб. 307, 308) или e-mail: support@rnc52.ru.
	Образцы документов находятся по адресу http://rnc52.ru/documents
	"""
	sbody = shead + "\n\t".join(autos) + sbutt
	return	send_file (tolist, files, body=sbody, subject=ssubj, fromaddr='support@rnc52.ru')

def	send_sorry (tolist, autos):
	""" Отправка уведомлений о регламентных работах 	"""
	if not autos:	return
	ssubj = "«РНИЦ Нижегородской области» уведомляет о изменении стоимости сервисных работ"
	shead = """Уважаемый абонент!\n
	Новый "ПРЕЙСКУРАНТ сервисных работ" находятся по адресу http://rnc52.ru/documents
	"""
	'''
	ssubj = "«РНИЦ Нижегородской области» уведомляет о регламентных работах"
	shead = """Уважаемый абонент!\n
	Сообщаем Вам, что с 18.00 06.10.2017 по 22.00 06.10.2017 специалистами 
	АО «РНИЦ Нижегородской области» будут выполняться профилактические работы.\n
	Ввиду вышеизложенного, возможны перерывы в работе сервисов.\n
	Приносим свои извинение за предоставленные неудобства.
	"""
	shead = """Добрый день!\n
	Настоящим уведомляем, что в ночь с 12 на 13 декабря 2018г технической службой АО "РНИЦ Нижегородской Области" 
	планируется проведение аварийно-восстановительных работ на оборудовании Центрального узла с остановкой сервиса.\n
	Расчетное время проведения работ: с 23ч00м 12.12.2018 по 06ч00м 13.12.2018
	"""
	'''
	sbody = shead + "\n\t".join(autos)
#	print sbody
	return	send_file (tolist, [], body=sbody, subject=ssubj)

def	send_reminder (tolist, autos):
	""" НАПОМИНАНИЕ О ПЕРЕЧИСЛЕНИИ ОПЛАТЫ ПО ДОГОВОРУ	"""
	ssubj =	"«РНИЦ Нижегородской области» НАПОМИНАНИЕ О ПЕРЕЧИСЛЕНИИ ОПЛАТЫ ПО ДОГОВОРУ"
	shead = """Уважаемый абонент!\n
	По заключенному Вами с АО "РНИЦ Нижегородской области" договору срок оплаты за январь истёк 25.02.2020г.
	Просим оплатить задолженность в кратчайшие сроки.\n
	Если у Вас возникли вопросы по задолженности, обращайтесь по телефону 8(831)261-75-96 (доб. 313).
	"""
	sbody = shead + "\n\t".join(autos)
#	print sbody
	return	send_file (tolist, [], body=sbody, subject=ssubj)
	
import	os, time, sys

toaddrs = [
	#	"d.kuchin@rnc52.ru",
	#	"r.burygin@rnc52.ru",
		"v.smirnov@rnc52.ru",
		"vdsmirnov152@yandex.ru",
	#	"vdsmirnov52@gmail.com",
	#	"a.ilicheva@rnc52.ru", "a.skameykin@rnc52.ru",	# Анна, Саша Скамейкин
	#	"a.kovalev@sumtel.ru",
	#	"a.larin@sumtel.ru",
	#	"sneg@pbox.ru",		# Alex Yevdokimov
		]

def	send_sssssssssss():
	""" Рассылка сообщений абонентам	"""
	import	dbtools

#	СМУ ПП 
	qqq = "select id_org, post, email FROM vpersons WHERE id_org IN (select id_org FROM organizations WHERE bm_ssys = 2 AND id_org IN (select DISTINCT id_org FROM contracts  WHERE ctype = 8)) AND email IS NOT NULL ORDER BY id_org;"
#	Всем
	qqq = "select id_org, post, email FROM vpersons WHERE id_org IN (select id_org FROM organizations WHERE id_org IN (select DISTINCT id_org FROM contracts  WHERE ctype = 8)) AND email IS NOT NULL ORDER BY id_org;"
	print qqq

	idb = dbtools.dbtools("host=127.0.0.1 dbname=contracts port=5432 user=smirnov")
	rows = idb.get_rows(qqq)
	if not rows:	return
	id_oooo = 0
	j = 0
	for r in rows:
		id_org, post, email = r
		if id_oooo == id_org:	continue
		if not email.strip() or len(email.strip()) < 10:	continue
		rc = idb.get_row("SELECT count(*) FROM wtransports WHERE id_org = %s" % id_org)	# наличие активного транспорта
		if not rc or rc[0] == 0:	continue
		j += 1
		if j < 553:	continue
		id_oooo = id_org
		print	j, id_org, id_oooo, post, email, rc,
		print	send_reminder ([email.strip()], ['rnic-nn@rnc52.ru'])
	#	send_sorry([email.strip()], ['###'])
	#	if id_oooo > 22:	break
		time.sleep(113)
	
if __name__ == "__main__":
	filepath = [r"/home/smirnov/MyTests/CGI/curr_status_TC.html", r"/tmp/temp_status_TC.csv"]
	'''
	fname = r"/home/smirnov/MyTests/CGI/curr_status_TC.txt"
	fname = r"/home/smirnov/MyTests/CGI/curr_status_TC.html"
	sss = file(fname)
	lll = []
	j = 0
	ssub = None
	for s in sss:
		j += 1
		if j == 2:	ssub = s.strip()	#	continue
		lll.append (s)
	body = ''.join(lll)
	'''
	send_sssssssssss()
#	send_reminder (toaddrs, ['rnic-nn@rnc52.ru'])
#	send_sorry (toaddrs, ['rnic-nn@rnc52.ru'])
	'''
	sdate = time.strftime("%d.%m.%Y", time.localtime(time.time()))
	ssub = "Работает Робот %s г." % sdate
	send_mail (toaddrs,  filepath, body="Работает Робот", subject=ssub)
	'''
#	send_file (toaddrs,  filepath, body="Работает Робот", subject=ssub)
#	send_notice (toaddrs, toaddrs)
#	send_file (toaddrs, filepath, body="Работает Робот", subject=ssub)
#	for to in toaddrs:	send_file (to, filepath, body="ZZZZZZZZZZ body", subject=ssub)
