#!/usr/bin/python -u
# -*- coding: utf-8 -*-

import	sys

LIBRARY_DIR = r"/home/smirnov/pylib"    # Путь к рабочей директории (библиотеке)
sys.path.insert(0, LIBRARY_DIR)
import	dbtools
import	send_mail

IDB_VMS = None		# Id DataBase vms_ws
IDB_CNTR = None		# Id DataBase contracts
ids_db = {
	#	'vms':	'host=10.40.25.176 dbname=vms_ws port=5432 user=vms',
		'vms':	'host=10.10.2.147 dbname=vms_ws port=5432 user=vms',	# DBMS-Test:
		# 'cntr':	'host=212.193.103.20 dbname=contracts port=5432 user=smirnov',
		'cntr':	'host=10.10.2.241 dbname=contracts port=5432 user=smirnov',	# Houm
	}

def	email_notice(inn):
	""" Оповещение отправлять каждую неделю информацию по нерабочим ТС, 
	оператор Технотрейд-НН, на  info@tehtd.ru, karta@tehtd.ru	"""
	global	IDB_CNTR

#	print "Оповещение INN", inn
	query = """SELECT t.id_org, gosnum, o.bname, t.p_org, bm_wtime FROM transports t 
		JOIN organizations o ON o.id_org = t.id_org 
		JOIN atts a ON a.autos = t.id_ts 
		WHERE t.p_org = 913 AND bm_wtime = 0 ORDER BY id_org;"""
	if not IDB_CNTR:	IDB_CNTR = dbtools.dbtools(ids_db['cntr'])

	rows = IDB_CNTR.get_rows(query)
	autos = ['\t']
	tolist = ['info@tehtd.ru', 'karta@tehtd.ru',
		'a.skameykin@rnc52.ru',
	#	'v.smirnov@rnc52.ru',
	]
	org = 0
	for r in rows:
		id_org, gosnum, bname = r[:3]
		if id_org != org:
			autos.append(bname)
			org = id_org
		autos.append('\t' + gosnum)
	#	print id_org, gosnum, bname, r[3:]
	#if autos:	print '\n\t'.join(autos)
	send_mail.send_notice(tolist, autos, addf=False)	# Отправка уведомлений об отсутствии данных от ТС

def	test():
	for c in ids_db.keys():		print c, ids_db[c], dbtools.dbtools(ids_db[c])

if __name__ == '__main__':
	print """ Оповещение отправлять каждую неделю информацию по нерабочим ТС, 
	оператор Технотрейд-НН, на  info@tehtd.ru, karta@tehtd.ru	"""
	#help(send_mail)
	#test()
	email_notice(123456)
