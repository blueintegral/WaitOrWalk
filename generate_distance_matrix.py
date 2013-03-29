#! /usr/bin/env python
import json
import urllib2
import time
import os

"""This script will call Google Maps to calculate the time to walk between every combination of bus stops and the time to drive between every combination of bus stops.

We can't do this live in the app because of rate limiting and because Google requires you show a map.
"""

def get_times(walking):
	"""Get the travel time either walking or driving to all the bus stops.

	We'll have to go through each of the 17 stops with one origin and all 16 other stops as destinations. 

	This will result in fitten.json, mcm8th.json, etc...

	Then you can access the JSON for the specific starting point, find the destination, and get the travel time.

	Rate limiting prevents doing this in a more elegant way with fewer API calls.
	"""

	index = 0
	mode = "walking" if walking else "driving"

	bus_stops = [
		("fitten", "33.7782,-84.4041"),
		("mcm8th", "33.7795,-84.4041"),
		("8thhemp", "33.7796,-84.4029"),
		("fershemrt", "33.7784,-84.4009"),
		("fersstmrt", "33.7782,-84.3994"),
		("fersatmrt", "33.7782,-84.3975"),
		("ferschmrt", "33.7772,-84.3956"),
		("5thfowl", "33.7769,-84.3938"),
		("tech5th", "33.7797,-84.3921"),
		("tech4th", "33.7752,-84.392"),
		("techbob", "33.774,-84.3919"),
		("technorth", "33.7715,-84.3919"),
		("nortavea_a", "33.7701,-84.3917"),
		("ferstcher", "33.7722,-84.3955"),
		("hubfers", "33.7728,-84.397"),
		("centrstud", "33.7735,-84.3991"),
		("765femrt", "33.7754,-84.4025")
	]

	for bus_stop in bus_stops:
		print "Fetching " + bus_stop[0] + " walk times..."

		url = "http://maps.googleapis.com/maps/api/distancematrix/json?origins=" + bus_stop[1] + "&destinations=33.7782,-84.4041|33.7795,-84.4041|33.7796,-84.4029|33.7784,-84.4009|33.7782,-84.3994|33.7782,-84.3975|33.7772,-84.3956|33.7769,-84.3938|33.7797,-84.3921|33.7752,-84.392|33.774,-84.3919|33.7715,-84.3919|33.7701,-84.3917|33.7722,-84.3955|33.7728,-84.397|33.7735,-84.3991|33.7754,-84.4025&sensor=false&mode=" + mode

		# Write the data to the file
		json_response = json.load(urllib2.urlopen(url))

		with open("data/" + mode + "/" + bus_stop[0] + ".json", 'w') as output_file:
			json.dump(json_response, output_file)

		index = index + 1

		# Wait for rate limit
		time.sleep(15)

if __name__ == '__main__':
	print "This will take about 10 minutes, so sit tight."

	# Make the driving directory if it does not exist
	if not os.path.exists("data/driving"):
		os.makedirs("data/driving")

	# Get the times to drive to all the bus stops
	get_times(False)

	# Make the walking directory if it does not exist
	if not os.path.exists("data/walking"):
		os.makedirs("data/walking")

	# Get the times to walk to all the bus stops
	get_times(True)