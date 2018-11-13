#!/usr/bin/python
# -*- coding: utf-8 -*-
"""	Утилита crontab	contr_status_TC.py
	Сбор данных для формирования отчета 'Справка по состоянию работоспособности ТС' БД 'contracts'
"""
import  os, sys, time,  getopt

LIBRARY_DIR = r"/home/smirnov/pylib"	# Путь к рабочей директории (библиотеке)
sys.path.insert(0, LIBRARY_DIR)
import  dbtools

#	Соответствие между кодами подсистем vms_ws: subsystem[code] <=> contracts: subsys[code] (subsys[pnc_labl])
ss_codes = { 'Тестирование БО': 1, 'ПП': 2, 'ША': 4, 'ЖКХ': 8, 'СОГ': 16, 'ОВ': 32, 'ЖКХ-М': 64, 'СМП': 128, 'ЧТС': 256, 'ПП ЦДС (тестовая)': 2048, 'ПП НПАП (тестовая)': 4096,
	'ВТ': 8192, 'СХ': 16384, 'ЛХ': 32768,
	'СП': 65536, 'ДТ-НН': 131072, 'ДТ-НО': 262144,
	}

curr_data =	time.strftime("%Y-%m-%d 00:00:00", time.localtime(time.time()))
query_get_tc = """ SELECT id_ts, bm_ssys, bm_status, bm_wtime, last_date FROM wtransports WHERE bm_status & 3072 = 0 ORDER BY bm_ssys; """

def	get_status_tc (sdate):
	""" Сбор данtных за сутки <sdate>	"""
	qqq = query_get_tc	# % (sdate, sdate, sdate, sdate, sdate, sdate)
	rows = DB_cont.get_rows(qqq)
	codes = {}
	sr1 = sr2 = sr3 = 0
	res = {}
	jall = jsys = 0
	if rows:
		for r in rows:
			r1 = r2 = r3 = r4 = 0
			id_ts, bm_ssys, bm_status, bm_wtime, last_date = r
	#		print id_ts, bm_ssys, bm_status, bm_wtime, last_date
			jall += 1
			r1 += 1
			if last_date:
				if str(last_date) > curr_data:	#'2018-01-22 00:00:00':
					r2 += 1
				else:	r3 += 1
			else:	r4 += 1
			for jss in inv_ss_codes.keys():
				if jss & bm_ssys:
					if jss in ssys_codes:	jsys += 1
					if codes.has_key(jss):
						codes[jss][0] += r1	# Всего
						codes[jss][1] += r2	# Сегодня
						codes[jss][2] += r3	# Ранее
						codes[jss][3] += r4	# Никогда
					else:	codes[jss] = [r1, r2, r3, r4]
	#		if jall > 111:	break
	#		print jall, codes
	#		continue
	#	out_text (jall, jsys, codes)
		return jall, jsys, codes
	else:	print qqq

query_region = """ SELECT id_ts, bm_ssys, bm_status, bm_wtime, last_date, region FROM wtransports WHERE bm_status & 3072 = 0 ORDER BY region, bm_ssys; """
#	stat_ts_log	(ctm, y, m, d, bm_ssys, total, today, earlier, never, rem)
#	select bm_ssys, sum(total) FROM stat_ts_log WHERE d = 18 GROUP BY bm_ssys ORDER BY bm_ssys;

def	get_region_ts ():
	print	""" Статистика по районам	"""
	curr_tm = int (time.time())
	rows = DB_cont.get_rows (query_region)
	if not rows:	return
	old_region = -1
	codes = {}
#	j = jc = 0
	for r in rows:
	#	j += 1
		id_ts, bm_ssys, bm_status, bm_wtime, last_date, region = r
		if not bm_ssys in order_codes and bm_ssys & 1:
			bm_ssys -= 1
		if old_region == -1:	old_region = region
		if old_region != region:
			querys = ["DELETE FROM stat_ts_log WHERE region = %d AND %s" % (old_region, time.strftime("y = %Y AND m =%m AND d = %d", time.localtime(curr_tm)))]
			for k in codes.keys():
