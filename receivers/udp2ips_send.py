#!/usr/bin/python -u
# -*- coding: utf-8 -*-
''' Установка пакетов: socat & tcpflow

'''
import	os, sys, time
import	thread, Queue, signal
import	socket
import	json

#	Test Wialon IPS:
#	ID_DEV число в диапазоне 230056-230065
IPS_IP = '109.95.210.203'
IPS_PORT = 2226
IPS_IDS = [6476641896, 6476626262, 6476546985, 6476408318, 6476433867,  183371206, 183365066, 183371220, 183371215, 183366474]
IPS_SEND = [None, None, None, None, None, None, None, None, None, None]

def	ips_send (queue, jid):
	global	IPS_SEND

	logn = ''
	ipsock = None
	j = 0
	jsp = queue.get()
	logn = jsp
	while True:
		print logn.strip(), '\t>>\t', jsp.strip(),
	#	if not logn:	logn = jsp
		try:
			if not ipsock:
				ipsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		#		ipsock.setblocking(False)
				ipsock.connect((IPS_IP, IPS_PORT))
			ipsock.send(jsp)
			while j < 5:
			#	j += 1
				time.sleep(2)
				result = ipsock.recv(1024)
				print '\t<<', result.strip()
				break
			if '#A' != result[:2]:
				ipsock.close()
				ipsock = None
				jsp = logn
				time.sleep(12)
				continue
		except socket.error:
			print '\nexcept ips_send', sys.exc_info()[1]
			ipsock.close()
			ipsock = None
			jsp = logn
			time.sleep(12)
			continue
		jsp = queue.get()
	print 'ips_send ipsock.close', 'Q'*22

nmea =	lambda  f: 100*int(f) +(f-int(f))*60
def	sint (sv):
	try:
		si= int(float(sv))
		if si >= 0:
			return str(si)
		else:	return 'NA'
	except:	return 'NA'

def	ips_pack (queue, jsp):
#	{u'lon': u'43.5611038', u'al': u'0', u's': u'11', u'v': u'20.0', u'lat': u'56.3225326', u'cr': u'283.0', u'dt': u'2017-11-20T06:39:20.000Z', u'id': u'6476546985'}
#	#D#251017;091211;5653.4112;N;04338.8960;E;76;24;110.000000;24;NA;0;0;NA,NA,NA,
#	#SD#date;time;lat1;lat2;lon1;lon2;speed;course;height;sats 
	try:
		dt = jsp['dt']
		sd = "#SD#%s%s%s;%s;%09.4f;N;%010.4f;E;%s;%s;NA;%s\r\n" % (dt[8:10], dt[5:7], dt[2:4], dt[11:19].replace(':', ''),
			nmea(float(jsp['lat'])), nmea(float(jsp['lon'])), sint(jsp['v']), sint(jsp['cr']), sint(jsp['s']))
		queue.put(sd)
	except:	pass

def	to_ips(jspack):
	global	IPS_SEND

	jspack = dict(jspack)
#	print type(jspack), '\t', jspack, jspack['id']	#, jspack.keys()
	if jspack.has_key('id') and int(jspack['id']) in IPS_IDS:
		iid = int(jspack['id'])
	#	print type(jspack['id']), iid
		j = IPS_IDS.index(iid)
		if IPS_SEND[j]:
		#	IPS_SEND[j].put(jspack)
			ips_pack (IPS_SEND[j], jspack)
		else:
			IPS_SEND[j] = Queue.Queue()
			IPS_SEND[j].put("#L#%d;NA\r\n" % (j+230056))
		#	IPS_SEND[j].put(jspack)
			ips_pack (IPS_SEND[j], jspack)
			thread.start_new_thread (ips_send, (IPS_SEND[j], j))

import	dbtools

DB_ID = None
BLOCK_sqldb = False
SQL_IDS = []
jquery = 0

