#!/usr/bin/python -u
# -*- coding: utf-8 -*-
"""	Файл	ytest.py
	Передача данных о Пассажирских перевозках в Yandex
	nohup /home/smirnov/MyTests/Yandex/ytest.py > /home/smirnov/MyTests/log/ytest.log &
"""
import	os, sys, time
import	urllib, json
import	requests

LIBRARY_DIR = r"/home/smirnov/MyTests/CGI/lib/"
sys.path.insert(0, LIBRARY_DIR)

import	dbtools

dbi = dbtools.dbtools('host=212.193.103.20 dbname=receiver port=5432 user=smirnov')

routes = {
	"222т": ["Н253УР152"], 
	"245":	["АУ23352", "Н258УР152", "АУ23252", "АУ53152", "ВА03352", "ВС17716", "ВА03452", "АУ23552", "АУ23652"],
	"235":	["Н246УР152", "Н247УР152", "Н248УР152", "Н254УР152"],
	}

'''
	5245014521 | МУП "Богородское ПАП"  |
	5246034418 | МУП "Борское ПАП"      |
	5229006724 | МП"Сергачский автобус" |
	5243019838 | МУП "АПАТ" Арзама
	5249006828 | МУП "Экспресс" Дзержинск
	SELECT * FROM vdata_pos WHERE gosnum IN (SELECT gosnum FROM recv_ts WHERE inn IN (5246034418, 5245014521))
'''

def	get_route (routes, gosnum):
	for k in routes.keys():
		if gosnum in routes[k]:	return	k
	return	"###"

def	get_data (routes, clid = 'nijniyoblast'):
	gnum_list = []
	for k in routes.keys():		gnum_list.extend(routes[k])
	swhere  = "('%s')" % "', '".join(gnum_list)
#	print swhere
	rid = dbi.get_row ("SELECT max(id_dp) FROM vdata_pos WHERE gosnum IN %s" % swhere)
	print "rid:", rid
	rows = dbi.get_rows ("SELECT * FROM vdata_pos WHERE id_dp > %s AND gosnum IN %s" % (rid[0], swhere))
	d = dbi.desc
