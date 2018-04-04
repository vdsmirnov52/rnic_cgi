#!/usr/bin/python
# -*- coding: utf-8 -*-
"""     Утилита crontab vms_copy.py - Копирование справочников из БД vms_ws -> contracts
"""
import	os, sys

LIBRARY_DIR = r"/home/smirnov/pylib"    # Путь к рабочей директории (библиотеке)
sys.path.insert(0, LIBRARY_DIR)
import  dbtools
bases = {
	'vms_ws': 'host=10.40.25.176 dbname=vms_ws port=5432 user=vms',
#	'wtm': 'host=127.0.0.1 dbname=worktime port=5432 user=smirnov',
	'contr': 'host=127.0.0.1 dbname=contracts port=5432 user=smirnov',
	}

tab_list = ['transporttype', 'navigationdevicetype', 'cellularoperator']

def	update_table (tname):
	DB_cont = dbtools.dbtools(bases['contr'])
	DB_vms = dbtools.dbtools(bases['vms_ws'])
	res = DB_vms.get_table (tname, 'id > 0 ORDER BY id')
	is_id = False
	print tname, "\t",  res[0], 'len:', len(res[1])
	d = res[0]
	jUPDATE = 0
	jINSERT = 0
	for r in res[1]:
		jcd = DB_cont.get_dict("SELECT * FROM %s WHERE id = %d" % (tname, r[d.index('id')]))
	#	print r[d.index('id')], jcd
		if jcd:
			if jcd.has_key('id_'):	is_id = True
			isup = []
			for c in d:
				if r[d.index(c)] and r[d.index(c)] != jcd[c]:
					isup.append ("%s = '%s'" % (c, str(r[d.index(c)])))
			if isup:
				query = "UPDATE %s SET %s WHERE id = %d;" % (tname, ", ".join(isup), r[d.index('id')])
				print query, DB_cont.qexecute(query)
				jUPDATE += 1
		else:
			cls = []
			vls = []
			for c in d:
				if r[d.index(c)] != None:
					cls.append(c)
					vls.append("'%s'" % str(r[d.index(c)]))
			if is_id:
				cls.append('id_')
				vls.append('(SELECT max(id_) FROM %s) +1' % tname)
			query = "INSERT INTO %s (%s) VALUES (%s);" % (tname, ", ".join(cls), ", ".join(vls))
			print query, DB_cont.qexecute(query)
			jINSERT += 1
	
	print '\tjUPDATE:', jUPDATE, '\tjINSERT:', jINSERT

def	test ():
	for key in bases:
		print key, "\t=", bases[key], '\t>',
		ddb = dbtools.dbtools (bases[key], 0)
		if not ddb.last_error:	print 'OK'
	print

if __name__ == "__main__":
	print sys.argv[1:]
	print "Обновить справочников из БД vms_ws -> contracts"
	test()
	for t in tab_list:
		update_table (t)
