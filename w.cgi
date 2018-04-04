#!/usr/bin/python -u
# -*- coding: utf-8 -*-

import  cgi, os, sys
import  time
import  urllib
import  urlparse

LIBRARY_DIR = r"/home/smirnov/Wialon/lib/"	# Путь к рабочей директории (библиотеке)
CONF_PATHNAME = r"/home/smirnov/Wialon/sys.ini"
sys.path.insert(0, LIBRARY_DIR)
request = {}
import	main

def     get_theform ():
	""" Читать файл параметры формы cgi.FieldStorage	"""
	theform = cgi.FieldStorage ()
	request = {}
	for field in theform.keys():
		if theform.has_key(field):
			if  type(theform[field]) != type([]):
				request[field] = theform[field].value
			else:   request[field] = theform.getlist(field)
	return  request

def	get_config (pathname = CONF_PATHNAME):
	""" Читать файл конфигурации ConfigParser	"""
	if os.access (pathname, os.F_OK):
		import ConfigParser
		config = ConfigParser.ConfigParser()
		config.read (pathname)
		return config
	else:	print 'Отсутствует файл: ', pathname, '<br />'

def     check ():
	try:
		request = get_theform ()
	#	print '<pre>', request, '</pre>\n'
		CPYSESSID = ''
		if os.environ.has_key('HTTP_REFERER') and os.environ['REQUEST_METHOD'] == 'POST':
			referer = os.environ['HTTP_REFERER']
			if request.has_key('this'):
				print """Content-Type: text/html; charset=utf-8;\n\n"""
				print "~log|",	# request, '<br />'
				if request['this'] == 'ajax':
					import  ajax
					ajax.main(os.environ['SCRIPT_NAME'], request, referer)
				sys.exit()
				'''
			elif request.has_key('login') and request.has_key('passwd'):
				import	rusers
				dusr = rusers.check_user(request['login'], request['passwd'])
				if dusr:
					import	session
					SS = session.session("%s:%s" % (request['login'].strip(), os.environ['REMOTE_ADDR']))	#.replace('.', '')))
					SS.set_obj('USER', dusr)
					SS.set_obj('logged_in', int(time.time()))
					SS.stop()
					CPYSESSID = "Set-Cookie: CPYSESSID=" +SS.ssident
					request['disp'] = str(dusr)	#['user_id'])
					request['message'] = ""
				else:	request['message'] = "<span style='color: #a00'>Ошибка: <b>Отсутствуют Login или Password.</b></span>"
			elif os.environ.has_key('HTTP_COOKIE') and ('CPYSESSID' in os.environ['HTTP_COOKIE']):
				request['disp'] = '123'
				request['message'] = ""
				'''
			else:
				pass
		elif request.has_key('this') and request['this'] == 'new_widow':
			print """Content-Type: text/html; charset=utf-8\n\n<!DOCTYPE HTML>\n<html>"""
			conf = get_config(CONF_PATHNAME)
			main.new_widow  (request, conf)
			sys.exit()
	#	else:
		print """Content-Type: text/html; charset=utf-8\n%s\n\n<!DOCTYPE HTML>\n<html>""" % CPYSESSID
		conf = get_config(CONF_PATHNAME)
		main.main(request, conf)
	except SystemExit:	pass
	except:
		exc_type, exc_value = sys.exc_info()[:2]
		print "check:", exc_type, exc_value

if __name__ == "__main__":
#	print "Content-Type: text/html; charset=utf-8\n"
#	print '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">\n'
#	print '<html>ZZZ'
	try:
		check ()
		'''
		print "<pre>"
		for k in os.environ:	print k, "\t", os.environ[k]
		print "</pre>"
		'''
	except:
		exc_type, exc_value = sys.exc_info()[:2]
		print "EXCEPT w.cgi:", exc_type, exc_value

