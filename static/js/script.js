

if (navigator.geolocation) {
    // Use method getCurrentPosition to get coordinates
    navigator.geolocation.getCurrentPosition(function (position) {

        alert(position.coords.latitude + ", " + position.coords.longitude);
    });
};

