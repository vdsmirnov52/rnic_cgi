#!/usr/bin/python -u
# -*- coding: utf-8 -*-
"""	Утилита 'server_test.py'
	Сервер приема данных по протоколу 'Wialon IPS' и ретрансляции их на другой сервер
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
	if isdebug:	print "Start server"
	not_len = 0
	jtm = 0
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
						#	print requests[fileno]
						#	jtm += 1
							jtm = 0
							res = agis_data_capture (fileno, requests[fileno])
							if res:
						#		print res.strip()
								connections[fileno].send(res)
							times[fileno] = intime
							not_len = 0
						else:
							not_len += 1
							print "Close", fileno, not_len
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
					if intime - times[fn] > 1900:	#1800:
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
			if jtm:		jtm += 1
			if jtm > 1000:	break	# максимальное время отсутствия данных
			'''
			if not int(time.time()) % 100000:
				print "DEBUG break"
				break	# DEBUG
			'''
	except	socket.error:
		pexcept ('server')
	except:		pexcept ('server')
	finally:
		print "\tserversocket.close"
		serversocket.close()

def	grad2nmea(f):	
	""" Преробразование координат WGS-84 градусы > NMEA	""" 
	i = int(f)
	r = 100*i +(f-i)*60
	print "\tgrad2nmea: %010.4f %09.4f" % (r, r)
	return r

def	nmea2grad(f):
	""" Преробразование координат NMEA > WGS-84 градусы	"""
	i = int(f/100)
	r = i +(f - 100*i)/60
	print "nmea2grad", r
	return r

import 	thread
import	Queue
mutex_data_pipe =  thread.allocate_lock()
data_pipe_desc =  {}

def	agis_data_capture (fileno, data):
	# Wialon IPS
	global	server_dlist
	global	server_not
	global	data_pipe_desc
#	new_connect = False
	jdlist = []
	try:
		if len(data) > 0:
		#	server_not = 0
			jdlist = data.split('\n')
			if not jdlist:	return	'#Z#'
			if not (data_pipe_desc and data_pipe_desc.has_key(fileno)):
				if jdlist[0][:3] != '#L#':
					if isdebug:	print "Ошибка формата данных.\n\t", data
					return '#AL#0\r\n'
				mutex_data_pipe.acquire()
				data_pipe_desc[fileno] = Queue.Queue()
				mutex_data_pipe.release()
			#	new_connect = True
				mutex_server.acquire()
				server_dlist.append((fileno, jdlist[0].strip()))
				mutex_server.release()
			jquu = data_pipe_desc[fileno]

	#		if isdebug:	print 'Wialon IPS :', data
			de = "ZZZZZZZZZZZZZZZZ"
			for d in jdlist:
				if not d or d == '':	continue
				if d[:1] != '#':	continue
				if d[-1:] != '\r':	break
				de = d.strip()
				if de[:3] == '#L#':
					jquu.put('#L#230056;NA')
					continue
				jquu.put(de)
		#		print de
		#	print	"Qsize:\t", jquu.qsize()
			if '#P#' == de.strip():	ans = '#AP#'
			elif '#L#' == de[:3]:		ans = '#AL#1'
			else:
				if de[2] == '#':	ans = '#A%s#1' % de[1]
				elif de[3] == '#':	ans = '#A%s#1' % de[1:3]
				else:	ans = '###'
			return ans +'\r\n'
		else:	pass
	except:
		pexcept('agis_data_capture')
		pdata (data)

def	sss (aaa):
	global	server_dlist
	global	data_pipe_desc

	print "sss %d, %s" % (aaa, time.strftime("%Y-%m-%d %T", time.localtime(time.time())))
#	print server_dlist
	while server_dlist:
		mutex_server.acquire()
		dpack = server_dlist.pop(0)
		mutex_server.release()
		fid = dpack[0]		# DEBUG
	#	print dpack, dpack[0], fid
		thread.start_new_thread (send_queue, (fid, ))
	'''
	for f in data_pipe_desc.keys():
		jquu = data_pipe_desc[f]
		while jquu.qsize():
			print "jquu>", jquu.get()
	'''
import	socket

def	send_queue (fid):
	global	data_pipe_desc
	host = "109.95.210.203"
	port = 2226
	sock = None

	if not (data_pipe_desc and data_pipe_desc.has_key(fid)):
		print "Not fid or data_pipe_desc"
		return
	jquu = data_pipe_desc[fid]
	print "send_queue jquu.qsize:", jquu.qsize()
#	try:
	while True:
		if not jquu.qsize():
			time.sleep(10)
			continue
		ssend = jquu.get() +'\r\n'
		print "jquu>\t", ssend
		if not sock:
			sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			sock.connect((host, port))
		sock.send(ssend)
		while True:
			time.sleep(.1)
			result = sock.recv(1024)
			print "result:", result
			break
			
#	except:	print "except: send_queue"
	
############################################
import	syslog
import	signal

isdebug = True
mutex_server =  thread.allocate_lock()
server_dlist =  []
mutex_dsend = thread.allocate_lock()
dsend_list = []

server_not = -222

if __name__ == "__main__":
	tmr = time.time()
	if isdebug:
		print "Start PID: %i" % os.getpid(), sys.argv[0], time.strftime("%Y-%m-%d %T", time.localtime(tmr))
		print	"\t", HOST, PORT
	'''
	ID_DEV число в диапазоне 230056-230065
	nmea2grad(2345.6789)
	grad2nmea(nmea2grad(2345.6789))
	grad2nmea(nmea2grad(5649.4458))
	grad2nmea(nmea2grad(04333.6342))
	thread.start_new_thread (server, ())
	print agis_data_capture (1, '#SD#181017;113355;NA;NA;NA;NA;NA;NA')
	while True:
		server()
		time.sleep(10)
	data = "#L#864287036626578;NA\r\n#D#251017;091211;5653.4112;N;04338.8960;E;76;24;110.000000;24;NA;0;0;NA,NA,NA,0.000000;NA;gps_full_mileage:2:5661.790000,gsm_st:1:3,nav_st:1:3,mw:1:1,sim_t:1:0,sim_in:1:1,st0:1:0,st1:1:0,st2:1:0,pwr_in:1:3,pwr_ext:2:13.950000,freq_1:1:0,wln_brk_max:2:0.124000,wln_accel_max:2:0.093000,wln_crn_max:2:0.257000,info_messages:1:315\r\n"
	agis_data_capture(4, data)
	sys.exit()
#	help(thread)
	'''
	syslog.openlog(logoption=syslog.LOG_PID)
	syslog.syslog("Start %s" % sys.argv[0])
	try:
		thread.start_new_thread (server, ())
	#	print "thread.error", thread.error()
	#	print "hread.start_new_thread",	thread.start_new_thread (server, (tmr, ))
		while True:
			mutex_server.acquire()
			server_not += 1
			mutex_server.release()
			if server_not > 10:
				server_not = -222
				thread.start_new_thread (server, ())
		#	print "hread.start_new_thread",
			if server_dlist:
				thread.start_new_thread (sss, (222, ))
			time.sleep(3)
	except	KeyboardInterrupt:	#	pass
		print "KeyboardInterrupt"
		
	except:	pexcept('MAIN')
	finally:
		print '#'*33
		syslog.syslog("Stop %s" % sys.argv[0])
