/**	\file	js/tree.js
 *	$Id$
$(document).ready(function () {
	$.ajaxSetup({ url: "region.cgi?this=ajax", type: "post", error: onAjaxError, success: onAjaxSuccess, timeout: 30000 });
	if (document.mainForm.jtab && document.mainForm.jtab.value != '') {
		$.ajax({data: 'shstat=view_table&' +$('form').serialize()});
	}
	})
 */

function	intkey(event) {		// фильтр на ввод - только цифры 0-9
	var	chCode = ('charCode' in event) ? event.charCode : event.keyCode;
	return (chCode < 32 || chCode >= 48 && chCode <= 57);	/* '0' - '9' */
	}

function	is_a15() {
	if (document.mainForm.set_age) {
		document.mainForm.set_age.value = prompt('Сколько лет?','');
		$.ajax({data:'shstat=next_node&iddom=dtree&' +$('form').serialize()});
	} else	alert ('Отсутствует document.mainForm.set_age !');
}
function	jset (sset, sval) {
	if (sset == 'set_sex') {
		if (document.mainForm.set_sex) {
			if (sval == 'G')
				document.mainForm.set_sex.value = 'Ж';
		} else	alert ('Отсутствует document.mainForm.set_sex !');
	} else	alert ('JSET sset = "' +sset +'", sval = "' +sval +'".');
}
function	clc_mbody (iddom) {
	$.ajax({data: 'shstat=mclick&cname=clc_mbody&iddom=' +iddom +'&' +$('form').serialize()});
}
function	clc_medev (iddom) {
	$.ajax({data: 'shstat=mclick&cname=clc_medev&iddom=' +iddom +'&' +$('form').serialize()});
}
