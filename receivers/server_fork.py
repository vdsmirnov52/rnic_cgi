#!/usr/bin/python -u
# -*- coding: utf-8 -*-
"""	Утилита 'server_fork.py'
	Сервер приема данных по протоколу 'Wialon IPS' и ретрансляции их на другой сервер
	nohup /home/smirnov/MyTests/receivers/server_fork.py > /home/smirnov/MyTests/log/server_fork.log &
"""

import	os, time, sys

HOST = '212.193.103.20'
PORT = 7778	#60745

def	pexcept (mark, exit = -1):
	exc_type, exc_value = sys.exc_info()[:2]
#	syslog.syslog ("EXCEPT %s:\t %s %s" % (mark, str(exc_type), str(exc_value)))
	if isdebug:	print "EXCEPT %s:\t" % mark, exc_type, exc_value
	if exit >= 0:	os._exit(exit)

def	pdata (data, sufx = None):	## DEBUD
	if len(data):
		for c in data:  print "%02x" % ord(c) ,
	if sufx:	print sufx, len(data)
	else:		print "<<<", len(data)

def	psdata (data, sufx = None):
	for d in data.split('\n'):
		if d[0] == '#':
			print "#>\t", d.strip()
		else:	pdata(d)

def	server():
	global	pre_fork
	if isdebug:	print "Start server"
	not_len = 0
	jtm = 0
	try:
		import	socket

		listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		listener.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
		keepalive = listener.getsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE)
	#	print "socket.SO_KEEPALIVE", keepalive 
		listener.bind((HOST, PORT))
		listener.listen(1)
	
		while True:
		#	sock = socket.accept (listener)
			connection, address = listener.accept()
			print 'Connect', connection.fileno(), address
			pid = os.fork()
			if pid > 0:	# PARENT
				pre_fork = 'PARENT'
				print pre_fork, pid
			if pid == 0:
				pre_fork = 'CHILD'
				listener.close()
				fno = connection.fileno()
				while True:
					result = connection.recv(1024)
					if len(result) == 0:	break
					connection.send('#AD#\r\n')
				#	print fno, '<<\t', result
					agis_data_capture (fno, result)
				connection.close()
				os._exit(0)
			
	except	socket.error:
	#	pexcept (pre_fork, -1)
		exc_type, exc_value = sys.exc_info()[:2]
		print "EXCEPT socket.error:\t", exc_type, exc_value
		if 'Address already in use' == exc_value:	sys.exit()
	except:
		pexcept ('ZZZ '+ pre_fork, -1)
		sys.exit()
#	finally:
#		print pre_fork, "\tlistener.close"
#		listener.close()

def	grad2nmea(f):	
	""" Преробразование координат WGS-84 градусы > NMEA	""" 
	i = int(f)
	r = 100*i +(f-i)*60
#	print "\tgrad2nmea: %010.4f %09.4f" % (r, r)
	return r

def	nmea2grad(f):
	""" Преробразование координат NMEA > WGS-84 градусы	"""
	i = int(f/100)
	r = i +(f - 100*i)/60
#	print "nmea2grad", r
	return r

