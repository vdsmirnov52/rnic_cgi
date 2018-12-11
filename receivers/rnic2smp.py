#!/usr/bin/python -u
# -*- coding: koi8-r -*-
#	Демон сбора и передачи данных о исполненых вызовах ОО в архив
#	nohup ./rnic2smp.py > log/rnic2smp.py.log &
#
#	Настройка KEEPAILVE
#	root # ./keepalive.sh
#	echo 5 >/proc/sys/net/ipv4/tcp_keepalive_intvl		время между повторами KEEPALIVE-проб
#	echo 5 >/proc/sys/net/ipv4/tcp_keepalive_probes 	максимальное количество KEEPALIVE-проб
#	echo 20 >/proc/sys/net/ipv4/tcp_keepalive_time 		время неактивности соединения


import  os, time, sys
import  syslog
import	thread

LIBRARY_DIR = r"/home/vds/03/mydev/pylib"          # Путь к рабочей директории (библиотеке)
sys.path.insert(0, LIBRARY_DIR)

debuglevel = 1
HOST = '223.254.254.13'
PORT = 12345

import	google
import	dbtools

ddb_oo =	"host=_dl dbname=b03 port=5432 user=vds"
ddb_nnmap =	"host=_wm dbname=_nnmap port=5432 user=vds"


def	pexcept (mark, exit = -1):
	exc_type, exc_value = sys.exc_info()[:2]
	syslog.syslog ("EXCEPT %s:\t %s %s" % (mark, str(exc_type), str(exc_value)))
	if debuglevel:	print "EXCEPT %s:\t" % mark, exc_type, exc_value
	if exit >= 0:	os._exit(exit)

import	msgpack
globj = 0	 ## DEBUD

def	pdata (data, sufx = None):	## DEBUD
	if len(data):
		j = 0
		for c in data:
			print "%02x" % ord(c) ,
			j += 1
			if j > 64:
				print	"...",
				break
	if sufx:	print sufx, len(data)
	else:		print "<<<", len(data)

def	agis_data_capture (fileno, data):
	global  globj
	global	server_not
	global	server_dlist
	try:
		if not (ord(data[-2]) == 0x0d and ord(data[-1]) == 0x0a):
			unpacked = msgpack.unpackb(data, use_list=False )
			#print unpacked
			ttm, lat, lon = unpacked[:3]
			stid = unpacked[5]	# Обрезаем длинный IMEI
			if len(stid) > 9:	stid = stid[6:]
			tid = int(stid)		# int(unpacked[5])
			currtm = int(time.time())
			if currtm - ttm > 36000:
				globj += 100
				return
			if ttm > currtm:
				globj += 1
				return

			direct = float(unpacked[3])/100
			speed = float(unpacked[4])/100
			ttype = unpacked[6]
			is_tkey = unpacked[7]	# Тревожная кнопка
			if is_tkey:
				print	"is_tkey Тревожная кнопка"
			globj = 0
			mutex_server.acquire()
			server_dlist.append((tid, ttm, lat, lon, direct, speed, ttype))
			server_not = 0
			mutex_server.release()
		elif len(data) > 0:
			pdata (data)
		else:	pass
	except	msgpack.ExtraData:
		pdata (data, '< ExtraData')
	except:
		pexcept('agis_data_capture')
		pdata (data)

