# -*- coding: utf-8 -*-

import	cgi, os, sys, time, string

LIBRARY_DIR = r"/home/smirnov/MyTests/CGI/lib/"
sys.path.insert(0, LIBRARY_DIR)
CONFIG = None

import	cglob
import	session

CDB_DESC = cglob.get_CDB_DESC('ZZZ')

def	authorize (message = '&nbsp;'):
#	global	CONFIG
	print """<div class='box' style='background-color: #ff8; text-align: center; padding: 30px; margin: 30px;'><big><b>%s</b></big><hr width=50%% />
		Версия: %s &nbsp; %s </div>""" % (CONFIG.get('System', 'name'), CONFIG.get('System', 'version'), CONFIG.get('System', 'copy'))
#	print """<div style='color: #a00; font-size: 22px; text-align: center;'><b>Вам необходимо зарегистрироваться!</b></div>"""
	print """<form name='mainForm' action='/cgi/index.cgi' method='post'><center>
	<div class='form' style='padding: 18px; margin: 4px; border: solid; border-width: 1px; width: 300px;'> <table>
		<tr><td align=right>Login:</td>		<td><input name='login' type='text' maxlength=15 id='us_login' value='' /></td></tr>
		<tr><td align=right>Password:</td>	<td><input name='passwd' type='password' maxlength=15 id='us_passwd' value='' /></td></tr></table>
		<input type='submit' id='id_check_user' value='Регистрация' />
		<div id='rez_authorize'>%s</div>
		</div></center>""" % message
	#	</div></center></form>""" % message
	#	<tr><td align=right>Код:</td><td><input name='disp' type='text' maxlength=5 onchange="check_user('disp_code');" id='us_disp' size=5 /></td></tr>
	#	<input type='submit' id='id_check_user' onclick="check_user('reg_user');" value='Регистрация' />
	#	<input type='button' id='id_close' onclick="window.close();" value='Отменить' />

def	jscripts (ssrc):
	for c in ssrc:
		print "\t<script type='text/javascript' src='%s'></script>" % c

def	rel_css (ssrc):
	for c in ssrc:
		print "\t<link rel='stylesheet' type='text/css' href='%s' />" % c

jslocal =  """<script type='text/javascript'>
	$(document).ready(function () {
	$.ajaxSetup({ url: "index.cgi?this=ajax", type: "post", error: onAjaxError, success: onAjaxSuccess, timeout: 30000 });
	$('#dbody').css({'height': (-100 + document.documentElement.clientHeight) +'px',  'overflow': 'auto'});
	$('#div_table').css({'height': (-200 + document.documentElement.clientHeight) +'px',  'overflow': 'auto'});
//	if (document.myForm.fform && document.myForm.fform.value == 'new_widow')	set_shadow('view_contr&id_contr=00086');
	})
	function	set_shadow (shstat) {	$.ajax({data: 'shstat='+ shstat +'&' +$('form').serialize()});	}
	function	add_row(tabname) {	$.ajax({data: 'shstat=add_row&table='+ tabname +'&' +$('form').serialize()});}
	function	set_message(txt) {	$('#message').html(txt);
//	alert('CSS offsetHeight:' +document.documentElement.offsetHeight +" clientHeight:"+ document.documentElement.clientHeight +" scrollHeight:"+ document.documentElement.scrollHeight);
//	$('thead').css({ 'width': '100%', 'position': 'fixed', 'height': '109px', 'top': '10' });
	}
//	window.parent
//	window.opener
//	about:CONFIG там есть группа настроек dom.disable_window_open там где стоит true - фича работать не будет.
	function	win_open(wname, options) {
		var width = 910;
		var height = 540;
		var left = (screen.width - width)/2;
		_win_open(wname, options, 'width=910, height=540, left=' +left+ ', top=300');
	}
	function	_win_open(wname, options, win_params) {
		var params = 'location=no, scrollbars=yes, ' +win_params;	//width=' +width+ ', height=' +height+ ', left=' +left+ ', top=300';
	//	alert ('index.cgi?this=new_widow&wname=' +wname +options);
		window.open ('index.cgi?this=new_widow&wname=' +wname +options, wname, params).focus(); return false;
	}
	function	check_user(reg_user) {
	$.ajax({data: 'stat='+ reg_user +'&' +$('form').serialize()});
	alert (reg_user);
	}
	function	out_bm_cstat (id_contr) {
	//	alert ('out_bm_cstat&id_contr=' +id_contr +'&WW=' +screen.width +'&WH=' +screen.height)
		set_shadow ('out_bm_cstat&id_contr=' +id_contr +'&WW=' +screen.width +'&WH=' +screen.height)
	}
	function	out_person (id_contr, id_org, id_persn) {
	//	alert ('&WW=' +screen.width +'&WH=' +screen.height)
		set_shadow ('out_person&id_contr=' +id_contr +'&id_org=' +id_org +'&id_persn=' +id_persn +'&WW=' +screen.width +'&WH=' +screen.height);
	}
	function	win_curr_status_TC() {
		var params = 'location=no, scrollbars=yes, width=1000, left=100, top=100, height=500';
		window.open('/curr_status_TC.html', 'health_status_TC', params).focus(); return false;
	}
	function	win_helps(file_name) {
		var params = 'location=no, scrollbars=yes, width=800, left=200, top=200, height=500';
		window.open('/helps/' +file_name, 'helps', params).focus(); return false;
	}
	function	set_order(corder) {
	//	alert(corder);
		document.myForm.orderby.value = corder;
		document.myForm.submit();
	}	
	</script>"""

