var start_g;
var end_g;

$(function() {
	$('<a name="top"/>').insertBefore($('body').children().eq(0));
	window.location.hash = 'top';
});

$(document).ready(function() {
	$(".end").hide();
	$(".wait").hide();
	$(".walk").hide();
	$(".thinking").hide();
	$(".rainy").hide();
	$(".cold").hide();
	$(".again").hide();
	$(".rainytext").hide();
	$(".coldtext").hide();

	$(".start").click(function() {
		start_g = this.id;

		$(".start").hide();
		$(".end").show();

		$(function() {
				 $('body').scrollTop(0);
			 });
	}); 

	$(".end").click(function(){
		end_g = this.id;
		$(".end").hide();
		$(".thinking").show();
		//Figure out if they should walk or wait.
		
		//Do a GET request to /shouldwait?start=startingLocation&end=endingLocation
		//it will return a 1 if you should wait and a 0 if you should walk
		$.get("/shouldwait", {"start" : start_g, "end" : end_g}, function(result) {
			//console.log(result);
			//Check weather, but only if the buses are operating (M-F, 7am-10pm)
			shouldwait = result.slice(0,1); 
			waittime = result.slice(2,4);

			var weather = 0;
			var currentdate = new Date();

			if ((currentdate.getDay() != 0) && (currentdate.getDay() != 6)) {
				//it's a weekday
				if ((currentdate.getHours() > 7) && (currentdate.getHours() < 22)) {
					//it's between 7am and 10pm
					var request = new XMLHttpRequest(); //jQuery? We don't need no stinkin' jQuery!
					request.open("GET", "/weather", false);
					request.send(null);

					weather = request.responseText;
					//console.log(weather);
				}
			}

			if (shouldwait == 0) {
				//walk
				$(".walk").show();
				$(".again").show();

				if (weather == 1) {
					//it's rainy
					$(".rainy").show();

					var phrase;

					if (waittime == 1) {
						phrase = waittime.toString() + " minute, you can ride the bus and stay dry."
					} else {
						phrase = waittime.toString() + " minutes, you can ride the bus and stay dry."
					}

					$(".rainytext").append(phrase);
					$(".rainytext").show();
				}

				if (weather == 2) {
					//it's cold
					$(".cold").show();

					var phrase;

					if (waittime == 1) {
						phrase = waittime.toString() + " minute, you can ride the bus and stay warm."
					} else {
						phrase = waittime.toString() + " minutes, you can ride the bus and stay warm."
					}

					$(".coldtext").append(phrase);
					$(".coldtext").show();
				}

				$(".thinking").hide();
			} else if (shouldwait == 1) {
				//wait
				$(".wait").show();
				$(".again").show();
				$(".thinking").hide();
			} else {
				console.log("Error: Got unexpected result from server");
			}
		});
	});
});