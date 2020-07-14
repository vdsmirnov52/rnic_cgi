#!/usr/bin/python -u
# -*- coding: utf-8 -*-
"""     Демон receivers/send_ts64ips.py		(Kozorez)

	nohup /home/smirnov/MyTests/CGI/receivers/send_ts64ips.py > /home/smirnov/MyTests/log/send_ts64ips.log &

	- Читает данные ТС ЖКХ-М (bm_ssys = 64) из БД receive.data_pos 
	- Формирует очередь пакетов протокола Wialon IPS UDP
	- Отправляет данные из очереди на 109.95.211.141 
"""
import	os, sys, time
import	thread, Queue, signal
import	socket
import	json

#	Test Wialon IPS:
#	ID_DEV число в диапазоне 230056-230065
# Test
#	Протоколы форматов omnicomm, wialon IPS, АвтоГраф принимаются на сервер 5.189.234.14 порт 2226 

IPS_IP = '5.189.234.14'
IPS_PORT = 2323		#2226
'''
IPS_IP =	'109.95.211.141'
IPS_PORT =	2241
'''
'''
# UDP		~/MyTests/egts/udp_test.py	- Прием данных
IPS_IP =	'127.0.0.1'
IPS_PORT =	50005
# TCP Local	~/MyTests/egts/egts_test.py	- Прием данных
IPS_IP =	'10.10.2.241'
IPS_PORT =	9145
'''
Q_SEND = None

def	ips_send (queue):

#	logn = ''
	ipsock = None
	jsp = queue.get()
	logn = jsp
	j = 0
	print 'ips_send\t>>\t'
	while True:
	#	print '\t>>\t', jsp.strip()
	#	print logn.strip(), '\t>>\t', jsp.strip(),
		if not logn:	logn = jsp
		try:
			if not ipsock:
				ipsock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)	# UDP
				ipsock.setblocking(False)
			#	ipsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)	# TCP
			#	ipsock.setblocking(True)
				ipsock.connect((IPS_IP, IPS_PORT))
				print "Connect ipsock.fileno:", ipsock.fileno()
			ipsock.send(jsp)
			'''
			while j < 5:		### TCP
			#	j += 1
			#	time.sleep(1)
				result = ipsock.recv(1024)
				print '\t<<', result.strip()
				break
			if '#A' != result[:2]:
				ipsock.close()
				ipsock = None
				jsp = logn
				time.sleep(11)
				continue
			'''
		except socket.error:
			print '\nexcept ips_send', sys.exc_info()[1]
			ipsock.close()
			ipsock = None
		#	jsp = logn
			time.sleep(11)
			continue
		jsp = queue.get()
	print 'ips_send ipsock.close', 'Q'*22

LIBRARY_DIR = r"/home/smirnov/pylib"    # Путь к рабочей директории (библиотеке)
sys.path.insert(0, LIBRARY_DIR)
import  dbtools
'''
bases = {
	'vms_ws': 'host=10.40.25.176 dbname=vms_ws port=5432 user=vms',
	'recvr': 'host=127.0.0.1 dbname=receiver port=5432 user=smirnov',
	'contr': 'host=127.0.0.1 dbname=contracts port=5432 user=smirnov',
	}
'''

def	get_racv_list ():
	dev_list = []
	res = RECVR.get_table('vrecv_ts', 'bm_ssys = 64', cols='device_id')
	if not res:	return
	for r in res[1]:
		if r[0]:	dev_list.append(str(r[0]))
	return	dev_list

RECVR =	None
recvr_dev_list = None
	
def	send_data ():
	global	Q_SEND
	
	while True:
		qsd = Q_SEND.get()
		print	qsd
		time.sleep(1)


def	main ():
	global	RECVR, recvr_dev_list
	global	Q_SEND
	nmea = lambda  f: 100*int(f) +(f-int(f))*60

	last_id = None
	max_id_dp = 0
	try:
		Q_SEND = Queue.Queue()
	#	thread.start_new_thread (send_data, ())
		thread.start_new_thread (ips_send, (Q_SEND,))
		RECVR =	dbtools.dbtools('host=127.0.0.1 dbname=receiver port=5432 user=smirnov')	#bases['recvr'])
		recvr_dev_list = get_racv_list ()
		print "len recvr_dev_list", len(recvr_dev_list)
		#	id_dp, ida, idd, x, y, t, sp, cr, ht, st
		query = "SELECT id_dp, ida, idd, x, y, t, sp, cr, ht, st FROM data_pos WHERE ida IN (%s) ORDER BY id_dp DESC LIMIT 1" % ', '.join(recvr_dev_list)
		if RECVR and recvr_dev_list:
			j = 0
			while True:
				tt = time.time()
			#	print query
				rows = RECVR.get_rows (query)
				print	"\tlen(rows)", len(rows), "\tdt:", (time.time() - tt), "\tmax_id_dp:", max_id_dp
				for r in rows:
					id_dp, ida, idd, x, y, t, sp, cr, ht, st = r
					# time.localtime Москва
			#		sd = "%s#SD#%s;%09.4f;N;%010.4f;E;%s;%s;NA;%s\r\n" % (ida, time.strftime('%d%m%y;%H%M%S', time.localtime(t)), nmea(float(x)), nmea(float(y)), sp, cr, st)
					# time.gmtime UTC
			#		sd = "%s#SD#%s;%09.4f;N;%010.4f;E;%s;%s;NA;%s\r\n" % (ida, time.strftime('%d%m%y;%H%M%S', time.gmtime(t)), nmea(float(x)), nmea(float(y)), sp, cr, st)
					sd = "%s#SD#%s;%09.4f;N;%010.4f;E;%s;%s;NA;%s\r\n" % (ida, time.strftime('%d%m%y;%H%M%S', time.gmtime(t)), nmea(float(y)), nmea(float(x)), sp, cr, st)
			#		print id_dp, ida, idd, x, y, t, sp, cr, ht, st,
			#		print "\t", sd[:-1]
					Q_SEND.put(sd)
					'''
					'''
				#	max_id_dp = id_dp
					if id_dp > max_id_dp:	max_id_dp = id_dp
				time.sleep(1)
			#	query = "SELECT id_dp, ida, idd, x, y, t, sp, cr, ht, st FROM data_pos WHERE id_dp > %d AND ida IN (%s) ORDER BY id_dp" % (max_id_dp, ', '.join(recvr_dev_list) )
				query = "SELECT id_dp, ida, idd, x, y, t, sp, cr, ht, st FROM data_pos WHERE id_dp > %d AND ida IN (%s)" % (max_id_dp, ', '.join(recvr_dev_list) )
				j += 1
				if j > 111:	break
		'''
		'''
		os._exit(0)
	except:
		exc_type, exc_value = sys.exc_info()[:2]
		print "main:", exc_type, exc_value
		os._exit(-1)
	
def	test ():
	print	"\tTest"

if __name__ == "__main__":
	print 'Start:', sys.argv, time.strftime('\t%T', time.localtime(time.time()))
	while True:
		try:
			pid = os.fork()
			if pid > 0:     # PARENT
				pre_fork = 'PARENT'
				print pre_fork, "os.waitpid"
				os.waitpid(pid, 0)
			elif pid == 0:
				pre_fork = 'CHILD'
				main ()
			else:
				pre_fork = 'ERROR'

			print pre_fork, pid
			time.sleep(50)
		except  KeyboardInterrupt:
			print "KeyboardInterrupt"
			break
		except:
			exc_type, exc_value = sys.exc_info()[:2]
			print "#"*22, exc_type, exc_value
			
		print	test()
