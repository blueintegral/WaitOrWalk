import json
import pprint
import urllib2

output_json = json.load(open('data/routeconfig.txt'))

# key: stop_tag, value: rds
shared_stops = dict()

# Gets the stop title from the stop tag
def get_stop_details(stop_tag, stops):
	for stop in stops:
		if stop["tag"] == stop_tag:
			return stop["title"]

def add_to_shared_stops(key, value):
	if key in shared_stops:
		shared_stops[key].append(value)
	else:
		shared_stops[key] = [value]

# (route, direction, stop)
def construct_shared_stops():
	for i in output_json["route"]:
		for j in i["direction"]:
			for k in j["stop"]:
				stop_title = get_stop_details(k["tag"], i["stop"])
				add_to_shared_stops(stop_title, (i["tag"], j["tag"], k["tag"]))

def get_possible_routes_and_directions(start_title, end_title):
	start_set = set()
	stop_set = set()

	for (r,d,s) in shared_stops[start_title]:
		start_set.add((r,d))

	for (r,d,s) in shared_stops[end_title]:
		stop_set.add((r,d))
	return start_set.intersection(stop_set).pop()

def stops_between(start, end, route, direction):
	start_index = 0
	end_index = 0
	num_stops = 0
	for r in output_json["route"]:
		if r["tag"] == route:
			for d in r["direction"]:
				if d["tag"] == direction:
					num_stops = len(d["stop"])
					for stop_index in range(len(d["stop"])):
						if start == d["stop"][stop_index]["tag"]:
							start_index = stop_index
						if end == d["stop"][stop_index]["tag"]:
							end_index = stop_index
	if start_index <= end_index:
		return end_index - start_index
	else:
		return end_index + (num_stops - start_index)
	# print(start_index, end_index)

def get_NextBus_time(stop, direction, route):
	print (route, direction, stop)
	response_json = json.load(urllib2.urlopen('http://desolate-escarpment-6039.herokuapp.com/bus/get?route='+route+'&direction='+direction+'&stop='+stop))
	print ""

	print response_json
	print ""
	if len(response_json["predictions"]) == 0:
		return 1000
	else:
		return int(response_json["predictions"][0])

def stop_tag_to_stop_title(stop_tag):
	for stop_title in shared_stops:
		for stop in shared_stops[stop_title]:
			if stop_tag == stop[2]:
				return stop_title

def stop_title_to_stop_tag_for_route(stop_title, route_tag):
	for stop_tuple in shared_stops[stop_title]:
		if stop_tuple[0] == route_tag:
			return stop_tuple[2]

construct_shared_stops()
# print stop_tag_to_stop_title("fitten_a")
# print(shared_stops["Fitten Hall"])

# print stop_title_to_stop_tag_for_route("Fitten Hall", "blue")
# print get_possible_routes_and_directions("Transit Hub", "Klaus Building")
# stops_between("hubfers", "5thfowl", "red", "Clockwise" )
# print(get_NextBus_time("red", "Clockwise", "fitten"))
