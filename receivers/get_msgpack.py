#!/usr/bin/python -u
# -*- coding: utf-8 -*-
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
		for c in data:  print "%02x" % ord(c) ,
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
			tid = int(unpacked[5])
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

mutex_server =	thread.allocate_lock()
server_dlist =	[]	# Блок пакетов данных принятых сервером
mutex_pcalls =	thread.allocate_lock()
pcalls_dlist =	[]	# Блок пакетов Вызовов принятых из b03
mutex_imdesc =	thread.allocate_lock()
imei_desc = 	{}	# Описание автомобилей из b03
mutex_autobrg =	thread.allocate_lock()
auto2brig =	{}	# Связка Машина -> Бригада
server_not =	-221

if __name__ == "__main__":
	syslog.openlog(logoption=syslog.LOG_PID)
	syslog.syslog("Start %s" % sys.argv[0])
	if debuglevel:	print "Start родительский процесс %i" % os.getpid(), sys.argv[0],
	try:
		tmr = time.time()
		if debuglevel:	print	time.strftime("%Y-%m-%d %T", time.localtime(tmr))
	#	thread.start_new_thread (get_oo, (tmr, ))
	#	thread.start_new_thread (oo2nnmap, (tmr, True))
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
			time.sleep(2)
			'''
			tmr = time.time()
			if (int(tmr) % 17) == 0:
				thread.start_new_thread (oo2nnmap, (tmr, ))
			elif (int(tmr) & 1023) == 0:	## 17.05 минут
				thread.start_new_thread (oo2nnmap, (tmr, True))
			if (int(tmr) % 5) == 0:
				thread.start_new_thread (sendat2nnmap, (tmr, ))
			'''
	except	KeyboardInterrupt:	pass
	except:	pexcept('MAIN')
	finally:
		syslog.syslog("Stop %s" % sys.argv[0])
	
