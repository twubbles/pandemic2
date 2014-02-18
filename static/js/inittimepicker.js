

if ($(".datetime").length > 0) {
	require( ["timepicker"], function( timepicker ) {
		$( ".datetime" ).addClass( "input-group date" );
		$(".datetime").datetimepicker({
			dateFormat: "yy-mm-dd",
			timeFormat: "HH:mm:ss",
			stepHour: 1,
			stepMinute: 1,
			stepSecond: 10,
			addSliderAccess: true,
			sliderAccessArgs: { touchonly: false },

		});	
	});
};

