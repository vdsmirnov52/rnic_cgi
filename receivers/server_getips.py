#!/usr/bin/python -u
# -*- coding: koi8-r -*-
"""	Утилита 'server_getips.py'
	Сервер приема данных по протоколу 'Wialon IPS' и ретрансляции их на другой сервер

	nohup /home/smirnov/MyTests/receivers/server_getips.py > /home/smirnov/MyTests/log/server_getips.log &

	Настройка KEEPAILVE
	# echo 5 >/proc/sys/net/ipv4/tcp_keepalive_intvl		время между повторами KEEPALIVE-проб
	# echo 5 >/proc/sys/net/ipv4/tcp_keepalive_probes 	максимальное количество KEEPALIVE-проб
	# echo 20 >/proc/sys/net/ipv4/tcp_keepalive_time 		время неактивности соединения
"""

import  os, time, sys
import  syslog
import	thread

LIBRARY_DIR = r"/home/vds/03/mydev/pylib"          # Путь к рабочей директории (библиотеке)
sys.path.insert(0, LIBRARY_DIR)

debuglevel = 1
HOST = '212.193.103.20'
PORT = 7778	#60745

import	google
import	dbtools

def	pexcept (mark, exit = -1):
	exc_type, exc_value = sys.exc_info()[:2]
	syslog.syslog ("EXCEPT %s:\t %s %s" % (mark, str(exc_type), str(exc_value)))
	if debuglevel:	print "EXCEPT %s:\t" % mark, exc_type, exc_value
	if exit >= 0:	os._exit(exit)

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
							agis_data_capture (fileno, requests[fileno])	### Обработка данных
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
				print "not keepalive and not ffno", keepalive, ffno
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
##############################################


def	grad2nmea(f):	
	""" Преробразование координат WGS-84 градусы > NMEA	""" 
	i = int(f)
	r = 100*i +(f-i)*60
	return r

def	nmea2grad(f):
	""" Преробразование координат NMEA > WGS-84 градусы	"""
	i = int(f/100)
	r = i +(f - 100*i)/60
	return r

def	check_pack (cols):
	""" Обработка навигационных данных	"""
	dprm = {}
	dpoint = {}
	ttms = time.mktime(time.strptime(cols[0]+cols[1], "%d%m%y%H%M%S")) -time.altzone
#	ttms = time.mktime(time.strptime(cols[0]+cols[1], "%d%m%y%H%M%S"))	# UTC
#	print cols[:2], ttms, time.strftime("[%T %d-%m-%Y]", time.localtime (ttms)),
#	print ttms, time.strftime("[%T %d-%m-%Y]", time.gmtime(ttms)),
	dpoint['t'] = int(ttms)
	# 5649.4540;N;04333.6557;E;
	if cols[2][:1].isdigit():
		yg = nmea2grad (float(cols[2]))
		dpoint['y'] = yg 

	if cols[4][:1].isdigit():
		xg = nmea2grad (float(cols[4]))
		dpoint['x'] = xg
	
	if cols[6][:1].isdigit():
		speed = int(cols[6])
		dpoint['sp'] = speed
	
	if cols[7][:1].isdigit():
		course = int(cols[7])
		dpoint['cr'] = course
	
	if cols[8][:1].isdigit():
		height = float(cols[8])
		dpoint['ht'] = height
	
	if cols[9][:].isdigit():
		sats = int(cols[9])
		dpoint['st'] = sats

	############### ?????????

	if cols[11][:].isdigit():		# цифровые входы, каждый бит числа соответствует одному входу
		dprm['inputs'] = int(cols[11])
	if cols[12][:].isdigit():		# цифровые выходы, каждый бит числа соответствует одному выходу
		dprm['outputs'] = int(cols[12])
	dprm['adc'] = cols[13]			# аналоговые входы, дробные числа, через запятую.
	dprm['ibutton'] = cols[14]		# код ключа водителя, строка произвольной длины.
	return ttms, dpoint, dprm

