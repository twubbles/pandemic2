if ($('#postfeed').length > 0) {
require( ["masonry"], function( masonry ) {
		

    var container = document.querySelector('#postfeed');
    var msnry = new masonry( container, {
        itemSelector: '.item',
        columnWidth: '.item',
    });

     msnry.layout();


});
};