def	server():
	not_len = 0
	try:
		import	socket, select

		serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
		keepalive = serversocket.getsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE)
		print "socket.SO_KEEPALIVE", keepalive 
		serversocket.bind((HOST, PORT))
		serversocket.listen(1)
		serversocket.setblocking(0)
	
		spoll = select.poll()
		spoll.register(serversocket.fileno(), select.POLLIN)
		connections = {}; requests = {}; responses = {}; times = {}
		while True:
			ffno = 0
			events = spoll.poll(1)
			for fileno, event in events:
				intime = int(time.time())
				if fileno == serversocket.fileno():
					connection, address = serversocket.accept()
					print "Connect:", connection.fileno(), address
					connection.setblocking(0)
					spoll.register(connection.fileno(), select.POLLIN)
					connections[connection.fileno()] = connection
					requests[connection.fileno()] = ''
				elif event & select.POLLIN:
					try:
						requests[fileno] = connections[fileno].recv(1024)
						if len(requests[fileno]):
							agis_data_capture (fileno, requests[fileno])
							times[fileno] = intime
							not_len = 0
						else:
							not_len += 1
							print "Close", fileno, not_len,
							ffno = fileno
							connections[fileno].close()
							spoll.unregister(fileno)
					except socket.error:
						print	"socket:", fileno, "error:"
						pexcept ("error")
						connections[fileno].close()
						spoll.unregister(fileno)
				elif event & select.POLLOUT:
					print "send", responses[fileno]
					byteswritten = connections[fileno].send(responses[fileno])
					responses[fileno] = responses[fileno][byteswritten:]
					if len(responses[fileno]) == 0:
						spoll.modify(fileno, 0)
						connections[fileno].shutdown(socket.SHUT_RDWR)
				elif event & select.POLLHUP:
					ffno = fileno
					print "\tevent & select.POLLHUP"
			if not_len > 100:
				print	time.strftime("\tBreack %Y-%m-%d %T", time.localtime(intime))
				break
			time.sleep(.01)
			if not keepalive and not ffno:
				for fn in times:
					if intime - times[fn] > 900:	#1800:
						print "POLL.unregister", fn
						ffno = fn
						break
			if ffno and times.has_key(ffno):
				print "\tffno", ffno, time.strftime("%Y-%m-%d %T", time.localtime(intime))
				del times[ffno]
				try:
					connections[ffno].close()
					spoll.unregister(ffno)
					del connections[ffno]
				except	KeyError:
					print "\t<exceptions.KeyError>"
	
	except	socket.error:
		pexcept ('server')
	except:		pexcept ('server')
	finally:	serversocket.close()

def	get_oo (tmr):
	global	imei_desc
	try:
		dboo = dbtools.dbtools("host=_dl dbname=b03 port=5432 user=vds")
		if not dboo:	return
		query = "SELECT imei, ind, auto, ntype FROM ndesc WHERE auto > 0 AND stat > 0;"	# LIMIT 11"
		rows = dboo.get_rows (query)
		if not rows:
			if debuglevel:	print	"Нет данных о машинах."
			return
		mutex_imdesc.acquire()
		for r in rows:
			imei_desc[r[0]] = r[1:]
		mutex_imdesc.release()
	except:	pexcept ('get_oo')

calls_colname = ["cnum_total","number","reasn","subst","street","house","korp","br_ref","nbrg","pbrg","nsbrg","doctor","t_get","t_send","t_arrl","t_done","reslt"]


