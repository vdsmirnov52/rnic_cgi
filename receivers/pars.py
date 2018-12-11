#!/usr/bin/python -u
# -*- coding: utf-8 -*-

xxx = [ '123456',
	'<item1 xmlns="" type="ru.infor.ws.objects.vms.entities.NDData">',
	'<alarm>0</alarm><createdDateTime>2017-10-29T09:39:50.000Z</createdDateTime>',
	'<deviceId>6390881898</deviceId><gpsSatCount>20</gpsSatCount>',
	'<gsmSignalLevel xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true" />',
	'<id xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true" />',
	'<lastStopStartedAt xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true" />',
	'<lat>56.399436950683594</lat><lon>43.66482925415039</lon><speed>65.0</speed>',
	'<ae0 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true" /><ae1 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true" />',
	'<ae2 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true" /><ae3 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true" />',
	'<ae4 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true" /><ae5 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true" />',
	'<ae6 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true" /><ae7 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true" />',
	'<ae8 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true" /><ae9>0.0</ae9>',
	'<alarmDevice>0</alarmDevice>',
	'<de0>0</de0><de1>0</de1><de2>0</de2><de3>0</de3><de4>0</de4><de5>0</de5><de6>0</de6><de7>0</de7>',
	'<de8 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true" /><de9>174870162</de9>',
	'<direction>298.0</direction>',
	'<powerSupply_id xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true" />',
	'<powerValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true" />',
	'<tripIndex>0</tripIndex>',
	'<type type="ru.infor.ws.objects.vms.entities.RecordType"><code>01</code>',
	'<description>.... ..............</description>',
	'<id>16922</id><isDeleted>0</isDeleted>',
	'<uniqueKey xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true" /></type>',
	'</item1>',
	'<item1 xmlns="" type="ru.infor.ws.objects.vms.entities.NDData">',
	'<alarmns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true" />',
	'<ae2 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true" />',
	'<ae3 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true" /><ae4 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true" />',
	'<ae5 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true" /><ae6 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true" />',
	'<ae7 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true" /><ae8 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true" /><ae9>0.0</ae9>',
	'<alarmDevice>0</alarmDevice>',
	'<de0>0</de0><de1>0</de1><de2>0</de2><de3>0</de3><de4>0</de4><de5>0</de5><de6>0</de6><de7>0</de7>',
	'<de8 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true" /><de9>174873162</de9>',
	'<direction>298.0</direction>',
	'<powerSupply_id xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true" />',
	'<powerValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true" />',
	'<tripIndex>0</tripIndex>',
	'<type type="ru.infor.ws.objects.vms.entities.RecordType"><code>01</code>',
	'<description>.... ..............</description><id>16922</id><isDeleted>0</isDeleted><uniqueKey xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true" /></type>',
	'</item1>',
	'<item1 xmlns="" type="ru.infor.ws.objects.vms.entities.NDData">',
	'<alarm>0</alarm>',
	'<createdDateTime>2017-10-29T09:39:44.000Z</createdDateTime>',
	'<deviceId>6390881898</deviceId>',
	'<gpsSatCount>19</gpsSatCount>',
	'<gsmSignalLevel xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true" />',
	'<id xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true" />',
	'<lastStopStartedAt xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true" />',
	'<lat>56.39897537231445</lat><lon>43.666358947753906</lon><speed>64.0</speed>',
	'<ae0 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true" /><ae1 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true" />',
	'<ae2 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true" /><ae3 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true" />',
	'<ae4 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true" /><ae5 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true" />',
	'<ae6 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true" /><ae7 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true" />',
	'<ae8 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true" /><ae9>0.0</ae9>',
	'<alarmDevice>0</alarmDevice>',
	'<de0>0</de0><de1>0</de1><de2>0</de2><de3>0</de3><de4>0</de4><de5>0</de5><de6>0</de6><de7>0</de7>',
	'<de8 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true" /><de9>174876162</de9>',
	'<direction>298.0</direction>',
	'<powerSupply_id xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true" />',
	'<powerValue xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true" />',
	'<tripIndex>0</tripIndex>',
	'<type type="ru.infor.ws.objects.vms.entities.RecordType"><code>01</code>',
	'<description>.... ..............</description><id>16922</id><isDeleted>0</isDeleted><uniqueKey xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true" /></type>',
	'</item1>',
	]
import	json

def	pars (sdata):
	j = jc = jk = 0
	rlist = []
	while True:
		j = sdata[jc:].find('<item1')
		if j >= 0:
			jc += j
			jk = sdata[jc+7:].find('item1>')
			if jk > 0:
				rrr = p_item (sdata[jc:jc+jk])
				if not rrr:
					pass
			#		print jc, jk, "\t", sdata[jc:jc+jk+13]
				else:
			#		print jc, jk, "\t", rrr
					rlist.append(rrr)
				jc += jk+13
			
			else:	jc += 100
		else:	break
	return	rlist

def	p_item (sdata):
	tags = ['alarm', 'createdDateTime', 'deviceId', 'gpsSatCount', 'lat', 'lon', 'speed', 'direction']
	tdict = {'alarm': 'al', 'createdDateTime': 'dt', 'deviceId': 'id', 'gpsSatCount': 's', 'lat': 'lat', 'lon': 'lon', 'speed': 'v', 'direction': 'cr'}

	j = 0
	jv = 1
	res = {}
#	res = []
	for tag in tags:
		ln_tag = len(tag)
		j += sdata[j:].find(tag)
		if j > 0:
			jv = j+ln_tag +1
			je = sdata[jv:].find(tag)
			if je < 0:
			#	if not sdata[jv].isdigit():	continue
				if sdata[jv] and not sdata[jv].isdigit():	continue	# 03.04.2018
				if len(res) > 5:		break
				print "EEE >\t", je, jv, res, len(res)
				return
			val = sdata[jv:jv+je-2]
			if tag in ['lat', 'lon',]:
				res[tdict[tag]] = val[:10]
			else:	res[tdict[tag]] = val
#			res.append('"%s":"%s"' % (tdict[tag], val))
			j = jv+ln_tag
		else:	return
	return	res
#	return "{%s}" % ', '.join (res)

if __name__ == "__main__":
	'''
	obj = [u'foo', {u'bar': [u'baz', None, 1.0, 2]}]
        print json.loads('["foo", {"bar":["baz", null, 1.0, 2]}]') == obj
	help (json)
	'''
	print json.loads('{"al":"0", "dt":"2017-10-29T09:39:50.000Z", "id":"6390881898", "s":"20", "lat":"56.399436950683594", "lon":"43.66482925415039", "v":"65.0", "cr":"298.0"}')
	print json.loads("{'lon': '43.9224700', 'al': '0', 's': '14', 'v': '7.0', 'lat': '56.2803802', 'cr': '208.0', 'dt': '2017-11-17T09:37:36.000Z', 'id': '6476626262'}")
#	print ''.join(xxx)
	for s in pars (''.join(xxx)):
		print "<%s>" % s
		'''
		try:
			print json.loads(s)
			print dict(json.loads(s))
		except ValueError:
			print "ZZZZ"
		'''
	print '#'*22