#				jc += codes[k]
				querys.append ("INSERT INTO stat_ts_log (region, ctm, y, m, d, bm_ssys, total) VALUES (%d, %d, %s, %d, %d)" % (old_region, curr_tm, time.strftime("%Y,%m,%d", time.localtime(curr_tm)), k, codes[k]))
			if not DB_cont.qexecute (";\n".join(querys)):
				print old_region, codes
	#		print old_region, codes
			codes = {}
			old_region = region
			codes[bm_ssys] = 1
		else:
			if codes.has_key (bm_ssys):
				codes[bm_ssys] += 1
			else:	codes[bm_ssys] = 1

	querys = ["DELETE FROM stat_ts_log WHERE region = %d AND %s" % (region, time.strftime("y = %Y AND m =%m AND d = %d", time.localtime(curr_tm)))]
	for k in codes.keys():
#		jc += codes[k]
		querys.append ("INSERT INTO stat_ts_log (region, ctm, y, m, d, bm_ssys, total) VALUES (%d, %d, %s, %d, %d)" % (region, curr_tm, time.strftime("%Y,%m,%d", time.localtime(curr_tm)), k, codes[k]))
	if not DB_cont.qexecute (";\n".join(querys)):	print old_region, codes

#	print "#"*22, j, jc, region, codes

def	out_text (jall, jsys, codes):
		print "	    Работали								 "
		print "    Всего   Сегодня     Ранее   Никогда  Наименование подсистемы		     "
		print "-------------------------------------------------------------------------------------------"
		jps = jss = 0
		for k in order_codes:
			if codes.has_key(k):
				jps += codes[k][0]
				if k in ssys_codes:	jss += codes[k][0]
				print '%9d %9d %9d %9d ' % (codes[k][0], codes[k][1], codes[k][2], codes[k][3]),
			else:	print '%9d %9d %9d %9d ' % (0,0,0,0),
			print inv_ss_codes[k]
		print "-------------------------------------------------------------------------------------------"
		print ' '*29, '%9d ' % jps, 'Итого в РНИС \t\t', (jall -jps)
		print ' '*29, '%9d ' % jss, 'Итого по подсистемам\t', (jsys - jss)


def	out_html (FILE_out, jall, jsys, codes):
	print >> FILE_out, HTML_head
	print >> FILE_out, 	"""<h3>Статистика о подключенных к региональной навигационно-информационной системе <br />
		Нижегородской области транспортных средств на %s  г.</h3>""" % time.strftime("%H:%M %d.%m.%Y", time.localtime (time.time ()))
	print >> FILE_out, "<table  cellpadding=4 cellspacing=0>"
	print >> FILE_out, "<tr><th> Всего </th><th> Сегодня </th><th> Ранее </th><th>  Никогда </th><th> Наименование подсистемы </th></tr>"
	jps = jss = 0
	for k in order_codes:
			print >> FILE_out, '<rt>',
			if codes.has_key(k):
				jps += codes[k][0]
				if k in ssys_codes:	jss += codes[k][0]
				print >> FILE_out, "<td align='right'>%d</td><td align='right'>%d</td><td align='right'>%d</td><td align='right'>%d</td>" % (codes[k][0], codes[k][1], codes[k][2], codes[k][3]),
			else:	print >> FILE_out, "<td align='right'>%d</td><td align='right'>%d</td><td align='right'>%d</td><td align='right'>%d</td>" % (0,0,0,0),
			print >> FILE_out, '<td>', inv_ss_codes[k], '</td></tr>'
	print >> FILE_out, "<rt><td class='tit' align='right' colspan=4>%d</td>" % jps, '<td class="tit"> Итого в РНИС </td></tr>'
	print >> FILE_out, "<rt><td class='tit' align='right' colspan=4>%d</td>" % jss, '<td class="tit"> Итого по подсистемам </td></tr>'
	print >> FILE_out, "</table>"
	print >> FILE_out, "</center></body></html>"

