#!/usr/bin/python -u
# -*- coding: utf-8 -*-
"""	Демон	ytest.py
	Передача данных о Пассажирских перевозках в Yandex
	nohup /home/smirnov/MyTests/Yandex/ytest.py > /home/smirnov/MyTests/log/ytest.log &
"""
import	os, sys, time
import	urllib, json
import	requests

LIBRARY_DIR = r"/home/smirnov/MyTests/CGI/lib/"
sys.path.insert(0, LIBRARY_DIR)

import	dbtools

DBRCV = dbtools.dbtools('host=212.193.103.20 dbname=receiver port=5432 user=smirnov')
DBGEO = dbtools.dbtools('host=212.193.103.21 dbname=geonornc52ru port=5432 user=smirnov')

routes = {
	"222т": ["Н253УР152"], 
	"245":	["АУ23352", "Н258УР152", "АУ23252", "АУ53152", "ВА03352", "ВС17716", "ВА03452", "АУ23552", "АУ23652"],
	"235":	["Н246УР152", "Н247УР152", "Н248УР152", "Н254УР152"],
	}

def	get_route (routes, gosnum):
	for k in routes.keys():
		if gosnum in routes[k]:	return	k
	return	"###"

def	get_data (routes, clid = 'nijniyoblast'):
	gnum_list = []
	for k in routes.keys():		gnum_list.extend(routes[k])
	swhere  = "('%s')" % "', '".join(gnum_list)
#	print swhere
	rid = DBRCV.get_row ("SELECT max(id_dp) FROM vdata_pos WHERE gosnum IN %s" % swhere)
	print "rid:", rid
	rows = DBRCV.get_rows ("SELECT * FROM vdata_pos WHERE id_dp > %s AND gosnum IN %s" % (rid[0], swhere))
	d = DBRCV.desc
#	print "DBRCV.desc", d
	iddp = rid[0]
	for j in xrange (22*10):	#555):
		time.sleep(.3)
		rows = DBRCV.get_rows ("SELECT * FROM vdata_pos WHERE id_dp > %s AND gosnum IN %s ORDER BY ida, t" % (iddp, swhere))
		idd = ""
		list_out = []
		if rows:
			for r in rows:
				if not r[d.index('x')]:		continue
				if r[d.index('id_dp')] > iddp:	iddp = r[d.index('id_dp')]
				if str(r[d.index('idd')]) != idd:
					if list_out:	list_out.append("</track>")
					route = get_route (routes, r[d.index('gosnum')])
					device = "HTC Diamond"	# Тип устройства, на котором запущены мобильные Яндекс.Карты.
					if r[d.index('ytype')]:
						vtype = r[d.index('ytype')]
					else:	vtype = "bus"
				#	list_out.append ("""<track uuid="%s" deviceid="%s" softid="Yandex Maps" softver="2.10" category="s" route="%s" vehicle_type="bus">""" % (str(r[d.index('idd')]), device, route))
					list_out.append ("""<track uuid="%s" deviceid="%s" softid="Yandex Maps" softver="2.10" category="s" route="%s" vehicle_type="%s">""" % (str(r[d.index('idd')]), device, route, vtype))
					idd = str(r[d.index('idd')])
			#	print r[d.index('t')], r[d.index('id_dp')], r[d.index('x')], r[d.index('y')], r[d.index('sp')], r[d.index('marka')]	# r[d.index('')]
			#	print r[d.index('t')], r[d.index('id_dp')], r[d.index('ida')], r[d.index('idd')], r[d.index('code')], r[d.index('gosnum')]	# r[d.index('')]

				list_out.append ("""\t<point latitude="%f" longitude="%f" avg_speed="%d" direction="%d" time="%s"/>""" % (
					float(r[d.index('y')]), float(r[d.index('x')]), int(r[d.index('sp')]), int(r[d.index('cr')]), time.strftime("%d%m%Y:%H%M%S", time.gmtime (r[d.index('t')])) ))
			print	time.strftime("%d.%m.%Y %T \t", time.localtime(time.time())), len (list_out),	#\t'	#"*"*11
			if list_out:
				list_out.append("</track>")
			#	print "\n".join(list_out)
				save_file (list_out, clid)
			#	break

def	save_file (list_out, clid = 'nijniyoblast'):
	""" Отправить данные Yandex	"""
        headers = {"Expect": None}
	data = ['<?xml version="1.0" encoding="utf-8"?><tracks clid="%s">' % clid]
	data.extend (list_out)
	data.append ('</tracks>')
