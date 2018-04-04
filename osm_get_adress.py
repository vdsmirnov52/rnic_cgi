#!/usr/bin/python
# -*- coding: utf-8 -*-

import	os, sys, time, getopt

LIBRARY_DIR = r"/home/smirnov/pylib"    # Путь к рабочей директории (библиотеке)
sys.path.insert(0, LIBRARY_DIR)
import  dbtools
"""
select b.id, b.adress, co.id, co.name, ic.id, t.owner_id, at.*, tk.*
FROM building b
 left join contractor co ON co.building_id = b.id
 left join individualcontractor ic ON ic.id = co.id
 left join transport t ON t.owner_id = co.id
 left join abstracttransportlink at ON at.transport_id = t.id
 left join transport2kindlink tk ON tk.id = at.id
 --left join transport2devicelink td ON at.id = td.id
 --left join account4mobilecommunication ac ON ac.transport_id = t.id
 --left join conversation cv ON cv.transport_id = t.id
 WHERE b.isdeleted >0;

-- Удаление из БД адресов с признаком isdeleted >0	--
	DELETE FROM individualcontractor WHERE id IN (select id FROM contractor WHERE building_id IN (select id FROM building WHERE isdeleted >0));
	DELETE FROM conversation WHERE transport_id IN (SELECT id FROM transport WHERE owner_id IN (select id FROM contractor WHERE building_id IN (select id FROM building WHERE isdeleted >0)));
	DELETE FROM account4mobilecommunication WHERE transport_id IN (SELECT id FROM transport WHERE owner_id IN (select id FROM contractor WHERE building_id IN (select id FROM building WHERE isdeleted >0)));
	DELETE FROM transport2devicelink WHERE id IN (SELECT id FROM abstracttransportlink WHERE transport_id IN (SELECT id FROM transport WHERE owner_id IN (select id FROM contractor WHERE building_id IN (select id FROM building WHERE isdeleted >0))));
	DELETE FROM transport2kindlink WHERE id IN (SELECT id FROM abstracttransportlink WHERE transport_id IN (SELECT id FROM transport WHERE owner_id IN (select id FROM contractor WHERE building_id IN (select id FROM building WHERE isdeleted >0))));
	DELETE FROM abstracttransportlink WHERE transport_id IN (SELECT id FROM transport WHERE owner_id IN (select id FROM contractor WHERE building_id IN (select id FROM building WHERE isdeleted >0)));
	DELETE FROM transport WHERE owner_id IN (select id FROM contractor WHERE building_id IN (select id FROM building WHERE isdeleted >0));
	DELETE FROM contractor WHERE building_id IN (select id FROM building WHERE isdeleted >0);
	DELETE FROM building WHERE isdeleted >0;
"""
"""
    select --count(*)

 'INSERT INTO building (id, isdeleted, createddatetime,createdby_id, settlement, region_id, cityname, street,housenumber, postcode,lat, lon, osmid, linestring)
select nextval(''hibernate_sequence''), 0, now(), (select min(id) from rightsowner where name=''admin'' and isdeleted=0), ''1'',
(select min(id) from buildingregion where description like '''|| COALESCE(region.v,'')||'''),'''|| COALESCE(city.v,'')||''', '''|| COALESCE(street.v,'')||''', '''|| COALESCE(housenumber.v,'')||''', '''||
 COALESCE(postcode.v,'')||''', '|| st_y(geom)||', '||st_x(geom)||
', '||w.id||',''SRID=4326;'|| st_astext(w.linestring)||''' where not exists (select id from building where cityname like '''||
COALESCE(city.v,'')||''' and street like '''|| COALESCE(street.v,'')||''' and housenumber like '''|| COALESCE(housenumber.v,'')||''' and lat = '||st_y(geom)||' and lon = '||st_x(geom)||');'
'
not_exists = "select id from building where cityname like '%s' and street like '%s' and housenumber like '%s' and lat = '%s' and lon = '%s'" % (city.v, street.v, housenumber.v, st_y(geom), st_x(geom))
"""
qget_osm = """
select w.id AS ways_id, region.v AS region, city.v AS city, street.v AS street, housenumber.v AS housenumber, postcode.v AS postcode, st_y(geom), st_x(geom) --, st_astext(w.linestring)
from ways w
 left join way_tags region on w.id = region.way_id and region.k = 'addr:district'
 left join way_tags city on w.id = city.way_id and city.k='addr:city'
 left join way_tags street on w.id = street.way_id and street.k='addr:street'
 left join way_tags housenumber on w.id = housenumber.way_id and housenumber.k='addr:housenumber'
 left join way_tags postcode on w.id = postcode.way_id and postcode.k='addr:postcode'
 left join way_nodes wn on wn.sequence_id =0 and wn.way_id  = w.id
 left join nodes n on wn.node_id = n.id
 left join way_tags wt on w.id = wt.way_id and wt.k='building'
where -- not(wt.k='building' and wt.v ='yes') and
 COALESCE(city.k,COALESCE(street.k,COALESCE(housenumber.k,'')))<>''
--ORDER by city, street, housenumber
--LIMIT 111
"""

