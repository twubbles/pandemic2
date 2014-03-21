require.config({
    "paths": {
        "jquery": "jquery-1.11.0.min",
		"qrcode": "qrcode",
		"timepicker": "timepicker",
		"datatables": "jquery.dataTables.min",
		"prefixfree": "prefixfree",
		"jqueryui": "jquery-ui-1.10.4.custom.min",
		"bootstrap":"bootstrap.min",
		"defaultview":"defaultview",
		"inittimepicker":"inittimepicker",
		"admintable":"admintable",
		"textareacheck":"textareacheck",
		"markitup":"jquery.markitup",
		"postpage":"postpage",
		"masonry":"masonry.min",

    },
    "shim": {
        "bootstrap": ["jquery"],
        "jqueryui": ["jquery"],
		"defaultview": ["jquery"],
		"inittimepicker": ["jquery"],
        "admintable": ["jquery"],
		"textareacheck": ["jquery"],
		"markitup":["jquery"],
		"postpage":["jquery"],
		"postpage":["masonry"],
		"masonry":["jquery"],


    }
});
require(["prefixfree", "jquery", "jqueryui","bootstrap","inittimepicker","admintable","defaultview","loadgeo", "textareacheck","postpage"], 
function (prefixfree, $, jqueryui, bootstrap, inittimepicker, admintable, defaultview,textareacheck,postpage) {

});
