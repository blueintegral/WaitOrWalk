#! /usr/bin/env python
import json
import os
import time
import urllib2

from BeautifulSoup import BeautifulSoup
from flask import Flask, render_template, request

app = Flask(__name__)

last_weather_download_time = time.time()
cold = False
rain = False

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/how')
def how():
	return render_template('how.html')

@app.route('/weather')
def weather():
	# Check current conditions every 5 minutes
	global last_weather_download_time
	global cold
	global rain

	if time.time() - last_weather_download_time > 300:
		last_weather_download_time = time.time() # Reset timer
		url_result = urllib2.urlopen('http://api.wunderground.com/api/your-api-key-here/conditions/q/30332.json')
		raw_json = url_result.read()
		parsed_json = json.loads(raw_json)

		temperature = parsed_json['current_observation']['temp_f']

		if temperature < 60:
			cold = True # It's cold

		conditions = parsed_json['current_observation']['weather']

		if conditions == 'Light Drizzle' or conditions == 'Heavy Drizzle' or conditions == 'Light Rain' or conditions == 'Heavy Rain' or conditions == 'Light Hail' or conditions == 'Heavy Hail' or conditions == 'Light Rain Mist' or conditions == 'Heavy Rain Mist' or conditions == 'Light Rain Showers' or conditions == 'Heavy Rain Showers' or conditions == 'Light Hail Showers' or conditions == 'Heavy Hail Showers' or conditions == 'Light Small Hail Showers' or conditions == 'Heavy Small Hail Showers' or conditions == 'Light Thunderstorm' or conditions == 'Heavy Thunderstorm' or conditions == 'Light Thunderstorms and Rain' or conditions == 'Heavy Thunderstorms and Rain' or conditions == 'Light Thunderstorms with Hail' or conditions == 'Heavy Thunderstorms with Hail' or conditions == 'Light Thunderstorms with Small Hail' or conditions == 'Heavy Thunderstorms with Small Hail' or conditions == 'Light Freezing Drizzle' or conditions == 'Heavy Freezing Drizzle' or conditions == 'Light Freezing Rain' or conditions == 'Heavy Freezing Rain' or conditions == 'Small Hail':
			rain = True # It's raining

	if rain:
		return str(1)
	elif cold:
		return str(2)
	else:
		return str(0)

@app.route('/shouldwait')
def start_api():
	if 'start' in request.args:
		if 'end' in request.args:
			# The page has passed both a start and end point
			start = request.args['start']
			end = request.args['end']

			route = get_route(start, end)
			wait_result = 1 if should_wait(start, end, route) else 0
			bus_result = get_nextbus_time(start, route)

			return str(wait_result) + " " + str(bus_result)