bases = {
	'vms_tt': 'host=10.40.25.180 dbname=vms_ws port=5432 user=vms',
	'vms_ws': 'host=10.40.25.176 dbname=vms_ws port=5432 user=vms',
	'osm': 'host=10.40.25.180 dbname=osm_2 port=5432 user=osm_2',
	'contr': 'host=127.0.0.1 dbname=contracts port=5432 user=smirnov',
	}

def	get_osm(odb):
	rows = odb.get_rows (qget_osm)
	if not rows:	return
	d = odb.desc
	print d
	print "len rows", len(rows)
	for r in rows:
		for v in r:
			print v, '\t',
		print ''	#r
	print "len rows", len(rows)

#def	compare (rj, ro, d, jcols = ['cityname', 'street', 'housenumber']):
#def	compare (rj, ro, d, jcols = ['osmid',]):
def	compare (rj, ro, d, jcols = ['region_id', 'cityname', 'street', 'housenumber']):
	for s in jcols:
		j = d.index(s)
		if rj[j] != ro[j]:	return	False
	return	True

def	compare_f (fj, fo, df = .0002):
	try:
		if abs(fj - fo) < df:	return	True
	except:	return False

def	prn_row (d, pcols, r, pref = '\t'):
	print pref,
	for s in pcols:	print s, r[d.index(s)], '\t',
	print ''

def	crear_sset (d, ro, rj, wset = None):
	if not wset:
		wset = ['adress', 'settlement', 'region_id', 'cityname', 'street', 'housenumber', 'postcode', 'lat', 'lon', 'linestring']
	res = []
	for c in wset:
		if rj[d.index(c)] and rj[d.index(c)] != ro[d.index(c)]:
			res.append("%s='%s'" % (c, str(rj[d.index(c)])))
	if res:	return ", ".join(res)
	else:	return ""

def	exec_querys (vdb, querys):
	try:
		vdb.qexecute("; ".join(querys))
	#	print "; ".join(querys)
	except:
		print "EXCEPT", "; ".join(querys)
	
qosmid = """SELECT id, adress, createddatetime, createdby_id, settlement, region_id, cityname, street, housenumber, postcode, lat, lon, osmid, linestring
	FROM building b
	WHERE isdeleted = 0
--	AND street = 'улица Калинина'
--	AND street LIKE '%Карла Маркса'
	ORDER BY  cityname, street,housenumber, osmid,id """
qstreet =  """SELECT id, adress, createddatetime, createdby_id, settlement, region_id, cityname, street, housenumber, postcode, lat, lon, osmid, linestring
	FROM building b
	WHERE isdeleted = 0 AND street LIKE '_%'
--	AND street = 'улица Калинина'
--	AND street LIKE '%Карла Маркса'
	ORDER BY  cityname, street,housenumber, id """

def	check_building (vdb, flag = 'osmid'):
	""" поиск дубликатов в building
	flag = 'osmid' | 'street'
	"""
	if flag == 'osmid':
		rows = vdb.get_rows (qosmid)
	elif flag == 'street':
		rows = vdb.get_rows (qstreet)
	else:
		help (check_building)
		return
#	rows = vdb.get_rows (q)
	d = vdb.desc
	print d
	rold = None
