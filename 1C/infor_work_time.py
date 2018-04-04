#!/usr/bin/python -u
# -*- coding: utf-8 -*-

#	Формирование файла отчета о работе транспорта

#	create VIEW vatnum AS select at.id, t.regnum, t.regnumber FROM transport t, abstracttransportlink at WHERE t.id = at.transport_id;
#	create VIEW vt2datnum AS select c.*, v.regnum, v.regnumber FROM transport2devicelink c, vatnum v WHERE c.id = v.id;
#	create VIEW vnav2gnum AS select code, imei, v.* FROM navigationdevice n, vt2datnum v WHERE n.id = v.device_id;

import	os, time, sys
import	getopt

LIBRARY_DIR = r"/home/smirnov/pylib"          # Путь к рабочей директории (библиотеке)
sys.path.insert(0, LIBRARY_DIR)
import	dbtools

desp = {}
bases = {
	'vtst': 'host=10.40.25.176 dbname=vms_ws port=5432 user=vms',
	'wtm': 'host=127.0.0.1 dbname=worktime port=5432 user=smirnov',
	'wialon': 'host=127.0.0.1 dbname=wialon port=5432 user=smirnov'}

#	CREATE VIEW vwork_ts AS SELECT lp.nm AS regnum, lp.inn, wt.* FROM work_ts wt INNER JOIN last_pos lp ON lp.id_lp = wt.id_lp;
#	SELECT * FROM work_ts WHERE id_lp NOT IN (SELECT id_lp FROM last_pos);

def	wialon_21C (swhere, fout = sys.stdout):
	""" Выгрузка ТС из БД 'wialon'	"""
	ignore_nm = [
	'А677НЕ152', 'А680НЕ152', 'АР31652', 'АУ59652', 'В247УО152', 'В763СК152', 'Е365РЕ152', 'Е428ЕК152', 'Е766ХТ152', 'К004КТ152',
	'К904ОС152', 'М024ВУ152', 'М503ММ152', 'М504ММ152', 'М509ММ152', 'М561МТ152', 'М824МТ152', 'М825МТ152', 'М826МТ152', 'М869РВ152',
	'М951ВЕ152', 'М992УР152', 'Н148ХУ152', 'Н180ХУ152', 'Н205ХУ152', 'Н430СК152', 'Н433ВН152', 'Н447ВН152', 'Н449ВН152', 'Н450ВН152',
	'Н559ВК152', 'Н563ВК152', 'Н567ВК152', 'Н569ВК152', 'Н571ВК152', 'Н572ВК152', 'Н585АР152', 'Н684ВУ152', 'Н822НА152', 'Р027СС152',
	'Т006СТ52', 'Х151СЕ52',
	]
#	swhere = "WHERE regnum IN ('O348УТ152', 'АУ33452', 'К259НХ152', 'К241НХ152', '52НН5225', '52НН5227', '52НН5227', '52НР5739', 'АА93952')"
	dbwialon = dbtools.dbtools(bases['wialon'])
#	regnum, id_lp, month, is_work, jw_time, where_set
#	query = "SELECT regnum, is_work, where_set FROM vwork_ts %s ORDER BY regnum;" % swhere
#	query = "SELECT regnum, is_work, where_set FROM vwork_ts WHERE regnum NOT IN ('%s') ORDER BY regnum;" % "', '".join(ignore_nm)
	fout.write(head_txt)
	query = "SELECT lp.nm AS regnum, is_work, where_set FROM work_ts wt INNER JOIN last_pos lp ON lp.id_lp = wt.id_lp WHERE lp.inn >0 AND lp.nm NOT IN ('%s') ORDER BY regnum;" % "', '".join(ignore_nm)
	rows = dbwialon.get_rows (query)
	if not rows:
		print 'Wialon not datas', query
		return	0
	jl = 0
	for r in rows:
		regnum, is_work, where_set = r
	#	print regnum, is_work, where_set
		if is_work == 1:
			fout.write ('"%s", True\n' % regnum)
		else:	fout.write ( '"%s", False\n' % regnum)
		jl += 1
	return	jl
	
def	create_21C (dbwtm, swhere, fout = sys.stdout):
	""" Выгрузка ТС из БД 'worktime'	"""