def	get_usconf (dboo, request):
	disp = int (request['disp'].strip())
	query = "SELECT u.*, u.type AS utype, t.name AS tname, p.name AS fio FROM usr03 u, sp_person p, sp_usrtype t WHERE (u.cod = p.cod) AND (u.type = t.cod) AND u.disp=%d;" % disp
	row = dboo.get_dict (query)
	if row:
		if row['ip_loc'].strip() == '*' and row['passwd'] == request['passwd'] and row['login'] == request['login']:
			return	row, ''
	return	None, "Пользователь отсутствует!"

def	out_head (SS, USER, title = None):
	import	rusers
	code_ssys = -1
	print "<div class='box' style='background-color: #dde;'><table width=100%><tr><td width=35%>"
	if title:	print "<span class='tit'>", title, "</span>"
	usrole = SS.get_key('role')
	role_name = 'None' if (not usrole) else usrole['rname']
	print "</td><td>Пользователь: <span class='bfgrey' title='%s'>%s %s</span>" % (role_name, USER['uname'], USER['ufam']), "</td><td>"
	
	print "Подсистема: <span class='bfgrey'>"
	ssystem = SS.get_key('subsystem')
	if not ssystem:		#SS.objpkl.has_key('subsystem'):
		res = rusers.get_ssystems(USER)
		if res and len (res[1]) == 1:
			sss = {}
			for k in res[0]:	sss[k] = res[1][0][res[0].index(k)]
			SS.set_obj('subsystem', sss)
			print SS.objpkl['subsystem']['ssname']
		elif  len (res[1]) >1:
			cglob.out_select('sssystem', res, ['code', 'ssname'], sopt = """onchange="set_shadow('sssystem');" """)
		else:	print res
	else:
		print	ssystem['ssname']
		code_ssys = ssystem['code']
	print "</span>"

	if not usrole:		# SS.objpkl.has_key('role'):
		print "</td><td>Роль: <b>"
		res = rusers.get_roles(USER, code_ssys)
		if res and len (res[1]) == 1:
			rrr = {}
			for k in res[0]:	rrr[k] = res[1][0][res[0].index(k)]
			SS.set_obj('role', rrr)
			print SS.objpkl['role']['rname']
		elif  len (res[1]) > 1:
			if not SS.objpkl.has_key('subsystem'):
				ssopt = """onchange="set_shadow('setrole');" disabled """
			else:	ssopt = """onchange="set_shadow('setrole');" """
			cglob.out_select('setrole', res, ['code', 'rname'], sopt = ssopt)	#"""onchange="set_shadow('setrole');" """)
		else:	print res
		print "</b></td>"
	
	print	"<td align=right>"
	print	"""<input id='sss' type='button' class='butt' value='TC' onclick="win_curr_status_TC();" title='Справка по состоянию ТС' />"""
	print	"""<input id='is_alarms' type='button' class='butt' value='Alarm' onclick="set_shadow('view_alarms');" />"""
	if SS.objpkl.has_key('win_view'):
		print	"""<input name='win_view' type='button' class='butt' value='DIV' onclick="set_shadow('sset_win_view');" />"""
	else:	print	"""<input name='win_view' type='button' class='butt' value='WIN' onclick="set_shadow('sset_win_view');" />"""
	print	"""<input type='button' class='butt' value=' Отменить ' onclick="set_shadow('clear');" />
		<input type='button' class='butt' value=' Выйти ' onclick="set_shadow('exit');" /></td>"""
	print	"""<td align=right><img onclick="document.myForm.submit();" title="Обновить" src="../img/reload3.png"></td>"""
	print	"</tr></table></div>"
	func_allowed = rusers.get_func_allowed(SS.get_key('USER'), SS.get_key('role'))
	if func_allowed:	SS.set_obj('func_allowed', func_allowed)

