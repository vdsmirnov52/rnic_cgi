#!/usr/bin/python
# -*- coding: utf-8 -*-
"""	Утилита crontab	health_status_TC.py
	1 12 * * *	/home/smirnov/MyTests/health_status_TC.py -simo /home/smirnov/MyTests/CGI/curr_status_TC.html > /home/smirnov/MyTests/log/health_status_TC.py.log
	Сбор данных для формирования отчета 'Справка по состоянию работоспособности ТС '
"""
import  os, sys, time,  getopt

LIBRARY_DIR = r"/home/smirnov/pylib"	# Путь к рабочей директории (библиотеке)
sys.path.insert(0, LIBRARY_DIR)
import  dbtools

query_get_tc = """
select code, sum(r1) as r1, sum(r2) as r2, count(*) as r3
from(
select code,
  (case when not days is null  then 1 else 0 end) as r2,
  (case when not days is null and (days-days2)=0 then 1 else 0 end) as r1
from
(select ss.code, t.id, t.regnum, nd.id, nd.code as nd_code, ndd.createddatetime, t.createdby_id,
  (extract(day from ndd.createddatetime)+extract(month from ndd.createddatetime)*30+extract(year from ndd.createddatetime)*365) as days,
  (extract(day from to_timestamp('%s 12:00:00','DD.MM.YYYY HH24:MI:SS'))+extract(month from to_timestamp('%s 12:00:00','DD.MM.YYYY HH24:MI:SS'))*30+extract(year from to_timestamp('%s 12:00:00','DD.MM.YYYY HH24:MI:SS'))*365) as days2
from transport  t
inner join subsystem ss on ss.id=t.subsystem_id
 inner join abstracttransportlink atl on atl.transport_id=t.id
 inner join transport2devicelink t2d on t2d.id=atl.id
 inner join navigationdevice nd on nd.id=t2d.device_id
 left join nddatacacheentry nddc on nddc.deviceid=nd.id
 left join nddata ndd on ndd.id=nddc.lastdata_id
where t.isdeleted=0
  and (t.discarddate is null or t.discarddate<='%s 12:00:00')
  and not t.subsystem_id is null
  and (atl.begindate<='%s 12:00:00' or atl.begindate is null)
  and (atl.enddate>='%s 12:00:00' or atl.enddate is null)
  and t.createdby_id in (select user_id from usergrouplink where group_id in (select primarygroupid from users where id=4023218516))
  ) rr
  ) rr2
  group by code
  order by code
;"""
#	CREATE UNIQUE INDEX ON ref_ts_stat (when_formed, bm_ssys);
#ttt = ['Выходило на связь за последние сутки', 'Выходило на связь за весь период', 'Введено в систему']

#	Соответствие между кодами подсистем vms_ws: subsystem[code] <=> contracts: subsys[code] (subsys[pnc_labl])
ss_codes = { 'Тестирование БО': 1, 'ПП': 2, 'ША': 4, 'ЖКХ': 8, 'СОГ': 16, 'ОВ': 32, 'ЖКХ-М': 64, 'СМП': 128, 'ЧТС': 256, 'ПП ЦДС (тестовая)': 2048, 'ПП НПАП (тестовая)': 4096,
	'ВТ': 8192, 'СХ': 16384, 'ЛХ': 32768,
	'СП': 65536, 'ДТ-НН': 131072, 'ДТ-НО': 262144,
	}

def	get_status_tc (sdate):
	""" Сбор данных за сутки <sdate>	"""
	qqq = query_get_tc % (sdate, sdate, sdate, sdate, sdate, sdate)
	rows = DB_vms.get_rows(qqq)
	codes = []
	sr1 = sr2 = sr3 = 0
	res = {}
	if rows:
		for r in rows:
			code, r1, r2, r3 = r
			codes.append(code)
		#	print	code, (r1, r2, r3)
			if code in ss_codes.keys():
				res[ss_codes[code]] = (r1, r2, r3)
			else:	print "\tUnknown code:\t", code, (r1, r2, r3)
			sr1 += r1
			sr2 += r2
			sr3 += r3
		res[0] = sr1, sr2, sr3
		return res
	else:	print qqq