#	print "\n".join(data), "\n", "#"*22
	try:
		r = requests.post("http://extjams.maps.yandex.net/mtr_collect/1.x/", data={"data": "\n".join(data), "compressed": 0}, headers=headers)
		print "\tyandex:", r, r.text,
		'''
		time.sleep(1)
		r = requests.post("https://www.bustime.ru/api/upload/yproto/nizhniy-novgorod/", data={"data": "\n".join(data), "compressed": 0}, headers=headers)
		print "\tbustime:", r.text,
		'''
		print clid
		
	except:
		exc_type, exc_value = sys.exc_info()[:2]
		print	"EXCEPT save_file", str(exc_type), exc_value
	return
	'''
	head = """compressed=0&data=<?xml version="1.0" encoding="utf-8"?>\n<tracks clid="nijniyoblast">\n"""
#	track = """<track uuid="0d63b6deacb91b00e46194fac325b72a" deviceid="HTC Diamond" softid="Yandex Maps" softver="2.10" category="s" route="190Б" vehicle_type="bus">"""
#	point = """<point latitude="55.716759" longitude="37.687881" avg_speed="53" direction="242" time="22042019:121045"/>"""
	fname = r'/tmp/data_yndex.xml'
	os.system("echo "" > %s" % fname)
	fout = open (fname, 'rb+')
	fout.write (head)
	fout.write ("\n".join(list_out))
	fout.write ("\n</tracks>\n")
	fout.close ()
#	os.system("cat %s" % fname)
#	cmnd = """curl -H "Expect:" --data @%s http://tst.extjams.maps.yandex.net/extjams_collect/""" % fname
#	cmnd = """curl -H "Expect:" --data @%s http://tst.extjams.maps.yandex.net/mtr_collect/1.x/""" % fname
	cmnd = """curl -H "Expect:" --data @%s http://212.193.103.21/cgi-bin/03.cgi""" % fname
	print cmnd
	os.system(cmnd)
	nn_pavlovo, nn_gorodets и nn_vyksa
	'''

inn2clid = {
	5243019838: 'nn_arzamas',	# МУП "АПАТ" Арзамас
	5249006828: 'nn_dzerzhinsk',	# МУП "Экспресс" Дзержинск	WialonHost
	5245014521: 'nn_bogorodskoe',	# МУП "Богородское ПАП"
	5246034418: 'nn_bor',		# МУП "Борское ПАП"
	5229006724: 'nn_sergach',	# МП"Сергачский автобус"
	5249076222: 'nn_dzerzhinsk',	# ООО "Орбита"
	5249084953: 'nn_dzerzhinsk',	# ООО "Орбита-2"
	5249061106: 'nn_dzerzhinsk',	# ООО "ДПП"
	5249066619: 'nn_dzerzhinsk',	# ООО "ДПП плюс"
	524928382620: 'nn_dzerzhinsk',	# ИП Вавилова Т.В.
	524900992249: 'nn_dzerzhinsk',	# ИП Лазарев Сергей Юрьевич
	524908186307: 'nn_dzerzhinsk',	# ИП Сафин Халит Мустафинович
	5249120827: 'nn_dzerzhinsk',	# ООО "Тройка"
	5249138831: 'nn_dzerzhinsk',	# ООО "Компания Тройка"
	5249066601: 'nn_dzerzhinsk',	# ООО "Транслайн плюс"
	5249057251: 'nn_dzerzhinsk',	# ООО "Транслайн"
	5249050619: 'nn_dzerzhinsk',	# ООО "Континент"
	5247048220: 'nn_vyksa',		# МУП "Выксунское ПАП"	858
	5252022315: 'nn_pavlovo',	# МУП "Павловское ПАП"		WialonHost	568
	5252010951: 'nn_pavlovo',	# ООО "Квант" 5252010951	WialonHost	938
	5252012557: 'nn_pavlovo',	# ООО "РусАвтоЛайн"		WialonHost	927
	5252028596: 'nn_pavlovo',	# ООО "Автотайм"	928
	5248024888: 'nn_gorodets',	# МУП "Городецпассажиравтотранс"	924
	5248016213: 'nn_gorodets',	# ООО "Экипаж"	921
	5254000797: 'nn_sarov',		# МУП "Горавтотранс" Саров
	}


def	update_ts (inns):
	""" Обновить списки транспорта в dbname=geonornc52ru	"""
