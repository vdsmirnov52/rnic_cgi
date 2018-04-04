/**     \file	js/check_forms.js
*/
function	check_form_contr() {
	var	 messg = '';
	if (document.myForm.org_name.value == '')	messg += '\tОтсутствует оргагизация!\n';
	if (document.myForm.cnum.value == '')	 	messg += '\tОтсутствует номер Договора (контракта)!\n';
	if (document.myForm.cdate.value == '')		messg += '\tОтсутствует дата Договора (контракта)!\n';
	if (document.myForm.ctype.value == '')		messg += '\tОтсутствует тип Договора (контракта)!\n';
	if (document.myForm.bm_ssys.value == '')	messg += '\tНе указана подсистема!\n';
//	if (document.myForm.period_valid.value == '')	messg += '\tНе указан Срок действия!\n';
//	if (document.myForm.csumma.value == '')		messg += '\tНе указана Сумма Договора!\n';
	if (messg != '') {	alert ('Ошибки в заполнении формы:\n' +messg);	return;	}
	set_shadow('save_new')
}
function	check_form_org() {
	var	messg = '';
	if (document.myForm.label.value == '')	messg += '\tОтсутствует Метка организации!\n';
	if (document.myForm.bname.value == '')	messg += '\tОтсутствует Краткое Наименоване организации!\n';
	if (document.myForm.fname.value == '')	messg += '\tОтсутствует Полное Наименоване организации!\n';
	if (document.myForm.inn.value == '')  {
		messg += '\tОтсутствует ИНН!\n';
	} else {
		if (! (document.myForm.inn.value.length == 10 || document.myForm.inn.value.length == 12))	messg += '\tНеверное колличество симполов в ИНН!\n';
	}
	if (document.myForm.region.value == '')	messg += '\tНе указан Район!\n';
	if (messg != '') {	alert ('Ошибки в заполнении формы:\n' +messg);	return;	}
	set_shadow('save_new')
}
function	check_form_add_doc() {	//	docnum, docdate, docteam
	var	messg = '';
	if (document.myForm.docnum.value == '')		messg += '\tОтсутствует Номер документа!\n';
	if (document.myForm.docdate.value == '')	messg += '\tОтсутствует Дата документа!\n';
	if (document.myForm.docteam.value == '')	messg += '\tОтсутствует Тема документа!\n';
	if (messg != '') {
		alert ('Ошибки в заполнении формы:\n' +messg);  return false;
	} else	return	true;
	}
function	check_new_bid() {	// 'bid_create': '14-06-2016', 'bid_type': '2'
	var	messg = '';
	if (document.myForm.bid_type.value == '')	 messg += '\tОтсутствует Тип заявки!\n';
	if (document.myForm.bid_num.value == '')	 messg += '\tОтсутствует Номер регистрации!\n';
	if (document.myForm.bid_create.value == '')	 messg += '\tОтсутствует Дата регистрации!\n';
	if (messg != '') {
		alert ('Не достаточно данных для регистрации заявки (письма):\n' +messg);	return false;
	}
	return	confirm ('Сохранить заявку (письмо)?')
}
function proverka(input) { 
	var value = input.value; 
	var rep = /[-\.;":'a-zA-Zа-яА-Я]/; 
	if (rep.test(value)) { 
		value = value.replace(rep, ''); 
		input.value = value; 
	} 
} 
function	email (input) {
	var value = input.value;
	var rep = /[-\/,;":'а-яА-Я]/;
	if (rep.test(value)) {
		value = value.replace(rep, '');
		input.value = value;
	}
}
function	intKey(input) {
	var value = input.value; 
	var rep = /[-\/\., ;":'a-zA-Zа-яА-Я]/; 
	if (rep.test(value)) { 
		value = value.replace(rep, ''); 
		input.value = value;
	}
}
