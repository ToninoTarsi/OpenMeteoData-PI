/****************************************
 *    corners.js                        *
 *                                      *
 *    Corner info for Google Maps       *
 ****************************************/ 

var corners = new Array();
var tmp;

corners["Bounds"]
corners["Centre"]

corners.Bounds = new Array();
corners.Centre = new Array();


corners.Bounds[2] = new google.maps.LatLngBounds(
        new google.maps.LatLng(42.6643448, 12.0637817), // SW
        new google.maps.LatLng(43.6735954, 13.4562378)  // NE
    );
corners.Centre[2] = new google.maps.LatLng(43.1689682, 12.7600098);

corners.Bounds[3] = new google.maps.LatLngBounds(
        new google.maps.LatLng(42.6099319, 11.9884644), // SW
        new google.maps.LatLng(43.7275581, 13.5314941)  // NE
    );
    corners.Centre[3] = new google.maps.LatLng(43.1687469, 12.7599792);


corners.Bounds[6] = new google.maps.LatLngBounds(
        new google.maps.LatLng(41.9717026, 11.1003418), // SW
        new google.maps.LatLng(44.3569832, 14.4196777)  // NE
    );
 corners.Centre[6] = new google.maps.LatLng(43.1643448, 12.7600098);

// UK 2km (Today)
// corners.Bounds[2] = new google.maps.LatLngBounds(
    // new google.maps.LatLng(49.5374451, -10.8640747), // SW
    // new google.maps.LatLng(59.4576149, 2.7055664)  // NE
// );
// corners.Centre[2] = new google.maps.LatLng(54.4975281, -4.0792542);