#	DBGEO = dbtools.dbtools('host=212.193.103.21 dbname=geonornc52ru port=5432 user=smirnov')
#	DBRCV = dbtools.dbtools('host=212.193.103.20 dbname=receiver port=5432 user=smirnov')
	for inn in inns:
		rowid = DBGEO.get_row ("SELECT id FROM data_organization WHERE inn = %s" % inn)
		if not rowid:	continue
		org_id = rowid[0]
		query = "SELECT t.number, t.organization_id FROM data_transport t WHERE t.organization_id = %s" % org_id
	#	query = "SELECT t.number, t.organization_id FROM data_transport t WHERE t.organization_id = (SELECT id FROM data_organization WHERE inn = %s)" % inn
		rows = DBGEO.get_rows (query)
		print query	#, rows
		list_gnum = []
		if rows:
			for r in rows:		list_gnum.append(r[0])
	#	org_id = organization_id = r[1]
	#	print	query, "org_id:", org_id
		if list_gnum:
			qrec = "SELECT gosnum, marka FROM vlast_pos WHERE tinn = %s AND gosnum NOT IN ('%s')" % (inn, "','".join(list_gnum))
		else:	qrec = "SELECT gosnum, marka FROM vlast_pos WHERE tinn = %s" % inn
		print qrec
		jrows = DBRCV.get_rows (qrec)
		if jrows:
			print	"%s\torganization_id: %s\n\t%s" % (inn, org_id, qrec)
			for jr in jrows:
				gosnum, marka = jr
		#		print	"\t", gosnum, marka
				if marka:	marka = "'%s'" % marka
				else:		marka = "NULL"
				qins = "INSERT INTO data_transport (number, title, organization_id, active) VALUES ('%s', %s, %s, 't');" % (gosnum, marka, org_id)
				print "\t", qins, DBGEO.qexecute(qins)
		'''
		'''
clid2route = {}

def	reload_route (inns):
	""" Читать новые данные о раскладке машин по маршрутам	"""
	global	clid2route
	clear_clid2route ()

#	DBGEO = dbtools.dbtools('host=212.193.103.21 dbname=geonornc52ru port=5432 user=smirnov')
#	query = "SELECT t.number, t.route_id, r.title FROM data_transport t JOIN data_route r ON r.id = t.route_id WHERE t.organization_id IN (SELECT id FROM data_organization WHERE inn IN (5246034418, 5245014521))"
	routes = {}
	for inn in inns:
		print	"ИНН:", inn
		query = "SELECT t.number, t.route_id, r.title FROM data_transport t JOIN data_route r ON r.id = t.route_id WHERE t.organization_id IN (SELECT id FROM data_organization WHERE inn = %s)" % inn
		rows = DBGEO.get_rows (query)
		if not rows:	continue

		crout = {}
		for r in rows:
				number, route_id, title = r
			#	print	number, route_id, title	# АУ23452 4 222Т
				if not routes.has_key(title):	routes[title] = []
				routes[title].append(number)

				if not crout.has_key(title):   crout[title] = []
				crout[title].append(number)

		if inn in inn2clid:
			clid = inn2clid [inn]
		else:	clid = 'nijniyoblast'
		if clid2route.has_key (clid) and clid2route [clid].has_key('routs') and clid2route [clid]['routs']:
		#	routs = clid2route [clid]['routs']
			for jt in crout.keys():
				if jt in clid2route [clid]['routs'].keys():
					clid2route [clid]['routs'][jt].extend(crout[jt])
				else:	clid2route [clid]['routs'][jt] = crout[jt]
		else:	clid2route [clid] = {'routs': crout }

def	clear_clid2route ():
	""" Очистить маршруты	"""
	global	clid2route

	for clid in clid2route.keys():
		if clid2route[clid].has_key('routs'):	del (clid2route[clid]['routs'])

def	creat_clid2route ():
	""" Собрать (обновить) раскладку машин по маршрутам и занам (районам) области	"""
	global	clid2route

	currtm = int(time.time())
	clid_list = []
	for clid in clid2route.keys():
		crouts = clid2route[clid].get('routs')
		if not	crouts:			continue
		clid_list.append(clid)
		'''
		crouts = clid2route[clid]['routs']
		print	clid_list
		for m in crouts.keys():
			print	"\t%s\t" % m,
			for j in xrange(len(crouts[m])):		print	crouts[m][j],
			print
		'''
		gnum_list = []
		for k in crouts.keys():         gnum_list.extend(crouts[k])
		clid2route[clid]['where']  = "('%s')" % "', '".join(gnum_list)
		if not (clid2route[clid].has_key('tm') and clid2route[clid]['tm']):
			clid2route[clid]['tm'] = currtm
	return	clid_list

