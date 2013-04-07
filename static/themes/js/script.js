var origin_stop;
var destination_stop;

var pick_origin;

$(document).ready(function() {
	pick_origin = true;

	$("#stops a").click(function() {
		// When any of the stop buttons are clicked...

		if (pick_origin) {
			// This is the first time we've clicked (i.e. the origin)
			// Remember the stop ID and move onto choosing the destination

			origin_stop = $(this).data("id");

			pick_origin = false;

			$("#originText").addClass("hide");
			$("#destinationText").removeClass("hide");

			$(document).scrollTop(0, 0);

			$("#stops a").addClass("btn-danger");
		} else {
			// This is the second time we've clicked (i.e. the destination)
			// Remember the stop ID and begin to show the results

			destination_stop = $(this).data("id");

			$("#setup").addClass("hide");

			$("#originText").removeClass("hide");
			$("#destinationText").addClass("hide");

			// Start to compute the results
			$("#stops").addClass("hide");

			$("#thinking").removeClass("hide");

			determineWaitOrWalk(origin_stop, destination_stop,
				function(should_wait, wait_time, weather) {
					// Success - The server has returned a result
					
					$("#thinking").addClass("hide");

					if (should_wait) {
						shouldWait();
					} else {
						shouldWalk(wait_time, weather);
					}

					$("#again").removeClass("hide");
					
					$("#results").removeClass("hide");
				}, function() {
					// Failure - The server returned something bad
					
					reset();
			});
		}
	});

	$("#again a").click(function() {
		// Reset back to choosing the origin if the again button is clicked
		reset();
	});
});

// Reset all elements back to their initial setup
function reset() {
	$("#rain").addClass("hide");
	$("#cold").addClass("hide");

	$("#wait").addClass("hide");
	$("#walk").addClass("hide");

	$("#thinking").addClass("hide");
	$("#results").addClass("hide");
	$("#again").addClass("hide");

	$("#setup").removeClass("hide");
	$("#stops").removeClass("hide");

	$("#stops a").removeClass("btn-danger");

	pick_origin = true;
}

// Show the walk elements given the wait time for a bus and the weather conditions
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

// Show the wait elements
function shouldWait() {
	$("#wait").removeClass("hide");
}

// Determine whether we should wait/walk from origin to dest
function determineWaitOrWalk(origin, destination, success, failure) {
	// Make a call to the server API with the start/end as params

	var data = { "start": origin, "end": destination };

	$.ajax({
			url: "/shouldwait",
			data: data
	}).done(function(result) {
		// Server responded - extract the data

		var should_wait = result.slice(0, 1) == 1 ? true : false;
		var wait_time = result.slice(2, 4);
		var weather;

		// Get the weather
		getWeather(function(result) {
			// Got the weather
			
			return success(should_wait, wait_time, result);
		}, function() {
			// Server could not get the weather for some reason
			
			console.error("Could not get weather.");

			return success(should_wait, wait_time, 0);
		});
	}).fail(function() {
		// Server did not respond

		console.error("Could not determine whether to wait or walk.");

		return failure();
	});
}

// Get the weather from the server
function getWeather(success, failure) {
	var now = new Date();

	// Only check weather if buses are operating
	// Buses operate M-F from 7 AM to 10 PM
	if (now.getDay() >= 1 && now.getDay() <= 5) {
		if (now.getHours() > 7 && now.getHours() < 22) {
			// Buses are operating
			$.ajax({
				url: "/weather"
			}).done(function(result) {
				// Got the weather

				return success(result);
			}).fail(function() {
				// Server did not respond

				return failure();
			});
		} else {
			return success(0);
		}
	} else {
		return success(0);
	}
}