#	print "dbi.desc", d
	iddp = rid[0]
	for j in xrange (11*10):	#555):
		time.sleep(2)
		rows = dbi.get_rows ("SELECT * FROM vdata_pos WHERE id_dp > %s AND gosnum IN %s ORDER BY ida, t" % (iddp, swhere))
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
					list_out.append ("""<track uuid="%s" deviceid="%s" softid="Yandex Maps" softver="2.10" category="s" route="%s" vehicle_type="bus">""" % (str(r[d.index('idd')]), device, route))
					idd = str(r[d.index('idd')])
			#	print r[d.index('t')], r[d.index('id_dp')], r[d.index('x')], r[d.index('y')], r[d.index('sp')], r[d.index('marka')]	# r[d.index('')]
			#	print r[d.index('t')], r[d.index('id_dp')], r[d.index('ida')], r[d.index('idd')], r[d.index('code')], r[d.index('gosnum')]	# r[d.index('')]

				list_out.append ("""\t<point latitude="%f" longitude="%f" avg_speed="%d" direction="%d" time="%s"/>""" % (
					float(r[d.index('y')]), float(r[d.index('x')]), int(r[d.index('sp')]), int(r[d.index('cr')]), time.strftime("%d%m%Y:%H%M%S", time.gmtime (r[d.index('t')])) ))
			print	time.strftime("%d.%m.%Y %T \t", time.localtime(time.time())), len (list_out), '\t',	#"*"*11
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
		print r, r.text, clid
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
	'''

inn2clid = {
	5243019838: 'nn_arzamas',	#     МУП "АПАТ" Арзамас
	5249006828: 'nn_dzerzhinsk',	#     МУП "Экспресс" Дзержинск
	5245014521: 'nn_bogorodskoe',	#     МУП "Богородское ПАП"
	5246034418: 'nn_bor',		#     МУП "Борское ПАП"
	5229006724: 'nn_sergach',	#     МП"Сергачский автобус"
	5249076222: 'nn_dzerzhinsk',	# ООО "Орбита"
	5249084953: 'nn_dzerzhinsk',	# ООО "Орбита-2"
	5249061106: 'nn_dzerzhinsk',	# ООО "ДПП"
	5249066619: 'nn_dzerzhinsk',	# ООО "ДПП плюс"
	524900992249: 'nn_dzerzhinsk',	# ИП Лазарев Сергей Юрьевич
	524908186307: 'nn_dzerzhinsk',	# ИП Сафин Халит Мустафинович
	5249120827: 'nn_dzerzhinsk',	# ООО "Тройка"
	5249066601: 'nn_dzerzhinsk',	# ООО "Транслайн плюс"
	5249057251: 'nn_dzerzhinsk',	# ООО "Транслайн"
	}

clid2route = {}

def	reload_route (inns):
	""" Читать новые данные о раскладке машин по маршрутам	"""
	global	clid2route
	clear_clid2route ()

	dbr = dbtools.dbtools('host=212.193.103.21 dbname=geonornc52ru port=5432 user=smirnov')
#	query = "SELECT t.number, t.route_id, r.title FROM data_transport t JOIN data_route r ON r.id = t.route_id WHERE t.organization_id IN (SELECT id FROM data_organization WHERE inn IN (5246034418, 5245014521))"
	routes = {}
	for inn in inns:
		print	"ИНН:", inn
		query = "SELECT t.number, t.route_id, r.title FROM data_transport t JOIN data_route r ON r.id = t.route_id WHERE t.organization_id IN (SELECT id FROM data_organization WHERE inn = %s)" % inn
		rows = dbr.get_rows (query)
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
		crouts = clid2route[clid].get('routs')
		if not	crouts:			continue
		swhere = clid2route[clid]['where']
		maxtm = clid2route[clid]['tm']
	#	print	"%s\t" % clid, swhere
		rows = dbi.get_rows ("SELECT * FROM vdata_pos WHERE t > %s AND gosnum IN %s ORDER BY ida, t" % (maxtm, swhere))
		d = dbi.desc
		idd = ""
		list_out = []
		if rows:
			for r in rows:
				if not r[d.index('x')]:		continue
				if r[d.index('t')] > maxtm:	maxtm = r[d.index('t')]
				if str(r[d.index('idd')]) != idd:
					if list_out:	list_out.append("</track>")
					route = get_route (crouts, r[d.index('gosnum')])
					device = "HTC Diamond"	# Тип устройства, на котором запущены мобильные Яндекс.Карты.
					list_out.append ("""<track uuid="%s" deviceid="%s" softid="Yandex Maps" softver="2.10" category="s" route="%s" vehicle_type="bus">""" % (str(r[d.index('idd')]), device, route))
					idd = str(r[d.index('idd')])

				list_out.append ("""\t<point latitude="%f" longitude="%f" avg_speed="%d" direction="%d" time="%s"/>""" % (
					float(r[d.index('y')]), float(r[d.index('x')]), int(r[d.index('sp')]), int(r[d.index('cr')]), time.strftime("%d%m%Y:%H%M%S", time.gmtime (r[d.index('t')])) ))
			clid2route[clid]['tm'] = maxtm
			if list_out:
				print	time.strftime("%d.%m.%Y %T \t", time.localtime(time.time())), len (list_out), '\t',	#"*"*11
				list_out.append("</track>")
				save_file (list_out, clid)

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
'''
	curl -X GET "http://nnovbus.rnc52.ru/api/depot/128/routes" -H "accept: application/json" -H "Authorization: Token 30e04452062e435a9b48740f19d56f45"      # Маршруты
	r = requests.post("http://tst.extjams.maps.yandex.net/mtr_collect/1.x/", data={"data": "\n".join(data), "compressed": 0}, headers=headers)
'''
def	get_nimbus (clid = 'nn_bor'):
	print	"get_nimbus"
	r = requests.get("http://nnovbus.rnc52.ru/api/depot/128/routes", headers={"accept": "application/json", "Authorization": "Token 30e04452062e435a9b48740f19d56f45"})
	print	r, type(r.text.encode('UTF-8'))
	data = json.loads (r.text.encode('UTF-8'))
	print	type (data), data.keys()
	for route in data['routes']:
		print	route.keys()
		for k in [u'a', u'd', u'tt', u'tp', u'n', u'tm', u'u', u'isc', u'st', u'id']:
			print	k, route[k]
		break

#	5249076222, 5249084953, 5249061106, 5249066619, 524900992249, 524908186307, 5249120827, 5249066601, 5249057251, 	
if __name__ == "__main__":
	j = 0
	while True:
	#	routes = reload_route ([5246034418, 5245014521, 5243019838, 5249006828])
		routes = reload_route ([5246034418, 5245014521, 5243019838, 5249006828, 5249076222, 5249084953, 5249061106, 5249066619, 524900992249, 524908186307, 5249120827, 5249066601, 5249057251])
		clid_list = creat_clid2route ()
	#	get_nimbus ()
	#	test (['nn_bor', 'nn_dzerzhinsk'])
	#	break
		for i in xrange(111):
			get_clid2route (clid_list)
			time.sleep(5)
		j += 1
		print '#'*22, j
	#	if j > 113:	break
	'''
	for k in routes.keys():
		print k, "=\t", 
		for j in xrange(len(routes[k])):	print routes[k][j],
		print
	return	routes

	j  = 0
	while j < 3:
		routes = reload_route ([5246034418, 5245014521, 5243019838, 5249006828, ])	# 5229006724	МП"Сергачский автобус"
		get_data (routes)	#, clid)
		j += 1
		print '#'*22, j
	
	'''