def	get_clid2route (clid_list):
	""" Собрать и подготовить данные к передаче	"""
	global	clid2route

	for clid in clid_list:
		try:
			crouts = clid2route[clid].get('routs')
		except:
			print "except: clid", clid
			return
		if not	crouts:			continue
		swhere = clid2route[clid]['where']
		maxtm = clid2route[clid]['tm']
	#	print	"%s\t" % clid, swhere
		rows = DBRCV.get_rows ("SELECT * FROM vdata_pos WHERE t > %s AND gosnum IN %s ORDER BY ida, t" % (maxtm, swhere))
		d = DBRCV.desc
		idd = ""
		list_out = []
		list_gosnum = []	### DDD
		curr_tm = int(time.time())
		if rows:
			for r in rows:
				if not r[d.index('x')]:		continue
				if curr_tm < r[d.index('t')]:	continue	###
				if r[d.index('t')] > maxtm:	maxtm = r[d.index('t')]
				list_gosnum.append(r[d.index('gosnum')])	### DDD
				if str(r[d.index('idd')]) != idd:
					if list_out:	list_out.append("</track>")
					route = get_route (crouts, r[d.index('gosnum')])
					device = "HTC Diamond"	# Тип устройства, на котором запущены мобильные Яндекс.Карты.
					if r[d.index('ytype')]:
						vtype = r[d.index('ytype')]
					else:	vtype = "bus"
				#	list_out.append ("""<track uuid="%s" deviceid="%s" softid="Yandex Maps" softver="2.10" category="s" route="%s" vehicle_type="bus">""" % (str(r[d.index('idd')]), device, route))
					list_out.append ("""<track uuid="%s" deviceid="%s" softid="Yandex Maps" softver="2.10" category="s" route="%s" vehicle_type="%s">""" % (str(r[d.index('idd')]), device, route, vtype))
					idd = str(r[d.index('idd')])

				if curr_tm < r[d.index('t')]:
			###		print (curr_tm - r[d.index('t')])
					etm = curr_tm
				else:	etm = r[d.index('t')]
				list_out.append ("""\t<point latitude="%f" longitude="%f" avg_speed="%d" direction="%d" time="%s"/>""" % (
				#	float(r[d.index('y')]), float(r[d.index('x')]), int(r[d.index('sp')]), int(r[d.index('cr')]), time.strftime("%d%m%Y:%H%M%S", time.gmtime (etm)) ))
					float(r[d.index('y')]), float(r[d.index('x')]), int(r[d.index('sp')]), int(r[d.index('cr')]), time.strftime("%d%m%Y:%H%M%S", time.gmtime (r[d.index('t')])) ))
			clid2route[clid]['tm'] = maxtm
			if list_out:
				print	time.strftime("%d.%m.%Y %T \t", time.localtime(time.time())), len (list_out),	# '\t',	#"*"*11
				list_out.append("</track>")
				save_file (list_out, clid)
			#	print	clid, ' '.join(list_gosnum)	### DDD

def	test (clids = None):
	for clid in clid2route.keys():
		if clids and clid not in clids:	continue
		dclid = clid2route.get(clid)
		print	clid
		routs = dclid.get('routs')
		if routs:
			for r in routs.keys():
				print	"\t%s\t" % r,
				for n in routs[r]:	print n,
				print


if __name__ == "__main__":
#	list_inn = [5246034418, 5245014521, 5243019838, 5249006828, 5249076222, 5249084953, 5249061106, 5249066619, 524900992249, 524908186307, 5249120827, 5249066601, 5249057251]
	list_inn = inn2clid.keys()
	j = 0
	while True:
		if j%144 == 0:
			print "Обновить списки транспорта"
			update_ts (list_inn)	# Обновить списки транспорта
	#	break

		routes = reload_route (list_inn)
		clid_list = creat_clid2route ()
	#	test (['nn_bor', 'nn_dzerzhinsk'])
	#	break
		for i in xrange(111):
			get_clid2route (clid_list)
			time.sleep(2)
		j += 1
		print '#'*22, j
	#	if j > 113:	break
