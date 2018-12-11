#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""	Утилита обмена данными с ISM модемом через сервер TCP2COM	"""

'''
HOST = '212.193.103.20'
PORT = 7778
'''
HOST = "109.95.210.203"	# Уаленный компьютер 
PORT = 2226		# порт на удаленном компьютере
fdebug = 1	# 1 - Режим отладки

import	socket
import	signal, os, sys, time
import	crc16

def	send_pack ():
	sid = '010000080000120001abcd010203040506070809000102dcba'	# 01 00 00 08 00 0012 0001 abcd 010203040506070809000102 dcba
	sc = ''
	crc16.crc_prepare()
	for j in range (0, len(sid), 2):
		x = int (sid[j:j+2], 16)
		sc += chr(x)
		crc16.crc_live(chr(x))
	return sc +chr(crc16.crc_h) +chr(crc16.crc_l)

def	view_pack (sc):
	for x in sc:
		print "%02x" % ord(x) ,
	print "=="

def	check_result(res):
	print 'check_result: "%s"' % res

def	connect (commands, chresult = 1):
	""" Обмен данными с демоном TCP2COM	"""
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((HOST, PORT))
	dr = {}
	try:
		for c in commands:
			ssend = c +'\r\n'
			jcc = ord(ssend[1])	## Send command Code
			jn = 1
			while jn:
				if fdebug:
				#	print "send %d\t>> %s" % (len (ssend), ssend)
				#	for j in range (0, len (ssend)):     print "%02x" % ord (ssend[j]) ,
					print "\t>>", ssend.strip()
				sock.send(ssend)
				while 1:
					time.sleep(1)
					result = sock.recv(1024)
					ln_res = len (result)
					print	'result', result, type(result), ln_res
					if len(result):	# < 4:
						if fdebug:
							for j in range (0, ln_res):	print "%02X" % ord (result[j]) ,
							print "\t<<< LEN:", ln_res
						break
					else:	break
				jn -= 1
				check_result (result)
				'''
				acc = ord(result[1])	## Answer command Code
				if result[0] != '<' or acc != (0x40 +jcc):
					if fdebug:
x
						for j in range (0, ln_res):	print "%02X" % ord (result[j]) ,
						print "\t<<< QQQ", jn
					if acc != 0x4d:	jn -= 1
					continue
				else:	break
			if chresult:
				ans = check_result (result)
			else:	ans = result

#			if fdebug:	print "ans: %d\t<< %02x %02x" % (jcc, ord(ans[1]), ord(ans[2]))
			dr [ord(c[1])] = ans
			break
				'''
		sock.send('')
		sock.close()
		return dr
	except socket.error:
		exc_type, exc_value = sys.exc_info()[:2]
		if fdebug:	print "socket.error:", exc_type, exc_value
		return 'except', exc_value

def	handler (signum, fname):
	if fdebug:	print 'handler', signum, fname
	sys.exit()

def	io_term (arg = None, chresult = 1):
	try:
		# Установить обработчик
		signal.signal(signal.SIGALRM, handler)
		signal.alarm(60)	# ожидать 30 сек

		if not arg:
			result = connect ((decomm['get_mac'], decomm['get_sn'], decomm['get_id']))
		else:	result = connect (arg, chresult)
		return result
	except:
		exc_type, exc_value = sys.exc_info()[:2]
		if fdebug:	print "EXCEPT io_term:", exc_type, exc_value
		return 'except', exc_value

if __name__ == '__main__':
	fdebug = 1
	tm_start = time.time()
	print "Start", sys.argv[0], tm_start
	
#	view_pack (send_pack())
#	print io_term ((send_pack(),))
	datas = ('#L#230056;NA',
		'#P#',
	#	'#D#181017;115636;5649.4458;N;04333.6342;E;0;0;130.000000;24;NA;0;0;NA,NA,NA,0.000000;NA;gps_full_mileage:2:4979.680000,gsm_st:1:3,nav_st:1:3,mw:1:0,sim_t:1:0,sim_in:1:1,st0:1:0,st1:1:0,st2:1:0,pwr_in:1:3,pwr_ext:2:13.350000,freq_1:1:0,info_messages:1:306',
	#	'#D#NA;NA;5650.1553;N;04333.7802;E;0;0;120.000000;23;NA;0;0;NA,NA,NA,0.000000;NA;gps_full_mileage:2:4977.990000,gsm_st:1:3,nav_st:1:3,mw:1:1,sim_t:1:0,sim_in:1:1,st0:1:0,st1:1:0,st2:1:0,pwr_in:1:3,pwr_ext:2:13.800000,freq_1:1:0,wln_brk_max:2:0.062000,info_messages:1:316',
		'#SD#181017;115636;5649.4458;N;04333.6342;E;10;20;300.0;11',
		'#SD#181017;115636;56.896598816;NA;43.654499054;NA;10;20;300.0;11',
		)
	print connect (datas)
#	print io_term (('#P#\r\n','#L#1234567890;NA\r\n'))
	sys.exit()