def get_route(start, end):
	if start == "fitten":
		if end == "fitten" or end == "mcm8th" or end == "8thhemp" or end == "fershemrt" or end == "fersstmrt" or end == "fersatmrt" or end == "ferschmrt" or end == "5thfowl" or end == "tech5th" or end == "tech4th" or end == "techbob" or end == "technorth":
			# Take the red route  
			route = "red"
		else:
			route = "blue"
	if start == "mcm8th":
		if end == "mcm8th" or end == "8thhemp" or end == "fershemrt" or end == "fersstmrt" or end == "fersatmrt" or end == "ferschmrt" or end == "5thfowl" or end == "tech5th" or end == "tech4th" or end == "techbob" or end == "technorth":
			route = "red"
		else:
			route = "blue"
	if start == "8thhemp":
		if end == "8thhemp" or end == "fershemrt" or end == "fersstmrt" or end == "fersatmrt" or end == "ferschmrt" or end == "5thfowl" or end == "tech5th" or end == "tech4th" or end == "techbob" or end == "technorth":
			route = "red"
		else:
			route = "blue"
	if start == "fershemrt":
		#This is the one place that doesn't have both a red and blue stop. You have to take red from here.
		route = "red"
	if start == "fersstmrt":
		if end == "fersstmrt" or end == "fersatmrt" or end == "ferschmrt" or end == "5thfowl" or end == "tech5th" or end == "tech4th" or end == "techbob" or end == "technorth" or end == "norteave_a" or end == "ferstcher":
			route = "red"
		else:
			route = "blue"
	if start == "fersatmrt":
		if end == "fersatmrt" or end == "ferschmrt" or end == "5thfowl" or end == "tech5th" or end == "tech4th" or end == "techbob" or end == "technorth" or end == "norteave_a" or end == "ferstcher" or end == "hubfers":
			route = "red"
		else:
			route = "blue"
	if start == "ferschmrt":
		if end == "ferschmrt" or end == "5thfowl" or end == "tech5th" or end == "tech4th" or end == "techbob" or end == "technorth" or end == "norteave_a" or end == "ferstcher" or end == "hubfers" or end == "centrstud":
			route = "red"
		else:
			route = "blue"
	if start == "5thfowl":
		if end == "5thfowl" or end == "tech5th" or end == "tech4th" or end == "techbob" or end == "technorth" or end == "norteave_a" or end == "ferstcher" or end == "hubfers" or end == "centrstud":
			route = "red"
		else:
			route = "blue"
	if start == "tech5th":
		if end == "tech5th" or end == "tech4th" or end == "techbob" or end == "technorth" or end == "norteave_a" or end == "ferstcher" or end == "hubfers" or end == "centrstud" or end == "765femrt" :
			route = "red"
		else:
			route = "blue"
	if start == "tech4th":
		if end == "tech4th" or end == "techbob" or end == "technorth" or end == "norteave_a" or end == "ferstcher" or end == "hubfers" or end == "centrstud" or end == "765femrt" :
			route = "red"
		else:
			route = "blue"
	if start == "techbob":
		if end == "techbob" or end == "technorth" or end == "norteave_a" or end == "ferstcher" or end == "hubfers" or end == "centrstud" or end == "765femrt" :
			route = "red"
		else:
			route = "blue"
	if start == "technorth":
		if end == "technorth" or end == "norteave_a" or end == "ferstcher" or end == "hubfers" or end == "centrstud" or end == "765femrt" or end == "fitten" or end == "mcm8th" or end == "8thhemp":
			route = "red"
		else:
			route = "blue"
	if start == "northeave_a":
		if end == "norteave_a" or end == "ferstcher" or end == "hubfers" or end == "centrstud" or end == "765femrt" or end == "fitten" or end == "mcm8th" or end == "8thhemp":
			route = "red"
		else:
			route = "blue"
	if start == "ferstcher":
		if end == "ferstcher" or end == "hubfers" or end == "centrstud" or end == "765femrt" or end == "fitten" or end == "mcm8th" or end == "8thhemp" or end == "fershemrt" or end == "fersstmrt":
			route = "red"
		else:
			route = "blue"
	if start == "hubfers":
		if end == "hubfers" or end == "centrstud" or end == "765femrt" or end == "fitten" or end == "mcm8th" or end == "8thhemp" or end == "fershemrt" or end == "fersstmrt" or end == "fersatmrt":
			route = "red"
		else:
			route = "blue"
	if start == "centrstud":
		if end == "centrstud" or end == "765femrt" or end == "fitten" or end == "mcm8th" or end == "8thhemp" or end == "fershemrt" or end == "fersstmrt" or end == "fersatmrt" or end == "ferschmrt":
			route = "red"
		else:
			route = "blue"
	if start == "765femrt":
		if end == "765femrt" or end == "fitten" or end == "mcm8th" or end == "8thhemp" or end == "fershemrt" or end == "fersstmrt" or end == "fersatmrt" or end == "ferschmrt":
			route = "red"
		else:
			route = "blue"

	return route

def get_nextbus_time(start, route):
	'''Returns next arrival time for given route and starting point scraped from NextBus.
	'''
	# Need to fake a user agent or else nextbus will reject the connection
			
	request = urllib2.Request("http://www.nextbus.com/predictor/simplePrediction.shtml?a=georgia-tech&r=" + route + "&s=" + start)
	request.add_header('User-agent','Mozilla/5.0')

	result = urllib2.urlopen(request)
	response = result.read()

	# Scrape prediction
	soup = BeautifulSoup(response)
	available = True

	if not soup:
		available = False
		result = 10000

	if soup.findAll(text='No prediction') != []:
		available = False
		result = 10000

	if available:
		prediction = soup.find('td', {'class':"predictionNumberForFirstPred"})
		result = []
		if prediction and prediction.find('div'):
			result = prediction.find('div').string.split(';')[1].strip()

			if result == "Arriving":
				result = 0
		else:
			result = 10000

	return int(result)