#####################################
data_0 = """#L#866192039696875;NA\r
#D#060218;072253;5616.7029;N;04411.6241;E;34;186;0.000000;12;NA;129;0;3.000000,8.000000;NA;valid_coords:1:1,navigation_system:3:GPS+Glonass,status:1:43312,gsm:1:-51,pwr_i2:1:0,pwr_i3:1:0,pwr_ext:2:4.103000,pwr_int:2:28.792000,event_code:3:5893,mileage:2:2421.181885,mileage_time:1:3,fuel_sens1_freq:1:0,fuel_sens1_temp:1:0,fuel_sens1_lvl:1:65531,fuel_sens2_freq:1:0,fuel_sens2_temp:1:0,fuel_sens2_lvl:1:65531,fuel_sens3_freq:1:0,fuel_sens3_temp:1:0,fuel_sens3_lvl:1:65531,temp1:1:26\r
#D#060218;072302;5616.6541;N;04411.6122;E;35;189;0.000000;12;NA;129;0;3.000000,8.000000;NA;valid_coords:1:1,navigation_system:3:GPS+Glonass,status:1:43312,gsm:1:-83,pwr_i2:1:0,pwr_i3:1:0,pwr_ext:2:4.103000,pwr_int:2:28.793000,event_code:3:5893,mileage:2:2421.267822,mileage_time:1:9,fuel_sens1_freq:1:0,fuel_sens1_temp:1:0,fuel_sens1_lvl:1:65531,fuel_sens2_freq:1:0,fuel_sens2_temp:1:0,fuel_sens2_lvl:1:65531,fuel_sens3_freq:1:0,fuel_sens3_temp:1:0,fuel_sens3_lvl:1:65531,temp1:1:28\r
#D#060218;072313;5616.6041;N;0441"""
data_1 = """1.5962;E;28;195;0.000000;12;NA;129;0;3.000000,8.000000;NA;valid_coords:1:1,navigation_system:3:GPS+Glonass,status:1:43312,gsm:1:-83,pwr_i2:1:0,pwr_i3:1:0,pwr_ext:2:4.103000,pwr_int:2:28.789000,event_code:3:5893,mileage:2:2421.357178,mileage_time:1:11,fuel_sens1_freq:1:0,fuel_sens1_temp:1:0,fuel_sens1_lvl:1:65531,fuel_sens2_freq:1:0,fuel_sens2_temp:1:0,fuel_sens2_lvl:1:65531,fuel_sens3_freq:1:0,fuel_sens3_temp:1:0,fuel_sens3_lvl:1:65531,temp1:1:26\r
#D#060218;072314;5616.5998;N;04411.5932;E;29;202;0.000000;12;NA;129;0;3.000000,8.000000;NA;valid_coords:1:1,navigation_system:3:GPS+Glonass,status:1:43312,gsm:1:-83,pwr_i2:1:0,pwr_i3:1:0,pwr_ext:2:4.103000,pwr_int:2:28.789000,event_code:3:5893,mileage:2:2421.365234,mileage_time:1:1,fuel_sens1_freq:1:0,fuel_sens1_temp:1:0,fuel_sens1_lvl:1:65531,fuel_sens2_freq:1:0,fuel_sens2_temp:1:0,fuel_sens2_lvl:1:65531,fuel_sens3_freq:1:0,fuel_sens3_temp:1:0,fuel_sens3_lvl:1:65531,temp1:1:27\r
"""
#####################################

pre_fork =	None
data_tail =	None
device_id =	None
dbase_id =	None
sstart_tm =	None
old_params = 	{}

def	agis_data_capture (fileno, data):
	""" Розбор пакетов протокола Wialon IPS	"""
	global	data_tail
	global	device_id
	global	dbase_id
	global	sstart_tm
	global	old_params

	jdlist = []
#	old_params = {}
	jdlist = data.split('\n')
	jlen = len(jdlist) -1
	print '#'*11, fileno,
	for j in xrange(jlen):
		if j == 0 and jdlist[0][:3] == '#L#':
			if device_id and device_id != jdlist[0].strip()[3:-3]:
				print 'D'*11, 'device_id', device_id, '!=', 
			#	sstart_tm = None
			#	old_params = {}
			device_id = jdlist[0].strip()[3:-3]
			if not dbase_id:
				dbase_id = dbtools.dbtools ('host=212.193.103.20 dbname=agro_test port=5432 user=smirnov')
	#		print  device_id
			continue
		if j == 0 and data_tail:
			pack = data_tail +jdlist[j]
		else:	pack = jdlist[j]
	#	print '\t', pack[:99]
		if '#D#' == pack[:3]:
			cols = pack[3:].split(';')
			ttms, dpoint, dprm = check_pack (cols[:-1])
			if not sstart_tm:
				sstart_tm = dpoint['t']
	#		print ttms, dpoint, dprm
			jprm = parse_params (cols[-1].strip())
			jprm.update(dprm)
			for k in jprm.keys():
				if not old_params.has_key(k):
					old_params[k] = jprm[k]
				elif old_params[k] != jprm[k]:
					old_params[k] = jprm[k]
				else:	del(jprm[k])
	#		print '\t', jprm 
			ins_dbase (dbase_id, device_id, dpoint, jprm, sstart_tm)
		elif '#SD#' == pack[:4]:
			cols = pack[4:].split(';')
			check_pack (cols)
		else:	print pack
	
	data_tail = jdlist[-1]
	if data_tail:	print 'data_tail', data_tail
	return

