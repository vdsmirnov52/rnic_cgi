#!/usr/bin/python
# -*- coding: utf-8 -*-

import  cgi, os
import  cgitb
import  cPickle as pickle

class   session:
	""" Вдение сессии CGI ( os.environ['HTTP_COOKIE'] => CPYSESSID ) и не только
	session_id	- Идентификатор сессии <starig>, по умолчанию:
		для CGI	'session:'+ os.environ['REMOTE_ADDR']
		иначе	'session_test'  
	as_new = True	- Принудительное открытие новой сессии, по умолчанию: False
	"""
	is_new = True
	objpkl = {}
	ssident = None	# Идентификатор сессии
	def __init__(self, session_id = None, as_new = False):
		if session_id:
			self.ssident = session_id
			self.is_new = as_new
		elif os.environ.has_key('REMOTE_ADDR'):
			self.ssident = 'session:'+ os.environ['REMOTE_ADDR']
		else:	self.ssident = 'session_test'

		if os.environ.has_key('HTTP_COOKIE'):
			cookie = os.environ['HTTP_COOKIE']
			for ss in cookie.split ('; '):
				s = ss.split ('=')
				if 'CPYSESSID' == s[0]:
					if self.ssident == s[1]:
						self.is_new = as_new	#False
					elif not session_id and not as_new:
						self.ssident = s[1]
						self.is_new = as_new
				#		print "Set-Cookie: CPYSESSID=" +self.ssident
				#		self.objpkl['CPYSESSID'] = None
				#	else:	self.is_new = 0
					break
		'''
		else:
			if os.environ.has_key('REMOTE_ADDR'):
				self.ssident = 'ip'+ os.environ['REMOTE_ADDR']
			else:	self.ssident = '_test_'
	#		print "Set-Cookie: CPYSESSID=" +self.ssident
		'''
		if self.ssident:
			self.filename = '/tmp/%s.pkl' % self.ssident
			if self.is_new or not os.path.isfile (self.filename):
				self.fid = open (self.filename, 'w+b')
				pickle.dump(self.objpkl, self.fid)
			else:
				self.fid = open (self.filename, 'r+b')
				self.is_new = False
				self.objpkl = pickle.load(self.fid)
		else:	print 'Отсутствует session_id'

	def start (self):
		""" Окрывает сессию
		возвращает <объект сессия> если она существует
		возвращает None если ее НЕТ
		"""
	#	print	self.filename
		if self.is_new:	return
		if self.fid:
			self.fid.seek(0)
			self.objpkl = pickle.load(self.fid)
			return  self.objpkl	#pickle.load(self.fid)

	def sset (self, object):
		""" Сохраняет <объект> как сессию целиком	"""
		if self.fid:
			self.fid.seek(0)
			return  pickle.dump(object, self.fid)

	def stop (self):
		""" Закрыавет файл сессии	"""
		if self.fid:	self.fid.close ()

	def	set_obj (self, key, object):
		""" Добавляет <объект> с именем <key> в текущую сессию и сохраняет ее	"""
		self.objpkl [key] = object
		if self.fid:
			self.fid.seek(0)
			pickle.dump(self.objpkl, self.fid)

	def	get_key (self, key):
		""" Извлекает <объект> с именем <key> из текущей сессии
		возвращает <объект> если он существует
		возвращает None если НЕТ
		"""
		if self.objpkl.has_key (key):	return self.objpkl[key]

	def	gets_key (self, key):
		""" Извлекает <объект> с именем <key> из текущей сессии
		возвращает <объект> если он существует
		возвращает ""	 если НЕТ
		"""
		if self.objpkl.has_key (key):	return self.objpkl[key]
		else:	return ""
	def	del_key (self, key):
		""" Удалить <объект> с именем <key> в текущей сессии и сохраняет ее	"""
		if self.objpkl.has_key (key):
			del(self.objpkl[key])
			self.fid.seek(0)
			pickle.dump(self.objpkl, self.fid)

'''
def getall(theform, nolist=False):
	data = {}
	for field in theform.keys():
		if type(theform[field]) ==  type([]):
			if not nolist:
				data[field] = theform.getlist(field)
			else:
				data[field] = theform.getfirst(field)
		else:
			 data[field] = theform[field].value
	return data
'''

if __name__ == '__main__':
	import	time
	print "TEST my_session"
#	help (session)
	ss = session ('my_session')	#(as_new = True)	#('my_session')
	
	ss.objpkl ['XXX']= 'YYY QQQ ZZZ'
	ss.set_obj ('TEST', time.strftime("%T", time.localtime (time.time ())))
	ss.set_obj ('TTT', {'time': time.strftime("%T %D", time.localtime (time.time ()))})
#	print "[%s] [%s]" % (ss.get_key('panele'), ss.get_key("time"))
	print ss.ssident, ss.objpkl
	ss.stop()
	print "##"*22
	SS = session ('my_session')
	SS.del_key ('TEST')
	print SS.ssident, SS.objpkl
	
