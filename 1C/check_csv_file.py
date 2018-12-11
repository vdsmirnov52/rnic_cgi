#!/usr/bin/python
# -*- coding: utf-8 -*-
"""	@brief Утилита 
	Сделать дамр БД worktime в файле <wbak_name>.
	Проверить наличие нового CSV файла от 1С /mnt/rnic/1C/WIN_YYYYmmdd.csv
	Если файл найден - запустить утилиту ch_worktime.py 
"""

import	os, sys, time
import	shutil, filecmp

win_dir = r'/mnt/rnic/1C'
loc_dir = r'/home/smirnov/MyTests/CGI/1C'
def	main():
	if not os.path.isdir (win_dir):
		print "Отсутствует доступ к '%s'." % win_dir
		return
	names = os.listdir(win_dir)	# +"/WIN*")
	last_mtime = 0
	last_fname = ''
	sss = time.strftime ("WIN_%Y", time.localtime(sttmr))
	for name in names:
		if sss != name[:8] or  name[-4:] not in [".csv", ".CSV"]:	continue
	#	print name[:8], name[-4:]
		fullname = os.path.join(win_dir, name)
		if os.path.getmtime(fullname) > last_mtime:
			last_mtime = os.path.getmtime(fullname)
			last_fname = name
		print fullname,  time.strftime("\t%Y-%m-%d %T", time.localtime(os.path.getmtime(fullname)))	#, time.strftime("\t%Y-%m-%d %T", time.localtime(os.path.getatime(fullname)))
	if not last_mtime:
		print "Отсутствует файл '%s*.csv' в директории '%s'" % (sss, win_dir)
		return

	print "#"*8, last_fname, time.strftime("\t%Y-%m-%d %T", time.localtime(last_mtime))
	loc_file =  os.path.join(loc_dir, last_fname)
	if os.path.isfile(loc_file):
		if filecmp.cmp(loc_file, os.path.join(win_dir, last_fname)):
			print "Файл '%s' уже загружен > '%s'" % (last_fname, loc_file)
			return
		else:
			print os.path.join(loc_dir, 'BU/')
			shutil.move(loc_file, os.path.join(loc_dir, 'BU/'))
	shutil.copy (os.path.join(win_dir, last_fname), os.path.join(loc_dir, last_fname))
	cmd = "/home/smirnov/MyTests/CGI/1C/ch_worktime.py -f %s > /home/smirnov/MyTests/log/ch_worktime.F.log" % loc_file
	print cmd
	os.system(cmd)

if __name__ == "__main__":
	sttmr = time.time()
	print "Start:", sys.argv, time.strftime("%Y-%m-%d %T", time.localtime(sttmr))
#	wbak_name = "/home/smirnov/backup/worktime.%s.sql " % time.strftime("%Y%m%d", time.localtime(sttmr))	## ZZZZZZZZZZZZZZZZZZZZZ
#	os.system ("/usr/bin/pg_dump -U smirnov worktime > %s ; chown smirnov:smirnov %s " % (wbak_name, wbak_name))	#time.strftime("%Y%m%d", time.localtime(sttmr)))
	main()