def	parse_params (params):
	""" Обработка параметров (протокол Wialon IPS)	"""
	pdict = {}
	try:
		for p in params.split(','):
			if not p:		continue
			pls = p.split(':', 3)
			if len (pls) < 3:
				print "\tparse_params", pls
				continue
			k, t, val = pls
			if 'wln_' in k:		continue
			if t == 1:
				pdict[k] = int(val)
			elif t == 2:
				pdict[k] = float(val)
			else:	pdict[k] = val
	except:
		pexcept ('parse_params')
		print	'\tparse_params', params, pdict
	finally:
		return	pdict

def	parse_datas (iddevice, list_datas):
	""" Разбор пакетов данных (параметров)	"""
	device_id = iddevice[3:-3]
#	print	iddevice, device_id
	
	sstart_tm = 0
	old_params = {}
	try:
		for pack in list_datas:
			if not pack.strip():	continue

			if '#D#' == pack[:3]:
				cols = pack[3:].split(';')
				ttms, dpoint, dprm = check_pack (cols[:-1])
				if not sstart_tm:
					sstart_tm = dpoint['t']
		#		print ttms, dpoint, dprm
				jprm = parse_params (cols[-1].strip())
		#		print 'jprm\t', jprm 
				jprm.update(dprm)
				for k in jprm.keys():
					if not old_params.has_key(k):
						old_params[k] = jprm[k]
					elif old_params[k] != jprm[k]:
						old_params[k] = jprm[k]
					else:	del(jprm[k])
		#		print '\t', jprm 
				ins_dbase (device_id, dpoint, jprm, sstart_tm)
			elif '#SD#' == pack[:4]:
				cols = pack[4:].split(';')
				print '#SD#', check_pack (cols)
			else:
				print	"###\t", pack
	except:
		pexcept ('parse_datas')
		print '\tparse_datas', list_datas	# datas
		print '\tparse_datas', pack

def	is_datas ():
	for fn in fileno_datas.keys():
		if len(fileno_datas[fn]) > 0:	return	True

def	sendat_datas (tmr):
	print	""" Собрать данные от навигаторов по devices_id	"""
	global	FL_getPoints
	global	fileno_devices
	global	fileno_datas
	if FL_getPoints:	return
	try:
		for fn in fileno_devices.keys():
			datas = fileno_datas.get(fn)
			if datas:
				FL_getPoints = True
				str_datas = ''.join(datas)
				list_datas = str_datas.split('\r\n')
				mutex_datas.acquire()
				if str_datas[-2:] == '\r\n':
					fileno_datas[fn] = []
				else:
					fileno_datas[fn] = [list_datas[-1]]
				mutex_datas.release()
				parse_datas (fileno_devices[fn], list_datas[:-1])

	except IndexError:	print "IndexError:", abrf, nms, vls
	except:		pexcept ('sendat_datas')
	finally:	FL_getPoints = False

ddb_receiver =	"host=212.193.103.20 dbname=receiver port=5432 user=smirnov"
ddb_atest =	"host=212.193.103.20 dbname=agro_test port=5432 user=smirnov"
devid_ates =	['864287036420295', '864287036626412', '864287036626578', '864287036626693', '864287036626909', '864287036627022', '864287036627055', '864287036627493', '864287036627501', '866192038866446', '866710036405972',]
idb_recvr =	None
idb_atest =	None

