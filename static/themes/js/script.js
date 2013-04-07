var origin_stop;
var destination_stop;

var pick_origin;

$(document).ready(function() {
	pick_origin = true;

	$("#stops a").click(function() {
		if (pick_origin) {
			origin_stop = $(this).data("id");

			pick_origin = false;

			$("#originText").addClass("hide");
			$("#destinationText").removeClass("hide");

			$(document).scrollTop(0, 0);

			$("#stops a").addClass("btn-danger");
		} else {
			destination_stop = $(this).data("id");

			$("#setup").addClass("hide");

			$("#originText").removeClass("hide");
			$("#destinationText").addClass("hide");

			$("#stops").addClass("hide");

			$("#thinking").removeClass("hide");

			determineWaitOrWalk(origin_stop, destination_stop,
				function(should_wait, wait_time, weather) {
					console.log("success");
					// Success
					$("#thinking").addClass("hide");

					if (should_wait) {
						shouldWait();
					} else {
						shouldWalk();
					}

					$("#again").removeClass("hide");
					
					$("#results").removeClass("hide");
				}, function() {
					// Failure
					reset();
			});
		}
	});

	$("#again a").click(function() {
		reset();
	});
});

function reset() {
	$("#rain").addClass("hide");
	$("#cold").addClass("hide");

	$("#wait").addClass("hide");
	$("#walk").addClass("hide");

	$("#thinking").addClass("hide");
	$("#results").addClass("hide");
	$("#out-of-service").addClass("hide");
	$("#again").addClass("hide");

	$("#setup").removeClass("hide");
	$("#stops").removeClass("hide");

	$("#stops a").removeClass("btn-danger");

	pick_origin = true;
}

function shouldWalk(wait_time, weather) {
	$("#walk").removeClass("hide");

	if (weather == 1) {
		// It is raining
		
		$("#rain").removeClass("hide");
		$("#rain #time").text(wait_time);
	} else if (weather == 2) {
		// It is cold
		
		$("#cold").removeClass("hide");
		$("#cold #time").text(wait_time);
	}
}

function shouldWait() {
	$("#wait").removeClass("hide");
}

function determineWaitOrWalk(origin, destination, success, failure) {
	var data = { "start": origin, "end": destination };

	$.ajax({
			url: "/shouldwait",
			data: data
	}).done(function(result) {
		str_split = result.split(' ');

		var should_wait = str_split[0] == 1 ? true : false;
		var wait_time = str_split[1];

		console.log([should_wait, wait_time, result]);
		getWeather(function(result) {
			console.log("got weather");
			return success(should_wait, wait_time, result);
		}, function() {
			console.error("Could not get weather.");
			return success(should_wait, wait_time, 0);
		});
	}).fail(function() {
		console.error("Could not determine whether to wait or walk.");

		return failure();
	});
}

function getWeather(success, failure) {
	var now = new Date();

	// Only check weather if buses are operating
	// Buses operate M-F from 7 AM to 10 PM
	if (now.getDay() >= 1 && now.getDay() <= 5) {
		if (now.getHours() > 7 && now.getHours() < 22) {
			console.log("stuff");
			// Buses are operating
			$.ajax({
				url: "/weather"
			}).done(function(result) {
				return success(result);
			}).fail(function() {
				return failure();
			});
		}
	}

	$("#results").removeClass("hide");
	$("#thinking").addClass("hide");
	$("#out-of-service").removeClass("hide");
	$("#again").removeClass("hide");

}