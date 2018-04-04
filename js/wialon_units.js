
function init() { // Execute after login succeed
	var sess = wialon.core.Session.getInstance(); // get instance of current Session
	// flags to specify what kind of data should be returned
	var flags = wialon.item.Item.dataFlag.base | wialon.item.Unit.dataFlag.lastMessage;
	sess.loadLibrary("itemIcon"); // load Icon Library	
	sess.updateDataFlags( // load items to current session
	[{type: "type", data: "avl_unit", flags: flags, mode: 0}], // Items specification
		function (code) { // updateDataFlags callback
			if (code) { msg(wialon.core.Errors.getErrorText(code)); return; } // exit if error code
			// get loaded 'avl_unit's items  
			var units = sess.getItems("avl_unit");
			if (!units || !units.length){ msg("Units not found"); return; } // check if units found
	msg ('flags: ' + flags +'; units.length: ' + units.length);	// DEBUG
			for (var i = 0; i< units.length; i++){ // construct Select object using found units
				var u = units[i]; // current unit in cycle
/* DEBUG
var pos = u.getPosition();
if (pos) msg(u.getName() +' \tX: ' +pos.x +' Y:' +pos.x);
else	msg(u.getName() +' \tNot Position');
*/				// append option to select
				$("#units").append("<option value='"+ u.getId() +"'>"+ u.getName()+ "</option>");
			}
			// bind action to select change event
			$("#units").change( getSelectedUnitInfo );
		}
	);
}

function getSelectedUnitInfo(){ // print information about selected Unit

	var val = $("#units").val(); // get selected unit id
	if(!val) return; // exit if no unit selected
	
	var unit = wialon.core.Session.getInstance().getItem(val); // get unit by id
	if(!unit){ msg("Unit not found");return; } // exit if unit not found
//	alert("DEBUG: " + val);
	
	// construct message with unit information
	var text = "<div>'"+unit.getName()+"' selected. "; // get unit name
	var icon = unit.getIconUrl(32); // get unit Icon url
	if(icon) text = "<img class='icon' src='"+ icon +"' alt='icon'/>"+ text; // add icon to message

	var pos = unit.getPosition(); // get unit position
	if(pos){ // check if position data exists
		var time = wialon.util.DateTime.formatTime(pos.t);
		text += "<b>Last message</b> "+ time +"<br/>"+ // add last message time
			"<b>Position</b> "+ pos.x+", "+pos.y +"<br/>"+ // add info about unit position
			"<b>Speed</b> "+ pos.s; // add info about unit speed
		// try to find unit location using coordinates 
		var code = unit.getId();
		wialon.util.Gis.getLocations([{lon:pos.x, lat:pos.y}], function(code, address){ 
			if (code) { msg(wialon.core.Errors.getErrorText(code)); return; } // exit if error code
			msg(text + "<br/><b>Location of unit</b>: "+ address+"</div>"); // print message to log
		});
		msg(text + "</div>");
	} else // position data not exists, print message
		msg(text + "<br/><b>Location of unit</b>: Unknown</div>");
}