def	oo2nnmap (tmr, start = False):
	''' Копировать статусы Машин Бригад в nnmap	'''
	global	pcalls_dlist
	global	auto2brig
	oo_calls = []
	autos_brf = {}
	brig_only = []
	pbrig_cnames = ['id_brg', 'bnum', 'profile', 'bn_pst', 'scall', 'b_stat', 'doctor', 'id_auto', 'a_stat']
	try:
		dboo = dbtools.dbtools(ddb_oo)
		if not dboo:	return
		dbnmap = dbtools.dbtools(ddb_nnmap)
		if not dbnmap:	return
		query = "SELECT %s FROM call ORDER BY cnum_total DESC;" % ','.join(calls_colname)
		mutex_pcalls.acquire()
		pcalls_dlist = dboo.get_rows (query) 
		mutex_pcalls.release()
	#	print pcalls_dlist

		query = "SELECT id_auto, stat, ref_navg, reg_num, n_pst, type AS atype FROM automobile ORDER BY id_auto;"
		rws = dboo.get_rows (query)
		if rws:
			for rw in rws:
				id_auto, stat, ref_navg, reg_num, n_pst, atype = rw
				autos_brf[id_auto] = [stat, ref_navg, reg_num.strip()]
				arw = dbnmap.get_row ("SELECT id_auto FROM automobile WHERE id_auto = %d;" % id_auto)
				if not arw and ref_navg > 0:
					query = "INSERT INTO automobile (id_auto, stat, ref_navg, reg_num, n_pst, type, dec_num) VALUES (%d, %d, %d, '%s', %d, %d, %s);" % (
							id_auto, stat, ref_navg, reg_num.strip(), n_pst, atype, reg_num[1:4])
					if not dbnmap.qexecute (query):
						print query
				if start:
					if ref_navg:
						query = "UPDATE automobile SET stat = %d, n_pst = %d, ref_navg = %d WHERE id_auto = %d;" % (stat, n_pst, ref_navg, id_auto)
					else:	query = "UPDATE automobile SET stat = %d, n_pst = %d, ref_navg = NULL WHERE id_auto = %d;" % (stat, n_pst, id_auto)
				else:	query = "UPDATE automobile SET stat = %d, n_pst = %d WHERE id_auto = %d;" % (stat, n_pst, id_auto)
				if not dbnmap.qexecute (query):
					return
		query = "SELECT * FROM bnaryd"
		rws = dboo.get_rows (query)
		if rws:
			bdesc = dboo.desc
			if autos_brf:
				for rw in rws:
					auto =  rw[bdesc.index('auto')]
					brr = [rw[bdesc.index('br_id')], rw[bdesc.index('number')], rw[bdesc.index('profile')].strip(), rw[bdesc.index('n_pst')],
							rw[bdesc.index('scall')], rw[bdesc.index('stat')], rw[bdesc.index('doctor')], auto]
					if autos_brf.has_key(auto):
						for rr in brr:
							autos_brf[auto].append(rr)
						brr.append (autos_brf[auto][0])	## auto stat
					else:	brr.append (None)	
		
					brig_only.append (brr)
				mutex_autobrg.acquire()
				auto2brig = autos_brf
				mutex_autobrg.release()
		if start:
			query = "DELETE FROM pbrig;\nDELETE FROM loc_points WHERE time < %d;" % int(tmr - 3600*8)	## Хранить в loc_points 8 часов
			if not dbnmap.qexecute (query):
				return
			for br in brig_only:
				nms = []
				vls = []
				for j in xrange(len (pbrig_cnames)):
					if br[j]:
						nms.append (pbrig_cnames[j])
						if isinstance(br[j], (basestring, )):
							vls.append("'%s'" % br[j])
						else:	vls.append (str(br[j]))
				query = "INSERT INTO pbrig (%s) VALUES (%s);" % (', '.join(nms), ', '.join(vls))
				dbnmap.qexecute (query)
	#		for k in auto2brig.keys():	print k, '=', auto2brig[k]
		else:
			for br in brig_only:
				id_brg = br[pbrig_cnames.index('id_brg')]
				sset = []
				if br[pbrig_cnames.index('scall')]:
					sset.append ('scall = %d' % br[pbrig_cnames.index('scall')])
				if br[pbrig_cnames.index('id_auto')]:
					sset.append ('id_auto = %d' % br[pbrig_cnames.index('id_auto')])
				if br[pbrig_cnames.index('a_stat')]:
					sset.append ('a_stat = %d' % br[pbrig_cnames.index('a_stat')])
				if br[pbrig_cnames.index('b_stat')]:
					sset.append ('b_stat = %d' % br[pbrig_cnames.index('b_stat')])
				if sset:
					query = "UPDATE pbrig SET %s WHERE id_brg=%d;" %(', '.join(sset), id_brg)
					dbnmap.qexecute (query)

		if start:	print "\too2nnmap OK start:", start
	#	print "\too2nnmap OK start:", start
	except:	pexcept ('oo2nnmap')

