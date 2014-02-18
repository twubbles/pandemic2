


if ($('.admintable').length > 0) {
	require( ['datatables'], function( datatables ) {
		$( "input, textarea, select" ).addClass( "form-control" );
		$( ".web2py_paginator ul:first" ).addClass( "pagination" );
		$( ".web2py_breadcrumbs" ).hide();
		$('.buttontext').addClass('btn btn-primary');
		$( "table:first" ).attr( "id", 'bigtable' );
		$( "table:last" ).attr( "id", 'bigtable2' );
		$('#bigtable').dataTable();
		$('#bigtable2').dataTable();

	});
};
