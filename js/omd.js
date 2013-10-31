//var imageBounds = new google.maps.LatLngBounds(
//	new google.maps.LatLng(42.5, 12.00),
//	new google.maps.LatLng(44.0, 13.5));

var map;
var googleEarth;
var param = 'convergence';
var time = 11;
var date = 0;
var theOverlay = null;
var serverDir = './out/'

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

	return ( data + "_"  + time + "_" +  param  )
	
}

function loadImage(image)
{
	if ( theOverlay != null )
		theOverlay.setMap(null);
	theOverlay = new google.maps.GroundOverlay("./maps/"+image+"_map.png",imageBounds);
	theOverlay.setOpacity(0.4);
	theOverlay.setMap(map);
	$("#img_legend").attr("src","./maps/"+image+"_legend.jpg");
	//alert("./out/"+image+"_map.png");

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
  