def	send_sqlbd (jspack):
	global	DB_ID
	global	jquery

	try:
		idd = int(jspack['id'])
		tm = time.mktime(time.strptime(jspack['dt'][:-5], "%Y-%m-%dT%H:%M:%S"))
		if time.time() - tm > 36000:
			print time.time(), tm, (time.time() - tm)
			return

		tm += 3*3600
		querys = ["DELETE FROM last_pos WHERE ida =%d;" % idd,
			"INSERT INTO last_pos (ida, idd, x, y, t, cr, sp, st) VALUES (%d, '%d', %s, %s, %s, %s, %s, %s);" % (idd, idd, jspack['lon'], jspack['lat'], int(tm), jspack['cr'], jspack['v'], jspack['s']),
			"INSERT INTO data_pos (ida, idd, x, y, t, cr, sp, st) VALUES (%d, '%d', %s, %s, %s, %s, %s, %s);" % (idd, idd, jspack['lon'], jspack['lat'], int(tm), jspack['cr'], jspack['v'], jspack['s']), ]
	#	print idd, jspack
		if DB_ID.qexecute('\n'.join (querys)):
			jquery += 1
	#	else:	print query, DB_ID.last_error
	except:
		print 'except:	send_sqlbd', jspack

def	to_sqlbd (jspack):
	global	DB_ID
	global	BLOCK_sqldb
	global	SQL_IDS

	if BLOCK_sqldb:	return
	if not DB_ID:
		DB_ID = dbtools.dbtools("host=212.193.103.20 dbname=receiver port=5432 user=smirnov")
	#	rows = DB_ID.get_rows("select device_id FROM recv_ts WHERE rem = 'ЖКХ' AND idd NOT LIKE 'NULL%'")
		rows = DB_ID.get_rows("select device_id FROM recv_ts WHERE inn > 0 AND idd LIKE 'idd%';")
		if not rows:
			print "ERROR to_sqlbd"
		for r in rows:
			SQL_IDS.append (int(r[0]))
		'''
		print 'SQL_IDS', SQL_IDS
		'''
		for i in IPS_IDS:
			if not i in SQL_IDS:	SQL_IDS.append(i)

	if not SQL_IDS:	BLOCK_sqldb = True 
	if SQL_IDS and jspack.has_key('id') and int(jspack['id']) in SQL_IDS:
		send_sqlbd (jspack)

UDP_IP = '127.0.0.1'
UDP_PORT = 50005

def	get_data():
	global	new_ports, ports_desc
	dtm = 0

	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)		# UDP
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)	# позволяет нескольким приложениям «слушать» сокет
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)	# указывает на то, что пакеты будут широковещательные
	sock.bind((UDP_IP, UDP_PORT))
	sock.setblocking(False)

	print "get_data", UDP_IP, UDP_PORT
	while True:
		try:
			data, addr = sock.recvfrom(65536) # buffer size is 1024 bytes
		#	jsp = json.loads(data.replace("'", '"'))
			jsp = json.loads(data)
	#		if SQL_IDS and jsp.has_key('id') and int(jsp['id']) in SQL_IDS:
			to_sqlbd(jsp)
	#		if jsp.has_key('id') and int(jsp['id']) in IPS_IDS:
	#			to_ips (jsp)
	#		else:	to_sqlbd(jsp)	#print 'jsp', len(jsp), jsp
			dtm = time.time()
		except ValueError:
			exc_type, exc_value = sys.exc_info()[:2]
			print 'get_data', exc_type, exc_value
			print '\t', data
		#	return
		except socket.error:
			time.sleep(.00001)
			if dtm == 0:
				pass
			elif time.time()-dtm > 360:
				sock.close()
				return
		#	time.sleep(.00001)

if __name__ == "__main__":
	try:
		thread.start_new_thread (get_data, ())
		while True:
			time.sleep(33)
			print 'WW'*5, 'jquery:', jquery,
			jquery = 0
			for j in range(len(IPS_SEND)):
				if IPS_SEND[j]:		print IPS_IDS[j],
			print '#'
	except  KeyboardInterrupt:
		print "\n\tStop", sys.argv[0]
		
	except:
		exc_type, exc_value = sys.exc_info()[:2]
		print '"__main__"',exc_type, exc_value
