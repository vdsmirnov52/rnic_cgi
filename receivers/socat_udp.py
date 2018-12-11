#!/usr/bin/python -u
# -*- coding: utf-8 -*-
'''
root@VSVR-TELEMATIC:~# ./socat_8080.sh
root@VSVR-TELEMATIC:~# cat socat_8080.sh
#!/bin/sh
        tcpflow -i eth0 -c dst port 8080 >> /tmp/ddd_fiflo &
        sleep  1
        socat -u open:/tmp/ddd_fiflo udp4-send:212.193.103.20:10045 &
        echo "ZZZ"

https://stackoverflow.com/questions/17449110/fifo-reading-in-a-loop
https://habrahabr.ru/post/132554/

010.040.025.172.55258-010.040.025.173.08080: #
'''

import	os, sys, time
sys.setrecursionlimit(2000)

import	thread, Queue, signal
import	socket

FIFO =	'/tmp/VSVR-TELEMATIC.get'
UDP_IP = "127.0.0.1"
UDP_PORT = 50005
quu_udp = Queue.Queue()

def	send_by_udp():
	""" Опправка данных по UDP	"""
	global	quu_udp

	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)		# UDP
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)	# позволяет нескольким приложениям «слушать» сокет
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)	# указывает на то, что пакеты будут широковещательные
	sock.bind((UDP_IP, UDP_PORT))
	sock.setblocking(False)

	print "send_by_udp"
	while True:
		if quu_udp.qsize() > 0:
			data = str(quu_udp.get()).replace("'", '"')
	#		print ">>>\t", data
			sock.sendto(data, (UDP_IP, UDP_PORT))
		else:	time.sleep(1)
'''
ports_desc =	{}
mutex_ports_desc = thread.allocate_lock()

new_ports =	[]
mutex_new_ports = thread.allocate_lock()
'''
stime = lambda: time.strftime("%Y-%m-%d %T\t", time.localtime(time.time()))
json_packs =	[]	# Список списков строк (json пакетов) для отправки по UDP
mutex_json_packs = thread.allocate_lock()

def	clear_ports_desc (sport):
	global	ports_desc

	if ports_desc.has_key(sport):
		mutex_ports_desc.acquire()
		del ports_desc[sport]
		mutex_ports_desc.release()

import	pars

def	get_POST (fid, pmark, tail, ins = None):
#	if ins:	print ins, "# POST ", pmark
#	print "\tget_POST", pmark, tail
	sh = ''
	ln_sum = 0
	get_mark = None
	dbox = []
	if 'NDDataWS' in tail:
		is_dbox = True
#		print stime(), "NDDataWS\t", pmark, tail.strip()
	else:
		is_dbox = False
#		print stime(), "# Others\t", pmark, tail.strip()
	try:
		while 'Content-Length' not in sh:
			sh = fid.readline()
			if '010.040.025.172.' == sh[:16] and sh[45:49] == 'POST':
	#			print stime(), '# in Head\t', pmark, tail.strip()
				get_POST (fid, sh[:45], sh[45:], '### ' +pmark)
		#		print time.strftime("%Y-%m-%d %T\t", time.localtime(time.time())), pmark, tail.strip()
		#		print '#YYYYYYYYY\t ', pmark, tail.strip()
				return

		ln_dbox = int(sh[15:])
		while ln_sum < ln_dbox:
			sd = fid.readline()
		#	ssd = sd.strip()
			if '010.040.025.172.' == sd[:16]:
				if pmark == sd[:45]:
					get_mark = None
					ln_sum += len(sd[45:-1])
					if is_dbox:	dbox.append (sd[45:-1])
				elif sd[45:49] == 'POST':
					get_mark = None
					get_POST (fid, sd[:45], sd[45:], pmark)
				elif sd[45:48] == 'GET':
					get_mark = sd[:45]
				if get_mark:	continue
			elif get_mark:		continue
			else:
				ln_sum += len(sd[:-1])
				if is_dbox:	dbox.append (sd[45:-1])
			if ':Envelope>' in sd[-12:]:	break
	#	print "\tget_POST", pmark, ln_dbox, ln_sum
		return	ln_dbox
