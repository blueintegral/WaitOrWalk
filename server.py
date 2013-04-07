#! /usr/bin/env python
import json
import os
import time
import urllib2
import re
import ConfigParser
from v2methods import *
import generate_distance_matrix

from BeautifulSoup import BeautifulSoup
from flask import Flask, render_template, request

app = Flask(__name__)
weather_data = {"last_updated" : 0, "cold" : False, "rain": False};

# Constants
DEFAULT_MAX_TIME = 1000
COLD_BELOW_TEMP = 60
INTERVAL_CHECK_WEATHER = 300 # 5 minutes

route_list_json = open('data/routeconfig.txt')
route_list = json.load(route_list_json)

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/favicon.ico')
def favicon_response():
	# print "favicon"
	return ""

@app.route('/weather')
def weather():	
	global weather_data	
	if "API_key" not in weather_data: # If the API key doesn't exist, just return weather as normal
		return str(0)
	
	if time.time() - weather_data["last_updated"] > INTERVAL_CHECK_WEATHER:
		weather_data["last_updated"] = time.time() # Reset timer
		url_result = urllib2.urlopen('http://api.wunderground.com/api/' + weather_data["API_key"] + '/conditions/q/30332.json')
		raw_json = url_result.read()
		parsed_json = json.loads(raw_json)

		temperature = parsed_json['current_observation']['temp_f']

		if temperature < COLD_BELOW_TEMP:
			weather_data["cold"] = True # It's cold

		conditions = parsed_json['current_observation']['weather']

		if re.search("Drizzle|Hail|Rain|Thunderstorm", conditions) != None:
			weather_data["rain"] = True # It's raining

	if weather_data["rain"]:
		return str(1)
	elif weather_data["cold"]:
		return str(2)
	else:
		return str(0)

@app.route('/shouldwait')
def start_api():
	# For sanitizing input, catches error and returns nothing.
	try: 
		start_tag = request.args['start']
		end_tag = request.args['end']

		start_title = stop_key_tag_value_title[start_tag]
		end_title = stop_key_tag_value_title[end_tag]	
	except KeyError:
		print "Invalid input for /shouldwait"
		return
	
	(route_tag, direction_tag) = get_route_and_direction(start_title, end_title)

	start_tag = stop_key_route_and_title_value_tag[(route_tag, start_title)]
	end_tag = stop_key_route_and_title_value_tag[(route_tag, end_title)]

	result = should_wait(start_tag, end_tag, route_tag, direction_tag)
	wait_time = get_nextbus_time(start_tag, direction_tag, route_tag)
	return ' '.join([str(result), str(wait_time)])

def should_wait(start_tag, end_tag, route_tag, direction_tag):
	'''Actually makes the decision to wait or walk. Returns 1 for waiting (basically wait for bus), or 0 to walk. '''
	# First get the time to wait until next bus arrives
	wait_time = get_nextbus_time(start_tag, direction_tag, route_tag)
	# Now add drive time to that. This should also include amount of time spent at stops.
	drive_time = get_time_for_method(start_tag, end_tag, "driving") 
	# Add an extra 15 seconds per stop made on the way
	stops = stops_between(start_tag, end_tag, route_tag, direction_tag)
	wait_time = wait_time + drive_time +  0.25*stops # 0.25 minutes or 15 seconds
	
	# Get walk time
	walk_time = get_time_for_method(start_tag, end_tag, "walking")
	
	# Comparing walk and bus times
	if(wait_time < walk_time):
		return 1
	else:
		return 0

def get_nextbus_time(stop, direction, route):
	'''Returns next arrival time for given route and starting point scraped from NextBus. '''
	request = urllib2.Request("http://www.nextbus.com/predictor/simplePrediction.shtml?a=georgia-tech&r="+route+"&d="+ direction +"&s="+stop)
	request.add_header('User-agent','Mozilla/5.0') # Need to fake a user agent or else nextbus will reject the connection

	try: 
		result = urllib2.urlopen(request)
		response = result.read()
	except urllib2.URLError, e:
		# Error in reaching to NextBus servers
		return DEFAULT_MAX_TIME
	
	# Scrape prediction
	soup = BeautifulSoup(response)
	available = True

	if not soup:
		available = False
		result = DEFAULT_MAX_TIME

	if soup.findAll(text='No prediction') != []:
		available = False
		result = DEFAULT_MAX_TIME

	if available:
		prediction = soup.find('td', {'class':"predictionNumberForFirstPred"})
		result = []
		if prediction and prediction.find('div'):
			result = prediction.find('div').string.split(';')[1].strip()

			if result in ["Arriving", "Departing"]:
				result = 0
		else:
			result = DEFAULT_MAX_TIME

	return int(result)

def get_time_for_method(start, end, method):
	try:
		# Get distance matrix for this trip
		raw_json = open("data/" + method + "/" + start + ".json").read()
		parsed_json = json.loads(raw_json)
	except IOError, e:
		print "ERROR - STARTING STOP DOESN'T EXIST - ERROR"
		return	DEFAULT_MAX_TIME

	try:
		end = generate_distance_matrix.key_stop_tag_value_index[end]
	except KeyError:
		print "ERROR - ENDING STOP DOESN'T EXIST - ERROR"
		return	DEFAULT_MAX_TIME	
		
	expected_time = parsed_json["rows"][0]["elements"][end]["duration"]["value"]
	expected_time = int(expected_time) / 60 # Convert to minutes
	return expected_time

if __name__ == '__main__':
	port = int(os.environ.get('PORT', 80))

	config = ConfigParser.ConfigParser()
	config.read("config.ini")

	try:
		weather_data["API_Key"] = config.get("WeatherUnderground", "API_Key")
	except ConfigParser.Error:
		print "Weather Underground API key not set."

	app.debug = os.environ.get('DEBUG', True)

	app.logger.info("Debug is set to: %s" % app.debug)

	app.run(host='0.0.0.0', port=port)