def	sendat_points (tmr, dbnmap):
	global	server_dlist
	global	imei_desc
	global	auto2brig
	global	FL_getPoints	# =  False
	if FL_getPoints:	return
	cnames = ['a_stat', '', 'gosn', 'r_brg', 'n_brg', 'p_brg', 'n_pst', '', 'b_stat']	#, 'scall', 'doctor']
	scol_brg = "a_stat, gosn, r_brg, n_brg, p_brg, n_pst, b_stat"
	ignore = []
	vloc_points = []	# INSERT INTO loc_points (ref_ndesc, ref_auto, x_grad, y_grad, direct, speed, time) VALUES 
	vals_pauto =  []	# INSERT INTO pauto (id_term,id_auto,ptype,t_get,x,y,gx,gy,speed, %s) VALUES
	last_ttm = {}
	jdpack = 0
	try:
		FL_getPoints = True
		print   time.strftime("Points\t%Y-%m-%d %T", time.localtime(tmr)), "\tglobj:", globj, "\tIs:", 
		while	server_dlist:
			mutex_server.acquire()
			dpack = server_dlist.pop(0)
			mutex_server.release()
			tid, ttm, lat, lon, direct, speed, ttype = dpack
			if not imei_desc.has_key(tid):	# Чужой прибор игнорировать
				if not dpack[0] in ignore:
					ignore.append(dpack[0])
			else:
		#		print dpack[0],
				if jdpack < 3:	print dpack[0],
				else:		print '.',
				jdpack += 1
				ind, auto, ntype = imei_desc[tid]
				vloc_points.append("(%s, %s, %s, %s, %s, %s, %s)" % (ind, auto, lon, lat, direct, speed, ttm))
				X = google.g20nx (lon)
				Y = google.g20ny (lat)
				if auto2brig.has_key(auto):
					vls = []
					abrf = auto2brig[auto]
					lnabrf = len (abrf)
					for j in xrange (len (cnames)):
						try:
							if not cnames[j]:	continue
							if j >= lnabrf:		vls.append('NULL')
							if abrf[j]:
								if isinstance(abrf[j], (basestring, )):
									vls.append ("'%s'" % abrf[j])
								else:	vls.append (str (abrf[j]))
							else:	vls.append('NULL')
						except IndexError:	pass
			#				print "auto2brig", abrf, j, vls
					val_brg = ', '.join(vls)
				else:
					val_brg = "NULL, NULL, NULL, NULL, NULL, NULL, NULL"
				ptype = 0
			#	print '\njdpack', jdpack, scol_brg, "###", ind, auto, ptype, ttm, X, Y, lon, lat, speed, val_brg
				svals = "(%d,%d,%d,%d,%d,%d,%9.5f,%9.5f,%6.3f, %s)" % (ind, auto, ptype, ttm, X, Y, lon, lat, speed, val_brg)
				vals_pauto.append(svals)
				if not last_ttm.has_key(auto):
					last_ttm[auto] = ttm
				elif last_ttm[auto] < ttm:
					last_ttm[auto] = ttm
	#			if jdpack > 3:	break
	#	print	last_ttm
	#	print	"SELECT * FROM pauto WHERE id_auto IN (%s) AND t_get IN (%s);" % (str(last_ttm.keys())[1:-1], str(last_ttm.values())[1:-1])

		if vloc_points:
			query = "INSERT INTO loc_points (ref_ndesc, ref_auto, x_grad, y_grad, direct, speed, time) VALUES %s" % ','.join(vloc_points)
			if not dbnmap.qexecute (query):
				print	query
		if vals_pauto:
			query = "INSERT INTO pauto (id_term,id_auto,ptype,t_get,x,y,gx,gy,speed, %s) VALUES %s" % (scol_brg, ','.join(vals_pauto))
		
			if not dbnmap.qexecute (query):
				print	query
			sttms = str(last_ttm.keys())[1:-1]
			dbnmap.qexecute ("DELETE FROM last_pauto WHERE id_auto IN (%s);\nINSERT INTO last_pauto (SELECT * FROM pauto WHERE id_auto IN (%s) AND t_get IN (%s))" % (
				sttms, sttms, str(last_ttm.values())[1:-1]))

		if ignore:	print "Ignore", ignore,
		print "\x7f#"
	except IndexError:
		print "IndexError:", abrf, vls
	finally:
		FL_getPoints = False

