import json
import pprint
import urllib2
import generate_distance_matrix

data_json = json.load(open('data/routeconfig.txt'))

''' 
Process for looking up the times for walking and bus:
	Get start and stop locations from get request which are stop tags
	Convert those to stop titles
	Find the routes that service both stop titles
	Get the corresponding stop titles from the stop tags for the route chosen
	Call the NextBus API with the stop tags
	Call own API with the stop tags
'''

# Used to find all the routes/directions that share a certain stop
# key: stop_title, value: (route_tag, direction_tag, stop_tag).
shared_stops = dict()
# key: route tag, value: {"direction": {"direction_tag": {"stop_tag": stop_index}}}
route_information = dict()
# key: stop tag, value: stop title
stop_key_tag_value_title = dict()
# key: (route,stop title), value: stop tag
stop_key_route_and_title_value_tag = dict()

def construct_shared_stops():
	for route in data_json["route"]:
		for direction in route["direction"]:
			for stop in direction["stop"]:
				key = stop_key_tag_value_title[stop["tag"]]
				value = (route["tag"], direction["tag"], stop["tag"])  # (Route,Direction,Stop)
				if key in shared_stops:
					shared_stops[key].append(value)
				else:
					shared_stops[key] = [value]

def construct_route_information():
	for route in data_json["route"]:
		current_route_info = dict()
		direction_all_dict = dict()

		for stop in route["stop"]:
			stop_key_tag_value_title[stop["tag"]] = stop["title"]
			stop_key_route_and_title_value_tag[(route["tag"], stop["title"])] = stop["tag"]
		
		for direction in route["direction"]:
			current_direction = dict()
			for stop_index in range(len(direction["stop"])):
				current_stop = direction["stop"][stop_index]
				current_direction[current_stop["tag"]] = stop_index
			direction_all_dict[direction["tag"]] = current_direction
		current_route_info["direction"] = direction_all_dict
		route_information[route["tag"]] = current_route_info
	
# Checks which routes/directions service the start/end stops titles
def get_route_and_direction(start_title, end_title):
	start_set = set()
	end_set = set()

	for (r, d, s) in shared_stops[start_title]:
		start_set.add((r, d))

	for (r, d, s) in shared_stops[end_title]:
		end_set.add((r, d))

	# Returns one of possible choices	
	possible_routes_directions = start_set.intersection(end_set)
	new_list= list()
	
	# Returning the route with the least number of stops, this isn't ideal. A better solution needs to exist for
	# when two routes service the start/end locations
	for (r, d) in possible_routes_directions:
		num_stops = stops_between(stop_title_to_stop_tag_for_route(start_title, r), stop_title_to_stop_tag_for_route(end_title, r), r, d)
		new_list.append((num_stops, r, d))
	(num_stops, r, d) = sorted(new_list, reverse=True).pop()

	return (r,d)

def stops_between(start_tag, end_tag, route_tag, direction_tag):
	num_stops = len(route_information[route_tag]["direction"][direction_tag])

	start_index = route_information[route_tag]["direction"][direction_tag][start_tag]
	end_index = route_information[route_tag]["direction"][direction_tag][end_tag]

	if start_index <= end_index:
		return end_index - start_index
	else:
		# For when the start index occurs after end index. 
		# So need to count start -> number of stops, and then how many stops are in end_index
		return end_index + (num_stops - start_index)

# Doesn't really need to be a function
def stop_title_to_stop_tag_for_route(stop_title, route_tag):
	return stop_key_route_and_title_value_tag[(route_tag,stop_title)]

construct_route_information()
construct_shared_stops()