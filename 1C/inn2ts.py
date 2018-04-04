#!/usr/bin/python -u
# -*- coding: utf-8 -*-

#       Обработка файла выгрузки 1С 
#       Формат - тексторый, 3 колонки ( ИНН\tНаименование\tВладелец или компания ), разденитель '\\t'


import	os, time, sys
import	getopt

LIBRARY_DIR = r"/home/smirnov/pylib"          # Путь к рабочей директории (библиотеке)
sys.path.insert(0, LIBRARY_DIR)
import	dbtools

def	get_file_1C (fname):
	""" Чтение файла выгрузки 1С
        Формат:\tИНН\tНаименование\tВладелец (компания)
	"""
	lautos = []
	dict_inn = {}
	if not os.path.isfile(fname):
		print "Файл %s отсутствует!"
		return
	f = open (fname, 'r')
	ffs = f.read()
	fs = ffs.split('\n')
	j = 0
	for s in fs:
		ss = s.strip()
		if not ss:	continue
		if ss[0] == '#':	continue
		lss = ss.split('\t')
		if len(lss) != 3 or not lss[0].isdigit():
			print lss
			continue
		inn, gon, owm = lss[:3]
	#	print inn, gon, owm
		if dict_inn.has_key(inn):
			dict_inn[inn].append(gon)
		else:
			dict_inn[inn] = [owm, gon]
		j += 1
#		if j > 222:	break
	print "TS:", j, "\tlen(dict_inn):", len(dict_inn)
	return	dict_inn

def	prn_dict_inn(dict_inn):
	for k in dict_inn.keys():
		print k, dict_inn[k][0], "\n\t",
		for g in dict_inn[k][1:]:
			print g,
		print ""
	print "len(dict_inn):", len(dict_inn)

"""	Коды статуса машины БД contracts transports.bm_status
    2 | Есть в 1С
    4 | Есть Контракт
    8 | Данные для Счета
   16 | Выставлен Счет
   32 | Скрыть статистику
 1024 | Блокирована
 2048 | Удалена
"""
def	set_fis_1C (dict_inn):
	print "set_fis_1C"
	for k in dict_inn.keys():
#		print k, '\t', dict_inn[k][0]
		dorg = contr.get_dict("SELECT * FROM organizations WHERE inn = %s" % k)
		if not dorg:
			print "NOT\t", k, '\t', dict_inn[k][0], ">\t",
			for g in dict_inn[k][1:]:
				print g,
			print ''
			continue
	#	query = "UPDATE transports SET vin = '%s' WHERE gosnum IN ('%s')" % (k, "', '".join(dict_inn[k][1:]))
		query = "UPDATE transports SET bm_status = (2 | bm_status) WHERE gosnum IN ('%s')" % "', '".join(dict_inn[k][1:])
		if not contr.qexecute(query):
			print dorg['id_org'], query

def	set_fis_contr(swhere = None):
	""" Изменить статус для работающих машин	"""
	if not swhere:
		rows = wtm.get_rows("SELECT regnum FROM vn2regnum")
	else:	rows = wtm.get_rows("SELECT regnum FROM vn2regnum WHERE %s" % swhere)
	if rows:
		lregnum = []
		for r in rows:
			lregnum.append(r[0])
		if not swhere:
			query = "UPDATE transports SET bm_status = (4 | bm_status) WHERE gosnum IN ('%s')" % "', '".join(lregnum)
		else:	query = "UPDATE transports SET bm_status = (8 | bm_status) WHERE gosnum IN ('%s')" % "', '".join(lregnum)
	#		query = "UPDATE transports SET pts = 'is_contr' WHERE gosnum IN ('%s')" % "', '".join(lregnum)
	#	else:	query = "UPDATE transports SET sregistr = '%s' WHERE gosnum IN ('%s')" % (swhere, "', '".join(lregnum))
		if not contr.qexecute(query):
			print query
	else:	print "set_fis_contr", swhere


def	get_vnav2gnum (ddb, swhere = None):	# Читать из vms_ws.vnav2gnum 
	if not swhere:
		swhere = ''
	query = "SELECT * FROM vnav2gnum %s" % swhere
	print	query
	rows = ddb.get_rows(query)
	return	rows

def	isnone(v):
	if not v:
		return 'NULL'
	else:	return "'%s'" % v

desp = {}
bases = {
	'vms_ws': 'host=10.40.25.176 dbname=vms_ws port=5432 user=vms',
#	'vms_ws': 'host=212.193.103.9 dbname=vms_ws port=5432 user=vms',
#	'vtst': 'host=10.40.25.180 dbname=vms_ws port=5432 user=vms',
	'wtm': 'host=127.0.0.1 dbname=worktime port=5432 user=smirnov',
	'contr': 'host=127.0.0.1 dbname=contracts port=5432 user=smirnov'}

def	check_bm_ssys ():
	""" Привязать transports.bm_ssys <= organizations.id_org	"""
	contr = dbtools.dbtools(bases['contr'])
	res = contr.get_rows("SELECT id_ts, gosnum, t.bm_ssys, o.bm_ssys FROM transports t LEFT JOIN organizations o ON t.id_org = o.id_org WHERE t.bm_ssys =0")
	if res:
		for r in res:
			id_ts, gosnum, tbm_ssys, obm_ssys = r
			if not obm_ssys:	continue
			print gosnum, "\t", contr.qexecute("UPDATE transports SET bm_ssys = %d WHERE id_ts = %d" % (obm_ssys, id_ts))

def	outhelp():
	print """
	Обработка файла выгрузки 1С 
	Формат - тексторый, 3 колонки ( ИНН\tНаименование\tВладелец или компания ), разденитель '\\t'
	-t	Контроль соединений с БД
	-f	Путь к файлу списка машин в формате (ИНН Наименование Владелец)
	-cf	Поиск ТС (навигаторов) для машин из файла 1С
	"""

if __name__ == "__main__":
	sttmr = time.time()
	file_name = None
	new_autos = None
	Fch_ts = False
	Ftest = False

	print "Start %i" % os.getpid(), sys.argv, time.strftime("%Y-%m-%d %T", time.localtime(sttmr))
	try:
		optlist, args = getopt.getopt(sys.argv[1:], 'tcf:')
	#	dbwtm = dbtools.dbtools (bases['wtm'], 1)
	#	dbvms = dbtools.dbtools (bases['vms_ws'], 1)
		for o in optlist:
			if o[0] == '-t':	Ftest = True
			if o[0] == '-f':	file_name = o[1]
			if o[0] == '-c':	Fch_ts = True
		'''
		if Fch_ts:
			print	"\tПоиск ТС (навигаторов)"
			rows = get_vnav2gnum (dbvms)
			if rows:
				check_new_nav (dbwtm, rows)
		'''
		if Ftest:
			for key in bases:
				print key, "\t=", bases[key], '\t>',
				ddb = dbtools.dbtools (bases[key], 0)
				if not ddb.last_error:	print 'OK'
			check_bm_ssys ()
		elif file_name:
			res = get_file_1C (file_name)
			if not Fch_ts:
				prn_dict_inn(res)
			else:
				contr = dbtools.dbtools(bases['contr'])
				set_fis_1C (res)
				wtm = dbtools.dbtools(bases['wtm'])
				set_fis_contr()
				set_fis_contr("work_time > 0.1")
		else:
			outhelp()
	except	getopt.GetoptError:	outhelp()
	if new_autos:
		print "new_autos"
		for sa in new_autos:
			print sa
	print "dt %9.4f" % (sttmr - time.time())