def	get_place (dbnmap, street, house, korp):
	""" Читать координаты места Вызова	"""
	query = "SELECT ind, tag FROM street WHERE name = '%s'" % street
	try:
		row = dbnmap.get_row(query)	# Читать street_id
		if not row:
			query = "SELECT ind, tag FROM street WHERE name LIKE '%s'" % street.replace(' ','%').replace('.','%').replace('-','%')
			row = dbnmap.get_row(query)	#SELECT ind, tag FROM street WHERE name LIKE 'ГАГАРИНА%П%Т%';
		if row:
			if row[1] and row[1] > 0:
				street_id = row[1]
			else:	street_id = row[0]
			if house:
				house = house.replace(' ', '')
				query = "SELECT gx, gy FROM oo_house WHERE street_id = %d AND gx > 0 AND gy > 0 AND house_num LIKE '%s%%'" % (street_id, house.strip())
			else:	query = "SELECT gx, gy FROM oo_house WHERE street_id = %d AND gx > 0 AND gy > 0" % street_id
			rxy = dbnmap.get_row(query)	# Читать координаты gx, gy
			if rxy and rxy[0] > 0.0 and rxy[1] > 0.0:
				lat, lon = rxy
				x = google.g20nx (float(rxy[0]))
				y = google.g20ny (float(rxy[1]))
				return	(street_id, rxy[0], rxy[1], x, y)
		print '"%s"\t' % street, query
	except:	pexcept ('get_place')

def	sendat_pcalls (tmr, dbnmap):
	""" Предать текущее состояниен Вызовов в pcall и поиск координат места Вызова	"""
	global	pcalls_dlist
	cdic = {'br_ref':'r_brg', 'nbrg':'n_brg', 'nsbrg':'n_pst', 't_send':'t_send', 't_arrl':'t_arrl', 't_done':'t_done', 'reslt':'reslt', 'pbrg':'pbrg'}
	ltotalnum = []
	lquerys = []
	print   time.strftime("Calls\t%Y-%m-%d %T", time.localtime(tmr)), '\tcalls:', len (pcalls_dlist)
	try:
		rmax = dbnmap.get_row ("SELECT max (totalnum) FROM pcall")
		max_tnum = rmax[0]
		mutex_pcalls.acquire()
		while	pcalls_dlist:
			dcall = pcalls_dlist.pop(0)
			ltotalnum.append (dcall[0])
			if dcall[0] > max_tnum:		# Новый вызов
	#			for j in xrange (len (dcall)):	print	calls_colname[j], "=>\t", dcall[j]
				lcn = ('t_get', 'reasn', 'street', 'house', 'korp')
				cls = ['totalnum', 'cnum']	# Периеменование полей
				vls = [str(dcall[0]), str(dcall[calls_colname.index('number')])]
				rxy = get_place (dbnmap, dcall[calls_colname.index('street')], dcall[calls_colname.index('house')], dcall[calls_colname.index('korp')])
				for key in lcn:
					if dcall[calls_colname.index(key)]:
						cls.append (key)
						if isinstance (dcall[calls_colname.index(key)], basestring):
							vls.append("'%s'" % dcall[calls_colname.index(key)])
						else:	vls.append(str(dcall[calls_colname.index(key)]))
				if rxy:
					street_id, gx, gy, x, y = rxy
					cls.append ("street_id, gx, gy, x, y")
					vls.append ("%d, %9.5f, %9.5f, %d, %d" % (street_id, gx, gy, x, y))
				quin = "INSERT INTO pcall (%s) VALUES (%s);" % (", ".join(cls), ", ".join(vls))
				lquerys.append (quin)
			else:				# Контроль изменений (исполнения)
				pcr  = dbnmap.get_dict("SELECT * FROM pcall WHERE totalnum = %d;" % dcall[0])
				if not pcr:	continue
				lsset = []
				for key in cdic.keys():
					if dcall[calls_colname.index(key)] != pcr[cdic[key]]:
						if dcall[calls_colname.index(key)]:
							val = dcall[calls_colname.index(key)]
							if key == 'pbrg':
								lsset.append("%s = '%s'" % (cdic [key], dcall[calls_colname.index(key)]))
							else:	lsset.append("%s = %s" % (cdic [key], dcall[calls_colname.index(key)]))
				if lsset:
					lquerys.append("UPDATE pcall SET %s WHERE totalnum = %d;" % (', '.join(lsset), dcall[0]))
		if ltotalnum:
			lquerys.append ( "DELETE FROM pcall WHERE totalnum  NOT IN (%s);" % str(ltotalnum)[1:-1])
		if lquerys:
			if not dbnmap.qexecute ('\n'.join (lquerys)):
				print lquerys
	#	print	"querys:", len(lquerys)
	except:	pexcept ('sendat_pcalls')
	finally:
		mutex_pcalls.release()