#	ids_del = None
#	is_updt = None
	pcols = ['id', 'osmid', 'createddatetime', 'lat', 'lon', 'region_id', 'cityname', 'street', 'housenumber', ]
	jr = jdu = 0
	prold_flag = True
	querys = []
	for r in rows:
		jr += 1
		if rold:
		#	querys = []
			if flag == 'osmid' and r[d.index('osmid')] and compare(r, rold, d, ['osmid',]):
				if not querys:
					prn_row (d, pcols, rold, "%d\t" % jr)
				prn_row (d, pcols, r)
				querys.append("DELETE FROM building WHERE id=%d" % r[d.index('id')])
				sset = crear_sset(d, rold, r)
				if sset:
					quup = "UPDATE building SET %s WHERE id=%d" % (sset, rold[d.index('id')])
				else:	quup = ''
			#	quup = "UPDATE  building SET lat=%11.7f, lon=%11.7f WHERE id=%d" % (r[d.index('lat')], r[d.index('lon')], rold[d.index('id')])
			#	querys.append("UPDATE  building SET lat=%11.7f, lon=%11.7f WHERE id=%d" % (r[d.index('lat')], r[d.index('lon')], rold[d.index('id')]))
				prold_flag = False
			elif flag == 'street' and compare(r, rold, d, ['region_id', 'cityname', 'street', 'housenumber']) and (compare_f(rold[d.index('lat')], r[d.index('lat')]) or compare_f(rold[d.index('lon')], r[d.index('lon')])):
				if not querys:
					prn_row (d, pcols, rold, "%d\t" % jr)
				prn_row (d, pcols, r)
				querys.append("DELETE FROM building WHERE id=%d" % r[d.index('id')])
				sset = crear_sset(d, rold, r, ['osmid', 'adress', 'settlement', 'region_id', 'cityname', 'street', 'housenumber', 'postcode', 'lat', 'lon', 'linestring'])
				if sset:
					quup = "UPDATE building SET %s WHERE id=%d" % (sset, rold[d.index('id')])
				else:	quup = ''
			else:
				rold = r
				prold_flag = True
			if prold_flag and querys:
				jdu += 1
			#	if quup:
				querys.append(quup)
				exec_querys (vdb, querys)
				querys = []
		else:	rold = r
	if querys:
		querys.append(quup)
		exec_querys (vdb, querys)
	print "##################", flag
	'''
		if rold and prold_flag:
			if ids_del:
				querys = []
				for i in ids_del:	querys.append("DELETE FROM building WHERE id=%d" %i)
				try:
					if is_updt:
						querys.append("UPDATE  building SET lat=%11.7f, lon=%11.7f WHERE id=%d" % (is_updt[1], is_updt[2], is_updt[0]))
				except:
					print "is_updt", is_updt
		#		print "   DELETE", ids_del, is_updt, "; ".join(querys)
				if not vdb.qexecute("; ".join(querys)):
					print "\t", "; ".join(querys)
				print jr, '\t', "; ".join(querys)
	#		for s in pcols:		print rold[d.index(s)], '\t',
	#		print	''
	#		prold_flag = False
			ids_del = []
			is_updt = None
		if rold and compare(r, rold, d):
			if prold_flag:
				prold_flag = False
				prn_row (d, pcols, rold, "%d\t" % jr)
			if not (compare_f(rold[d.index('lat')], r[d.index('lat')], .01) and compare_f(rold[d.index('lon')], r[d.index('lon')], .01)):
		#		print "   QQ\t",
				prold_flag = True
				rold = r
				continue
			else:
				jdu += 1
				ids_del.append( r[d.index('id')])
				if not (compare_f(rold[d.index('lat')], r[d.index('lat')]) and compare_f(rold[d.index('lon')], r[d.index('lon')])):
					is_updt = (rold[d.index('id')], r[d.index('lat')], r[d.index('lon')])
				print '   >>\t',
			for s in pcols:
				if r[d.index(s)]:
					if type(r[d.index(s)]) == '':
						print "'%s'" %  r[d.index(s)].strip() ,'\t',
					else:	print r[d.index(s)], '\t',
				else:
					print r[d.index(s)], '\t',
			print ''
		else:
			prold_flag = True
			rold = r
	'''
	print "len rows", len(rows), jr, jdu

def	outhelp():
	print qget_osm

if __name__ == "__main__":
	FL_test = False	#True
	FL_help = False	#True
	try:
		if FL_test:
			for key in bases:
				print key, "\t=", bases[key], '\t>',
				ddb = dbtools.dbtools (bases[key], 0)
				if not ddb.last_error:	print 'OK'
		elif FL_help:	outhelp()
#		get_osm (dbtools.dbtools(bases['osm']))		
		check_building (dbtools.dbtools(bases['vms_tt']), flag = 'osmid')
		check_building (dbtools.dbtools(bases['vms_tt']), flag = 'street')
	except:
		exc_type, exc_value = sys.exc_info()[:2]
		print "EXCEPT:", exc_type, exc_value