#	 when_formed | bm_ssys | last_day | all_time | into_system
def	res_save (sdate, res):
	""" Сохранить результаты в таблице 'ref_ts_stat' БД 'contracts'.
	DB_cont = 'host=127.0.0.1 dbname=contracts port=5432 user=smirnov'
	"""
	qus = []
	print '\r', sdate
	ksort = res.keys()
	ksort.sort()
	ksort.reverse()
	jbm_ssys = 0x020000
	for code in ksort:
		if code == 0:	jcode = jbm_ssys
		else:
			jcode = code
			jbm_ssys += code
		qus.append("INSERT INTO ref_ts_stat (when_formed, bm_ssys, last_day, all_time, into_system) VALUES ('%s', %d, %d, %d, %d)" % (
			sdate, jcode, res[code][0], res[code][1], res[code][2]))
#		print	code, res[code]
#	print ''
	if not DB_cont.qexecute (";\n".join(qus)):
		print ";\n".join(qus)
		sys.exit(-1)

inv_ss_codes = {
	1: 'Тестирование навигационного оборудования',
	2: 'Подсистема мониторинга и управления пассажирскими перевозками',
	4: 'Подсистема мониторинга и управления школьными автобусами',
	8: 'Подсистема мониторинга транспортных средств жилищно-коммунального хозяйства',
	16: 'Подсистема мониторинга перевозок специальных, опасных, крупноргабаритных грузов',
	32: 'Данные мониторинга и управления ТС органов государственной власти',
	64: 'Данные о категории транспортных средств вывозящих ТБО-Мусоровозы(Экология)',
	128: 'Подсистема мониторинга транспорта медицины катастроф, скорой помощи',
	256: 'Данные мониторинга транспортных средств  частных пользователей',
	2048: 'Данные поступающие в РНИС из Центральная диспетчерская служба городского пассажирского транспорта Н.Новгорода (тестовая)',
	4096: 'Данные поступающие в РНИС от  НижегородПассажирАвтоТранс (тестовая)',
	8192: 'Данные мониторинга водного транспорта', 
	16384: 'Данные мониторинга сельскохозяйственной техники',
	32768: 'Данные мониторинга техники лесного хозяйства', 
	65536: 'Данные мониторинга транспорта физкультурно-оздоровительных комплексов',
	131072: 'Данные мониторинга Дорожной техники Нижнего Новгорода',
	262144: 'Данные мониторинга Дорожной техники Нижегородской области',
	}
ssys_codes = [2, 4, 8,16,128]
order_codes = [2, 4, 8,16,128, 32, 256, 8192, 16384, 32768, 65536, 131072, 262144, 2048, 4096, 1,]

def	res_print (sdate, res, fout = sys.stdout):
	""" Формировать текстовый файл	"""
	if FILE_out:
		fout = FILE_out
	else:	fout = sys.stdout
	ssys_res = [0, 0, 0]
	print >> fout, "\n\tСправка по состоянию работоспособности ТС РНИС на", sdate, 'г.'
#	inv_ss_codes = dict((v,k) for k, v in ss_codes.iteritems())
#	for j in inv_ss_codes.keys():	print inv_ss_codes[j]
	ksort = order_codes
	print >> fout, '-'*64
	print >> fout,	"  За сутки  : За все время :  В системе   :  Подсистема"
	print >> fout, '-'*64
	for code in ksort:
	#	if code == 0:	continue
		if not (code and res.has_key(code)): continue
	#	if code in ssys_codes:	print code
		j = 0
		for x in res[code]:
			if code in ssys_codes:	ssys_res[j] += x
			j += 1
			print >> fout,	"%11d : " % x,
		print >> fout,	inv_ss_codes[code]
	print >> fout, '-'*64
	for x in ssys_res:	print >> fout,  "%11d : " % x,
	print >> fout,	"Итого за Подсистемаы"
	
	for x in res[0]:	print >> fout,	"%11d : " % x,
	print >> fout,	"Итого за РНИС"
	print ssys_res

def	res_prn_html (sdate, res):
	""" Формировать HTML файл	"""
	if FILE_out:
		fout = FILE_out
	else:	fout = sys.stdout
	ssys_res = [0, 0, 0]
	stime = time.strftime("%H:%M", time.localtime (time.time ()))
#	print >> fout, "<h3>Справка по состоянию работоспособности ТС РНИС на", stime, sdate, "г.</h3>"
	print >> fout, "<h3>Статистика о подключенных к региональной навигационно-информационной системе<br> Нижегородской области транспортных средств на", stime, sdate, "г.</h3>"
#	inv_ss_codes = dict((v,k) for k, v in ss_codes.iteritems())
	ksort = order_codes