def	perror (tit = None, txt = None):
	if not tit:	tit = ''
	print	"<div class='error'><b>%s</b> %s</div>" % (str(tit), str(txt))

def	new_widow (request, conf):
	global	CONFIG
	CONFIG = conf
	try:
		print "<head> <meta name='Author' content='V.Smirnov'> <title>%s</title>" % CONFIG.get('titWindows', request['wname'])
		rel_css ((r'/css/style.css', r'/css/calendar.css', r'/css/new_widow.css'))
		jscripts ((r'/jq/jquery.onajax_answer.js', r'/jq/jquery.js', r'/js/calendar.js', r'/js/check_forms.js'))
		print jslocal, "</head>"
		if request['wname'] == 'listalarms':
			bgc = '#fa6'
		elif request['wname'] == 'blank_arm':
			bgc = '#fff'
		else:	bgc = '#440'
		print """<body id='id_body' style='background-color: %s; padding: 0px;'>
			<form name='myForm' action='/cgi/index.cgi' method='post'><fieldset class='hidd'>
			<input name='orderby' type='hidden' value='' />
			<input name='valid' type='hidden' value='' />
			<input name='fform' type='hidden' value='new_widow' />""" % bgc
		import	conract
		import	dbtools
		idb = dbtools.dbtools (CDB_DESC)	#CONFIG.get('dbNames', 'contracts'))
		SS = session.session()
		if request['wname'] == 'new_contr':
			stat = 'new'
			print """<input name='stable' type='hidden' value='vcontracts' /> <input name='npkey' type='hidden' value='id_contr' /></fieldset>"""
			row = idb.get_row("SELECT * FROM vcontracts WHERE id_contr = 0;")
			cdict = idb.desc	#conract.DICT_TABS['vcontracts']
			if request.has_key('id_org') and request['id_org'].isdigit():
				conract.out_vcontracts(SS, idb, row, cdict, stat, int(request['id_org']))
			else:	conract.out_vcontracts(SS, idb, row, cdict, stat)
		elif request['wname'] == 'new_org':
			stat = 'new'
			print """<input name='stable' type='hidden' value='vorganizations' /> <input name='npkey' type='hidden' value='id_org' /></fieldset>"""
			row = idb.get_row("SELECT * FROM vorganizations WHERE id_org = 0;")
			cdict = idb.desc
			conract.out_vorganizations(SS, idb, row, cdict, stat)
		elif request['wname'] == 'transport':
			cglob.ppobj (request)
		elif request['wname'] == 'blank_arm':
			print   "</fieldset>"
			import	arms
			arms.blank(SS, idb, request)
		elif request['wname'] == 'listalarms':
			print	"</fieldset>"
			import	alarms
			alarms.alist(SS, idb, request)
		elif request['wname'] == 'view' and request.has_key('table'):
			print	"<div id='widget'>"	# class='wform' style='background-color: #989;'>"
			conract.out_tform (SS, request['table'], request['pkname'], request['idrow'])
			print	"</div>"
		else:	#	pass
			print "<div class='wform'>"
			cglob.ppobj (request)
			cglob.ppobj (SS.objpkl)
			print	"</div><!-- wform	-->"
	#	print	request, CONFIG	, CONFIG.get('dbNames', 'contracts')
	#	print "<table><tr><td><div", "></div></td><td><div ".join(["id='shadow'","id='shadow2'", "id='widget'", "id='error'", "id='warnn'"]), "></div></td></tr></table>"
		print "<table><tr><td><div", "></div></td><td><div ".join(["id='shadow'","id='shadow2'", "id='error'", "id='warnn'"]), "></div></td></tr></table>"
		if request['wname'] == 'new_contr' and request.has_key('id_org') and request['id_org'].isdigit():
			print "id_org:", request['id_org']
	except:
		exc_type, exc_value = sys.exc_info()[:2]
		perror ("EXCEPT new_widow", " ".join(["<pre>", str(exc_type).replace('<', '# '), str(exc_value), "</pre>"]))
		print "<span style='background-color: #ffa; color: #a00; padding: 4px;'> EXCEPT new_widow:", exc_type, exc_value, "</span>"
	finally:
	#	print	"""</fieldset>"""
		print "</form></body></html>"

