#! /usr/bin/env python
import json
import os
import time
import urllib2
import re
from v2methods import *

from BeautifulSoup import BeautifulSoup
from flask import Flask, render_template, request

app = Flask(__name__)

last_weather_download_time = time.time()
cold = False
rain = False

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

	if time.time() - last_weather_download_time > 300:
		last_weather_download_time = time.time() # Reset timer
		url_result = urllib2.urlopen('http://api.wunderground.com/api/your-api-key-here/conditions/q/30332.json')
		raw_json = url_result.read()
		parsed_json = json.loads(raw_json)

		temperature = parsed_json['current_observation']['temp_f']

		if temperature < 60:
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
	if (not ('start' in request.args and 'end' in request.args)):
		return
	#the page has passed both a start and end point
	start_tag = request.args['start']
	end_tag = request.args['end']
	#Sanitize input
	if (not (any (start_tag in s["tag"] for s in route_list["route"][0]["stop"]))):
		return
	if (not (any (end_tag in s["tag"] for s in route_list["route"][0]["stop"]))):
		return
	 
	start_title = stop_key_tag_value_title[start_tag]
	end_title = stop_key_tag_value_title[end_tag]

	(route_tag, direction_tag) = get_route_and_direction(start_title, end_title)

	start_tag = stop_key_route_and_title_value_tag[(route_tag, start_title)]
	end_tag = stop_key_route_and_title_value_tag[(route_tag, end_title)]


	# print (start_tag, end_tag, route_tag)

	result = should_wait(start_tag, end_tag, route_tag, direction_tag)
	wait_time = get_nextbus_time(start_tag, direction_tag, route_tag)
	return  ' '.join([str(result), str(wait_time)])

def should_wait(start_tag, end_tag, route_tag, direction_tag):
	'''Actually makes the decision to wait or walk '''
	#First get the time until next bus
	wait_time = get_nextbus_time(start_tag, direction_tag, route_tag)
	#Now add drive time to that. This should also include amount of time spent at stops.
	#Add an extra 15 seconds per stop made on the way
	drive_time = get_time(start_tag, end_tag, "driving") 
	stops = stops_between(start_tag, end_tag, route_tag, direction_tag)
	wait_time = wait_time + drive_time +  0.25*stops #that's .25 minutes
	#Get walk time
	walk_time = get_time(start_tag, end_tag, "walking")
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

def get_time(start, end, method):
	#Get distance matrix for this trip
	#	Needs to be fixed when walking data has all stops information
	
	if not os.path.isfile("data/"+method+"/"+start+".json"):
		print "ERROR STARTING STOP DOESN'T EXIST ERROR"
		return	1000

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

	# Needs to be fixed when walking data has all stops information
	if isinstance(end, str) or isinstance(end, unicode):
		print "ERROR ENDING STOP DOESN'T EXIST ERROR"
		return	1000	
		
	expected_time = parsed_json["rows"][0]["elements"][end]["duration"]["value"]
	expected_time = int(expected_time) / 60 # Convert to minutes
	return expected_time

if __name__ == '__main__':
	port = int(os.environ.get('PORT', 80))

	app.debug = os.environ.get('DEBUG', True)

	app.logger.info("Debug is set to: %s" % app.debug)

	app.run(host='0.0.0.0', port=port)
