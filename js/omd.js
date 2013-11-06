//var imageBounds = new google.maps.LatLngBounds(
//	new google.maps.LatLng(42.5, 12.00),
//	new google.maps.LatLng(44.0, 13.5));

var map;
var googleEarth;
var param = 'convergence';
var time = 11;
var date = 0;
var theDate = "";
var theOverlay = null;
//var serverDir = './maps/'
var serverDir = 'http://www.vololiberomontecucco.it/omdpi/maps/'
	
var description = {"convergence":"Andamento dei venti al suolo e in rosso aree di massima convergenza",
					"topbl":"Andamento dei venti in quota e altezza del Boundary Layer", 
					"wstar":"Forza delle termiche",
					"clouds":"Mappa della nuvolosita e pioggie"};

google.load('earth', '1');
google.maps.event.addDomListener(window, 'load', init);




function init() {
    map = new google.maps.Map(document.getElementById('map'), {
      zoom: 10,
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
	var newimg = serverDir+image+"_map.png";
	if ( theOverlay != null )
		theOverlay.setMap(null);
	theOverlay = new google.maps.GroundOverlay(newimg,imageBounds);
	theOverlay.setOpacity(0.4);
	theOverlay.setMap(map);
	$("#img_legend").attr("src",serverDir+image+"_legend.jpg");
	$("#description").html(theDate + " - " + description[param]);
	//alert(newimg);

}

function addOverlays() {
	

	loadImage(getOverlayName());
	
//	theOverlay = new google.maps.GroundOverlay("./out/25102013_11_vsfc_map.png",imageBounds);
//	theOverlay.setOpacity(0.4);
//	theOverlay.setMap(map);

}

function timeChanged(selectedValue, selectedName,element) {
	if ( time != selectedValue )
	{
		time = selectedValue;
		loadImage(getOverlayName());
		
	}
	
} 
  
function dateChanged(selectedValue, selectedName,element) {
	if ( date != selectedValue)
	{
		date = selectedValue;
		loadImage(getOverlayName());
	}
	  

  }
  
  function parameterChanged(selectedValue, selectedName,element) {
		if ( param != selectedValue)
		{
			param = selectedValue;
			loadImage(getOverlayName());

		}
	}
  