def	main (request, conf):
	global	CONFIG
	CONFIG = conf
#	print """<html xmlns="http://www.w3.org/1999/xhtml">"""
	try:
		print "<head> <meta name='Author' content='V.Smirnov'> <title>%s</title>" % CONFIG.get('System', 'title')
		rel_css ((r'/css/style.css', r'/css/calendar.css'))
		jscripts ((r'/jq/jquery.onajax_answer.js', r'/jq/jquery.js', r'/js/calendar.js', r'/js/check_forms.js'))
		print jslocal, "</head>"
		print """<body>"""
		SS = session.session()
#		cglob.ppobj(SS.objpkl)
		USER = SS.get_key('USER')
		if USER and USER['user_id']:
			print	"""<form name='myForm' action='/cgi/index.cgi' method='post'><fieldset class='hidd'>
			<input name='orderby' type='hidden' value='' />
			<input name='stat' type='hidden' value='' />
			</fieldset>"""
			out_head (SS, USER, CONFIG.get('System', 'name'))
			print	"<div id='dbody' class='hidd'>"
		#	print	"### DEBUG CDB_DESC:", CDB_DESC
		#	cglob.ppobj(request)
			subsystem = SS.get_key('subsystem')
			ROLE = SS.get_key('role')
			if not subsystem:
				cglob.wdgwarnn("Внимание", "<center><br /><span class='tit'>Нужно выбрать рабочую подсистему.</span><br /></center>", obj=SS.objpkl)
			elif not ROLE:
				cglob.wdgwarnn("Внимание", "<center><br /><span class='tit'>Нужно выбрать роль пользователя в подстсиеме.</span><br /></center>", obj=SS.objpkl)
			else:
				if subsystem['label'] == 'RUSERS':	# Ведение пользователей РНИЦ
					import	rusers
					rusers.out_users(SS, USER)
				elif subsystem['label'] == 'WORK_TS':	# Работа ТС
				#	print "<h2>Работа ТС</h2>"
					import tranport
					tranport.main(SS, conf, request)
				elif subsystem['label'] == 'CONTRCT':
					import	conract
					conract.main(SS, request)
				else:	cglob.wdgwarnn("out_users", obj=SS.objpkl)
		#	else:	cglob.ppobj(SS.objpkl)
			print	"</div><!-- dbody	-->"
		else:
			if request.has_key('message'):
				authorize (request['message'])
			else:	authorize ()
	#	print 'main', request, CONFIG.get('System', 'version'), CONFIG.get('System', 'copy')
		if request.has_key('message'):
			print "<div id='message' style='text-align:center;'>%s</div>" % request['message']
		else:	print "<div id='message' style='text-align:center;'>message</div>"
		print """<script language="JavaScript">setTimeout ("set_message ('')", 10000);</script>"""
		print """<table><tr><td><div id='shadow'>shadow</div></td><td><div id='shadow2'>shadow2</div></td><td>
		<div id='widget'>widget</div></td><td><div id='error'>error</div></td><td><div id='warnn'>warnn</div></td></tr></table>"""
		print os.environ['REMOTE_ADDR']
		ggg = globals()
		if ggg.has_key('LIBRARY_DIR'):
			print	ggg['LIBRARY_DIR']
		else:	cglob.wdgwarnn('globals', ggg)
	except:
		exc_type, exc_value = sys.exc_info()[:2]
		perror ("EXCEPT main_page", " ".join(["<pre>", str(exc_type).replace('<', '# '), str(exc_value), "</pre>"]))
		print "<span style='background-color: #ffa; color: #a00; padding: 4px;'> EXCEPT main_page:", exc_type, exc_value, "</span>"
	finally:
		print "</form></body></html>"