def	ins_dbase (device_id, dpoint, dparams, sstart_tm):
	global	idb_recvr
	global	idb_atest

	cols = ['idd']
	sidd = str(device_id)
	vals = [sidd]
	print device_id, time.strftime("%Y-%m-%d %T", time.localtime(int(sstart_tm))),	#sstart_tm, 

	if device_id in devid_ates:
		if not idb_atest:	idb_atest = dbtools.dbtools (ddb_atest)
		idb = idb_atest
	else:
		if not idb_recvr:	idb_recvr = dbtools.dbtools (ddb_receiver)
		cols.append ('ida')
		vals.append (sidd)
		idb = idb_recvr
	if not idb:	return

	is_pos = 0
	for k, val in dpoint.iteritems():
		if k in 'xy':	is_pos += 1
		cols.append (k)
		vals.append (str(val))

	querys = ["INSERT INTO data_pos (%s) VALUES ('%s')" % (', '.join(cols), "', '".join(vals))]
	if is_pos:
		querys.append ("DELETE FROM last_pos WHERE idd = '%s'" % sidd)
		querys.append ("INSERT INTO last_pos (%s) VALUES ('%s')" % (', '.join(cols), "', '".join(vals)))

	if dparams:
		print "\t", dparams ,
		sparams = str(dparams).replace("'", '"')
		dtm = dpoint['t'] - sstart_tm
		if dtm <= 0:
			idb.qexecute ("DELETE FROM last_prms WHERE idd = '%s';INSERT INTO last_prms (idd, tm, dtm, params) VALUES ('%s', %d, %d, '%s');" % (sidd, sidd, sstart_tm, dtm, sparams))
	#	if dtm == 0:	querys.append ("DELETE FROM last_prms WHERE idd = '%s'" % sidd)
	#	querys.append ("INSERT INTO last_prms (idd, tm, dtm, params) VALUES ('%s', %d, %d, '%s')" % (sidd, sstart_tm, dtm, sparams))
		querys.append ("INSERT INTO data_prms (idd, t, params) VALUES ('%s', %d, '%s')" % (sidd, dpoint['t'], sparams))
#	print ';\n'.join(querys)
	print idb.qexecute (';\n'.join(querys))

def	agis_data_capture (fileno, data):
	global	server_not
	global	fileno_devices
	global	fileno_datas

	try:
	#	print data
		dlists = data.split('\r\n', 1)
		if dlists[0][:3] == '#L#':
			if fileno_datas.get(fileno):
				print   "#>>>", fileno_devices [fileno], fileno_datas.get(fileno)
			mutex_devices.acquire()
			fileno_devices [fileno] = dlists[0]
			mutex_devices.release()
			print	fileno_devices [fileno]
	#		print	fileno_datas.get(fileno)
			mutex_datas.acquire()
			fileno_datas [fileno] = [dlists[1]]
			mutex_datas.release()
		else:
			mutex_datas.acquire()
			fileno_datas [fileno].append(data)
			mutex_datas.release()
	#		print	fileno_datas.get(fileno)
		
	#	print "<<<", fileno
		mutex_server.acquire()
		server_not = 0
		mutex_server.release()
		return
	except:
		pexcept('agis_data_capture')
		pdata (data)

########################

mutex_devices =	thread.allocate_lock()	# Устройсва открыкрывшие соединения 
fileno_devices =	{}
mutex_datas = thread.allocate_lock()	# Данные полеченные от Устройсва
fileno_datas =	{}
mutex_server =	thread.allocate_lock()
server_not =	-221

########################
FL_getPoints =	False	# Флаг - Идет обработка данных от навигаторов

if __name__ == "__main__":
	syslog.openlog(logoption=syslog.LOG_PID)
	syslog.syslog("Start %s" % sys.argv[0])
	if debuglevel:	print "Start родительский процесс %i" % os.getpid(), sys.argv[0],
	try:
		tmr = time.time()
		if debuglevel:	print	time.strftime("%Y-%m-%d %T", time.localtime(tmr))
	#	thread.start_new_thread (get_oo, (tmr, ))
		thread.start_new_thread (server, ())
		while True:
			mutex_server.acquire()
			server_not += 1
			mutex_server.release()
	#		print	server_not, tmr
			if server_not > 31:
				server_not = -221
				thread.start_new_thread (server, ())
				#break
			tmr = time.time()
			if is_datas():
			#	print "FL_getPoints:", FL_getPoints
				thread.start_new_thread (sendat_datas, (tmr, ))
				time.sleep(2)
			else:	time.sleep(1)
	except	KeyboardInterrupt:	pass
	except:	pexcept('MAIN')
	finally:
		syslog.syslog("Stop %s" % sys.argv[0])
	