inv_ss_codes = {
	1: 'Тестирование навигационного оборудования',
	2: 'Подсистема мониторинга и управления пассажирскими перевозками',
	4: 'Подсистема мониторинга и управления школьными автобусами',
	8: 'Подсистема мониторинга транспортных средств жилищно-коммунального хозяйства',
	16: 'Подсистема мониторинга перевозок специальных, опасных, крупногабаритных грузов',
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
order_codes = [2, 4, 8,16,128, 32, 256, 8192, 16384, 32768, 131072, 262144, 65536, #2048, 4096,
		1,]

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
	print >> fout, "<table style=''width: 740px; font-size: 16px;><tr><th width=70%> Подсистемы РНИС </th><th> За сутки </th><th> Выходило на связь с 01.01.2017 </th><th>  Введено в систему </th></tr>"
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
	
fcsv_name = r"/tmp/health_status_TC.csv"
bases = {
	'wtm': 'host=127.0.0.1 dbname=worktime port=5432 user=smirnov',
	'contr': 'host=127.0.0.1 dbname=contracts port=5432 user=smirnov',
#	'contr': 'host=212.193.103.20 dbname=contracts port=5432 user=smirnov',
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
	-i	Формировать HTML
	-o	файл вывода [stdout]	/home/smirnov/MyTests/CGI/health_status_TC.html
	-m	отправить файл по e-mail
	-r	Формировать данные по регионам в stat_ts_log
	"""	# % bases['contr']

###	select * FROM atts WHERE autos IN (SELECT id_ts FROM transports WHERE id_org IN (SELECT id_org FROM organizations WHERE inn = 5251002531));
#DB_vms =	None
DB_cont =	None
FILE_out =	None
HTML_head =	"""<!DOCTYPE html>\n<html><head>\n<meta charset='utf-8'>
	<meta	HTTP-EQUIV='Cache-Control: max-age=3600, must-revalidate'>
	<title>Статистика РНИС</title>\n<link rel='stylesheet' type='text/css' href='/css/style.css' />\n</head><body style='font-size: 14px;'><center>"""

if __name__ == "__main__":
	FL_help = False
	FL_test = False
	FL_html = False
	FL_regs = False
	FL_email = False
	file_name = None
	str_date = time.strftime("%d.%m.%Y", time.localtime(time.time()))
	try:
		optlist, args = getopt.getopt(sys.argv[1:], 'htrim:o:')
		for o in optlist:
			if o[0] == '-h':	FL_help = True
			if o[0] == '-t':	FL_test = True
			if o[0] == '-r':	FL_regs = True
			if o[0] == '-i':	FL_html = True
			if o[0] == '-m':	FL_email = True
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
		elif FL_regs:	# Статистика по районам
			DB_cont = dbtools.dbtools (bases['contr'])
			get_region_ts()
		elif FL_help:	outhelp()
		else:
		#	if not str_date:	str_date = time.strftime("%d.%m.%Y", time.localtime(time.time()))
			DB_cont = dbtools.dbtools (bases['contr'])
			res = get_status_tc (str_date)
			if not res:
				print "#"*44, str_date
			else:
				jall, jsys, codes = res
				if FL_html:
					out_html (FILE_out, jall, jsys, codes)
				else:
					out_text (jall, jsys, codes)

		if FILE_out:
			if FL_html:	print >> FILE_out, "</center></body></html>"
			FILE_out.close()
		if FL_email:
			import	send_mail
			toaddrs = [
			#	"a.kovalev@rnc52.ru",	# Александр Ковалев
			#	"a.larin@rnc52.ru",
			#	"kalyaev@inform.kreml.nnov.ru",
			#	"kalyaev@mininform.kreml.nnov.ru",
			#	"ya.ivan.kalyaev@yandex.ru",
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
