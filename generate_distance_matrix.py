#! /usr/bin/env python
import json
import urllib2
import time
import os
import pprint


"""This script will call Google Maps to calculate the time to walk between every combination of bus stops and the time to drive between every combination of bus stops.
We can't do this live in the app because of rate limiting and because Google requires you show a map.
"""

data_json = json.load(open('data/routeconfig.txt'))

def construct_bus_stops():
	route_set = set()
	for route in data_json["route"]:
		stop_dict = dict()
		for stop in route["stop"]:
			stop_dict[stop["tag"]] = (stop["title"], stop["lat"], stop["lon"])
		for direction in route["direction"]:
			for stop in direction["stop"]:
				(title, lat, lon) = stop_dict[stop["tag"]]
				route_set.add((str(stop["tag"]), "{0},{1}".format(lat, lon)))
	return list(route_set)
	
bus_stops = construct_bus_stops()

key_stop_tag_value_index = dict()
for i in range(len(bus_stops)):
	(stop_tag, coord) = bus_stops[i]
	key_stop_tag_value_index[stop_tag] = i

def get_times(mode):
	"""Get the travel time either walking or driving to all the bus stops.
	We'll have to go through each of the N stops with one origin and all N-1 other stops as destinations. 
	This will result in fitten.json, mcm8th.json, etc...
	Then you can access the JSON for the specific starting point, find the destination, and get the travel time.
	Rate limiting prevents doing this in a more elegant way with fewer API calls.
	"""

	# Mode is either walking or driving

	for index, bus_stop in enumerate(bus_stops):
		print "Fetching " + bus_stop[0] + " " + mode + " times..."
		
		if os.path.isfile("data/" + mode + "/" + bus_stop[0] + ".json"):
			print "Path information already exists" # Skipping over routes that already exist
			continue

		coordinates_formatted = "|".join([coordinate for (stop_tag, coordinate) in bus_stops])
		
		url = "http://maps.googleapis.com/maps/api/distancematrix/json?origins=" + bus_stop[1] + "&destinations=" + coordinates_formatted + "&sensor=false&mode=" + mode
		
		# Write the data to the file
		json_response = json.load(urllib2.urlopen(url))

		with open("data/" + mode + "/" + bus_stop[0] + ".json", 'w') as output_file:
			json.dump(json_response, output_file)

		# Wait for rate limit
		time.sleep(15)

if __name__ == '__main__':
	'''This can take a long time, the server will throw a OVER_QUERY_LIMIT if there are many requests'''

	# Make the driving directory if it does not exist
	if not os.path.exists("data/driving"):
		os.makedirs("data/driving")

	# Get the times to drive to all the bus stops
	get_times("driving")

	# Make the walking directory if it does not exist
	if not os.path.exists("data/walking"):
		os.makedirs("data/walking")

	# Get the times to walk to all the bus stops
	get_times("walking")