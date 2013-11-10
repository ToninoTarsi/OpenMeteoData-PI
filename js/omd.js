//var imageBounds = new google.maps.LatLngBounds(
//	new google.maps.LatLng(42.5, 12.00),
//	new google.maps.LatLng(44.0, 13.5));

//var use_tiles = false;
//var zoom_min = 7
//var zoom_max = 12


var map;
var googleEarth;
var param = 'convergence';
var time = 11;
var date = 0;
var theDate = "";
var theOverlay = null;
var image = "";
var waypointsLayer = null;


var serverDir = './maps/'
//var serverDir = 'http://www.vololiberomontecucco.it/omdpi/maps/'
	
var description = {"convergence":"Andamento dei venti al suolo con intensita in rosso espressa in kmh mentre la campitura indica, in rosso, le aree di massima convergenza",
					"topbl":"Andamento dei venti in quota con intensità in rosso espressa in kmh e altezza del Boundary Layer ( zona nella quale di hanno movimenti convettivi )", 
					"wstar":"Intensità media delle termiche espressa in metri al secondo",
					"clouds":"Mappa della nuvolosita e pioggie"};

google.load('earth', '1');
google.maps.event.addDomListener(window, 'load', init);


waypointsLayer = new google.maps.KmlLayer(serverDir + 'waipoints.kml');

var maptiler = new google.maps.ImageMapType({
    getTileUrl: function(coord, zoom) { 
        var proj = map.getProjection();
        var z2 = Math.pow(2, zoom);
        var tileXSize = 256 / z2;
        var tileYSize = 256 / z2;
        var tileBounds = new google.maps.LatLngBounds(
                proj.fromPointToLatLng(new google.maps.Point(coord.x * tileXSize, (coord.y + 1) * tileYSize)),
                proj.fromPointToLatLng(new google.maps.Point((coord.x + 1) * tileXSize, coord.y * tileYSize))
            );        
        
        var y = coord.y;
		y = (Math.pow(2,zoom)-coord.y-1); // Tony
        if (imageBounds.intersects(tileBounds) && (zoom_min <= zoom) && (zoom <= zoom_max))
        {
        	//alert(serverDir + image +  "_map/" + zoom + "/" + coord.x + "/" + y + ".png");
            //return newimg;
            return serverDir + image +  "_map/" + zoom + "/" + coord.x + "/" + y + ".png";
        }
        	 
        else
            return "http://www.maptiler.org/img/none.png";
    },
    tileSize: new google.maps.Size(256, 256),
    isPng: true,
    opacity: 0.4
});


function init() {
    map = new google.maps.Map(document.getElementById('map'), {
      zoom: 10,
      minZoom: zoom_min, 
      maxZoom: zoom_max,
      center: new google.maps.LatLng(43.33733, 12.733563),
      mapTypeControlOptions: {
          mapTypeIds: [google.maps.MapTypeId.TERRAIN]
      },
      mapTypeId: google.maps.MapTypeId.TERRAIN 
    });

    googleEarth = new GoogleEarth(map);
    google.maps.event.addListenerOnce(map, 'tilesloaded', addOverlays);
 }


function getOverlayName()
{
	var T = new Date();
	if ( date == 1) 
		T = new Date(T.getTime() + (24 * 60 * 60 * 1000));
	var G = T.getDate();
	var M = (T.getMonth()+ 1);
	if (G < 10)
	{
		var gg = "0" + T.getDate();
	}
	else
	{
		var gg = T.getDate();
	}

	if (M < 10)
	{
		var mm = "0" + (T.getMonth() +1 );
	}
	else
	{
		var mm = (T.getMonth() + 1  );
	}

	var aa = T.getFullYear();

	var data = gg + "" + mm + "" + aa;

	theDate =  gg + "/" + mm + "/" + aa;
	return ( data + "_"  + time + "_" +  param  )
	
}

function loadImage(image)
{
	if ( ! use_tiles )
	{
		var newimg = serverDir+image+"_map.png";
		if ( theOverlay != null )
			theOverlay.setMap(null);
		theOverlay = new google.maps.GroundOverlay(newimg,imageBounds);
		theOverlay.setOpacity(0.4);
		theOverlay.setMap(map);

		//alert(newimg);
	}
	else
	{
		//map.overlayMapTypes.removeAt(0);
		//map.overlayMapTypes.removeAt(0)
		map.overlayMapTypes.setAt(0, maptiler);

	}
	$("#img_legend").attr("src",serverDir+image+"_legend.jpg");
	$("#description").html(theDate + " - " + description[param] + "<br>Ultimo run : " + run);
}

function addOverlays() {
	
	image = getOverlayName();
	loadImage(image);
	
//	theOverlay = new google.maps.GroundOverlay("./out/25102013_11_vsfc_map.png",imageBounds);
//	theOverlay.setOpacity(0.4);
//	theOverlay.setMap(map);

}

function timeChanged(selectedValue, selectedName,element) {
	if ( time != selectedValue )
	{
		time = selectedValue;
		image = getOverlayName();
		loadImage(image);		
	}
	
} 
  
function dateChanged(selectedValue, selectedName,element) {
	if ( date != selectedValue)
	{
		date = selectedValue;
		image = getOverlayName();
		loadImage(image);	
	}
	  

  }
  
  function parameterChanged(selectedValue, selectedName,element) {
		if ( param != selectedValue)
		{
			param = selectedValue;
			image = getOverlayName();
			loadImage(image);
		}
	}
  
  function toggleWaipoints( element) {
		if ( element.checked ) {
			waypointsLayer.setMap(map);
			//alert("Checkd");
		}
		else {
			//alert("UnCheckd");
			waypointsLayer.setMap(null);
		}
	}
  
  