import	dbtools
def	ins_dbase (idb, device_id, dpoint, dparams, sstart_tm):
	cols = ['idd']
	sidd = str(device_id)
	vals = [sidd]
	print device_id, sstart_tm, 
	is_pos = 0
	for k, val in dpoint.iteritems():
		if k in 'xy':	is_pos += 1
		cols.append(k)
		vals.append(str(val))

	querys = ["INSERT INTO data_pos (%s) VALUES ('%s')" % (', '.join(cols), "', '".join(vals))]
	if is_pos:
		querys.append ("DELETE FROM last_pos WHERE idd = '%s'" % sidd)
		querys.append ("INSERT INTO last_pos (%s) VALUES ('%s')" % (', '.join(cols), "', '".join(vals)))
	if dparams:
		dtm = dpoint['t'] - sstart_tm
		if dtm == 0:	querys.append ("DELETE FROM last_prms WHERE idd = '%s'" % sidd)
		sparams = str(dparams).replace("'", '"')
		querys.append ("INSERT INTO last_prms (idd, tm, dtm, params) VALUES ('%s', %d, %d, '%s')" % (sidd, sstart_tm, dtm, sparams))
		querys.append ("INSERT INTO data_prms (idd, t, params) VALUES ('%s', %d, '%s')" % (sidd, dpoint['t'], sparams))
	print idb.qexecute (';\n'.join(querys))
#	print ';\n'.join(querys), idb.qexecute (';\n'.join(querys))

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
#	print '<<<'
	return ttms, dpoint, dprm

#	params Name:Type:Value	Type = {1 - int, 2 - double, 3 - string}
#	SOS:1:1 - нажата тревожная кнопка
''' Arnavi
	cell_id:1:23911, lac:1:5249, mnc:1:2, mcc:1:250, gsm:1:3, gps_full_mileage:2:894.230000, gsm_st:1:3, nav_st:1:1,
	mw:1:0, sim_t:1:0, sim_in:1:1, st0:1:0, st1:1:0, st2:1:0,
	pwr_in:1:1, pwr_ext:2:0.000000, freq_1:1:0, info_messages:1:306
	'''

def	parse_params (params):
	""" Обработка параметров (протокол Wialon IPS)	"""
	pdict = {}
	for p in params.split(','):
		if not p:		continue
		k, t, val = p.split(':', 3)
		if 'wln_' in k:		continue
		if t == 1:
			pdict[k] = int(val)
		elif t == 2:
			pdict[k] = float(val)
		else:	pdict[k] = val
	return	pdict

############################################
	
import	syslog
import	signal

def	sigchld (signum, fname):
	if isdebug:	print pre_fork, 'SIGCHLD', signum
	time.sleep(0.01)
	rrr = os.wait()
#	print os.system('ps -ef | grep _fork.py$')
#	rrr = os.waitpid(0, os.WNOHANG)
	print 'SIGCHLD', rrr
	
isdebug = True

if __name__ == "__main__":
	tmr = time.time()
	if isdebug:
		print "Start PID: %i" % os.getpid(), sys.argv[0], time.strftime("%Y-%m-%d %T", time.localtime(tmr))
		print	"\t", HOST, PORT
	'''
	agis_data_capture(4, data_0)
	agis_data_capture(4, data_1)
	sys.exit()
	'''
	syslog.openlog(logoption=syslog.LOG_PID)
	syslog.syslog("Start %s" % sys.argv[0])
	try:
		signal.signal(signal.SIGCHLD, sigchld)
		while True:	server()
	except	KeyboardInterrupt:	#	pass
		print "KeyboardInterrupt"
		sys.exit(0)
		
	except:	pexcept('"__main__"')
	finally:
		print '#'*33
		syslog.syslog("Stop %s" % sys.argv[0])