def should_wait(start, end, route):
	'''Actually makes the decision to wait or walk '''
	# First get the time until next bus
	wait_time = get_nextbus_time(start, route)

	# Now add drive time to that. This should also include amount of time spent at stops.
	# Add an extra 15 seconds per stop made on the way
	drive_time = get_time(start, end, "driving") 
	stops = get_stops_between(start, end)

	wait_time = wait_time + drive_time +  0.25 * stops # That's 0.25 minutes

	# Get walk time
	walk_time = get_time(start, end, "walking")

	# Compare two times
	if wait_time < walk_time:
		return True
	else:
		return False

def get_time(start, end, method):
	# Get distance matrix for this trip
	raw_json = open("data/" + method + "/" + start + ".json").read()
	parsed_json = json.loads(raw_json)

	# Figure out destination number
	if end == "fitten":
		end = 0
	if end == "mcm8th":
		end = 1
	if end == "8thhemp":
		end = 2
	if end == "fershemrt":
		end = 3
	if end == "fersstmrt":
		end = 4
	if end == "fersatmrt":
		end = 5
	if end == "ferschmrt":
		end = 6
	if end == "5thfowl":
		end = 7
	if end == "tech5th":
		end = 8
	if end == "tech4th":
		end = 9
	if end == "techbob":
		end = 10
	if end == "technorth":
		end = 11
	if end == "nortavea_a":
		end = 12
	if end == "ferstcher":
		end = 13
	if end == "hubfers":
		end = 14
	if end == "centrstud":
		end = 15
	if end == "765femrt":
		end = 16
		
	expected_time = parsed_json["rows"][0]["elements"][end]["duration"]["value"]
	expected_time = int(expected_time) / 60 # Convert to minutes
	
	return expected_time

def get_stops_between(start, end):
	if start == "fitten":
		start = 1
	if start == "mcm8th":
		start = 2
	if start == "8thhemp":
		start = 3
	if start == "fershemrt":
		start = 4
	if start == "fersstmrt":
		start = 5
	if start == "fersatmrt":
		start = 6
	if start == "ferschmrt":
		start = 7
	if start == "5thfowl":
		start = 8
	if start == "tech5th":
		start = 9
	if start == "tech4th":
		start = 10
	if start == "techbob":
		start = 11
	if start == "technorth":
		start =12
	if start == "nortavea_a":
		start = 13
	if start == "ferstcher":
		start = 14
	if start == "hubfers":
		start = 15
	if start == "centrstud":
		start = 16
	if start == "765femrt":
		start = 17
	
	if end == "fitten":
		end = 1
	if end == "mcm8th":
		end = 2
	if end == "8thhemp":
		end = 3
	if end == "fershemrt":
		end = 4
	if end == "fersstmrt":
		end = 5
	if end == "fersatmrt":
		end = 6
	if end == "ferschmrt":
		end = 7
	if end == "5thfowl":
		end = 8
	if end == "tech5th":
		end = 9
	if end == "tech4th":
		end = 10
	if end == "techbob":
		end = 11
	if end == "technorth":
		end =12
	if end == "nortavea_a":
		end = 13
	if end == "ferstcher":
		end = 14
	if end == "hubfers":
		end = 15
	if end == "centrstud":
		end = 16
	if end == "765femrt":
		end = 17
	
	if end >= start:
		stops = end - start - 1
	else:
		stops = (17 - start) + end -1

	return stops

if __name__ == '__main__':
	port = int(os.environ.get('PORT', 80))

	app.debug = os.environ.get('DEBUG', True)

	app.logger.info("Debug is set to: %s" % app.debug)

	app.run(host='0.0.0.0', port=port)