#	print >> fout, "<table width=720px><tr><th width=70%> Подсистемы РНИС </th><th> За сутки </th><th> За все время </th><th> В системе </th></tr>"
	print >> fout, "<table style=''width: 740px; font-size: 14px;><tr><th width=70%> Подсистемы РНИС </th><th> За сутки </th><th> Выходило на связь с 01.03.2017 </th><th>  Введено в систему </th></tr>"
	for code in ksort:
	#	if code == 0:	continue
		if not (code and res.has_key(code)): continue
		print >> fout, "<tr><td>", inv_ss_codes[code], "</td>",
		j = 0
		for x in res[code]:
			if code in ssys_codes:	ssys_res[j] += x
			j += 1
			print >> fout, "<td align='right'>", x, "</td>",
		print >> fout, "</tr>"
	print >> fout, "<tr class='tit'><td>Итого за РНИС</td>",
	for x in res[0]:	print >> fout, "<td align='right'>", x, "</td>",

	print >> fout, "<tr class='tit'><td>Итого за подистемы</td>",
	for x in ssys_res:	print >> fout, "<td align='right'>", x, "</td>",
	print >> fout, "</tr></table>"

def	res_prn_csv (sdate, res):
	""" Формировать CSV файл	"""
	ssys_res = [0, 0, 0]
	fout = open (r"/tmp/temp_status_TC.csv", 'w')	#health_status_TC.csv", 'w')
	stime = time.strftime("%H:%M", time.localtime (time.time ()))
	print >> fout, '"Справка по состоянию работоспособности ТС РНИС на %s %s г.";;;;' % (stime, sdate)
	print >> fout, '"Статистика о подключенных к региональной навигационно-информационной системе\n Нижегородской области транспортных средств на %s %s г.";;;;' % (stime, sdate)
	print >> fout, '"Подсистема"; "Выходило на связь за последние сутки"; "Выходило на связь за весь период"; "Введено в систему"'
#	inv_ss_codes = dict((v,k) for k, v in ss_codes.iteritems())
	ksort = order_codes
	for code in ksort:
	#	if code == 0:	continue
		if not (code and res.has_key(code)): continue
		print >> fout, '"%s";' % inv_ss_codes[code],
		j = 0
		for x in res[code]:
			if code in ssys_codes:	ssys_res[j] += x
			j += 1
			print >> fout, "%d;" % x,
		print >> fout, ""
	print >> fout, '"Итого за РНИС";',
	for x in res[0]:	print >> fout,"%d;" % x,
	print >> fout, ""
	print >> fout, '"Итого за подсистемаы";',
	for x in ssys_res:	print >> fout,"%d;" % x,
	print >> fout, ""
	fout.close()
#	iconv -f utf-8 -t cp1251 /tmp/health_status_TC.csv > ~/health_status_TC.csv
	os.system ('/usr/bin/iconv -f utf-8 -t cp1251 /tmp/temp_status_TC.csv > %s' % fcsv_name)
	
def	get_history_tc (sdate, days = 30):
	""" Сбор данных за период от <sdate> <days> назад	"""
	stm = time.strptime(sdate, "%d.%m.%Y")
	jtm = time.mktime(stm)
#	if FL_email:	fout = open (fcsv_name, 'w')	#r"/tmp/health_status_TC.csv", 'w')
	for j in xrange(days):
		jsdate = time.strftime("%d.%m.%Y", time.localtime(jtm))
	#	print	jsdate
		res = get_status_tc(jsdate)
		if DB_cont:
			res_save (jsdate, res)
		else:
			if not FL_html:	res_print (jsdate, res)
		if FL_html:	res_prn_html (jsdate, res)
		if FL_email:	res_prn_csv (sdate, res)
		jtm -= 24*3600
#	if FL_email:	fout.close()

fcsv_name = r"/tmp/health_status_TC.csv"
bases = {
	'vms_ws': 'host=10.40.25.176 dbname=vms_ws port=5432 user=vms',
	'wtm': 'host=127.0.0.1 dbname=worktime port=5432 user=smirnov',
	'contt': 'host=127.0.0.1 dbname=contr_tst port=5432 user=smirnov',
	'contr': 'host=127.0.0.1 dbname=contracts port=5432 user=smirnov',
	}

list_sformat = ['%d.%m.%Y', '%Y.%m.%d', '%d.%m.%Y', '%d.%m.%y', '%m.%d.%y']
def	sfdate (sdate, jfs = 0):
	""" Преобразовать строку даты в формат записи в БД	"""
	if not sdate.strip():	return
	ts = None
	sdate = sdate.strip().replace(' ', '.').replace('/', '.').replace('-', '.').replace(',', '.').replace(':', '.')
	try:
		ts = time.strptime(sdate, list_sformat[jfs])
	except ValueError:
		jfs += 1
		if jfs < len(list_sformat):	return	sfdate (sdate, jfs)
	finally:
		if ts:	return	time.strftime(list_sformat[0], ts)

