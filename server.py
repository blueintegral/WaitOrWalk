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

last_weather_download_time = time.time()
cold = False
rain = False

wunderground_api_key = ""

# Constants
DEFAULT_MAX_TIME = 1000
COLD_BELOW_TEMP = 60
INTERVAL_CHECK_WEATHER = 300

route_list_json = open('data/routeconfig.txt')
route_list = json.load(route_list_json)

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/weather')
def weather():
	# Check current conditions every 5 minutes
	global last_weather_download_time
	global cold
	global rain

	if not wunderground_api_key: # If the API key doesn't exist, just return weather as normal
		return str(0)
	
	if time.time() - last_weather_download_time > INTERVAL_CHECK_WEATHER:
		last_weather_download_time = time.time() # Reset timer
		url_result = urllib2.urlopen('http://api.wunderground.com/api/' + wunderground_api_key + '/conditions/q/30332.json')
		raw_json = url_result.read()
		parsed_json = json.loads(raw_json)

		temperature = parsed_json['current_observation']['temp_f']

		if temperature < COLD_BELOW_TEMP:
			cold = True # It's cold

		conditions = parsed_json['current_observation']['weather']

		if re.search("Drizzle|Hail|Rain|Thunderstorm", conditions) != None:
			rain = True # It's raining

	if rain:
		return str(1)
	elif cold:
		return str(2)
	else:
		return str(0)

@app.route('/shouldwait')
def start_api():
	if not ('start' in request.args and 'end' in request.args):
		return
	# the page has passed both a start and end point
	start_tag = request.args['start']
	end_tag = request.args['end']
	
	# Sanitize input
	if not (start_tag in stop_key_tag_value_title and end_tag in stop_key_tag_value_title):
		return
		 
	start_title = stop_key_tag_value_title[start_tag]
	end_title = stop_key_tag_value_title[end_tag]

	(route_tag, direction_tag) = get_route_and_direction(start_title, end_title)

	start_tag = stop_key_route_and_title_value_tag[(route_tag, start_title)]
	end_tag = stop_key_route_and_title_value_tag[(route_tag, end_title)]

	# print (start_tag, end_tag, route_tag)

	result = should_wait(start_tag, end_tag, route_tag, direction_tag)
	wait_time = get_nextbus_time(start_tag, direction_tag, route_tag)
	return ' '.join([str(result), str(wait_time)])

def should_wait(start_tag, end_tag, route_tag, direction_tag):
	'''Actually makes the decision to wait or walk. Returns 1 for waiting (basically wait for bus), or 0 to walk '''
	# First get the time until next bus
	wait_time = get_nextbus_time(start_tag, direction_tag, route_tag)
	# Now add drive time to that. This should also include amount of time spent at stops.
	# Add an extra 15 seconds per stop made on the way
	drive_time = get_time(start_tag, end_tag, "driving") 
	print ("Drive time:" , drive_time)
	stops = stops_between(start_tag, end_tag, route_tag, direction_tag)
	print ("Stops Time",	 0.25*stops)
	print ("Wait time", wait_time)
	wait_time = wait_time + drive_time +  0.25*stops # that's .25 minutes
	#Get walk time
	walk_time = get_time(start_tag, end_tag, "walking")
	
	print ("Wait:", wait_time, "Walk:", walk_time)
	#compare two times
	if(wait_time < walk_time):
		return 1
	else:
		return 0


def get_nextbus_time(stop, direction, route):
	'''Returns next arrival time for given route and starting point scraped from NextBus. '''
	request = urllib2.Request("http://www.nextbus.com/predictor/simplePrediction.shtml?a=georgia-tech&r="+route+"&d="+ direction +"&s="+stop)
	request.add_header('User-agent','Mozilla/5.0') # Need to fake a user agent or else nextbus will reject the connection

	result = urllib2.urlopen(request)
	response = result.read()

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

			if result == "Arriving" or result == "Departing":
				result = 0
		else:
			result = DEFAULT_MAX_TIME

	return int(result)

def get_time(start, end, method):
	# Get distance matrix for this trip
	
	# This might not be needed anymore
	if not os.path.isfile("data/" + method + "/" + start + ".json"):
		print "ERROR STARTING STOP DOESN'T EXIST ERROR"
		return	DEFAULT_MAX_TIME

	# Get distance matrix for this trip
	raw_json = open("data/" + method + "/" + start + ".json").read()
	parsed_json = json.loads(raw_json)

	# This might not be needed anymore
	if end not in generate_distance_matrix.key_stop_tag_value_index:
		print "ERROR ENDING STOP DOESN'T EXIST ERROR"
		return	DEFAULT_MAX_TIME	

	end = generate_distance_matrix.key_stop_tag_value_index[end]
		
	expected_time = parsed_json["rows"][0]["elements"][end]["duration"]["value"]
	expected_time = int(expected_time) / 60 # Convert to minutes
	return expected_time

if __name__ == '__main__':
	port = int(os.environ.get('PORT', 80))

	config = ConfigParser.ConfigParser()
	config.read("config.ini")

	try:
		wunderground_api_key = config.get("WeatherUnderground", "API_Key")
	except ConfigParser.Error:
		print "Weather Underground API key not set."

	app.debug = os.environ.get('DEBUG', True)

	app.logger.info("Debug is set to: %s" % app.debug)

	app.run(host='0.0.0.0', port=port)
