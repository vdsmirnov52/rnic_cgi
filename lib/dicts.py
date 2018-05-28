#!/usr/bin/python
# -*- coding: utf-8 -*-
#	Глобальный справочники

SFDATE = ['cdate', 'period_valid', 'date_close', 'actdate', 'acdate', 'year', 'pts_date', 'sreg_date']
SSDATE = ['period_valid', 'date_close']
RUSERS = {
	'rusers': {	'title': "Список пользователей",
		'order': ['login', 'uname', 'ufam', 'bm_ssys', 'bm_role'],	# Default == dbtools.desc результат запроса к <table name>
		'thead': {'login': 'Login', 'uname': 'Имя', 'ufam': 'Фамилия',#'bm_ssys': 'Подсистемы',
			'bm_role': 'Роли'},
		'key': 'user_id',		# Default == order[0]
		'functs': {'mark': "mark", 'ordbycol': "ordbycol"},
		},
	}
	
CONTRCT = {
	# CREATE VIEW varms AS SELECT a.*, o.bname AS oname, c.cnum, b.bid_num, o.region, o.rname FROM arms a LEFT JOIN vorganizations o ON a.id_org = o.id_org LEFT JOIN contracts c ON a.id_contr = c.id_contr LEFT JOIN bids b ON a.id_bid = b.id_bid ;	
	# alter table arms ADD column sn_bid character varying(32);
	# id_arm | id_org | id_bid | id_contr | login | passwd | family | pname | post | phones | emails | url | tm_creat | tm_send | who_send | ps | rem | dt_creat | oname | cnum | bid_num, o.region, o.rname
	'varms':	{	'title':        "Список АРМов", 'form_tit': "Описание контакта",
		'order': ['dt_creat', 'oname', 'sn_bid',
			'login', 'passwd',
			'family', 'pname', 'phones', #'emails',
			'post', #'tm_creat', 'tm_send',
			],
		'update': { 'login': 's:64', 'passwd': 's:64', 'sn_bid': 's:32',
			'family': 's:32', 'pname': 's:32', 'phones': 's:32', 'post': 's:32', #'sn_bid': 's:32',
		#	'rem': 't:256', 'ps': 't:256', 'url':'s:128', 'emails': 's:128',	# 'id_org': 'i', 'id_bid': 'i', 'id_contr': 'i'
			},
		'thead': {'family': "Фамилия", 'pname': "Имя Отчество", 'phones': "Телефон", 'email': "E-mail", 'post': "Должность", 'oname': "Организация", 'sn_bid': '№ Заявки',
			'login': 'Логин', 'passwd': 'Пароль',},
		'key':  'id_arm',
		'functs': {'mark': "mark", },
		},
	# INSERT INTO persons (id_persn) values (0);
	# id_persn | family | names| phones | email | post | rem | obname| region | rname
	'vpersons':	{	'title':	"Список контактов", 'form_tit': "Описание контакта",
		'order': ['family', 'names', 'phones', 'email', 'post', #'id_org',
		'obname', 'rname', 'rem'],
		'thead': {'family': "Фамилия", 'names': "Имя Отчество", 'phones': "Телефон", 'email': "E-mail", 'post': "Должность",
			'obname': "Наименование организации", 'rname': "Район", },
		'update': {'email': 's:64', 'post': 's:32', 'phones': 's:32', 'family': 's:32', 'names': 's:32', 'rem': 't:256'},
		'key':	'id_persn',
		'functs': {'mark': "mark", },
		'orderby': 'family, names',
		},
	'persons':	{	'title':	"Список контактов", 'form_tit': "Описание контакта",
		'order': ['family', 'names', 'phones', 'email', 'post', 'rem'],
		'thead': {'family': "Фамилия", 'names': "Имя Отчество", 'phones': "Телефон", 'email': "E-mail", 'post': "Должность", },
		'key':	'id_persn',
		'functs': {'mark': "mark", },
		'orderby': 'family, names',
		},
	# id, logdate, who_id, who_name, label, id_org, id_contr, messge
	'history':	{	'title': "История изменений БД",
		'order': ['logdate', 'who_name', 'label', 'id_org', 'id_contr', 'messge'],
		'key':	'id',
		'orderby': 'logdate DESC LIMIT 300',
		'functs': {'mark': "mark", },
	},
	# CREATE VIEW vhistory AS SELECT h.*, c.cnum FROM history h LEFT JOIN contracts c ON c.id_contr = h.id_contr;
	'vhistory':	{	'title': "История изменений БД",
		'order': ['logdate', 'who_name', 'label', 'id_org', 'id_contr', 'cnum', 'messge'],
		'thead': {'id_org': "idO", 'id_contr': "idC", 'cnum': "numContact"},
		'key':	'id',
		'orderby': 'logdate DESC LIMIT 300',
		'functs': {'mark': "mark", },
	},
	# CREATE VIEW vcontracts AS SELECT c.*, o.label, o.bname, o.fname, o.region, o.rname FROM vorganizations o, contracts c WHERE c.id_org = o.id_org;
	# id_contr, cnum, cdate, period_valid, is_valid, id_org, add_consents, add_acts, ctype, is_paid, pfix, ref_docx, rem, date_close, label,  bname
	'vcontracts':	{ 'title': "Договора и Контракты",
	#	'order': ['cnum', 'cdate', 'bname', 'bm_cstat', 'period_valid', 'ctype', 'bm_ssys', 'csumma', 'rname', 'rem'],
		'order': ['cnum', 'cdate', 'bname', 'bm_cstat', 'period_valid', 'date_close', 'ctype', 'bm_ssys', 'csumma', 'rname', 'rem'],
		'update': {'csumma': 'i',
			'cnum': 's:32', 'is_valid': 'i', 'is_nds': 'i', 'ctype': 'i', 'cdate': 'd', 'bm_cstat': 'i', 'bm_ssys': 'i', 'period_valid': 'd', 'rem': 's:256', 'id_org': 'i'},
		'thead': {'cnum': '№ Дог.', 'cdate': '&nbsp;&nbsp;&nbsp;Дата&nbsp;&nbsp;&nbsp;&nbsp;', 'label': "Метка", 'bname': "Наименование организации",
			'ctype': "Тип&nbsp;",
			'bm_cstat': "Состояние&nbsp;договора",
			'period_valid': "Действует",
			'date_close': "Завершен",
			'csumma': "Сумма договора",
			'fname': "Наименование организации", 'rname': "Район",
			},
		'key':	'id_contr',
		'orderby': 'bm_cstat, cdate',
		'functs': {'mark': "mark", },
		},
	# CREATE VIEW vorganizations AS SELECT o.*, r.rname FROM organizations o, region r WHERE id=region;
	# id_org, p_org, inn, label, bname, fname, region, bm_ssys, stat, cod_1c, rem, rname
	'vorganizations': {'title':  'Данные по Организациям',
		'order': ['p_org', 'inn', 'label', 'bname', #'fname',
			'rname', 'bm_ssys', 'bl_mail', 'rem'], 
		'update': {'inn': 'i', 'label': 's:32', 'bname': 's:128', 'fname': 's:256', 'rem': 's:256', 'region': 'i', 'bl_mail': 'i'},
		'thead': {'inn': "ИНН", 'label': "Метка", 'bname': "Наименование организации", 'fname': "Наименование организации", 'rname': "Район",
			'bl_mail': "M",
			#'bm_ssys': "Подсистема",
			},
		'key':	'id_org',
		'orderby': 'bname',
		'functs': {'mark': "mark", },
		},
	# INSERT INTO transports (id_ts) values (0);
	# INSERT INTO organizations (id_org) values (0);
	# INSERT INTO atts (id_att) values (0);
	# CREATE VIEW vtransports AS SELECT t.*, o.bname AS oname, y.ttname FROM transports t, organizations o, ts_types y  WHERE t.id_org = o.id_org AND t.ts_type = y.id_tts;
	# id_ts, garnum, gosnum, marka, modele, vin, year, pts, pts_date, sregistr, sreg_date, bm_ssys, id_att, id_tgroup, region, id_org, ts_type, rem
	'vtransports':	{ 'title': "Список Транспорта", 'form_tit': "Транспорт",
		'order': ['garnum', 'gosnum', 'marka', 'bm_ssys', 'ttname', 'oname', 'rname',
			'id_mail', 'bm_status',
			'rem'],	# 'modele', 'vin', 'pts', 'pts_date', 'sregistr', 'sreg_date', 'rem'],
		'thead': {'garnum': "Гараж. №", 'gosnum': "Гос.№ ТС", 'marka': "Марка ТС", 'modele': "Модель", 'ttname': "Тип ТС &nbsp;", 'rname': "Район",
			'oname': "Наименование организации", 'id_mail': "M", 'bm_status': "Стат.ТС",
			},
		'update': {'garnum': 's:32', 'gosnum': 's:32', 'marka': 's:64', 'modele': 's:64', 'vin': 's:16', 'pts': 's:32', 'rem': 't:256',
			'pts_date': 'd', 'sregistr': 's:32', 'sreg_date': 'd',
			'bm_status': 'i',
			},
		'key':  'id_ts',
		'functs': {'mark': "mark", }
		},
	'wtransports':	{ 'title': "Транспорт в работе", 'form_tit': "Транспорт",
		'order': ['gosnum', 'amark', 'last_date', 'oname',
			'rname', 'bid', 'tm_creat',
			'bm_wtime',
			'id_mail', 'bm_status',
		#	'tm_close', 'id_bid',
			'rem'],	# 'modele', 'vin', 'pts', 'pts_date', 'sregistr', 'sreg_date', 'rem'],
		'thead': { 'gosnum': "Гос.№ ТС", 'amark': "Марка АТТ", 'modele': "Модель", 'ttname': "Тип ТС &nbsp;",
			'rname': "Район", 'bid': "Сервс.", 'tm_creat': "Когда",
			'oname': "Наименование организации", 'id_mail': "M", 'bm_status': "Стат.ТС",
			'bm_wtime': "Работа ТС", 'last_date': "Последние данные",
			},
		'update': {'bm_status': 'i', 'rem': 't:256',
			},
		'key':  'id_ts',
		'orderby': 'bm_wtime, oname',
		'functs': {'mark': "mark", }
		},
	# CREATE VIEW voatts AS SELECT a.*, t.gosnum, o.id_org, o.label AS olabel, o.bname AS obname, o.region, o.bm_ssys FROM atts a, transports t, organizations o WHERE a.autos = t.id_ts AND t.id_org = o.id_org;
	# id_att, autos, mark, modele, uin, sim_1, sim_2, bm_options, last_date, gosnum, id_org, olabel, obname, region
	'voatts':	{ 'title': "Список Оборудования", 'form_tit': "Оборудование",
		'order': [ 'mark', 'modele', 'uin', 'sim_1', 'sim_2', 'bm_options', 'last_date', 'gosnum', 'obname', 'bm_ssys', ],
		'thead': {'mark': "Марка устройства", 'modele': "Модель устройства",
			# 'uin': "", 'sim_1': "", 'sim_2': "",
			'bm_options': "Доп.Опции", 'last_date': "Последние данные", 'gosnum': "Гос.№ ТС", 'olabel': "Организация", 'obname': "Наименование организации"},
		'update': {
			'mark': 's:32', 'modele': 's:32', 'uin': 's:32', 'sim_1': 's:32', 'sim_2': 's:32', 'rem': 't:256',
			},
		'key':  'id_att',
		'functs': {'mark': "mark", }
		},
	'add_consents':	{
		'update':	{'id_contr': 'i', 'id_org': 'i',  'docnum': 's:16', 'docdate': 'd', 'docteam': 's:256', 'rem': 't:512', },
		},
	'add_acts':	{
		'update':	{'id_contr': 'i', 'id_org': 'i',  'docnum': 's:16', 'docdate': 'd', 'docteam': 's:256', 'rem': 't:512',  },
		},
	# alarms	id, id_bid, bm_btype, bm_bstat, id_org, id_contr, tm_creat, tm_alatm, tm_close, who_clos
	# CREATE  VIEW vbids AS SELECT b.*, t.bname, o.bname AS obname, o.region, o.rname FROM bids b, bid_type t, vorganizations o WHERE b.bm_btype=t.code  AND b.id_org = o.id_org;
	# vbids	id_bid, bid_num, biddate, bm_btype, bm_bstat, id_org, id_contr, tm_creat, tm_alarm, tm_close, rem, bname
	'vbids':{'title': "Список Заявок", 'form_tit': "Заявка",
		'order': ['bid_num', # 'biddate',
			'bname', 'obname', 'bm_bstat', #'obname',
			'tm_creat', 'tm_alarm', 'tm_close', 'rname', 'rem',],
		'thead': {'bid_num': '№ заявки', 'bname': 'Тип заявки', 'rname': "Район", 'obname': "Наименование организации",
			'tm_creat': 'Принята', 'tm_alarm': 'Исплнть', 'tm_close': 'Закрыта',
			'bm_bstat': 'Статус исполнения', },
		'key':  'id_bid',
		'update': {'rem': 't:256', },
		'functs': {'mark': "mark", }
		},
	# select * FROM mail_to;
	# CREATE VIEW vmail_to AS SELECT m.*, o.id_org, o.bname AS obname, o.region, o.rname FROM mail_to m, vorganizations o WHERE m.id_org = o.id_org;
	'vmail_to':{'title': "Отправка почты", 'form_tit': "E-mail",
	 	'order': [#'id', 'id_org',
			'obname', 'rname', 'body', 'date_send', 'who_name', 'date_ack',# 'ch_ack',	# 'j_send', 'bl_send',
			'rem',
			],
		'thead': {'obname': "Наименование организации", 'date_send': "Когда отправлено", 'who_name': "Кто отправил", 'date_ack': "Пришел ответ", 'body': "Текст сообщения"},
		'key':  'id_mail',
		'orderby': 'date_send DESC',
		'update': {'ch_ack': 'i', 'date_ack': 'd',	# 'bl_send': 'i',
			'rem': 't:256', },
		'functs': {'mark': "mark", }
	 	},
	}