def	outhelp():
	print """
	Утилита crontab
        Сбор данных для формирования отчета 'Справка по состоянию работоспособности ТС '
	-h	Справка
	-t	Контроль соединений с БД
	-s	Сохранять в БД %s
	-i	Формировать HTML
	-o	файл вывода [stdout]	/home/smirnov/MyTests/CGI/health_status_TC.html
	-m	отправить файл по e-mail
	-d DD.MM.YYYY	Дата сбора данных 
	-l ddd		за сколько дней собирать даные от -d DD.MM.YYYY -l ddd дней назад
	""" % bases['contr']

DB_vms =	None
DB_cont =	None
FILE_out =	None
HTML_head =	"""<!DOCTYPE html>\n<html><head>\n<meta charset='utf-8'>
	<meta	HTTP-EQUIV='Cache-Control: max-age=3600, must-revalidate'>
	<title>Curr TC</title>\n<link rel='stylesheet' type='text/css' href='/css/style.css' />\n</head><body style='font-size: 14px;'><center>"""

if __name__ == "__main__":
	FL_help = False
	FL_test = False
	FL_save = False
	FL_html = False
	FL_email = False
	str_date = None
	str_days = None
	file_name = None
	days = 1
	try:
		optlist, args = getopt.getopt(sys.argv[1:], 'htsimd:l:o:')
		for o in optlist:
			if o[0] == '-h':	FL_help = True
			if o[0] == '-t':	FL_test = True
			if o[0] == '-s':	FL_save = True
			if o[0] == '-i':	FL_html = True
			if o[0] == '-m':	FL_email = True
			if o[0] == '-d':	str_date = sfdate(o[1])
			if o[0] == '-l':	str_days = o[1]
			if o[0] == '-o':	file_name = o[1]

		if file_name:
			sdir, sfile = os.path.split(file_name)
		#	print file_name, sdir, sfile
			if os.path.isdir(sdir):
				FILE_out = open(os.path.join(sdir, sfile), 'w')
				if not FILE_out:
					print "\n\tНе могу открыть файл:", os.path.join(sdir, sfile)
				elif FL_html:	print >> FILE_out, HTML_head
			else:	print "\n\tОтсутствует путь", sdir, "к файлу", sfile
		if FL_test:
			for key in bases:
				print key, "\t=", bases[key], '\t>',
				ddb = dbtools.dbtools (bases[key], 0)
				if not ddb.last_error:	print 'OK'
		elif FL_help:	outhelp()
		else:
			if not str_date:	str_date = time.strftime("%d.%m.%Y", time.localtime(time.time()))
			if str_days and str_days.isdigit():	days = int(str_days)
			if FL_save:
				DB_cont = dbtools.dbtools (bases['contr'])	# contr
			DB_vms = dbtools.dbtools (bases['vms_ws'], 1)
	#		get_status_tc(time.strftime("%d.%m.%Y", time.localtime(time.time())))
			get_history_tc (str_date, days)
		if FILE_out:
			if FL_html:	print >> FILE_out, "</center></body></html>"
			FILE_out.close()
		if FL_email:
			import	send_mail
			toaddrs = [
			#	"a.kovalev@rnc52.ru",	# Александр Ковалев
				"a.larin@rnc52.ru",
			#	"kalyaev@inform.kreml.nnov.ru",
				"kalyaev@mininform.kreml.nnov.ru",
				"ya.ivan.kalyaev@yandex.ru",
			#	"ganin@mininform.kreml.nnov.ru",
			#	"a.morozov@rnc52.ru",	# Морозов Алексей Евгеньевич 
				"v.smirnov@rnc52.ru",
				]
			files_list = [fcsv_name]
			if FILE_out:	files_list.append (os.path.join(sdir, sfile))
			ssub = "РНИС Справка по состоянию ТС от %s г." % time.strftime("%d.%m.%Y", time.localtime(time.time()))
			send_mail.send_file (toaddrs, files_list, body=ssub, subject=ssub)
		#	for to in toaddrs:
		#		send_mail.send_file (to, files_list, body=ssub, subject=ssub)	# os.path.join(sdir, sfile), body=ssub, subject=ssub)
	except:
		exc_type, exc_value = sys.exc_info()[:2]
		print "EXCEPT:", exc_type, exc_value
