

if ($('#no_table_timeshared__row').length > 0) {

var $sliderdiv = $( "<div id='slider'/>" );
var $slidertd = $( "<td colspan=3 id='slidertd'/>" );
var $slidertr = $( "<tr id='slidertr'/>" );

var $slidertotaltd = $( "<td colspan=3 id='slidertotaltd'/>" );
var $slidertotal = $( "<span style='text-align:center;' id='slidertotal'>Use the Slider to choose how much time to save in your biteshare</span>" );
$( "#no_table_timeshared__row" ).hide();

$('#no_table_share').change(
function() {
    if ($(this).is(':checked')) {
       $( "#no_table_timeshared__row" ).show();
       $( "#no_table_timeshared__row > td" ).hide();
       $( '#no_table_timeshared__row' ).append( $slidertotaltd );
       $('#slidertotaltd').append( $slidertotal );

       $('#no_table_timeshared__row').after( $slidertr );
       $('#slidertr').append( $slidertd );
       $('#slidertd').append( $sliderdiv );
        $(function() {
        $( "#slider" ).slider({
          min: $minShare,
          max: $maxShare,
          step: 3600,
          slide: function( event, ui ) {
        $( "#no_table_timeshared" ).val( ui.value );
        $( "#slidertotal" ).text( ((ui.value/60)/60) + " Hours" );
      }
    });

  });
    }
    else {
        $( "#slidertr" ).empty();
        $( "#no_table_timeshared__row" ).hide();
        $( "#slidertotaltd").remove();
    }
});

};