#	else:
	except:
		print stime(), '#except\t', pmark, tail.strip()
		exc_type, exc_value = sys.exc_info()[:2]
		print "\t", exc_type, exc_value
		'''
		while ':Envelope>' not in sh[-12:]:
			sh = fid.readline()
			if '010.040.025.172.' == sh[:16]  and sh[45:49] == 'POST':
				get_POST (fid, sh[:45], sh[45:], '#TT ' +pmark)
				print '############\n', fid.readline()
				return
		#	print "#\t", sh[:111].strip(), sh[-22:].strip()
		'''
	finally:
		if dbox:
			if ln_dbox > 2200:
		#		print "#\tget_POST", pmark, tail.strip(), ln_dbox, ln_sum
				sdata = ''.join(dbox)
		#		print '\tfinally dbox', len(dbox), len(sdata), '# "%s"' % sdata[:113]
				jpack = pars.pars (sdata)
				if jpack:	
                			mutex_json_packs.acquire()
					json_packs.append(jpack)
        			        mutex_json_packs.release()
			#	for s in jpack:		print '\t', s
	
def	read_fifo():
	global	ports_desc

	ln_dbox = 0
	sport = '99999'
	pmark = smark = 'X'*45
	get_mark = None
	f = open(FIFO, 'r')
#	f = open('./oooooo.socat.log', 'r')
#	f = open('./ooo2.socat.log', 'r')
	j = 0
	ssd = 'Start'
	while True:
		time.sleep(.00001)
	#	with open(FIFO, 'r') as f:
		sd = f.readline()
		if sd:
		#	ssd = sd[:-1]
			ssd = sd.strip()
			if '010.040.025.172.' == ssd[:16]:
				smark = ssd[:45]
				if ssd[45:49] == 'POST':
					ln_dbox = get_POST (f, smark, ssd[45:])
					pmark = ssd[45:]
					get_mark = None
					if ln_dbox:	j += 1
				elif ssd[45:48] == 'GET':
					get_mark = ssd[:45]
				elif get_mark:	continue
				else:		print ssd[:99], "######"
			elif get_mark:	continue
			else:
				if ssd:		print 'QQQ', stime(), ln_dbox, ssd
		else:
			print 'read_fifo', stime(),  ssd
			time.sleep(1)
		#	break

DList2WIPS =	['6476641896', '6476626262', '6476546985', 'Е417ОМ152', '6476433867', '183371206', '183365066', '183371220', '183371215', '183366474']	# Wialon IPS	Экологи
def	jspfilter ():
	active_test = ['5358058752', '4782262841', '5421197527', '183367151', '5816844269', '6271149422', '6390881898', '6491584623', '40399981', '40399974', '80532577']
	if not json_packs:
		time.sleep(1)
	else:
		while json_packs:
			mutex_json_packs.acquire()
			jpack = json_packs.pop(0)
			mutex_json_packs.release()
			for s in jpack:
				try:
					quu_udp.put(s)	# отправит весь поток данных
	#				continue
	#				if s['id'] in active_test:	quu_udp.put(s)
	#				if s['id'] in DList2WIPS:	quu_udp.put(s)
				except KeyError:	pass
	
if __name__ == "__main__":
	thread.start_new_thread (send_by_udp, ())
	scmnd = 'killall socat; socat -u udp4-listen:10045 stdout > %s &' % FIFO	#'/tmp/VSVR-TELEMATIC.get'
	res = os.system (scmnd)
	'''
	read_fifo()
	'''
	print stime(), '#'*11, scmnd, res
	thread.start_new_thread (read_fifo, ())
	while True:
		time.sleep(1)
	#	print "WWW"*7, len(json_packs), quu_udp.qsize()
		thread.start_new_thread (jspfilter, ())
		'''
		for jsp in ports_desc.keys():
			jqu = ports_desc[jsp]
			jqln = jqu.qsize()
			if jqln == 0:
				clear_ports_desc(jsp)
				continue
			else:	#if jqln < 3:
				for j in range(jqln):
					print jsp, jqln, jqu.get()
			break
		if not ports_desc:	break
		'''

