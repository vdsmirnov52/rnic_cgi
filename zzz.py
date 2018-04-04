import sys
import time

def timer():
	while True:
		line = sys.stdin.readline()
		if not line:
			break
		if line.rstrip() != "time":
			result = "error"
		else:
			result = str(time.time())
		sys.stdout.write("%s\n" % result)
		sys.stdout.flush()

if __name__ == "__main__":
#	timer()
	last_date = "2016-12-15 11:22:33"
	ttms = time.mktime(time.strptime(last_date[:16], "%Y-%m-%d %H:%M"))
	print	last_date, ttms
	print	time.strftime("%H:%M %d.%m.%y", time.localtime(ttms))