def	sendat2nnmap (tmr):
	''' Передать данные навигаторов в nnmap	'''
	global	server_dlist
	global	pcalls_dlist
	try:
		if server_dlist or pcalls_dlist:
			dbnmap = dbtools.dbtools(ddb_nnmap)
			'''
			tm_act = int(time.time()) -3600*72	#print '# Max время хранения данных 3 суток'
			dbnmap.qexecute ("DELETE FROM pauto WHERE t_get < %d; DELETE FROM last_pauto WHERE t_get < %d; DELETE FROM loc_points WHERE time < %d;" % (
				tm_act, tm_act, tm_act))
			'''
			if server_dlist:
				sendat_points (tmr, dbnmap)
			if pcalls_dlist:
				sendat_pcalls (tmr, dbnmap)
		else:
			print ".\r",
	#		print "server_dlist AND pcalls_dlist == None"
	except IndexError:
		print "IndexError:", abrf, nms, vls
	except:	pexcept ('sendat2nnmap')

mutex_server =	thread.allocate_lock()
server_dlist =	[]	# Блок пакетов данных принятых сервером
mutex_pcalls =	thread.allocate_lock()
pcalls_dlist =	[]	# Блок пакетов Вызовов принятых из b03
mutex_imdesc =	thread.allocate_lock()
imei_desc = 	{}	# Описание автомобилей из b03
mutex_autobrg =	thread.allocate_lock()
auto2brig =	{}	# Связка Машина -> Бригада
server_not =	-221
FL_getPoints =	False	# Флаг - Идет обработка данных от навигаторов

if __name__ == "__main__":
	syslog.openlog(logoption=syslog.LOG_PID)
	syslog.syslog("Start %s" % sys.argv[0])
	if debuglevel:	print "Start родительский процесс %i" % os.getpid(), sys.argv[0],
	try:
		tmr = time.time()
		if debuglevel:	print	time.strftime("%Y-%m-%d %T", time.localtime(tmr))
		thread.start_new_thread (get_oo, (tmr, ))
		thread.start_new_thread (oo2nnmap, (tmr, True))
		while not imei_desc:	pass
		thread.start_new_thread (server, ())
		while True:
			mutex_server.acquire()
			server_not += 1
			mutex_server.release()
			if server_not > 18:
				server_not = -221
				thread.start_new_thread (server, ())
				#break
			tmr = time.time()
			if (len(server_dlist) > 7) or ((int(tmr) % 29) == 0):
			#	print "FL_getPoints:", FL_getPoints
				thread.start_new_thread (sendat2nnmap, (tmr, ))
				time.sleep(1)
			if (int(tmr) % 17) == 0:
				thread.start_new_thread (oo2nnmap, (tmr, ))
				time.sleep(3)
			elif (int(tmr) & 1023) == 0:	## 17.05 минут
				thread.start_new_thread (oo2nnmap, (tmr, True))
				time.sleep(5)
			else:	time.sleep(1)
	except	KeyboardInterrupt:	pass
	except:	pexcept('MAIN')
	finally:
		syslog.syslog("Stop %s" % sys.argv[0])
	