#	print "create_21C"
	fout.write(head_txt)
#	query = "SELECT w.*, a.regnum, a.regnumber FROM nav_work_time w, nav2regnum a WHERE w.id_auto=a.id ORDER BY w.id_auto"
	query = "SELECT * FROM vn2regnum %s ORDER BY regnum, is_work DESC" % swhere
	rows = dbwtm.get_rows (query)
	ri = dbwtm.desc
	jl = 0
	oldr = (0, 0, 0, 0.0, '', '', '')
	for r in rows:
		if (r[ri.index('regnum')] == oldr[ri.index('regnum')]):
			print	oldr[ri.index('regnum')], oldr[ri.index('is_work')], "\t>>>", r[ri.index('regnum')], r[ri.index('is_work')]
			if r[ri.index('is_work')] <= oldr[ri.index('is_work')]:	continue
		jl += 1
		if not r[ri.index('regnum')]:
			sregnum = r[ri.index('regnumber')]
		else:	sregnum = r[ri.index('regnum')]
		if r[ri.index('is_work')]:
			fout.write ('"%s", True\n' % sregnum)
		else:	fout.write ( '"%s", False\n' % sregnum)
		oldr = r
	return	jl

def	outhelp():
	print """ infor_work_time.py [Опции]	Формирование данных о работе машин за месяц
	Опции:
	-t	Тестирование соединений с Базами данных
	-o	файл, куда положить результат (по умолчание info_work-YYYY-nm.csv) 
	-f	файл - список машин из 1С
	-h	Настоящее сообщение
	"""

def	get_file_1C (fname):
	lautos = []
	if not os.path.isfile(fname):
		print "Файл '%s' отсутствует!" % fname
		return
	f = open (fname, 'r')
	sfs = f.read()
	fs = sfs.split('\n')
	if 'tbeg' in fs[0]:
		stbeg = fs[0].split('"')[1]
	if 'tend' in fs[1]:
		stend = fs[1].split('"')[1]
	print stbeg, stend
	for s in fs[2:]:
		if not s.strip():	continue
		lautos.append (s.strip()[1:-1])
	return stbeg, stend, lautos

def test_file_1c(dbwtm, lst):
	""" Анализ файла от 1С. Поиск и удаление дубликатных ГОС номеров. 	"""
	#	./infor_work_time.py -tf 27-04-2017.csv
	j = 0
	lst_regnum = []
	ddb = dbtools.dbtools (bases['vtst'])
	for l in lst[2]:
		'''
	#	query = "SELECT * FROM vn2regnum WHERE regnum = '%s'" % l
		query = "SELECT * FROM nav2regnum WHERE regnum = '%s'" % l
		rows = dbwtm.get_rows (query)
		'''
		rows = dbwtm.get_table ('nav2regnum', "regnum = '%s'" % l)
		if not rows:
#			print l, j
			lst_regnum.append(l)
		elif len(rows[1]) > 1:
			res = ddb.get_table('vvv', "regnum = '%s'" % l)
			if not res:
				print "regnum isn't in vvv\t", l
				continue
			for i in xrange(len(res[0])):	print res[0][i], res[1][0][i], ";\t",
			print "\tlen.res\t", len(res[1])
			'''
			'''
			dw = rows[0]
			dr = res[0]
			for r in rows[1]:
				if res[1][0][0] and res[1][0][0] == r[0]:
					rvvv = r[:]
					print ">>",
				else:	rddd = r[:]
			if rvvv and rvvv[dw.index('stat')] != None:
				query = ""
				stat = rvvv[dw.index('stat')]
				if stat == 2:	# rvvv[dw.index('stat')] and rvvv[dw.index('stat')] == 2:
					query = "DELETE FROM nav2regnum WHERE id = %d;" % rddd[dw.index('id')]
				elif stat == 0 and rddd[dw.index('stat')] == 2:
					if rvvv[dw.index('device_id')] == rddd[dw.index('device_id')]:
						query = "UPDATE nav2regnum SET stat=2, where_mod='%s' WHERE id = %d;\nDELETE FROM nav2regnum WHERE id = %d;" % (
							rddd[dw.index('where_mod')], rvvv[dw.index('id')],  rddd[dw.index('id')])
					else:	query = "UPDATE nav2regnum SET stat=1, where_mod=NULL WHERE id = %d;" % rvvv[dw.index('id')]
				elif rddd[dw.index('stat')] == -3 or rddd[dw.index('stat')] == 3:
					query = "UPDATE nav2regnum SET stat=1, where_mod=NULL WHERE id = %d;\nDELETE FROM nav2regnum WHERE id = %d;" % (
						rvvv[dw.index('id')],  rddd[dw.index('id')])
				elif stat < 0:
					query = "UPDATE nav2regnum SET stat = 1 WHERE id = %d;" % rvvv[dw.index('id')]
				#	if rddd[dw.index('stat')] == 0:		query += "DELETE FROM nav2regnum WHERE id = %d;" % rddd[dw.index('id')]
				else:	print "VVV", stat, rddd[dw.index('stat')]
				if query:
					print query, dbwtm.qexecute(query)
					continue
			j += 1
			for v in rvvv:	print "\t", v,
			print
			for v in rddd:	print "\t", v,
			print
	#		if j >22:	break
	print j
	if lst_regnum:
	#	print lst_regnum
	#	ddb = dbtools.dbtools (bases['vtst'])
		swhere = "regnum IN ('%s')" % "', '".join(lst_regnum)
		print swhere
		res = ddb.get_table('vvv', swhere, "code, imei, id, device_id, regnum, regnumber")
	#	res = ddb.get_table('vnav2gnum', swhere)
		if not res:
			print res, swhere
			return
		for r in res[1]:
			vals = []
			for v in r:
				if v:
					vals.append("'%s'" % str(v))
				else:	vals.append("NULL")
			print "INSERT INTO nav2regnum (%s, stat) VALUES (%s, 1);" % (", ".join(res[0]), ", ".join(vals))

if __name__ == "__main__":
	sttmr = time.time()
	Ftest = Fhelp = False
	swhere = ''
	file_1c = None
	print "Start %i" % os.getpid(), sys.argv, time.strftime("%Y-%m-%d %T", time.localtime(sttmr))
#	fout_name = time.strftime("info_work-%Y%m.csv", time.localtime(sttmr))
	try:
		optlist, args = getopt.getopt(sys.argv[1:], 'to:f:')
		for o in optlist:
			if o[0] == '-t':	Ftest = True
			if o[0] == '-h':	Fhelp = True
			if o[0] == '-o':	fout_name = o[1]
			if o[0] == '-f':	file_1c = o[1]

		dbwtm = dbtools.dbtools (bases['wtm'], 1)
		ssdct = dbwtm.get_dict ("SELECT * FROM session_opt LIMIT 1")
		if not ssdct:
			print 'Оштбка доступа к БД', bases['wtm']
			sys.exit()
		head_data = str(ssdct['tmbeg'])
		head_txt = 'tbeg, "%s"\ntend, "%s"\n' % (ssdct['tmbeg'], ssdct['tmend'])
		fout_name = "info_work-%s.csv" % head_data[:7]
#		fout_wlname = "info_work-%s.WL.csv" % head_data[:7]

		if Fhelp:	outhelp()
		elif Ftest:
			for key in bases:
				print key, '\t>',
				ddb = dbtools.dbtools (bases[key], 0)
				if not ddb.last_error:	print 'OK'
			if file_1c:
				test_file_1c(dbwtm, get_file_1C (file_1c))
		else:
			if file_1c:
				res = get_file_1C (file_1c)
				print file_1c	#, res
				if res:
					stbeg, stend, lautos = res
					swhere = "WHERE regnum IN ('%s')" % "','".join(lautos)
	
			if fout_name:
				print "\tSave data in file:\t", fout_name
				fout = open (fout_name, 'w')
				jl = create_21C (dbwtm, swhere, fout)
				fout.close()
				print "\tRNUC Lines:\t\t\t", jl

				fout_wlname = '%s.WLN%s' % (fout_name[:-4], fout_name[-4:]) 
				print '\tSave Wialon data in file:\t', fout_wlname
				fout = open (fout_wlname, 'w')
				jl = wialon_21C(swhere, fout)
				fout.close()
				print "\tWialon Lines:\t\t\t", jl
	except	getopt.GetoptError:	outhelp()
	print "dt %9.4f" % (sttmr - time.time())
